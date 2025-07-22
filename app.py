from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecret'
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# store {file_id: {"filename": ..., "saved": ..., "password": ...}}
file_data = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    download_link = None
    if request.method == 'POST':
        file = request.files['file']
        password = request.form.get('password')

        if file:
            original_name = secure_filename(file.filename)
            file_id = uuid.uuid4().hex
            saved_name = f"{file_id}_{original_name}"
            file.save(os.path.join(UPLOAD_FOLDER, saved_name))

            file_data[file_id] = {
                "filename": original_name,
                "saved": saved_name,
                "password": password.strip() if password else ""
            }

            download_link = url_for('download', file_id=file_id, _external=True)

    return render_template('index.html', download_link=download_link)

@app.route('/download/<file_id>', methods=['GET', 'POST'])
def download(file_id):
    file_info = file_data.get(file_id)
    if not file_info:
        return "Invalid or expired link", 404

    if request.method == 'POST':
        user_password = request.form.get('password')
        if file_info['password'] and user_password != file_info['password']:
            flash('Incorrect password')
            return render_template('download.html', needs_password=True)

        return send_from_directory(UPLOAD_FOLDER, file_info['saved'], as_attachment=True)

    return render_template('download.html', needs_password=bool(file_info['password']))


if __name__ == '__main__':
    app.run(debug=True)
