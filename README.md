\documentclass[11pt, a4paper]{article}

% --- UNIVERSAL PREAMBLE BLOCK ---
\usepackage[a4paper, top=2.5cm, bottom=2.5cm, left=2cm, right=2cm]{geometry}
\usepackage{fontspec}

\usepackage[english, bidi=basic, provide=*]{babel}

\babelprovide[import, onchar=ids fonts]{english}

% Set default/Latin font to Sans Serif in the main (rm) slot
\babelfont{rm}{Noto Sans}

% Add because main language is not English (Standard Protocol)
\usepackage{enumitem}
\setlist[itemize]{label=-}

% Packages for code blocks and formatting
\usepackage{verbatim}
\usepackage{xcolor}
\usepackage{titlesec}

% Hyperref should be last
\usepackage[hidelinks]{hyperref}

\title{\textbf{Bite-Sized Learning App (MVP)}}
\author{}
\date{}

\begin{document}

\maketitle

\noindent A hybrid learning platform that combines the addictive simplicity of short-form video feeds (like Instagram Reels/TikTok) with structured micro-learning courses.

\section*{Features}

\begin{itemize}
    \item \textbf{Learning Feed:} Scrollable video feed with auto-play.
    \item \textbf{Interactive:} Like, comment, and bookmark videos.
    \item \textbf{Creators:} Upload short educational videos.
    \item \textbf{Micro-Courses:} Organize saved videos into specific subjects (Maths, Coding, etc.).
    \item \textbf{User Profiles:} Track streaks, XP, followers, and manage uploads.
\end{itemize}

\section*{Prerequisites}

\noindent Before running the app, ensure you have the following installed:

\begin{enumerate}
    \item \textbf{Python} (3.x or higher)
    \item \textbf{MySQL Server} (and MySQL Workbench for easier management)
\end{enumerate}

\section*{Installation \& Setup}

\subsection*{1. Download the Project}

\noindent Ensure your folder structure looks like this:

\begin{verbatim}
/bite-sized-learning
├── app.py
├── requirements.txt
├── setup_database.py
├── /static
│   └── /uploads
└── /templates
    ├── index.html
    └── login.html
\end{verbatim}

\subsection*{2. Install Dependencies}

\noindent Open your terminal (Command Prompt or Terminal) in the project folder and run:

\begin{verbatim}
pip install -r requirements.txt
\end{verbatim}

\subsection*{3. IMPORTANT: Configure Database Password}

\noindent You must connect the Python app to your local MySQL server.

\begin{enumerate}
    \item Open the file \texttt{app.py} in your code editor.
    \item Locate the \texttt{db\_config} dictionary (usually near the top, around line 10).
    \item Update the \texttt{'password'} field with your actual MySQL root password.
\end{enumerate}

\noindent \textbf{Example in \texttt{app.py}:}

\begin{verbatim}
# --- CONFIGURATION ---
db_config = {
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD_HERE',  # <--- CHANGE THIS!
    'host': 'localhost',
    'database': 'bite_sized_learning'
}
\end{verbatim}

\noindent \textit{(If your MySQL user is not 'root', change that too).}

\section*{How to Run}

\subsection*{Option A: First Time Run (Auto-Setup)}

\noindent The application is designed to automatically create the database and tables when you run it for the first time.

\begin{enumerate}
    \item Run the application:
    \begin{verbatim}
python app.py
    \end{verbatim}
    \item Look for the message: \texttt{Database \& Tables initialized successfully.}
    \item Open your browser and go to: \url{http://127.0.0.1:5000}
\end{enumerate}

\subsection*{Option B: Hard Reset (If you face DB errors)}

\noindent If you see "Table doesn't exist" errors or want to wipe all data and start fresh:

\begin{enumerate}
    \item Open \texttt{setup\_database.py}.
    \item Ensure the password inside \texttt{setup\_database.py} is also correct.
    \item Run the reset script:
    \begin{verbatim}
python setup_database.py
    \end{verbatim}
    \item Then run the main app:
    \begin{verbatim}
python app.py
    \end{verbatim}
\end{enumerate}

\section*{How to Use}

\begin{enumerate}
    \item \textbf{Login/Signup:} Create an account (e.g., username "Alex", password "123").
    \item \textbf{Upload:} Click the \textbf{+} button to upload a \texttt{.mp4} video from your computer.
    \item \textbf{Feed:} Scroll through videos. Click the \textbf{Heart} to like or the \textbf{Star} to bookmark.
    \item \textbf{Profile:} Click the \textbf{User Icon} to see your stats, uploads, and create Courses.
\end{enumerate}

\section*{Known Limitations \& Future Roadmap}

\noindent While this MVP demonstrates the core functionality, the following features are currently placeholders or planned for future updates:

\begin{itemize}
    \item \textbf{Search Functionality:} The search icon is present in the navigation bar, but the backend search logic is not yet implemented.
    \item \textbf{Direct Messaging:} The "Message" button on public profiles currently displays a "Coming Soon" alert. Real-time chat is planned for future versions.
    \item \textbf{AI Integration:} Features such as AI-generated quizzes and summaries are part of the concept but are not currently connected to an LLM API.
    \item \textbf{Video Optimization:} Uploaded videos are stored in their raw format. Future versions will include transcoding for optimized streaming performance.
\end{itemize}

\end{document}
