import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai


app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

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
    if 'cvFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['cvFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        # In a real app, you would save and process the PDF here.
        # For this MVP, we're just acknowledging the upload.
        # The user should provide CV text via the textarea for analysis.
        print(f"Received CV file: {file.filename}. (Actual PDF parsing not implemented in MVP).")
        return jsonify({'message': f'File {file.filename} received. Please ensure to paste CV text for analysis.'}), 200
    return jsonify({'error': 'File upload failed'}), 500



if __name__ == '__main__':
    app.run()
