from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import pandas as pd
from functools import wraps
from EventsModeler import EventsModeler

USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.secret_key = "REPLACE_WITH_A_SECURE_KEY"
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['VISUALIZATION_FOLDER'] = 'static/'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VISUALIZATION_FOLDER'], exist_ok=True)

def requires_login(func):
    """
    Decorator to ensure the user is authenticated.
    Redirects to the login page if not.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@requires_login
def index():
    """Renders the main page (index.html) after login."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login form with predefined username/password."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Incorrect username or password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route clears session and redirects to login."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/files', methods=['GET'])
@requires_login
def list_files():
    """
    Returns a JSON array of all files in the 'uploads/' folder.
    e.g. ["file1.xlsx", "file2.xlsx"]
    """
    all_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(all_files)

@app.route('/upload', methods=['POST'])
@requires_login
def upload_files():
    """
    Handle multiple file uploads at once.
    Check if any file has an 'Event' column (for multi-event selection).
    Return JSON with { multiple_events: bool, events: [...unique events...] }
    """
    if 'files' not in request.files:
        return jsonify({"multiple_events": False}), 400

    files = request.files.getlist('files')
    all_events = set()
    multiple_events = False

    for f in files:
        if f and f.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(filepath)
            try:
                df = pd.read_excel(filepath)
                if "Event" in df.columns:
                    unique_events = df["Event"].unique().tolist()
                    for evt in unique_events:
                        all_events.add(evt)
                    multiple_events = True
            except Exception as e:
                print(f"Error reading file {f.filename}: {e}")

    if multiple_events and all_events:
        return jsonify({"multiple_events": True, "events": sorted(list(all_events))})
    else:
        return jsonify({"multiple_events": False})

@app.route('/visualize', methods=['POST'])
@requires_login
def visualize():
    """
    Creates visualizations for each selected or uploaded file (one chart per file).
    Also computes a summary of the data for easier consumption.
    """
    query = request.form.get('query')
    selected_events = request.form.getlist('events')

    dataframes = []
    filenames = []

    # 1) Newly uploaded files
    uploaded_files = request.files.getlist('files')
    if uploaded_files and any(f.filename for f in uploaded_files):
        for file in uploaded_files:
            if file.filename:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                try:
                    df = pd.read_excel(filepath)
                    if selected_events and "Event" in df.columns:
                        df = df[df["Event"].isin(selected_events)]
                    dataframes.append(df)
                    filenames.append(file.filename)
                except Exception as e:
                    print(f"Error reading file {file.filename}: {e}")

    # 2) Existing files
    existing_files = request.form.getlist('filenames')
    if existing_files:
        for fname in existing_files:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            if os.path.exists(filepath):
                try:
                    df = pd.read_excel(filepath)
                    if selected_events and "Event" in df.columns:
                        df = df[df["Event"].isin(selected_events)]
                    dataframes.append(df)
                    filenames.append(fname)
                except Exception as e:
                    print(f"Error reading existing file {fname}: {e}")

    if not dataframes:
        return "No valid files were provided or found.", 400

    modeler = EventsModeler()
    chart_info_list = []
    for i, df in enumerate(dataframes):
        chart_path, summary = modeler.model_with_summary(
            data=df,
            query=query,
            output_folder=app.config['VISUALIZATION_FOLDER']
        )
        chart_info_list.append({
            "filename": filenames[i],
            "chart_path": chart_path,
            "summary": summary
        })

    # We pass multiple charts + summaries to results.html
    return render_template('results.html', charts=chart_info_list)

@app.route('/delete_file', methods=['POST'])
@requires_login
def delete_file():
    """Delete a file from 'uploads/'."""
    filename = request.form.get('filename')
    if not filename:
        return jsonify({"success": False, "error": "No filename provided"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        return jsonify({"success": False, "error": "File does not exist"}), 404

@app.route('/rename_file', methods=['POST'])
@requires_login
def rename_file():
    """
    Renames a file in 'uploads/'.
    Expects form data: old_filename, new_filename
    """
    old_filename = request.form.get('old_filename')
    new_filename = request.form.get('new_filename')
    if not old_filename or not new_filename:
        return jsonify({"success": False, "error": "Missing filenames"}), 400

    old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

    # Basic check: if new_path already exists, we can handle collision
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

if __name__ == "__main__":
    app.run(debug=True)
