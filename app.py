

import cv2
import os
import numpy as np
from flask import Flask, request, jsonify, render_template_string
import imutils
# import easyocr


app = Flask(__name__)

# Enforce a maximum file upload size (e.g., 16 Megabytes) to protect server memory
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# --- MOBILE OPTIMIZED HTML FRONTEND ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AWS Plate Scanner</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            text-align: center; 
            padding: 20px; 
            background-color: #f5f5f7; 
            margin: 0;
        }
        .container { 
            max-width: 420px; 
            margin: 40px auto; 
            background: white; 
            padding: 30px; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
        }
        h2 { color: #1d1d1f; margin-bottom: 25px; font-weight: 600; }
        .btn { 
            background: #007aff; 
            color: white; 
            border: none; 
            padding: 16px 20px; 
            font-size: 17px; 
            font-weight: 500;
            border-radius: 12px; 
            cursor: pointer; 
            width: 100%; 
            transition: background 0.2s ease;
            -webkit-tap-highlight-color: transparent;
        }
        .btn:active { background: #0056b3; }
        #result { 
            margin-top: 25px; 
            font-size: 26px; 
            font-weight: 700; 
            color: #1d1d1f; 
            border: 3px solid #e5e5ea; 
            padding: 20px; 
            border-radius: 14px; 
            display: none; 
            background: #fbfbfd;
            letter-spacing: 1px;
        }
        #loading { 
            display: none; 
            color: #86868b; 
            margin-top: 20px; 
            font-size: 15px;
        }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0,122,255,.1);
            border-radius: 50%;
            border-top-color: #007aff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 10px;
            vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h2>Vehicle Plate Scanner</h2>
        
        <!-- capture="environment" targets the rear camera on iPhones -->
        <input type="file" id="cameraInput" accept="image/*" capture="environment" style="display: none;">
        <button class="btn" onclick="document.getElementById('cameraInput').click()">Scan License Plate</button>
        
        <div id="loading"><div class="spinner"></div>Analyzing image...</div>
        <div id="result"></div>
    </div>

    <script>
        document.getElementById('cameraInput').addEventListener('change', async (e) => {
            const files = e.target.files;
            if (files.length === 0) return;

            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('result');
            
            loading.style.display = 'block';
            resultDiv.style.display = 'none';

            const formData = new FormData();
            formData.append('image', files[0]);

            try {
                const response = await fetch('/scan', { 
                    method: 'POST', 
                    body: formData 
                });
                const data = await response.json();
                
                loading.style.display = 'none';
                resultDiv.style.display = 'block';
                
                if (data.success) {
                    resultDiv.innerText = data.plate;
                    resultDiv.style.borderColor = "#34c759";
                    resultDiv.style.color = "#144620";
                } else {
                    resultDiv.innerText = "Error: " + data.error;
                    resultDiv.style.borderColor = "#ff3b30";
                    resultDiv.style.color = "#ff3b30";
                }
            } catch (err) {
                loading.style.display = 'none';
                resultDiv.style.display = 'block';
                resultDiv.style.borderColor = "#ff3b30";
                resultDiv.innerText = "Server communication failed.";
            }
        });
    </script>
</body>
</html>
"""

# --- ROUTE DEFINITIONS ---

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/scan', methods=['POST'])
def scan():
    return jsonify({
        "success": True,
        "plate": "12D12345"
    })
    
# @app.route('/scan', methods=['POST'])
# def scan_plate():
#     if 'image' not in request.files:
#         return jsonify({'success': False, 'error': 'No image partition found'}), 400
        
#     file = request.files['image']
#     if file.filename == '':
#         return jsonify({'success': False, 'error': 'No file selected'}), 400

#     try:
#         # Stream the upload binary file directly into RAM memory
#         file_bytes = np.frombuffer(file.read(), np.uint8)
#         # Decode the file bytes into a classic OpenCV image BGR matrix
#         img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
#         if img is None:
#             return jsonify({'success': False, 'error': 'Corrupt or unsupported image format'}), 400

#         ##############################################################################
#         # 1. Read in Image, Grayscale and Blur
#         # img = cv2.imread('pics/image4.jpg') # my code snippet on its own needs this to define img
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)



#         #2. Apply filter and find edges for localization
#         bfilter = cv2.bilateralFilter(gray, 11, 17, 17) #Noise reduction
#         edged = cv2.Canny(bfilter, 30, 200) #Edge detection



#         #3. Find Contours and Apply Mask
#         keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#         contours = imutils.grab_contours(keypoints)
#         contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
#         location = None
#         for contour in contours:
#             approx = cv2.approxPolyDP(contour, 10, True)
#             if len(approx) == 4:
#                 location = approx
#                 break

#         mask = np.zeros(gray.shape, np.uint8)
#         new_image = cv2.drawContours(mask, [location], 0,255, -1)
#         new_image = cv2.bitwise_and(img, img, mask=mask)

#         (x,y) = np.where(mask==255)
#         (x1, y1) = (np.min(x), np.min(y))
#         (x2, y2) = (np.max(x), np.max(y))
#         cropped_image = gray[x1:x2+1, y1:y2+1]



#         # 4. Use Easy OCR To Read Text
#         reader = easyocr.Reader(['en'])
#         result = reader.readtext(cropped_image, detail=0)
#         # To get EasyOCR to return only the detected text without the bounding box coordinates and confidence scores, 
#         # you need to set the detail parameter to 0 inside the readtext() function.

#         # print(result)
        
#         detected_plate = result  # Replace this value with your variable output
#         ##############################################################################


#         return jsonify({'success': True, 'plate': detected_plate})

#     except Exception as e:
#         return jsonify({'success': False, 'error': f"Internal Processing Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Local fallback parameters
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    # app.run(host='127.0.0.1', port=port, debug=True) # local host
