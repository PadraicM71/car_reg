from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps
import os
import re
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




# helper functions:
def extract_and_strip_irish_plates(ocr_results):
    county_codes = (
        r"(?:C|CE|CN|CW|D|DL|G|KE|KK|KY|L|LD|LH|LK|LM|LS|MH|MN|MO|MS|OY|RN|SO|T|TN|TS|W|WD|WH|WX|WW)"
    )
    
    # Matches plates with or without spaces/hyphens
    flexible_pattern = rf"^\d{{2,3}}[-\s]*{county_codes}[-\s]*\d{{1,6}}$"
    
    valid_stripped_plates = []
    
    for plate in ocr_results:
        cleaned_plate = str(plate).strip().upper()
        
        if re.match(flexible_pattern, cleaned_plate):
            # Remove all hyphens and spaces from the valid plate
            stripped = re.sub(r'[- \s]', '', cleaned_plate)
            valid_stripped_plates.append(stripped)
            
    return valid_stripped_plates





@app.route("/")
def index():
    return render_template("index.html")




@app.route("/reg")
def reg():

    reg = request.args.get("reg")

    return render_template(
        "reg.html",
        reg=reg
    )




@app.route("/upload", methods=["POST"])
def upload():
    photo = request.files["photo"]
    filepath = os.path.join(UPLOAD_FOLDER, "latest.jpg")
    photo.save(filepath)


    # Open image
    img = Image.open(filepath)
    # Apply the EXIF orientation - keeps taken pic orientation
    img = ImageOps.exif_transpose(img)
    # Save the corrected orientated image
    img.save(filepath)

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


    # *********** START OCR for function creation ***********
    # do OCR experimenting here and just return the result in 'image_details' for now
    # late you will make this a function on its own and a specific interface in index.html
    result = ocr.predict(filepath)
    print(type(result))
    ocr_found = []
    for line in result:
        for text in line["rec_texts"]:
            print(text)
            ocr_found.append(text)
    image_details["ocr"]=ocr_found
    # need to convert all 'I' to a 1 as confusion between I and 1 can happen on some reg plates
    updated_list_I_conversion = [text.replace('I', '1') for text in ocr_found]
    irish_reg_plates = extract_and_strip_irish_plates(updated_list_I_conversion)

    image_details["valid_regs"]=irish_reg_plates

    # Debugging (not required - just information to generate on Render runs):
    print('filename:', photo.filename)
    print('Long OCR Result from Paddle:', result)
    print('file size:', file_size_mb)
    print('image width:', img.width)
    print('image height:', img.height)
    print('image format:', img.format)
    print('color mode:', img.mode)
    print('latitude:', latitude)
    print('longitude:', longitude)
    print('all ocr found by line (list format):', ocr_found)


    # *********** FIN OCR for function creation *************





    
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
