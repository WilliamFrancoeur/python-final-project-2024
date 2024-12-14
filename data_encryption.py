import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import sqlite3

load_dotenv()
encryption_key = os.getenv('ENCRYPTION_KEY')

if not encryption_key:
    encryption_key = Fernet.generate_key()
    with open('.env', 'w') as f:
        f.write(f'ENCRYPTION_KEY={encryption_key.decode()}')

fernet = Fernet(encryption_key.encode())

conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        encrypted_ip TEXT NOT NULL
    )
''')

@staticmethod
def encrypt_data(data: str) -> str:
    """Encrypt a string"""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt an encrypted string"""
    return fernet.decrypt(encrypted_data.encode()).decode()

def add_user(username: str, ip: str):
    encrypted_ip = encrypt_data(ip)
    cursor.execute(
        'INSERT INTO users (username, encrypted_ip) VALUES (?, ?)',
        (username, encrypted_ip)
    )
    conn.commit()

def get_user(username: str) -> dict:
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user:
        return {
            'ip': decrypt_data(user[0])
        }
    return None





if __name__ == '__main__':
    print("Inserting record: \nName: john doe \nIP: 192.168.2.10")
    add_user('john_doe', '192.168.2.10')
    print("Added record: \nName: john doe \nIP: 192.168.2.10")
    user = get_user('John_doe')
    print(f"Retrieve user: {user}")

    cursor.execute('SELECT * FROM users')
    raw_data = cursor.fetchall()
    print(f"\nRaw database content: {raw_data}")

    conn.close()
