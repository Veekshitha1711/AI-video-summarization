import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json

# --- CONFIG ---
st.set_page_config(page_title="Universal Marketplace Guard", layout="wide")
st.title("🛡️ Universal Listing Auditor")

# --- API SETUP ---

api_key = os.environ.get("API_KEY")

if not api_key:
    st.error("Missing API Key! Please set the GEMINI_API_KEY environment variable.")
    st.stop()

client = genai.Client(api_key=api_key)
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Listing Details")
    category = st.selectbox("Category", ["Automobiles", "Mobiles", "Laptops", "Fashion", "Appliances", "Furniture"])
    user_title = st.text_input("Listing Title (Specific Model)", placeholder="e.g. 2022 Honda Civic RS or Rolex Submariner")
    uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "png"])

with col2:
    st.header("Audit Result")
    if uploaded_file and user_title:
        img = Image.open(uploaded_file)
        st.image(img, width=400)
        
        if st.button("Perform Deep Audit"):
            with st.spinner("Analyzing specific model features..."):
                prompt = f"""
                You are an expert appraiser. A user is listing an item in '{category}' with the title '{user_title}'.
                
                Your Task:
                1. Identify the specific make, model, and year/version of the object in the image.
                2. Determine if it is a GENUINE match for the user's title: '{user_title}'.
                3. Scan for safety: Ensure no offensive content, weapons, or illegal items.
                
                Return JSON:
                {{
                  "is_safe": bool,
                  "exact_match": bool,
                  "detected_model": "string",
                  "confidence": "0-100%",
                  "discrepancies": ["list of visual mismatches"],
                  "decision": "APPROVE | REJECT | FLAG"
                }}
                """

                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=[prompt, img],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )

                res = json.loads(response.text)

                # Output Logic
                if res['decision'] == "APPROVE":
                    st.success(f"✅ APPROVED: Detected {res['detected_model']}")
                elif res['decision'] == "FLAG":
                    st.warning(f"⚠️ FLAG: {res['detected_model']} detected but has discrepancies.")
                else:
                    st.error(f"❌ REJECTED: Mismatch detected.")
                
                st.json(res)