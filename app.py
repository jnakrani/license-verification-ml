import os
from flask import Flask, request,jsonify
from werkzeug.utils import secure_filename
import cv2
from deepface import DeepFace
from dotenv import load_dotenv
load_dotenv()
import logging
from datetime import datetime
import pytesseract
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import re


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploaded_images'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif', 'jfif'])
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key

def generate_dynamic_path(filename):
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class ImageApp:
    def __init__(self):
        pass
    def preprocess_image_and_recognize_text(self,filepath1):
    # Load the image
        selfie_image = cv2.imread(filepath1)

    # Preprocess the image.
        selfie_image = cv2.cvtColor(selfie_image, cv2.COLOR_BGR2GRAY)
        selfie_image = cv2.threshold(selfie_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Recognize the text in the image.
        text = pytesseract.image_to_string(selfie_image)
        # text = "Your OCR text"
        # logging.info(f"Recognized Text: {text}")
        return text


    def calculate_age_from_text(self,text):
        dob_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\d{2}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YY
            r'\d{2}/\d{2}/\d{2}'
        ]
        dob_keywords = [
            'DOB:',
            'Date of Birth:',
            'Birthdate:',
            'D of B:',
            'D of B',
            'DofB',
            'D of B',
            'vos:',
            'pos\t ',
            'BRO ',
            'pos ',
            'oof8 ',
        ]

        for dob_pattern in dob_patterns:
            for dob_keyword in dob_keywords:
                dob_match = re.search(rf'{dob_keyword} {dob_pattern}', text)
                if dob_match:
                    dob = dob_match.group(0).split(' ')[1]

                    try:
                        # Convert the DOB string to a datetime object
                        try:
                            dob_datetime = datetime.strptime(dob, '%d/%m/%Y')
                        except ValueError:
                            dob_datetime = datetime.strptime(dob, '%d-%m-%y')

                        # Get the current date
                        current_datetime = datetime.now()

                        # Calculate the age
                        age_ocr = current_datetime.year - dob_datetime.year
                        

                        # Adjust for cases where the birthday hasn't occurred this year yet
                        if (current_datetime.month, current_datetime.day) < (dob_datetime.month, dob_datetime.day):
                            age_ocr -= 1
                            # logging.info(f"Calculated Age: {age_ocr}")
                        return age_ocr
                    except ValueError as e: 
                        print("", e)
                        return None
        return None
    

    def process_images(self, filepath1, filepath2):
            
            image1=filepath1
            image2=filepath2
            Age=DeepFace.analyze(img_path = image2, 
                    actions = ["age", "gender", "emotion", "race"])
            predicted_age_text = Age[0]['age']
            result = DeepFace.verify(img1_path=image1, img2_path=image2,distance_metric="cosine",model_name="VGG-Face")
            # Calculate the similarity percentage
            # threshold=result['threshold']  #if thresold> 0.4 (depend) value then it is not same person
            similarity_percentage = (1.0 - result['distance']) * 100
            logging.info(f"Predicted Age (DeepFace): {predicted_age_text}")
            logging.info(f"Similarity Percentage (DeepFace): {similarity_percentage}")
            return predicted_age_text, similarity_percentage

    def upload(self):
        image_app = ImageApp()
        predicted_age_text = None
        similarity_percentage = None
        age_ocr = None

        

        license_image = request.files['license_image']
        selfie_image = request.files['selfie_image']

        if 'license_image' not in request.files or 'selfie_image' not in request.files:
            return jsonify({"error": "Both 'License_image' and 'Selfie_image' files are required."}), 400
        
        if license_image and allowed_file(license_image.filename) and selfie_image and allowed_file(selfie_image.filename):
            # Generate dynamic file paths for saving the uploaded images
            filename1 = secure_filename(license_image.filename)
            filename2 = secure_filename(selfie_image.filename)
            filepath1 = generate_dynamic_path(filename1)
            filepath2 = generate_dynamic_path(filename2)

            # Save the uploaded images to the designated paths
            license_image.save(filepath1)
            selfie_image.save(filepath2)

            # Process the images and obtain results
            predicted_age_text, similarity_percentage = image_app.process_images(filepath1, filepath2)
            text = image_app.preprocess_image_and_recognize_text(filepath1)
            age_ocr = image_app.calculate_age_from_text(text)

            # Log the results
            app.logger.info(f"Predicted Age (DeepFace): {predicted_age_text}")
            app.logger.info(f"Age OCR (Tesseract): {age_ocr} Years")
            app.logger.info(f"Similarity Percentage (DeepFace): {similarity_percentage}")
            

            # Return JSON response
            response_data = {
                "predicted_age_from_selfie_image": f"{predicted_age_text} year",
                "calculated_age_from_license": f"{age_ocr} year",
                "face_similarity_percentage": "{:.2f}%".format(similarity_percentage)
             }

            return jsonify(response_data), 200

        # Return an error response if the request is not valid or any processing fails
        return jsonify({"error": "Invalid request or processing failed."}), 400


@app.route('/ping')
def index():
    return {"success": "True"}, 200

@app.route('/upload', methods=['POST'])
def upload():
    image_app = ImageApp()

    return image_app.upload()

if __name__ == "__main__":
    logging.basicConfig(filename='api_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Run the app in debug mode
    app.run(debug=True)

