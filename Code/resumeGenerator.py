import requests
import json
import os
from os import listdir
from os.path import isfile, join
from PyPDF2 import PdfReader
import docx
from transformers import BartForConditionalGeneration, BartTokenizer

# Read the user's Canvas API token
API_TOKEN = input("Enter your Canvas API key: ")
BASE_URL = "https://sfsu.instructure.com/api/v1"

#Function that facilitates submission downloading   
def download_submission(course_id,assignment_id):

    submission_url = f"{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/self"
    response = requests.get(submission_url, headers=headers)

    if response.status_code == 200:
        submission_data = response.json()

        if "attachments" in submission_data and len(submission_data["attachments"]) > 0:
            attachment = submission_data["attachments"][0]
            download_url = attachment["url"]
            file_response = requests.get(download_url)

            if file_response.status_code == 200:
                file_name = attachment["filename"]
                with open(file_name, "wb") as file:
                    file.write(file_response.content)
                    print(f"PDF file '{file_name}' downloaded successfully.")
            else:
                print("Failed to download the file:", file_response.status_code)

        else:
            print("No attachments found in the submission data.")

    else:
        print("Failed to retrieve submission data:", response.status_code)

# Get a list of all enrolled courses from Canvas
courses_url = f'{BASE_URL}/courses'
headers = {'Authorization': f'Bearer {API_TOKEN}'}
response = requests.get(courses_url, headers=headers)

# Heuristics to select or reject an assignment
included_words = ["project", "team", "group"]
excluded_words = ["mid", "midterm", "final", "extra", "credit", "exam"]

# Check if the request was successful
if response.status_code == 200:
    courses_data = response.json()
    print("\nSelect one or more courses from the list of all registered courses:")
    # Print all registered course list for user to select from
    for index, course in enumerate(courses_data, start=1):
        course_id = course['id']
        course_name = course.get('name', 'Name not available')
        print(f"{index}. {course_name}")

    # Prompt the user to input the course indexes they want to download assignments from
    print("\nChoose the course(s) (choose one or more) that you want to be considered for resume generation and enter the course numbers as comma-separated values without spaces.")
    print("Example: 1,5,6")
    selected_indexes = input("\nEnter your choice of course numbers: ")
    selected_indexes = [int(index) for index in selected_indexes.split(',')]

    # Iterate through the selected courses and download submissions
    for index, course in enumerate(courses_data, start=1):

        if index not in selected_indexes:
            continue

        course_id = course['id']
        course_name = course.get('name', 'Name not available')

        assignments_url = f"{BASE_URL}/courses/{course_id}/assignments"
        response = requests.get(assignments_url, headers=headers)

        if response.status_code == 200:
            assignments = response.json()
            project_or_team_assignments = []

            for assignment in assignments:
                assignment_id = assignment['id']
                assignment_name = assignment.get('name', 'Name not available')

                # Check if the assignment name contains included words
                if any(word in assignment_name.lower() for word in included_words):
                    project_or_team_assignments.append({'id': assignment_id, 'name': assignment_name})

            if project_or_team_assignments:
                # Print assignments with included words in their names and download the file
                print(f"\nSelected submissions from {course_name}:")
                for assignment_info in project_or_team_assignments:
                    print("\nName:", assignment_info['name'])
                    download_submission(course_id,assignment_info['id'])
            
            else:
                # If no assignments with included words
                all_assignments = [{'id': assignment['id'], 'name': assignment['name']} for assignment in assignments]
                # Exclude assignments with excluded words from the last two assignments
                last_assignments = [assignment for assignment in all_assignments if all(word not in assignment['name'].lower() for word in excluded_words)]

                if len(last_assignments) >= 2:
                    print(f"\nSelected submissions from {course_name}:")

                    for assignment_info in last_assignments[-2:]:
                            print("\nName:", assignment_info['name'])
                            download_submission(course_id,assignment_info['id'])

                else:
                    print("No suitable submissions to download.")

        else:
            print(f"Error retrieving assignments for Course ID {course_id}")

else:
    print(f"Error: {response.status_code} - {response.text}")

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file_path):
    pdf_text = ''
    pdf_reader = PdfReader(pdf_file_path)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    return pdf_text

# Function to extract text from a DOC file
def extract_text_from_docx(docx_file_path):
    doc_text = ''
    doc = docx.Document(docx_file_path)
    for paragraph in doc.paragraphs:
        doc_text += paragraph.text + '\n'
    return doc_text

# Function to Generate summary
def generate_summary(text):
    # Load pre-trained BART model and tokenizer
    model_name = "facebook/bart-large-cnn"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    # Tokenize and prepare inputs
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)

    # Generate summary
    summary_ids = model.generate(
        inputs["input_ids"],
        num_beams=4,
        min_length=30,
        max_length=200,
        length_penalty=2.0,
        early_stopping=True
    )

    # Decode summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Function to send text to ChatGPT and receive a response
def generate_resume_bullet_point(prompt):
    openai_api_key = 'REPLACE WITH YOUT OPEN AI API KEY'
    if openai_api_key == '':
        raise ValueError("OpenAI API key is not set.")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    full_prompt = (
        f"This is a summary of a computer science student project or class assignment: {prompt}\n"
        "Generate resume bullet points based on the above summary following these rules:\n"
        "1. Give a concise title for the project for the resume.\n"
        "2. Generate 2 to 3 bullet points with each point between 20 - 30 words.\n"
        "3. Use STAR format.\n"
        "4. Avoid responsibility-oriented language like 'Responsible for'.\n"
        "Note that the summary provided is generated by a summarization tool and may lack in-depth details. Generate bullet points addressing any gaps and nuances in the summary."
    )

    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": "You are a professional resume expert specializing in generating resumes for different industries and roles."},
            {"role": "user", "content": full_prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise ValueError(f"Error from OpenAI: {response.status_code}, {response.text}")

# All the files downloaded that summaries need to be generated
downloads_folder = os.path.dirname(os.path.realpath(__file__))
downloads_folder = downloads_folder.replace("\\", "\\\\") + "\\\\"

# List all PDF and Word files in the downloads folder
all_files = [f for f in listdir(downloads_folder) if isfile(join(downloads_folder, f)) and (f.lower().endswith(".pdf") or f.lower().endswith(".docx"))]

# Iterate over each file and generate summaries and bullet points
for file in all_files:
    file_path = join(downloads_folder, file)

    # Extract text based on file type
    if file.lower().endswith(".pdf"):
        file_text = extract_text_from_pdf(file_path)
    elif file.lower().endswith(".docx"):
        file_text = extract_text_from_docx(file_path)
    else:
        continue

    summary = generate_summary(file_text)

    # Generate bullet points based on summary generated
    resume_bullet_point = generate_resume_bullet_point(summary)
    
    # Print the  resume bullet point
    print(f"\nSummary generated for {file}\n")
    print("\nGenerated Resume Bullet Point:\n",resume_bullet_point,"\n")
