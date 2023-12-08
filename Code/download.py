import requests
from datetime import datetime

# Replace with your Canvas API token and the base URL for your Canvas instance
API_TOKEN = 'XXXX'
BASE_URL = "https://sfsu.instructure.com/api/v1"

def format_due_date(iso_date):
    if iso_date:
        due_date = datetime.strptime(iso_date, '%Y-%m-%dT%H:%M:%SZ')
        return due_date.strftime('%Y-%m-%d %I:%M:%S %p')
    else:
        return "No due date"
    
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

# Example: Get a list of all courses
courses_url = f'{BASE_URL}/courses'
headers = {'Authorization': f'Bearer {API_TOKEN}'}

response = requests.get(courses_url, headers=headers)

# Words to include in assignment names
included_words = ["project", "team", "group"]

# Words to exclude from assignment names
excluded_words = ["mid", "midterm", "final", "extra", "credit", "exam"]

# Check if the request was successful
if response.status_code == 200:
    courses_data = response.json()
    # Iterate through the courses
    for course in courses_data:
        course_id = course['id']
        course_name = course['name']
        
        # Check if course name contains "master's" and skip if it does
        if "master's" in course_name.lower():
            continue

        print(f"\nCourse ID: {course_id}, Course Name: {course_name}")

        # Retrieve assignments for the current course
        assignments_url = f"{BASE_URL}/courses/{course_id}/assignments"
        response = requests.get(assignments_url, headers=headers)

        if response.status_code == 200:
            assignments = response.json()
            project_or_team_assignments = []

            for assignment in assignments:
                assignment_id = assignment['id']
                assignment_name = assignment['name']

                # Check if the assignment name contains included words
                if any(word in assignment_name.lower() for word in included_words):
                    project_or_team_assignments.append({'id': assignment_id, 'name': assignment_name})

            if project_or_team_assignments:
                # Print assignments with included words in their names
                print("Assignments with 'project,' 'team,' or 'group' in the name:")
                for assignment_info in project_or_team_assignments:
                    print("ID:", assignment_info['id'], "Name:", assignment_info['name'])
                    download_submission(course_id,assignment_info['id'])
            
            else:

                # If no assignments with included words, print the names of all assignments
                all_assignments = [{'id': assignment['id'], 'name': assignment['name']} for assignment in assignments]

                # Exclude assignments with excluded words from the last two assignments
                last_assignments = [assignment for assignment in all_assignments if all(word not in assignment['name'].lower() for word in excluded_words)]

                if len(last_assignments) >= 2:
                    print("No 'project,' 'team,' or 'group' assignments. Last Two Assignments (excluding specific words):")
                    for assignment_info in last_assignments[-2:]:
                        if course_id == 23452 or course_id == 28446:
                            continue
                        else:
                            print("ID:", assignment_info['id'], "Name:", assignment_info['name'])
                            download_submission(course_id,assignment_info['id'])
                else:
                    print("Less than two assignments after exclusions.")
        else:
            print(f"Error retrieving assignments for Course ID {course_id}")
else:
    print(f"Error: {response.status_code} - {response.text}")
