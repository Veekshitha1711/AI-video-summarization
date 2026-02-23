import os
import streamlit as st
import json
from google import genai
from google.genai import types
from PIL import Image

# 1. SETUP
api_key = os.environ.get("API_KEY")
client = genai.Client(api_key=api_key)

st.set_page_config(page_title="Universal AI Marketplace Guard", layout="wide")
st.title("🛡️ Universal AI Marketplace Guard")

# 2. DYNAMIC INPUTS
st.sidebar.header("Listing Configuration")
# Now you can type ANY category, or choose from common ones
category_input = st.sidebar.text_input("Category", "Mobiles") 
item_title = st.sidebar.text_input("Exact Model/Title", "iPhone 15 Pro Max, Blue Titanium")

uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "png"])

if uploaded_file and item_title:
    img = Image.open(uploaded_file)
    st.image(img, width=500)
    
    if st.button("🚨 Run Full Forensic Audit"):
        with st.spinner(f"Analyzing '{item_title}' for fraud & edge cases..."):
            # THE UNIVERSAL PROMPT: Works for ANY item (drill, car, watch, phone)
            prompt = f"""
            You are an expert quality control agent for a global marketplace.
            The user is listing an item in the category: '{category_input}'.
            The user claims this specific model/item is: '{item_title}'.

            AUDIT INSTRUCTIONS:
            1. IDENTIFICATION: Look at the unique hardware/design features. Is this exactly what they claim? 
               (e.g., if it's a car, check headlights/grills; if a phone, check ports/cameras; if a watch, check dial details).
            2. SPOOFING CHECK: Is this a real photo, or a photo of a screen/monitor? Look for moiré patterns or pixel grids.
            3. CONDITION & AUTHENTICITY: Does the branding/logo look genuine? Are there any 'Frankenstein' parts (mixed parts)?
            4. SAFETY: Does it contain prohibited content (weapons, drugs, nudity)?

            OUTPUT ONLY JSON:
            {{
              "decision": "APPROVE" | "REJECT" | "FLAG_FOR_HUMAN",
              "confidence_score": 0.0,
              "detected_model": "string",
              "mismatch_found": bool,
              "safety_violation": bool,
              "is_photo_of_screen": bool,
              "technical_reason": "string"
            }}
            """

            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, img],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )

            res = json.loads(response.text)

            # 3. DISPLAY RESULTS
            st.divider()
            if res['decision'] == "APPROVE":
                st.success(f"✅ **APPROVED**")
                st.balloons()
            elif res['decision'] == "FLAG_FOR_HUMAN":
                st.warning(f"⚠️ **FLAGGED FOR REVIEW**")
            else:
                st.error(f"❌ **REJECTED**")

            # Deep Details Table
            st.write("### Forensic Breakdown")
            st.table({
                "Attribute": ["Detected As", "Category Match", "Is Screen Photo?", "Confidence"],
                "Value": [res['detected_model'], not res['mismatch_found'], res['is_photo_of_screen'], f"{res['confidence_score']*100}%"]
            })
            st.info(f"**AI Logic:** {res['technical_reason']}")