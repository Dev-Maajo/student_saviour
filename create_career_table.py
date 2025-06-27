import sqlite3

conn = sqlite3.connect('resume_data.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS career_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT,
    response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')

conn.commit()
conn.close()

print("✅ career_queries table created (if not existed).")
