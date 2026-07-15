from flask import Flask, render_template, request, send_file
from PIL import Image
import os

from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

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


    # Open image and inspect
    img = Image.open(filepath)

    # Resize so the longest side is 1500 pixels
    # img.thumbnail((1500, 1500)) # this work fine - but lets try 800
    # 1000 worked well - going to 800 the reg was still perfect but the other insignificant text of
    # an image started to suffer - which is fine - my testing suggests 800 is the perfect balance point
    # update: on your mac 800 looks like its near the minimum - but on render I think you could go lower!
    # (explore this!)
    img.thumbnail((800, 800)) # keep 800
    img.save(filepath)

    # Get file details

    file_size_bytes = os.path.getsize(filepath)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    image_details["filename"] = photo.filename
    image_details["filesize"] = file_size_mb
    image_details["width"] = img.width
    image_details["height"] = img.height
    image_details["format"] = img.format
    image_details["mode"] = img.mode
    image_details["latitude"] = latitude
    image_details["longitude"] = longitude


    # *********** START OCR Skunk Works ***********
    # do OCR experimenting here and just return the result in 'image_details' for now
    # late you will make this a function on its own and a specific interface in index.html
    result = ocr.predict(filepath)
    # image_details["ocr"] = result
    print(type(result))
    ocr_found = []
    for line in result:
        for text in line["rec_texts"]:
            print(text)
            ocr_found.append(text)

    image_details["ocr"]=ocr_found


    # *********** FIN OCR Skunk Works *************
    
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








# Paste above from vscode

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
