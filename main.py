from flask import Flask, jsonify, request
from flask_cors import CORS
from db import db, fetch_data
import boto3
import json

sns = boto3.client('sns', region_name='us-east-2')

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
CORS(app)

@app.get("/")
def hello():
    """Return a friendly HTTP greeting."""
    return "Hello World 2!\n"

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
            "schedule_id": schedule.id,
            "name": data.get("name", "N/A"),
            "schedule_name": data.get("schedule_name","N/A"),
            "email_id": data.get("email_id", "N/A"),
            "degree": data.get("degree", "N/A"),
            "major1": data.get("major1", "N/A"),
            "planned_semesters": data.get("planned_semesters", "N/A"),
            "previous_semesters": data.get("previous_semesters","N/A"),
            "uni":data.get("uni","N/A"),
        }

        # Displaying courses information
        # courses = data.get('planned_semesters', [])
        # schedule_info["courses"] = []
        # for semester_courses in courses:
        #     for course in semester_courses.get("courses", []):
        #         course_info = {
        #             "course_code": course.get("course_code", "N/A"),
        #             "course_name": course.get("course_name", "N/A"),
        #             "credits": course.get("credits", "N/A"),
        #         }
        #         schedule_info["courses"].append(course_info)
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
        "schedule_id": schedule_doc.id,
        "name": data.get("name", "N/A"),
        "schedule_name": data.get("schedule_name","N/A"),
        "email_id": data.get("email_id", "N/A"),
        "degree": data.get("degree", "N/A"),
        "major1": data.get("major1", "N/A"),
        "planned_semesters": data.get("planned_semesters", "N/A"),
        "previous_semesters": data.get("previous_semesters", "N/A"),
        "uni": data.get("uni", "N/A"),
    }

    # Displaying courses information
    # courses = data.get('planned_semesters', [])
    # schedule_info["courses"] = []
    # for semester_courses in courses:
    #     for course in semester_courses.get("courses", []):
    #         course_info = {
    #             "course_code": course.get("course_code", "N/A"),
    #             "course_name": course.get("course_name", "N/A"),
    #             "credits": course.get("credits", "N/A"),
    #         }
    #         schedule_info["courses"].append(course_info)

    return jsonify({"schedule": schedule_info}), 200

@app.route("/users/<uni>/schedules", methods=["POST"])
def create_schedule(uni):
    try:
        # Assuming the request contains JSON data with schedule information
        schedule_data = request.json
        #print(schedule_data)

        # Validate that the request contains necessary data
        required_fields = ["name","schedule_name", "email_id", "degree", "major1", "planned_semesters", "previous_semesters"]
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

        # Get the document reference from the tuple
        new_schedule_doc_ref = new_schedule_ref[1]

        # Get the document data
        new_schedule_doc = new_schedule_doc_ref.get().to_dict()

        # Extracting planned_semesters information
        planned_semesters = new_schedule_doc.get('planned_semesters', [])

        # Constructing formatted_message
        formatted_message = (
            "Hello,\nYour new schedule was created. Here is your copy:\n\n"
            f"Schedule Name: {new_schedule_doc.get('schedule_name', 'N/A')}\n"
            f"Name: {new_schedule_doc.get('name', 'N/A')}\n"
            f"Email: {new_schedule_doc.get('email_id', 'N/A')}\n"
            f"Degree: {new_schedule_doc.get('degree', 'N/A')}\n"
            f"Major 1: {new_schedule_doc.get('major1', 'N/A')}\n"
            "Planned Semesters:\n"
        )

        # Iterating through each semester
        for semester in planned_semesters:
            formatted_message += f"  Semester: {semester['semester']}\n"
            formatted_message += f"  Max Credits: {semester['max_credits']}\n"

            # Iterating through each course in the semester
            formatted_message += "  Courses:\n"
            for course in semester.get('courses', []):
                formatted_message += f"    Course Code: {course.get('course_code', 'N/A')}\n"
                formatted_message += f"    Course Name: {course.get('course_name', 'N/A')}\n"
                formatted_message += f"    Credits: {course.get('credits', 'N/A')}\n"
                formatted_message += f"\n"

        formatted_message += f"Regards,\n"
        formatted_message +="UniTrackerPro Team"


        sns_message = {
            "scheduled_info": formatted_message
        }

        sns.publish(
            TopicArn='arn:aws:sns:us-east-2:256273164694:ScheduleChangeTopic',
            Message=sns_message['scheduled_info'],
            Subject="New Schedule Created",
            MessageStructure='string'
        )

        # Respond with a success message and the document_id
        return jsonify({"message": f"Schedule with {new_document_id} was created"}), 202


    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<uni>/schedules/<schedule_id>", methods=["PUT"])
def update_schedule(uni, schedule_id):
    try:
        # Assuming the request contains JSON data with updated schedule information
        updated_schedule_data = request.json

        # Fetch data from Firestore using schedule_id
        schedules_ref = db.collection("schedules").document(schedule_id)
        schedule_data = schedules_ref.get().to_dict()

        # Verify if the uni in the fetched data matches uni in the URL
        if schedule_data.get("uni") != uni:
            return jsonify({"error": f"Schedule with {schedule_id} does not belong to user with uni {uni}"}), 400

        # Define fields that are not allowed to be updated
        fields_not_allowed_to_update = ["name", "email_id", "uni", "schedule_name"]

        # Check if request body contains fields not allowed to be updated
        disallowed_fields = set(updated_schedule_data.keys()) & set(fields_not_allowed_to_update)
        if disallowed_fields:
            return jsonify({"error": f"Fields not allowed to be updated: {', '.join(disallowed_fields)}"}), 400

        # Remove fields that should not be updated
        for field in fields_not_allowed_to_update:
            updated_schedule_data.pop(field, None)

        # Update the schedule in Firestore
        schedules_ref = db.collection("schedules").document(schedule_id)
        schedules_ref.update(updated_schedule_data)

        # Respond with a success message
        return jsonify({"message": f"Schedule with {schedule_id} has been updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<uni>/schedules/<schedule_id>", methods=["DELETE"])
def delete_schedule(uni, schedule_id):
    try:
        # Fetch data from Firestore using schedule_id
        schedules_ref = db.collection("schedules").document(schedule_id)
        schedule_data = schedules_ref.get().to_dict()

        # Verify if the uni in the fetched data matches uni in the URL
        if schedule_data.get("uni") != uni:
            return jsonify({"error": f"Schedule with {schedule_id} does not belong to user with uni {uni}"}), 400

        # Delete the schedule from Firestore
        schedules_ref.delete()

        # Respond with a success message
        return jsonify({"message": f"Schedule with {schedule_id} has been deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Used when running locally only. When deploying to EC2
    # a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="0.0.0.0", port=8080, debug=False)
