# schedules_microservice
Schedule microservice for UniTrackerPro.
This app will be running on EC2 instance and will be connected to a Firestore database.
Users can read/create/edit/delete schedules- which are the courses that they plan to take in future semesters. 
A user can create multiple schedules with different subject combinations if they want to see how their degree track would look if they take different subjects.
Whenever a user creates a new schedule, we trigger AWS Lambda function to send an email to the email IDs subscribed to the SNS topic. 
The email contains information about the newly created schedule.
