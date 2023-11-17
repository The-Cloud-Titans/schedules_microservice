import os
import flask
from google.cloud import firestore
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access the credential file path
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

db = firestore.Client.from_service_account_json(credentials_path)

app = flask.Flask(__name__)

@app.route("/fetch_data")
def fetch_data():
    schedules_ref = db.collection("schedules")
    schedules = schedules_ref.stream()

    # Display fetched data
    result = "Fetched data from Firestore:\n"
    for schedule in schedules:
        data = schedule.to_dict()
        result += f"Document ID: {schedule.id}\n"
        result += f"Name: {data.get('name', 'N/A')}\n"
        result += f"Email: {data.get('email_id', 'N/A')}\n"
        result += f"Degree: {data.get('degree', 'N/A')}\n"
        result += f"Major: {data.get('major1', 'N/A')}\n"
        result += f"Planned Semesters: {data.get('planned_semesters', 'N/A')}\n"

        # Displaying courses information
        courses = data.get('planned_semesters', [])
        for semester_courses in courses:
            result += f"\nSemester: {semester_courses.get('semester', 'N/A')}\n"
            for course in semester_courses.get('courses', []):
                result += f"  Course Code: {course.get('course_code', 'N/A')}\n"
                result += f"  Course Name: {course.get('course_name', 'N/A')}\n"
                result += f"  Credits: {course.get('credits', 'N/A')}\n"

    return result

