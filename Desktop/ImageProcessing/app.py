import os
from google import genai
from google.genai import types
import PIL.Image

# 1. Setup the Client
# Ensure you have set your API key in your terminal: set GEMINI_API_KEY=your_key
# CHANGE THIS:
# client = genai.Client(api_key=os.environ.get("AIzaSyD..."))

# TO THIS:
client = genai.Client(api_key="AIzaSyD6Fv74_6yJUK0tioUUY1DD0VS_QBZ877E")

def validate_listing(image_path, category):
    # Open the image file
    img = PIL.Image.open(image_path)
    
    # Modern Prompt
    prompt = f"""
    Act as a marketplace moderator. The user is listing this item under: '{category}'.
    
    Please analyze the image and provide a JSON response:
    1. 'is_safe': (boolean) False if it contains nudity, violence, or offensive content.
    2. 'category_match': (boolean) True if the image shows an item belonging to '{category}'.
    3. 'reason': (string) A short explanation.
    """
    
    # Using the latest Gemini 3 Flash model
    response = client.models.generate_content(
        model="gemini-3-flash",
        contents=[prompt, img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    return response.text

if __name__ == "__main__":
    # Test with your local image
    try:
        print(validate_listing("car_photo.jpg", "Electronics"))
    except Exception as e:
        print(f"Error: {e}")