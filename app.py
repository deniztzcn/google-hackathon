import os
import json
import tempfile
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# === Configuration ===
API_KEY = "AIzaSyCCRQSEJWrUz8q_j6dqne71Y-ePtX1-HyM"
MODEL_NAME = "gemini-2.5-flash"
client = genai.Client(api_key=API_KEY)

# === Prompt Templates ===
with open("prompts/cv_extraction_prompt.txt") as f:
    PROMPT_CV_EXTRACT = f.read()

with open("prompts/job_extraction_prompt.txt") as f:
    PROMPT_JOB_EXTRACT = f.read()

with open("prompts/comparison_prompt.txt") as f:
    PROMPT_COMPARISON = f.read()


# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'cvUploaded' not in request.files:
        return jsonify({'error': 'No CV file part in the request'}), 400

    file = request.files['cvUploaded']
    job_link = request.form.get('jobOfferLink')

    if not file or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a valid PDF file'}), 400

    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            file.save(temp)
            temp_file_path = temp.name

        uploaded_file = client.files.upload(file=temp_file_path)

        result_cv = extract_cv_data(uploaded_file)

        result_job = extract_job_data(job_link)

        # Compare CV with job description
        comparison_result = compare_cv_with_job(result_cv, result_job)

        return jsonify(comparison_result), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An internal error occurred while processing the CV.'}), 500

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def extract_cv_data(uploaded_file):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[PROMPT_CV_EXTRACT, uploaded_file],
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)


def extract_job_data(job_link):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[PROMPT_JOB_EXTRACT, job_link],
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)


def compare_cv_with_job(cv_data, job_data):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[PROMPT_COMPARISON, f"Candidate info:\n{json.dumps(cv_data)}", f"Job description:\n{json.dumps(job_data)}"],
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
