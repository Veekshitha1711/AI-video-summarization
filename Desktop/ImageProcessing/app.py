import google.generativeai as genai
import PIL.Image

# 1. Setup (Replace with your free key from Google AI Studio)
genai.configure(api_key="AIzaSyD6Fv74_6yJUK0tioUUY1DD0VS_QBZ877E")
model = genai.GenerativeModel('gemini-1.5-flash')

def validate_listing(image_path, category):
    img = PIL.Image.open(image_path)
    
    prompt = f"""
    Act as a marketplace moderator. The user says this item is in the category: '{category}'.
    Check:
    1. Is the image safe (no violence, offensive content, or nudity)?
    2. Does the image match the category '{category}'?
    
    Response format (JSON):
    {{ "is_safe": bool, "category_match": bool, "reason": "string" }}
    """
    
    response = model.generate_content([prompt, img])
    return response.text

# 4. Test it
if __name__ == "__main__":
    # You can use a local path like 'test_image.jpg' or a PIL object
    print(validate_listing("car_photo.jpg", "Electronics"))