import json
import boto3

sns = boto3.client('sns')

def notify_schedule_creation(schedule_info, email_address):
    # Construct the email message
    subject = "New Schedule Created"

    # Include relevant schedule information in the message
   # message = f"Schedule ID: {schedule_info['schedule_id']}\n"
    message  = f"Name: {schedule_info['name']}\n"
    message += f"Degree: {schedule_info['degree']}\n"
    message += f"Major: {schedule_info['major1']}\n"
    message += f"Planned Semesters: {schedule_info['planned_semesters']}\n"
    message += f"Previous Semesters: {schedule_info['previous_semesters']}\n"
    message += f"UNI: {schedule_info['uni']}\n"

    # Include courses information if available
    courses = schedule_info.get('courses', [])
    if courses:
        message += "\nCourses:\n"
        for course in courses:
            message += f"  Course Code: {course.get('course_code', 'N/A')}\n"
            message += f"  Course Name: {course.get('course_name', 'N/A')}\n"
            message += f"  Credits: {course.get('credits', 'N/A')}\n"

    # Send the email
    sns.publish(
        TopicArn='arn:aws:sns:us-east-2:256273164694:ScheduleCreationTopic',
        Subject=subject,
        Message=message,
        MessageStructure='string'
    )

