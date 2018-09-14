from flask import Flask, request, Response
import hashlib
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SALT = 'Make NPC great again!'

# API: 驗證社員 id 是否在資料庫中
@app.route('/v1/verify', methods=['POST'])
def verify():
    uid = request.form['uid']
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute('SELECT uid FROM accounts where uid=?', (uid,))
    if c.fetchone():
        return Response(status=200)
    else:
        return Response(status=403)

# 生成社員 id
def generate_uid(studentId):
    s = hashlib.sha256()
    s.update(studentId.encode("utf-8"))
    hash1 = s.hexdigest()
    s.update(hash1.encode("utf-8"))
    s.update('Make NPC great again!'.encode('utf-8'))
    return s.hexdigest()

# API: 透過學號新增社員
@app.route('/v1/member', methods=['POST'])
def add_member():
    studentId = request.form['studentId']
    uid = generate_uid(studentId)
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts(
        uid           TEXT     NOT NULL,
        studentId     TEXT     NOT NULL);''')
    c.execute('''INSERT INTO accounts (uid,studentId)
        VALUES (?, ?)''', (uid, studentId))
    conn.commit()
    return Response(uid, status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)