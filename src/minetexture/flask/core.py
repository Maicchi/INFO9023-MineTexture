from flask import Flask, render_template

app = Flask(__name__)

# TODO: Add dashboard related api

request = {"id": 1, "name": "Example Request", "status": "pending"}


@app.route("/", methods=["GET"])
def home_page():
    return render_template("homepage.html", request=request)


@app.route("/", methods=["POST"])
def add_request():
    return "Request added!"


if __name__ == "__main__":
    app.run(debug=True)  # TODO: ENLEVER DEBUT
