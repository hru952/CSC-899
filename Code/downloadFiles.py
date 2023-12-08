import requests

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
        course_name = course['name']
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
        course_name = course['name']

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