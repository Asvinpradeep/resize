from flask import Flask, request, jsonify
from PIL import Image
import requests
from io import BytesIO
import os

app = Flask(__name__)

@app.route('/resize-upload', methods=['POST'])
def resize_and_upload():
    try:
        # Step 1: Get image URL from JSON body
        data = request.get_json()
        image_url = data.get('image_url')
        if not image_url:
            return jsonify({"error": "Missing image_url in request"}), 400

        # Step 2: Download the image
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download image"}), 400

        img = Image.open(BytesIO(response.content))

        # Step 3: Resize to 480x480
        img_resized = img.resize((480, 480))

        # Step 4: Save temporarily
        temp_filename = "temp_resized.jpg"
        img_resized.save(temp_filename)

        # Step 5: Upload to tmpfiles.org
        with open(temp_filename, 'rb') as f:
            upload_response = requests.post(
                'https://tmpfiles.org/api/v1/upload',
                files={'file': f}
            )

        # Remove temp file
        os.remove(temp_filename)

        # Step 6: Handle upload response
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            file_url = upload_data.get('data', {}).get('url')
            return jsonify({"uploaded_url": file_url})
        else:
            return jsonify({"error": "Failed to upload image"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
