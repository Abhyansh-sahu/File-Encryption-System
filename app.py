from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import random
import os
app = Flask(__name__, static_folder='.')
CORS(app)
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="encry_registration"
    )
CHAR = [
    'a','b','c','d','e','f','g','h','i','j','k','l','m',
    'n','o','p','q','r','s','t','u','v','w','x','y','z',
    'A','B','C','D','E','F','G','H','I','J','K','L','M',
    'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
    '0','1','2','3','4','5','6','7','8','9','!','"','#',
    '$','%','&',"'",'(',')','+',',','-','.','/',':',
    ';','<','=','>','?','@','[','\\',']','^','_','`','{','|','}','~',' '
]
def rand_code(existing_codes):
    while True:
        code = ''.join(random.choices(CHAR, k=3))
        if code not in existing_codes:
            return code
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '').strip()
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
    if '@gmail.com' not in email:
        return jsonify({'success': False, 'message': 'Only Gmail addresses are allowed.'}), 400
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT Email FROM data WHERE Email = %s", (email,))
    if cursor.fetchone():
        cursor.close(); db.close()
        return jsonify({'success': False, 'message': 'Email already registered.'}), 409
    cursor.execute("INSERT INTO data (Name, Email, Password) VALUES (%s, %s, %s)", (name, email, password))
    db.commit()
    cursor.close(); db.close()
    return jsonify({'success': True, 'message': f'Account created for {name}.'})
@app.route('/api/login', methods=['POST'])
def login():
    data     = request.json
    email    = data.get('email', '').strip()
    password = data.get('password', '').strip()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM data WHERE Email = %s AND Password = %s", (email, password))
    result = cursor.fetchone()
    cursor.close(); db.close()
    if result:
        return jsonify({'success': True, 'name': result[1], 'email': result[2]})
    return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    data      = request.json
    file_path = data.get('file_path', '').strip()
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': 'File not found. Check the path.'}), 404
    file_name = os.path.basename(file_path).replace('.', '_').replace(' ', '_')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{file_name}` (
            letter VARCHAR(10) PRIMARY KEY,
            Code VARCHAR(100) UNIQUE,
            updated_code VARCHAR(100) UNIQUE
        )
    """)
    db.commit()
    with open(file_path, 'r') as f:
        lines = f.readlines()
    seen_letters = []
    cursor.execute(f"SELECT updated_code FROM `{file_name}`")
    existing_codes = {r[0] for r in cursor.fetchall()}
    for line in lines:
        for ch in line:
            if ch in CHAR and ch not in seen_letters:
                seen_letters.append(ch)
                code = rand_code(existing_codes)
                existing_codes.add(code)
                cursor.execute(
                    f"INSERT IGNORE INTO `{file_name}` (letter, Code, updated_code) VALUES (%s, %s, %s)",
                    (ch, code, code)
                )
                db.commit()
    cursor.execute(f"SELECT letter, Code FROM `{file_name}`")
    mapping = {letter: code for letter, code in cursor.fetchall()}
    enc_file = f"{file_name}_1.txt"
    with open(enc_file, 'a') as f:
        for line in lines:
            for ch in line:
                if ch == ' ':
                    f.write('\n')
                elif ch in mapping:
                    f.write(mapping[ch])
    sample = list(mapping.items())[:10]
    cursor.close(); db.close()
    return jsonify({
        'success': True,
        'file_name': file_name,
        'encrypted_file': enc_file,
        'total_chars': len(seen_letters),
        'sample_mapping': [{'char': ch, 'code': cd} for ch, cd in sample]
    })
@app.route('/api/regenerate', methods=['POST'])
def regenerate():
    data      = request.json
    file_name = data.get('file_name', '').strip()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    if file_name not in tables:
        cursor.close(); db.close()
        return jsonify({'success': False, 'message': 'Table not found in database.'}), 404
    cursor.execute(f"SELECT letter FROM `{file_name}`")
    letters = [r[0] for r in cursor.fetchall()]
    cursor.execute(f"SELECT updated_code FROM `{file_name}`")
    existing_codes = {r[0] for r in cursor.fetchall()}
    new_mapping = []
    for letter in letters:
        existing_codes.discard(None)
        new_code = rand_code(existing_codes)
        existing_codes.add(new_code)
        cursor.execute(
            f"UPDATE `{file_name}` SET updated_code = %s WHERE letter = %s",
            (new_code, letter)
        )
        db.commit()
        new_mapping.append({'char': letter, 'code': new_code})
    cursor.execute(f"SELECT letter, updated_code FROM `{file_name}`")
    mapping = {letter: code for letter, code in cursor.fetchall()}
    cursor.execute(f"SELECT letter, Code FROM `{file_name}`")
    orig_mapping = {letter: code for letter, code in cursor.fetchall()}
    cursor.close(); db.close()
    return jsonify({
        'success': True,
        'file_name': file_name,
        'keys_updated': len(letters),
        'sample_mapping': new_mapping[:10]
    })
@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    file_name = data.get('file_name', '').strip()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    if file_name not in tables:
        cursor.close(); db.close()
        return jsonify({'success': False, 'message': 'Table not found in database.'}), 404
    enc_file = f"{file_name}_1.txt"
    if not os.path.exists(enc_file):
        cursor.close(); db.close()
        return jsonify({'success': False, 'message': f'Encrypted file "{enc_file}" not found.'}), 404
    cursor.execute(f"SELECT letter, updated_code FROM `{file_name}`")
    result =cursor.fetchall()
    decrypt_dict ={code: letter for letter, code in result}
    with open(enc_file, 'r') as f:
        raw =f.read()
    words =raw.split()
    decrypted = ''
    for word in words:
        decrypted += decrypt_dict.get(word, '?')
    output_file = f"{file_name}_decrypted.txt"
    with open(output_file, 'w') as f:
        f.write(decrypted)
    cursor.close(); db.close()
    return jsonify({
        'success': True,
        'file_name': file_name,
        'output_file': output_file,
        'preview': decrypted[:300]
    })
@app.route('/api/tables', methods=['GET'])
def list_tables():
    db =get_db()
    cursor =db.cursor()
    cursor.execute("SHOW TABLES")
    tables =[t[0] for t in cursor.fetchall() if t[0] != 'data']
    cursor.close(); db.close()
    return jsonify({'tables': tables})
if __name__ == '__main__':
    app.run(debug=True, port=5000)