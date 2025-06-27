# utils/models.py

import sqlite3
from datetime import datetime

# ✅ Path to DB file
DB_PATH = 'resume_data.db'

# ✅ Create the resumes table if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_text TEXT,
            feedback TEXT,
            score INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Save resume details to DB
def save_resume_to_db(resume_text, feedback, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_text = "\n".join(feedback)

    c.execute(
        "INSERT INTO resumes (resume_text, feedback, score, timestamp) VALUES (?, ?, ?, ?)",
        (resume_text, feedback_text, score, timestamp)
    )
    conn.commit()
    conn.close()

# ✅ Fetch all resumes for resume_history page
def get_all_resumes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, score, feedback, timestamp FROM resumes ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    return data

def save_career_query_to_db(prompt, response, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        INSERT INTO career_queries (prompt, response, timestamp)
        VALUES (?, ?, ?)
    ''', (prompt, response, timestamp))

    conn.commit()
    conn.close()


# ✅ Run this file directly to initialize DB
if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully.")
