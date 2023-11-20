from flask import Flask, jsonify
from db import db, fetch_data

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

@app.get("/")
def hello():
    """Return a friendly HTTP greeting."""
    return "Hello World!\n"

@app.route("/show_data")
def show_data():
    # Call the fetch_data function from db.py
    data = fetch_data()
    return data

@app.route("/users/<uni>/schedules", methods=["GET"])
def get_schedules(uni):
    schedules_ref = db.collection("schedules")
    #schedules = schedules_ref.stream()

    query = schedules_ref.where("uni", "==", uni).get()

    # Display fetched data
    # result = "Fetched data from Firestore:\n"
    schedules_data = []
    for schedule in query:
        data = schedule.to_dict()
        schedule_info = {
            "document_id": schedule.id,
            "name": data.get("name", "N/A"),
            "email": data.get("email_id", "N/A"),
            "degree": data.get("degree", "N/A"),
            "major": data.get("major1", "N/A"),
            "planned_semesters": data.get("planned_semesters", "N/A"),
        }

        # Displaying courses information
        courses = data.get('planned_semesters', [])
        schedule_info["courses"] = []
        for semester_courses in courses:
            for course in semester_courses.get("courses", []):
                course_info = {
                    "course_code": course.get("course_code", "N/A"),
                    "course_name": course.get("course_name", "N/A"),
                    "credits": course.get("credits", "N/A"),
                }
                schedule_info["courses"].append(course_info)
        schedules_data.append(schedule_info)

    return jsonify({"schedules": schedules_data}), 200


if __name__ == "__main__":
    # Used when running locally only. When deploying to EC2
    # a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="0.0.0.0", port=8080, debug=False)
