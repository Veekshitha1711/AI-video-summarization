import os
import streamlit as st
import json
from google import genai
from google.genai import types  # Added for HttpOptions
from PIL import Image

# 1. SETUP WITH AUTOMATIC RETRIES
api_key = os.environ.get("API_KEY")

# The Client is now configured to retry 5 times if the server is busy (503)
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=5,                  # Try 5 times before giving up
            initial_delay=2.0,           # Wait 2 seconds before first retry
            max_delay=60.0,              # Maximum wait of 60 seconds
            http_status_codes=[503, 504, 429]  # Retry on Overload, Timeout, and Rate Limit
        )
    )
)

st.set_page_config(page_title="AI Marketplace Guard Pro", layout="wide")
st.title("🛡️ Universal AI Marketplace Guard")

# 2. DYNAMIC INPUTS
st.sidebar.header("Listing Configuration")
item_title = st.sidebar.text_input("What are you selling? (Title/Model)", "e.g., iPhone 15 Pro Max")
uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "png"])

if "suggestions" not in st.session_state:
    st.session_state.suggestions = None

if uploaded_file and item_title:
    img = Image.open(uploaded_file)
    st.image(img, width=400)
    
    # --- STEP 1: AUTO-CATEGORY PREDICTION ---
    if st.session_state.suggestions is None:
        with st.spinner("Predicting best categories (retrying if server busy)..."):
            try:
                cat_prompt = f"Look at this image and the title '{item_title}'. Suggest 3 marketplace categories. Return ONLY a JSON list of 3 strings."
                cat_response = client.models.generate_content(
                    model="gemini-2.0-flash", # Using stable flash model
                    contents=[cat_prompt, img],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                st.session_state.suggestions = json.loads(cat_response.text)
            except Exception as e:
                st.error("🔌 The AI server is overloaded. Please refresh or try again in a minute.")
                st.stop()

    st.write("### 🏷️ Select the correct category:")
    cols = st.columns(len(st.session_state.suggestions))
    selected_category = None
    
    for idx, cat in enumerate(st.session_state.suggestions):
        if cols[idx].button(f"📁 {cat}", use_container_width=True):
            selected_category = cat

    # --- STEP 2: FULL FORENSIC AUDIT ---
    if selected_category:
        st.divider()
        with st.spinner(f"Performing Forensic Audit..."):
            try:
                audit_prompt = f"""
                Audit this listing. Category: '{selected_category}', Title: '{item_title}'.
                OUTPUT JSON:
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
                    model="gemini-2.0-flash",
                    contents=[audit_prompt, img],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                res = json.loads(response.text)

                # --- DISPLAY RESULTS ---
                if res['decision'] == "APPROVE":
                    st.success(f"✅ **LISTING APPROVED**")
                    st.balloons()
                elif res['decision'] == "FLAG_FOR_HUMAN":
                    st.warning(f"⚠️ **FLAGGED FOR MANUAL REVIEW**")
                else:
                    st.error(f"❌ **LISTING REJECTED**")

                st.table({
                    "Attribute": ["Category", "Detected As", "Hardware Match", "Screen Spoofing?", "Confidence"],
                    "Value": [selected_category, res['detected_model'], not res['mismatch_found'], res['is_photo_of_screen'], f"{res['confidence_score']*100}%"]
                })
                st.info(f"**AI Logic:** {res['technical_reason']}")
            except Exception:
                st.error("The server timed out. Please try clicking the category again.")