from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps
import os
import re
from paddleocr import PaddleOCR
from server_reg import get_details

from file_api import upload_file    # my file API
from datetime import datetime       # used to generate unique filename below for storage
import json


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


# used for storage to give unique filename based on date and time including milliseconds to prevent overwritting
# store most recent photo (latest.jpg) on moranai server - rename with a date related timestamp
# stored at reg_app/pics
def store_photo():
    filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".jpg"

    file_for_storage = os.path.join(UPLOAD_FOLDER, "latest.jpg")

    store_pic_using_file_api = upload_file(
        file_path=file_for_storage,
        filename=filename,
        app="reg_app",
        folder="pics"
    )
    print('*********** START *************************************')  # used for clarity in terminal printout during execution
    print('Stored photo on remote server details:', store_pic_using_file_api)

    return filename # we only do this to store it in the csv file - pic already stored above



# store photo details as json - contents of 'image_details' dictionary
# stored at reg_app/photo_details
def store_photo_details(image_details):
    filename = image_details["filename_timestamped"].replace(".jpg", ".json")
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        # Temporarily create JSON file
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(image_details, file, indent=4)

        # Upload to File API
        result = upload_file(
            file_path=filepath,
            app="reg_app",
            folder="photo_details",
            filename=filename
        )

        return result

    finally:
        # Remove temporary local JSON file
        if os.path.exists(filepath):
            os.remove(filepath)




@app.route("/")
def index():
    return render_template("index.html")



@app.route("/reg")
def reg():

    registration = request.args.get("reg")

    vehicle = get_details(registration)

    return render_template(
        "reg.html",
        vehicle=vehicle
    )



# take uploaded image, process OCR and collate image/user data
# future updates may put some of this function content outside in helper functions - no rush - works well here
@app.route("/upload", methods=["POST"]) # here upload means upload pic from user - ie: the taken photo - dont confuse with file API
def upload():
    photo = request.files["photo"]
    filepath = os.path.join(UPLOAD_FOLDER, "latest.jpg")    # this just saves another copy showing its the latest photo - it will be overwritten on next new photo
    photo.save(filepath)

    # Get visitor's User-Agent
    user_agent = request.headers.get("User-Agent")

    # Open image
    img = Image.open(filepath)
    # Apply the EXIF orientation - keeps taken pic orientation; need to import ImageOps too for this
    img = ImageOps.exif_transpose(img)
    # Save the corrected orientated image
    img.save(filepath) # can i get rid of this??? its done below???

    # Resize so the longest side is 1500 pixels
    # img.thumbnail((1500, 1500)) # this work fine - but lets try 800
    # 1000 worked well - going to 800 the reg was still perfect but the other insignificant text of
    # an image started to suffer - which is fine - my testing suggests 800 is the perfect balance point
    # update: on your mac 800 looks like its near the minimum - but on render I think you could go lower!
    # (explore this!)
    img.thumbnail((800, 800)) # keep 800
    img.save(filepath)

    # store photo on server
    # helper function above to store latest photo to moranai.net file api - renames it with a date and time stamp incl milliseconds
    # function is executed, we only use returned value to get new timestamped filename
    new_filename_timestamped = store_photo()

    # Get file details
    file_size_bytes = os.path.getsize(filepath)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    # collate image details obtained so far in image_details dictionary
    image_details["filename"] = photo.filename
    image_details["filesize"] = file_size_mb
    image_details["width"] = img.width
    image_details["height"] = img.height
    image_details["format"] = img.format
    image_details["mode"] = img.mode
    image_details["latitude"] = latitude
    image_details["longitude"] = longitude
    image_details["user_agent"] = user_agent
    image_details["filename_timestamped"] = new_filename_timestamped

    # *********** START OCR ******************************************************
    # do OCR - append results in 'image_details' dictionary
    result = ocr.predict(filepath)  # very verbose - we just need 'rec_texts'
    ocr_found = []
    for line in result:
        for text in line["rec_texts"]:
            ocr_found.append(text)
    image_details["ocr"]=ocr_found
    # need to convert all 'I' to a '1' as confusion between 'I' and '1' can happen on some reg plates
    #       can do as no county contains an 'I'
    updated_list_I_conversion = [text.replace('I', '1') for text in ocr_found]
    irish_reg_plates = extract_and_strip_irish_plates(updated_list_I_conversion)
    image_details["valid_regs"]=irish_reg_plates
    # *********** FIN OCR ********************************************************


    # Save image details as JSON
    store_photo_details(image_details)


    # Debugging (just information to generate on runs):
    print('\nfilename timestamped:'.ljust(26) + new_filename_timestamped)
    print('filename:'.ljust(25) + photo.filename)
    # print('Long OCR Result from Paddle:', result) # not needed for debug as Paddle OCR working as expected - very verbose
    print('file size:'.ljust(25) + str(file_size_mb))
    print('image width:'.ljust(25) + str(img.width))
    print('image height:'.ljust(25) + str(img.height))
    print('image format:'.ljust(25) + str(img.format))
    print('color mode:'.ljust(25) + img.mode)
    print('latitude:'.ljust(25) + latitude)
    print('longitude:'.ljust(25) + longitude)
    print('all ocr found:'.ljust(25) + str(ocr_found))
    print("valid registrations:".ljust(25) + str(irish_reg_plates))
    print("user agent:".ljust(25) + user_agent)
    print('\nimage_details dict:'.ljust(25) + str(image_details))
    print('*********** END ***************************************')  # used for clarity in terminal printout during execution

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
