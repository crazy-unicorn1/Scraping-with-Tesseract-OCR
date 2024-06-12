import pytesseract
import cv2
import numpy as np
import requests
from io import BytesIO

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        img_data = response.content
        img_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    else:
        raise Exception("Failed to download image")

def ocr_image(img_url):
    try:
        # Download the image
        img = download_image(img_url)
        
        if img is None:
            raise FileNotFoundError("The image could not be loaded.")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Extract text using Tesseract
        text = pytesseract.image_to_string(gray)

        # Print the extracted text
        return text
    except FileNotFoundError as fnf_error:
        return null
    except Exception as e:
        return null