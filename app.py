from flask import Flask, request, Response
import hashlib
import sqlite3
from flask_cors import CORS
from  pymongo import MongoClient

app = Flask(__name__)
CORS(app)
m = MongoClient('mongo', port=27017)
db = m.npc_db
collection = db.record_activity

SALT = 'Make NPC great again!'

def recordActivity(json):
    collection.insert_one(json)

# API: 驗證社員 id 是否在資料庫中
@app.route('/v1/verify', methods=['POST'])
def verify():
    json = request.get_json(force=True)
    uid = json['uid']
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute('SELECT uid FROM accounts where uid=?', (uid,))
    if c.fetchone():
        recordActivity(json)
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