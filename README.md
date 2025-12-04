📱 Bite-Sized Learning App (MVP)

A hybrid learning platform that combines the addictive simplicity of short-form video feeds (like Instagram Reels/TikTok) with structured micro-learning courses.

🚀 Features

Learning Feed: Scrollable video feed with auto-play.

Interactive: Like, comment, and bookmark videos.

Creators: Upload short educational videos.

Micro-Courses: Organize saved videos into specific subjects (Maths, Coding, etc.).

User Profiles: Track streaks, XP, followers, and manage uploads.

🛠️ Prerequisites

Before running the app, ensure you have the following installed:

Python (3.x or higher)

MySQL Server (and MySQL Workbench for easier management)

⚙️ Installation & Setup

1. Download the Project

Ensure your folder structure looks like this:

/bite-sized-learning
├── app.py
├── requirements.txt
├── setup_database.py
├── /static
│   └── /uploads
└── /templates
    ├── index.html
    └── login.html


2. Install Dependencies

Open your terminal (Command Prompt or Terminal) in the project folder and run:

pip install -r requirements.txt


3. ⚠️ IMPORTANT: Configure Database Password

You must connect the Python app to your local MySQL server.

Open the file app.py in your code editor.

Locate the db_config dictionary (usually near the top, around line 10).

Update the 'password' field with your actual MySQL root password.

Example in app.py:

# --- CONFIGURATION ---
db_config = {
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD_HERE',  # <--- CHANGE THIS!
    'host': 'localhost',
    'database': 'bite_sized_learning'
}


(If your MySQL user is not 'root', change that too).

🏃‍♂️ How to Run

Option A: First Time Run (Auto-Setup)

The application is designed to automatically create the database and tables when you run it for the first time.

Run the application:

python app.py


Look for the message: ✅ Database & Tables initialized successfully.

Open your browser and go to: http://127.0.0.1:5000

Option B: Hard Reset (If you face DB errors)

If you see "Table doesn't exist" errors or want to wipe all data and start fresh:

Open setup_database.py.

Ensure the password inside setup_database.py is also correct.

Run the reset script:

python setup_database.py


Then run the main app:

python app.py


📱 How to Use

Login/Signup: Create an account (e.g., username "Alex", password "123").

Upload: Click the + button to upload a .mp4 video from your computer.

Feed: Scroll through videos. Click the Heart to like or the Star to bookmark.

Profile: Click the User Icon to see your stats, uploads, and create Courses.
