from flask import Flask, render_template, request

app = Flask(__name__)

# Hard-coded but should be replaced by a call to the output database
users_request = [{"id": 1, "prompt_text": "Example Request", "status": "pending"}]


@app.route("/", methods=["GET", "POST"])
def home_page():
    # input_prompt = ""
    if request.method == "POST":
        # input_prompt = request.form.get("prompt")
        # TODO: Build the message and send input_prompt to the model
        return render_template(
            "homepage.html", users_request=users_request, added_request=True
        )

    return render_template(
        "homepage.html", users_request=users_request, added_request=False
    )


if __name__ == "__main__":
    app.run(debug=True)  # TODO: ENLEVER DEBUG
