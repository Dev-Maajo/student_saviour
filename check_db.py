import sqlite3

conn = sqlite3.connect('resume_data.db')
c = conn.cursor()

c.execute("SELECT * FROM resumes ORDER BY id DESC")
rows = c.fetchall()

for row in rows:
    print("ID:", row[0])
    print("Score:", row[3])
    print("Feedback:\n", row[2])
    print("Uploaded at:", row[4])
    print("="*40)

conn.close()
