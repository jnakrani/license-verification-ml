# license-verification-ml
This Flask application allows users to verify their age and identity using two images: a license image and a selfie image. The application uses face detection and recognition techniques along with OCR (Optical Character Recognition) to extract the age from the selfie image and compare it with the age on the license image for verification. The similarity percentage between the faces in the two images is also calculated to assess the match.


## Prerequisites
Before running the application, make sure you have the following installed:
> Python (version 3.9.1)
> Tesseract OCR (install it separately and provide the path in the code)


## Endpoints

 - ##### Ping Endpoint
  ```GET /ping```

-- Use this endpoint to check if the server is running. It returns a simple success message.
 - ##### Upload Endpoint
 
  ```POST /upload```

-- Use this endpoint to upload the "License_image" and "Selfie_image" files and get the results.

- ##### Request
- Method: POST
- Headers: Content-Type: multipart/form-data
- Body: Form-data
  - Key: License_image, Type: File
  - Key: Selfie_image, Type: File

- ##### Response
The API will process the uploaded images and return the following JSON response:
```json
{
  "predicted_age_from_selfie_image": "30 year",
  "calculated_age_from_license": "32 year",
  "face_similarity_percentage": "80.50%"
}
```

- `predicted_age_from_selfie_image`: The predicted age from the selfie image in years.
- `calculated_age_from_license`: The calculated age from the license image in years.
- `face_similarity_percentage`: The similarity percentage between the license image and the selfie image.

## Usage

1. Ensure you have Python and the required packages installed (Flask, deepface, pytesseract, etc.).

2. Clone or download the project files to your local machine.

3. Install the required packages using the following command:
```
pip install -r requirements.txt
```

4. Create a `.env` file in the project directory and set the `TESSERACT_PATH` variable to the path of your Tesseract OCR executable. For example:
```
TESSERACT_PATH=/path/to/tesseract
```
5. Run the Flask app:
```
python app.py
```

6. The app will be running on http://127.0.0.1:5000/.

7. Open Postman or any other API client.

8. Use the "ping" endpoint to check if the server is running by making a GET request to http://127.0.0.1:5000/ping.

9. To use the "upload" endpoint, create a POST request to http://127.0.0.1:5000/upload.

10. In the body of the request, choose the "form-data" option and add two keys:

  - Key: license_image, Type: File (Select your license image file).
  - Key: selfie_image, Type: File (Select your selfie image file).

11. Send the request, and the API will process the images and return the JSON response with the face similarity and age information.

12. You will see the logs in the api_log.log file located in the project directory.

Note: Make sure the images you are uploading are in one of the allowed formats: png, jpg, jpeg, gif, jfif.

## Important Notes

- The API uses the deepface library to perform face recognition and age prediction.

- It uses Tesseract OCR to recognize text from the "License_image" (if present) to calculate the age from the license.

- The app saves the uploaded images temporarily in the static/uploaded_images folder. For production use, consider handling image storage differently.

- Ensure you provide a secure secret key for the app (change the app.config['SECRET_KEY'] value) when deploying it to production.


That's it! You can now use the API to analyze face similarity and age information from your uploaded images