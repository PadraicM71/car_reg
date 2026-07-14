from flask import Flask, render_template, request, send_file
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

image_details = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    photo = request.files["photo"]

    filepath = os.path.join(UPLOAD_FOLDER, "latest.jpg")

    photo.save(filepath)

    # Get file details
    file_size_bytes = os.path.getsize(filepath)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    # Open image and inspect
    img = Image.open(filepath)

    image_details["filename"] = photo.filename
    image_details["filesize"] = file_size_mb
    image_details["width"] = img.width
    image_details["height"] = img.height
    image_details["format"] = img.format
    image_details["mode"] = img.mode
    
    return render_template(
        "index.html",
        image=True,
        details=image_details
    )


@app.route("/image")
def image():
    return send_file(
        "uploads/latest.jpg",
        mimetype="image/jpeg"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
