import os
import json
from google import genai
from google.genai import types
import tempfile
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

API_KEY = "AIzaSyCCRQSEJWrUz8q_j6dqne71Y-ePtX1-HyM"

model = "gemini-2.5-flash"
client = genai.Client(api_key=API_KEY)
# This is the prompt that tells the AI what to do
prompt_to_cv_data_extract = """
You are a highly skilled CV analysis assistant. Your task is to analyze the content of the attached CV PDF and extract specific information.
Follow these instructions precisely:
1.  Read the entire CV.
2.  Identify all technologies, skills, and past job positions mentioned.
3.  Make the names of technologies, skills, and positions short (preferably one or two words).
4.  List ONLY the positions and skills that are explicitly mentioned in the document. Do not infer or add any information that isn't present.
5.  Provide a brief, professional opinion of the CV's strengths.
6.  List potential improvements for the CV.
7.  Format your entire output as a single JSON object matching the provided schema. Do not include any text, markdown formatting like ```json, or explanations before or after the JSON object.

The required JSON schema is:
{
    "programing_languages": ["..."],
    "experience": ["..."],
    "technology_stack": ["..."],
    "topics_of_projects": ["..."],
    "soft_skills": ["..."],
    "languages": ["..."],
    "opinion": "...",
    "improvements": ["..."]
}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'cvUploaded' not in request.files:
        return jsonify({'error': 'No CV file part in the request'}), 400
        
    file = request.files['cvUploaded']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a valid PDF file'}), 400

    # These variables need to be defined before the try block
    # so they are accessible in the 'finally' clause for cleanup.
    temp_file_path = None
    uploaded_file = None
    
    # CORRECTED STRUCTURE: Use a try...except...finally block
    try:
        # Step 1: Save the uploaded file to a temporary location.
        # This provides a stable file path for the Gemini API to read.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            file.save(temp)
            temp_file_path = temp.name
        print(f"File saved temporarily to: {temp_file_path}")

        # Step 2: Upload the file to the Gemini API File Service.
        print("Uploading file to Gemini...")
        uploaded_file = client.files.upload(file=temp_file_path)
        print(f"File uploaded successfully to Gemini: {uploaded_file.uri}")

        # Step 3: Call the Gemini API to analyze the file.
        print("Generating content from Gemini...")
        response = client.models.generate_content(
            model=model,
            contents=[prompt_to_cv_data_extract, uploaded_file],
            config={
        "response_mime_type": "application/json",}
        )
        
        # Step 4: The API returns JSON as text, so parse it into a Python dict.
        result_data = json.loads(response.text)
        print(response.text)
        # Step 5: Return the structured data as a successful JSON response.
        return jsonify(result_data), 200

    # This 'except' block will catch ANY error during the process
    except Exception as e:
        print(f"An error occurred: {e}")
        # Return a generic error message to the user for security.
        return jsonify({'error': 'An internal error occurred while processing the CV.'}), 500

    # This 'finally' block will ALWAYS run, whether the 'try' succeeded or failed.
    # This is CRITICAL for cleaning up resources.
    
    # Clean up the temporary file from our local server disk
    if temp_file_path and os.path.exists(temp_file_path):
        print(f"Deleting temporary local file: {temp_file_path}")
        os.remove(temp_file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))