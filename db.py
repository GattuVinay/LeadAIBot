import sqlite3

def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            job_title TEXT,
            location TEXT,
            linkedin_url TEXT,
            phone_number TEXT PRIMARY KEY,
            requestSent INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_lead(lead):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO leads (job_title, location, linkedin_url, phone_number, requestSent)
        VALUES (?, ?, ?, ?, ?)
    ''', (lead['job_title'], lead['location'], lead['linkedin_url'], lead['phone_number'], 0))
    conn.commit()
    conn.close()

def is_message_sent(phone_number):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute('SELECT requestSent FROM leads WHERE phone_number = ?', (phone_number,))
    row = cursor.fetchone()
    conn.close()
    return row is not None
