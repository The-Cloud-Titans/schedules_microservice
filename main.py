import flask
from db import app as db_app, fetch_data

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = flask.Flask(__name__)

@app.get("/")
def hello():
    """Return a friendly HTTP greeting."""
    return "Hello World!\n"

@app.route("/show_data")
def show_data():
    # Call the fetch_data function from db.py
    data = fetch_data()
    return data

if __name__ == "__main__":
    # Used when running locally only. When deploying to EC2
    # a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host="0.0.0.0", port=8080, debug=False)
