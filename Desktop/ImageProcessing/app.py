import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Marketplace Guard AI", page_icon="🛡️", layout="centered")

st.title("🛡️ Marketplace Image Guard")
st.subheader("Automated Moderation & Category Validation")

# --- API SETUP ---
# Replace with your key or set it in your environment
API_KEY = "AIzaSyD6Fv74_6yJUK0tioUUY1DD0VS_QBZ877E" 
client = genai.Client(api_key=API_KEY)

# --- APP LOGIC ---
st.sidebar.header("Listing Details")
category = st.sidebar.selectbox(
    "Select Listing Category",
    ["Electronics", "Vehicles", "Real Estate", "Fashion", "Home & Garden"]
)

uploaded_file = st.file_uploader("Upload an item image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_container_width=True)
    
    if st.button("Validate Listing"):
        with st.spinner("AI is analyzing the listing..."):
            try:
                prompt = f"""
                You are a marketplace moderator for an app like OLX.
                The user has listed this item under: '{category}'.
                
                Analyze the image and return ONLY a JSON object with:
                1. 'is_safe': boolean (false if it contains nudity, violence, or offensive content).
                2. 'category_match': boolean (true if the item matches '{category}').
                3. 'reason': string (short explanation).
                """

                # Call Gemini 3 Flash
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=[prompt, img],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

                # Parse JSON Result
                result = json.loads(response.text)

                # --- DISPLAY RESULTS ---
                st.divider()
                
                if result['is_safe'] and result['category_match']:
                    st.success("✅ **Listing Approved!** This post is safe and matches the category.")
                else:
                    st.error("❌ **Listing Rejected**")
                    
                # Detailed breakdown
                col1, col2 = st.columns(2)
                col1.metric("Safety Status", "PASS" if result['is_safe'] else "FAIL")
                col2.metric("Category Match", "MATCH" if result['category_match'] else "MISMATCH")
                
                st.info(f"**AI Reasoning:** {result['reason']}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

else:
    st.info("Please upload an image to begin the validation process.")

# Footer
st.caption("POC powered by Gemini 3 Flash & Streamlit")