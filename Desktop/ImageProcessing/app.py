import os
from openai import OpenAI

# 1. Initialize the AI Client
client = OpenAI() # It will automatically find your env variable key

def process_listing(image_path, user_category):
    """
    Analyzes an image for safety and category accuracy.
    """
    # System instructions to ensure the AI behaves like a moderator
    instructions = f"""
    You are an AI Moderator for a marketplace app. 
    The user claims this is a: {user_category}.
    Task: 
    1. Check for offensive content (Safety).
    2. Verify if the image matches the category (Validation).
    Return your answer in JSON format only: 
    {{ "safe": bool, "match": bool, "reason": "string" }}
    """

    # For the POC, we are using a vision-capable model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": [
                {"type": "text", "text": "Analyze this listing image."},
                {"type": "image_url", "image_url": {"url": image_path}} # You can also upload local files
            ]}
        ],
        response_format={ "type": "json_object" }
    )

    return response.choices[0].message.content

# 2. Test your POC
if __name__ == "__main__":
    # Replace with a real image link for testing
    sample_img = "https://upload.wikimedia.org/wikipedia/commons/a/af/Free_phone_on_the_wall.jpg"
    print(process_listing(sample_img, "Electronics"))