from flask import Flask, render_template, request, jsonify
import os
app = Flask(__name__)


@app.route('/')
def index():
    """
    Renders the main application page.
    This page contains the form for user input and displays results via JavaScript.
    """
    return render_template('index.html')

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    """
    Handles CV file upload. For this MVP, it just confirms receipt of the file.
    Actual PDF parsing would happen here in a full application.
    """
    if 'cvUploaded' not in request.files:
        return jsonify({'error': 'No CV file part in the request'}), 400
        
    file = request.files['cvUploaded']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        print(f"Received CV file: {file.filename}. (Actual PDF parsing not implemented in MVP).")

    return jsonify({'message': f'File {file.filename} received. Please ensure to paste CV text for analysis.'}), 200
    #return jsonify({'error': 'File upload failed'}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
