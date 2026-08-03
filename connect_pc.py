from flask import Flask, jsonify, request

app = Flask(__name__)
# This holds the data your PC uploads
shared_data = {"list": []}

# Your PC sends the list here
@app.route('/upload', methods=['POST'])
def upload():
    shared_data["list"] = request.json.get("data", [])
    return "OK", 200

# Your Web/Mobile users read the list from here
@app.route('/view', methods=['GET'])
def view():
    return jsonify(shared_data["list"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

