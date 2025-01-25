from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from EventsModeler import EventsModeler

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['VISUALIZATION_FOLDER'] = 'static/'

# In-memory storage for events
events = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        uploaded_data = pd.read_excel(filepath)

        # Check if the "Event" column exists
        if "Event" in uploaded_data.columns:
            events_list = uploaded_data["Event"].unique().tolist()
            return {"multiple_events": True, "events": events_list}
        else:
            return {"multiple_events": False}

    return redirect(url_for('index'))

@app.route('/visualize', methods=['POST'])
def visualize():
    file = request.files['file']
    query = request.form['query']
    selected_events = request.form.getlist('events')  # Get selected events

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        uploaded_data = pd.read_excel(filepath)

        if selected_events:
            uploaded_data = uploaded_data[uploaded_data['Event'].isin(selected_events)]

        modeler = EventsModeler()
        visualization_path = modeler.model(
            filepath=None,  # Pass data directly
            data=uploaded_data,
            query=query,
            output_folder=app.config['VISUALIZATION_FOLDER']
        )

        return render_template('results.html', visualization=visualization_path)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
