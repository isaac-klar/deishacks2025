from flask import Flask, render_template, request, redirect, url_for
import os
from EventsModeler import EventsModeler  # Import the updated script

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
        # Save the uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Generate visualization
        modeler = EventsModeler()
        visualization_path = modeler.model(
            filepath=filepath,
            query="Are you a member of Waltham Chamber of Commerce",
            output_folder=app.config['VISUALIZATION_FOLDER']
        )

        # Pass visualization to the results page
        return render_template('results.html', visualization=visualization_path)
    return redirect(url_for('index'))
if __name__ == "__main__":
    app.run(debug=True)
