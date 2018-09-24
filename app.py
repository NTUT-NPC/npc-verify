from flask import Flask, request, Response
import hashlib
import sqlite3
from flask_cors import CORS
from  pymongo import MongoClient
import json

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
    reqjson = request.get_json(force=True)
    uid = reqjson['uid']
    data = reqjson['data']
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM accounts where uid=?', (uid,))
    info = c.fetchone()
    if info:
        recordActivity(data)
        return Response(json.dumps({'uid': info[1], 'name': info[2], 'class': info[3]}), mimetype='application/json', status=200)
    else:
        return Response(status=403)

# 生成社員 id
def generate_uid(studentId):
    s = hashlib.sha256()
    s.update(studentId.encode("utf-8"))
    hash1 = s.hexdigest()
    s.update(hash1.encode("utf-8"))
    s.update(SALT.encode('utf-8'))
    return s.hexdigest()

# API: 透過學號新增社員
@app.route('/v1/member', methods=['POST'])
def add_member():
    studentId = request.form['studentId']
    studentClass = request.form['class']
    name = request.form['name']
    uid = generate_uid(studentId)
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts(
        uid           TEXT     NOT NULL,
        studentId     TEXT     NOT NULL,
        name          TEXT     NOT NULL,
        class         TEXT     NOT NULL);''')
    c.execute('''INSERT INTO accounts (uid,studentId, name, class)
        VALUES (?, ?, ?, ?)''', (uid, studentId, name, studentClass))
    conn.commit()
    return Response(uid, status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)