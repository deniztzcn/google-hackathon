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
You are helping with tailoring users' CV. Analyze CV located in PDF. List technologies, skills and past experience from this CV. Make names of technologies, skills and past positions short (preferably one/two word names). List only positions and skills that were explicitly mentioned. Also, give an opinion of this CV, and list possible improvements.
Output should be in accordance to following json:
{
"type": "object",
"properties": {
"programing_languages": {
"type": "array",
"items": {
"type": "string"
}
},
"experience": {
"type": "array",
"items": {
"type": "string"
}
},
"technology_stack": {
"type": "array",
"items": {
"type": "string"
}
},
"topics_of_projects": {
"type": "array",
"items": {
"type": "string"
}
},
"soft_skills": {
"type": "array",
"items": {
"type": "string"
}
},
"tech_skills": {
"type": "array",
"items": {
"type": "string"
}
},
"languages": {
"type": "array",
"items": {
"type": "string"
}
},
"opinion": {
"type": "string"
},
"improvements": {
"type": "array",
"items": {
"type": "string"
}
}
},
"required": [
"soft_skills",
"languages",
"opinion",
"improvements",
"tech_skills"
]
}
"""
prompt_to_job_data_extract = """
You are helping with tailoring the user's CV for a given job offer. Analyze job offer from the link (job_offer_url). What are the requirements of this job offer? Make names of technologies and skills short (preferably one word names). Insert only data that is explicitly listed in an offer.
Format of an output has to be in accordance to the following json:
{
    {
"type": "object",
"properties": {
"mandatory_requirements": {
"type": "array",
"items": {
"type": "string"
}
},
"optional_requirements": {
"type": "array",
"items": {
"type": "string"
}
},
"required_experience": {
"type": "string"
},
"company_name": {
"type": "string"
},
"position_name": {
"type": "string"
},
"salary_range": {
"type": "string"
}
},
"required": [
"mandatory_requirements",
"optional_requirements",
"required_experience",
"company_name",
"position_name",
"salary_range"
]
}

}
"""

prompt_to_comparision = """
You are helping with tailoring the user's CV. What is the match (in percentage) of a user's skills to the job requirements? Which user's skills might be missing? What advice would you give to this user? Advice should consist of 3-4 sentences. Also, provide 5 possible questions during an interview.
Candidate info:
[json from the cv analysis]
Job description:
[json from the job offer]
Output should be in accordance to following json:
{
"type": "object",
"properties": {
"match": {
"type": "number"
},
"missing_skills": {
"type": "array",
"items": {
"type": "string"
}
},
"Advice": {
"type": "string"
},
"matching_skills": {
"type": "array",
"items": {
"type": "string"
}
},
"interview_questions": {
"type": "string"
},
"opinion": {
"type": "string"
},
"improvements": {
"type": "array",
"items": {
"type": "string"
}
}
},
"required": [
"match",
"missing_skills",
"Advice",
"Matching_skills",
"opinion",
"improvements"
]
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
    job_link =request.files['jobOfferLink']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a valid PDF file'}), 400

    temp_file_path = None
    uploaded_file = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            file.save(temp)
            temp_file_path = temp.name
        print(f"File saved temporarily to: {temp_file_path}")

        print("Uploading file to Gemini...")
        uploaded_file = client.files.upload(file=temp_file_path)
        print(f"File uploaded successfully to Gemini: {uploaded_file.uri}")

        print("Generating content from Gemini...")
        response = client.models.generate_content(
            model=model,
            contents=[prompt_to_cv_data_extract, uploaded_file],
            config={
                "response_mime_type": "application/json", }
        )

        result_cv = json.loads(response.text)
        print(response.text)
        result_job = get_job_description_extracted(job_link)
        comparision_result = compare_cv_and_job(result_cv, result_job)
        return jsonify(comparision_result), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An internal error occurred while processing the CV.'}), 500

    if temp_file_path and os.path.exists(temp_file_path):
        print(f"Deleting temporary local file: {temp_file_path}")
        os.remove(temp_file_path)


def get_job_description_extracted(job_link: str):
    """
    Fetches content from a job offer URL, extracts the main text,
    and uses Gemini API to structure the job description data.

    Args:
        job_link: The URL of the job offer.

    Returns:
        A dictionary with structured job description data, or None if an error occurs.
    """
    response = client.models.generate_content(model=model, contents=[prompt_to_job_data_extract, job_link],
                                              config={
                                                  "response_mime_type": "application/json",
                                              })
    result_job = json.loads(response.text)
    print(result_job.text)
    return response

def compare_cv_and_job(result_cv, result_job):
    response = client.models.generate_content(model=model, contents=[result_cv, result_job],
                                              config={
                                                  "response_mime_type": "application/json",
                                              })
    comparision_result = json.loads(response.text)
    print(comparision_result.text)
    return comparision_result



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
