import os
import uuid
from flask import Flask, render_template, jsonify, request
import mysql.connector
import json
from datetime import date, timedelta

app = Flask(__name__)

# --- CONFIGURATION ---
# ⚠️ Ensure this password matches your MySQL setup
db_config = {
    'user': 'root',
    'password': '500124743', 
    'host': 'localhost',
    'database': 'bite_sized_learning'
}

# --- UPLOAD CONFIGURATION ---
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- DATABASE CONNECTION ---
def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"❌ Connection Error: {err}")
        return None

# --- AUTO-INITIALIZE TABLES ---
def init_db():
    """Creates database and tables automatically on startup"""
    try:
        # Connect to Server directly to check/create DB
        conn = mysql.connector.connect(
            user=db_config['user'], 
            password=db_config['password'], 
            host=db_config['host']
        )
        cursor = conn.cursor()
        
        # Create DB
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        cursor.execute(f"USE {db_config['database']}")
        
        # 1. Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(255),
            level VARCHAR(50) DEFAULT 'Novice',
            xp INT DEFAULT 0,
            streak INT DEFAULT 0,
            last_active DATE
        )
        """)

        # 2. Videos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(100),
            creator VARCHAR(50),
            description TEXT,
            tags VARCHAR(255),
            video_url VARCHAR(255),
            likes INT DEFAULT 0,
            is_course BOOLEAN DEFAULT FALSE,
            modules_json JSON DEFAULT NULL
        )
        """)

        # 3. Likes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            video_id INT,
            UNIQUE KEY unique_user_video (user_id, video_id)
        )
        """)

        # 4. Courses
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(100),
            subject VARCHAR(50),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 5. Bookmarks
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            video_id INT,
            course_id INT DEFAULT NULL,
            UNIQUE KEY unique_bookmark (user_id, video_id)
        )
        """)

        # 6. Followers
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS followers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            follower_id INT,
            followed_id INT,
            UNIQUE KEY unique_follow (follower_id, followed_id)
        )
        """)

        # 7. Comments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            video_id INT,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Migration check for streak
        try: cursor.execute("ALTER TABLE users ADD COLUMN last_active DATE")
        except: pass

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database & Tables initialized successfully.")
    except Exception as e:
        print(f"❌ Init DB Error: {e}")

# --- HELPER: STREAK LOGIC ---
def update_streak(user_id, conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT streak, last_active FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    if not user: return 0
    
    today = date.today()
    last = user['last_active']
    current_streak = user['streak'] or 0
    
    if last == today:
        return current_streak 
    
    if last == today - timedelta(days=1):
        new_streak = current_streak + 1
    else:
        new_streak = 1 
        
    cursor.execute("UPDATE users SET streak = %s, last_active = %s WHERE id = %s", (new_streak, today, user_id))
    conn.commit()
    return new_streak

# --- HELPER: STATS ---
def get_user_stats(cursor, user_id):
    cursor.execute("SELECT COUNT(*) as c FROM followers WHERE followed_id = %s", (user_id,))
    followers = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM followers WHERE follower_id = %s", (user_id,))
    following = cursor.fetchone()['c']
    return {'followers': followers, 'following': following}

# --- PAGE ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

# --- AUTH ROUTES ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        today = date.today()
        cursor.execute("INSERT INTO users (username, password, level, xp, streak, last_active) VALUES (%s, %s, 'Novice', 0, 1, %s)", 
                       (data['username'], data['password'], today))
        conn.commit()
        return jsonify({'success': True, 'user_id': cursor.lastrowid, 'username': data['username']})
    except: 
        return jsonify({'success': False, 'message': 'Username exists'})
    finally: conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (data['username'], data['password']))
    user = cursor.fetchone()
    
    if user:
        update_streak(user['id'], conn)
        conn.close()
        return jsonify({'success': True, 'user_id': user['id'], 'username': user['username']})
    conn.close()
    return jsonify({'success': False, 'message': 'Invalid credentials'})

# --- FEED & UPLOAD ---

@app.route('/api/feed')
def get_feed():
    conn = get_db_connection()
    if not conn: return jsonify([])
    cursor = conn.cursor(dictionary=True)
    user_id = request.headers.get('X-User-ID')
    
    try:
        cursor.execute("SELECT * FROM videos ORDER BY id DESC")
        videos = cursor.fetchall()
        
        liked_ids = set()
        bookmarked_ids = set()
        if user_id:
            cursor.execute("SELECT video_id FROM video_likes WHERE user_id = %s", (user_id,))
            liked_ids = {row['video_id'] for row in cursor.fetchall()}
            cursor.execute("SELECT video_id FROM bookmarks WHERE user_id = %s", (user_id,))
            bookmarked_ids = {row['video_id'] for row in cursor.fetchall()}
        
        for video in videos:
            video['liked_by_me'] = video['id'] in liked_ids
            video['bookmarked_by_me'] = video['id'] in bookmarked_ids
            if video.get('modules_json'):
                try: video['modules'] = json.loads(video['modules_json'])
                except: video['modules'] = []
            else: video['modules'] = []
        return jsonify(videos)
    finally: conn.close()

@app.route('/api/upload', methods=['POST'])
def upload_video():
    user_id = request.headers.get('X-User-ID')
    if not user_id: return jsonify({'success': False})
    file = request.files['video']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    creator = cursor.fetchone()['username']
    
    filename = str(uuid.uuid4()) + ".mp4"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    url = f"/{UPLOAD_FOLDER}/{filename}"
    
    cursor.execute("""INSERT INTO videos (user_id, title, creator, description, tags, video_url) 
                      VALUES (%s, %s, %s, %s, %s, %s)""", 
                   (user_id, request.form['title'], creator, request.form['description'], request.form['tags'], url))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# --- PROFILE & STATS ---

@app.route('/api/profile')
def get_profile():
    user_id = request.headers.get('X-User-ID')
    if not user_id: return jsonify({})
    
    conn = get_db_connection()
    update_streak(user_id, conn) # Update streak on profile view
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    user.update(get_user_stats(cursor, user_id))
    
    cursor.execute("SELECT * FROM videos WHERE user_id = %s ORDER BY id DESC", (user_id,))
    my_videos = cursor.fetchall()
    
    cursor.execute("SELECT * FROM courses WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    courses = cursor.fetchall()
    
    cursor.execute("""SELECT v.*, b.course_id FROM bookmarks b 
                      JOIN videos v ON b.video_id = v.id WHERE b.user_id = %s ORDER BY b.id DESC""", (user_id,))
    bookmarks = cursor.fetchall()
    
    conn.close()
    return jsonify({'user': user, 'videos': my_videos, 'courses': courses, 'bookmarks': bookmarks})

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    user_id = request.headers.get('X-User-ID')
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = %s, level = %s WHERE id = %s", 
                   (data['username'], data['level'], user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/user/<int:other_id>')
def public_profile(other_id):
    curr_id = request.headers.get('X-User-ID')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, username, level, xp, streak FROM users WHERE id = %s", (other_id,))
    user = cursor.fetchone()
    if not user: return jsonify({'success': False})
    
    user.update(get_user_stats(cursor, other_id))
    
    user['is_following'] = False
    if curr_id:
        cursor.execute("SELECT 1 FROM followers WHERE follower_id = %s AND followed_id = %s", (curr_id, other_id))
        if cursor.fetchone(): user['is_following'] = True
        
    cursor.execute("SELECT * FROM videos WHERE user_id = %s ORDER BY id DESC", (other_id,))
    videos = cursor.fetchall()
    conn.close()
    return jsonify({'success': True, 'user': user, 'videos': videos})

# --- INTERACTIONS ---

@app.route('/api/like/<int:video_id>', methods=['POST'])
def like(video_id):
    uid = request.headers.get('X-User-ID')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM video_likes WHERE user_id=%s AND video_id=%s", (uid, video_id))
    if cur.fetchone():
        cur.execute("DELETE FROM video_likes WHERE user_id=%s AND video_id=%s", (uid, video_id))
        cur.execute("UPDATE videos SET likes=GREATEST(likes-1,0) WHERE id=%s", (video_id,))
        act = 'unliked'
    else:
        cur.execute("INSERT INTO video_likes (user_id, video_id) VALUES (%s, %s)", (uid, video_id))
        cur.execute("UPDATE videos SET likes=likes+1 WHERE id=%s", (video_id,))
        act = 'liked'
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'action': act})

@app.route('/api/comments/<int:vid>', methods=['GET'])
def get_comments(vid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT c.text, u.username FROM comments c 
                      JOIN users u ON c.user_id = u.id WHERE c.video_id = %s ORDER BY c.id DESC""", (vid,))
    res = cursor.fetchall()
    conn.close()
    return jsonify(res)

@app.route('/api/comments/<int:vid>', methods=['POST'])
def add_comment(vid):
    uid = request.headers.get('X-User-ID')
    txt = request.json.get('text')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (user_id, video_id, text) VALUES (%s, %s, %s)", (uid, vid, txt))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/follow/<int:oid>', methods=['POST'])
def follow(oid):
    uid = request.headers.get('X-User-ID')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM followers WHERE follower_id=%s AND followed_id=%s", (uid, oid))
    if cursor.fetchone():
        cursor.execute("DELETE FROM followers WHERE follower_id=%s AND followed_id=%s", (uid, oid))
        act = 'unfollowed'
    else:
        cursor.execute("INSERT INTO followers (follower_id, followed_id) VALUES (%s, %s)", (uid, oid))
        act = 'followed'
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'action': act})

# --- COURSES & BOOKMARKS ---

@app.route('/api/courses', methods=['POST'])
def add_course():
    uid = request.headers.get('X-User-ID')
    d = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO courses (user_id, title, subject) VALUES (%s, %s, %s)", (uid, d['title'], d['subject']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/courses/<int:cid>', methods=['DELETE'])
def del_course(cid):
    uid = request.headers.get('X-User-ID')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM courses WHERE id=%s AND user_id=%s", (cid, uid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/courses/<int:cid>/videos')
def get_course_videos(cid):
    uid = request.headers.get('X-User-ID')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT v.* FROM bookmarks b JOIN videos v ON b.video_id = v.id 
                      WHERE b.user_id=%s AND b.course_id=%s""", (uid, cid))
    vids = cursor.fetchall()
    conn.close()
    return jsonify({'success': True, 'videos': vids})

@app.route('/api/bookmark/<int:vid>', methods=['POST'])
def bookmark(vid):
    uid = request.headers.get('X-User-ID')
    cid = request.json.get('course_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM bookmarks WHERE user_id=%s AND video_id=%s", (uid, vid))
    if cursor.fetchone():
        if cid: cursor.execute("UPDATE bookmarks SET course_id=%s WHERE user_id=%s AND video_id=%s", (cid, uid, vid)); act='updated'
        else: cursor.execute("DELETE FROM bookmarks WHERE user_id=%s AND video_id=%s", (uid, vid)); act='removed'
    else:
        cursor.execute("INSERT INTO bookmarks (user_id, video_id, course_id) VALUES (%s, %s, %s)", (uid, vid, cid)); act='added'
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'action': act})

@app.route('/api/delete/<int:vid>', methods=['POST'])
def delete_video(vid):
    uid = request.headers.get('X-User-ID')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT video_url FROM videos WHERE id=%s AND user_id=%s", (vid, uid))
    res = cursor.fetchone()
    if res:
        try: os.remove(res['video_url'].lstrip('/'))
        except: pass
        cursor.execute("DELETE FROM videos WHERE id=%s", (vid,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    init_db()
    print("🚀 Server running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)