import os
from openai import OpenAI

# Initialize the client (Ensure your API key is in environment variables)
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

def validate_marketplace_listing(image_url, selected_category):
    """
    Performs a dual-check for Safety and Category Match.
    """
    
    prompt = f"""
    Analyze this image for a marketplace app (similar to OLX).
    The user has listed this under the category: '{selected_category}'.
    
    Please provide a JSON response with the following fields:
    1. "is_safe": (boolean) False if it contains nudity, violence, or hate speech.
    2. "category_match": (boolean) True if the image actually shows a {selected_category}.
    3. "reason": (string) A brief explanation of your decision.
    """

    response = client.chat.completions.create(
        model="gpt-4o", # Using a vision-capable model
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        response_format={ "type": "json_object" }
    )

    return response.choices[0].message.content

# --- Example Usage ---
# Test 1: A car image listed in 'Electronics'
result = validate_marketplace_listing(
    "https://example.com/car_photo.jpg", 
    "Mobile Phones"
)
print(result)