from flask import Flask, jsonify, request
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
            "uni":data.get("uni","N/A"),
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

@app.route("/users/<uni>/schedules/<schedule_id>", methods=["GET"])
def get_schedule_by_id(uni, schedule_id):
    schedules_ref = db.collection("schedules")
    schedule_doc_ref = schedules_ref.document(schedule_id)
    schedule_doc = schedule_doc_ref.get()

    if not schedule_doc.exists:
        return jsonify({"error": "Schedule not found"}), 404

    data = schedule_doc.to_dict()

    # Check if the schedule belongs to the specified uni
    if data.get("uni") != uni:
        return jsonify({"error": "Schedule does not belong to the specified user. Access not granted"}), 403

    schedule_info = {
        "document_id": schedule_doc.id,
        "name": data.get("name", "N/A"),
        "email": data.get("email_id", "N/A"),
        "degree": data.get("degree", "N/A"),
        "major": data.get("major1", "N/A"),
        "planned_semesters": data.get("planned_semesters", "N/A"),
        "uni": data.get("uni", "N/A"),
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

    return jsonify({"schedule": schedule_info}), 200

@app.route("/users/<uni>/schedules", methods=["POST"])
def create_schedule(uni):
    try:
        # Assuming the request contains JSON data with schedule information
        schedule_data = request.json
        #print(schedule_data)

        # Validate that the request contains necessary data
        required_fields = ["name", "email_id", "degree", "major1", "planned_semesters"]
        for field in required_fields:
            if field not in schedule_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        #TODO: add code to add non-required fields too

        # Validate that uni in URL matches uni in the request data
        if schedule_data.get("uni") != uni:
            return jsonify({"error": "uni in URL does not match uni in request data"}), 400

        # Add the schedule to Firestore
        schedules_ref = db.collection("schedules")
        new_schedule_ref = schedules_ref.add(schedule_data)

        # Get the auto-generated document ID from the tuple
        new_document_id = new_schedule_ref[1].id

        # Respond with a success message and the document_id
        return jsonify({"message": f"Schedule with {new_document_id} was created"}), 202


    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Used when running locally only. When deploying to EC2
    # a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="0.0.0.0", port=8080, debug=False)
