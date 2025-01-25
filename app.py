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
    # Get the uploaded file
    file = request.files['file']
    query = request.form['query']  # Get the selected query
    selected_events = request.form.getlist('events')  # Get selected events

    if file:
        # Save the uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Collect data for selected events (if any)
        combined_data = pd.DataFrame()
        if selected_events:
            for event in selected_events:
                event_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{event}.xlsx")
                if os.path.exists(event_path):
                    event_data = pd.read_excel(event_path)
                    combined_data = pd.concat([combined_data, event_data])

        # Add the newly uploaded file to the combined data
        uploaded_data = pd.read_excel(filepath)
        combined_data = pd.concat([combined_data, uploaded_data])

        # Generate visualization
        modeler = EventsModeler()
        visualization_path = modeler.model(
            filepath=None,  # We'll pass combined data directly
            data=combined_data,
            query=query,
            output_folder=app.config['VISUALIZATION_FOLDER']
        )

        # Pass visualization to the results page
        return render_template('results.html', visualization=visualization_path)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
