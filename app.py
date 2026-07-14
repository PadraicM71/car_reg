from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    photo = request.files["photo"]

    filepath = os.path.join(UPLOAD_FOLDER, "latest.jpg")
    photo.save(filepath)

    return render_template("index.html", image=True)


@app.route("/image")
def image():
    return send_file("uploads/latest.jpg", mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
