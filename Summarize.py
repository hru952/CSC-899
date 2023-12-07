from os import listdir
from os.path import isfile, join
from transformers import BartForConditionalGeneration, BartTokenizer
from PyPDF2 import PdfReader
import os
import requests
import json
from bardapi import Bard
import os

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file_path):
    pdf_text = ''
    pdf_reader = PdfReader(pdf_file_path)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    return pdf_text

# Function to generate summary for a given text
def generate_summary(text):
    model_name = "facebook/bart-large-cnn"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs["input_ids"], num_beams=4, min_length=30, max_length=200, length_penalty=2.0, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def generate_resume_bullet_point(text):

    os.environ['_BARD_API_KEY']="dwgvVW30vG_0tdngqIzCtPhnvML7dAgeNGCwKgD8lg9OAXwd_tiRiqT4i58taykBlYT-bQ."
    
    #input_text = f"Generate a 2 line summary for this project I did to add to my resume:\n{text}"
    input_text = f"This is a summary of a computer science student project or class assignment: {text} \n. Generate resume bullet points based on this, following these rules: 3 to 5 bullet points each with length no more than 2 lines i.e 20 - 30 words per bullet. USe Strong Action Verbs and past tense. Don't use of any responsibility-oriented language, such as 'Responsible for' or 'Duties included', on the resume."

    bard_output = Bard().get_answer(input_text)['content']
    return bard_output

# Folder containing PDF files
#pdf_folder = "C:\\Users\\hruth\\Desktop\\SEM3\\899-Project\\"

pdf_folder = os.path.dirname(os.path.realpath(__file__))
# Replace single backslashes with double backslashes
pdf_folder = pdf_folder.replace("\\", "\\\\") + "\\\\"

# Get a list of all PDF files in the folder
pdf_files = [f for f in listdir(pdf_folder) if isfile(join(pdf_folder, f)) and f.lower().endswith(".pdf")]

# Iterate over each PDF file and generate summaries
for pdf_file in pdf_files:
    pdf_file_path = join(pdf_folder, pdf_file)
    pdf_text = extract_text_from_pdf(pdf_file_path)
    summary = generate_summary(pdf_text)
    resume_bullet_point = generate_resume_bullet_point(summary)
    
    # Print the summary for each file
    print(f"Summary for {pdf_file}: \n{summary}\n")
    print("\nGenerated Resume Bullet Point:\n",resume_bullet_point,"\n")
