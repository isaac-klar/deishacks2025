from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import pandas as pd
from functools import wraps
from EventsModeler import EventsModeler

USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_HERE"
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['VISUALIZATION_FOLDER'] = 'static/'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VISUALIZATION_FOLDER'], exist_ok=True)

def requires_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@requires_login
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username')
        pwd = request.form.get('password')
        if uname == USERNAME and pwd == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Incorrect username or password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/files', methods=['GET'])
@requires_login
def list_files():
    """Return a JSON array of the files in 'uploads/'."""
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)

@app.route('/upload', methods=['POST'])
@requires_login
def upload():
    """Stores new files in 'uploads/'."""
    if 'files' not in request.files:
        return jsonify({"success": False, "error": "No 'files' field"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"success": False, "error": "Empty file list"}), 400

    saved = []
    for f in files:
        if f.filename:
            path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(path)
            saved.append(f.filename)

    if saved:
        return jsonify({"success": True, "files": saved})
    else:
        return jsonify({"success": False, "error": "No valid filenames"}), 400

@app.route('/visualize', methods=['POST'])
@requires_login
def visualize():
    """
    Collect new + existing files => pass to EventsModeler => single or multi chart.
    """
    query = request.form.get('query')
    new_files = request.files.getlist('files')
    existing_files = request.form.getlist('filenames')

    dataframes = []
    labels = []

    # Load newly uploaded
    for f in new_files:
        if f.filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(filepath)
            try:
                df = pd.read_excel(filepath)
                dataframes.append(df)
                labels.append(f.filename)
            except Exception as e:
                print(f"Error reading new file {f.filename}: {e}")

    # Load existing
    for fname in existing_files:
        path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
        if os.path.exists(path):
            try:
                df = pd.read_excel(path)
                dataframes.append(df)
                labels.append(fname)
            except Exception as e:
                print(f"Error reading existing file {fname}: {e}")

    if not dataframes:
        return "No valid files found.", 400

    modeler = EventsModeler()
    chart_filename = modeler.model(dataframes, labels, query, app.config['VISUALIZATION_FOLDER'])
    return render_template('results.html', chart_filename=chart_filename)

@app.route('/delete_file', methods=['POST'])
@requires_login
def delete_file():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({"success": False, "error": "No filename"}), 400

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        try:
            os.remove(path)
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        return jsonify({"success": False, "error": "File does not exist"}), 404

@app.route('/rename_file', methods=['POST'])
@requires_login
def rename_file():
    old_filename = request.form.get('old_filename')
    new_filename = request.form.get('new_filename')
    if not old_filename or not new_filename:
        return jsonify({"success": False, "error": "Missing filenames"}), 400

    old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

    if os.path.exists(new_path):
        return jsonify({"success": False, "error": "File with that name already exists"}), 400

    if os.path.exists(old_path):
        try:
            os.rename(old_path, new_path)
            return jsonify({"success": True, "old_filename": old_filename, "new_filename": new_filename})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        return jsonify({"success": False, "error": "Old file does not exist"}), 404

if __name__ == '__main__':
    app.run(debug=True)
