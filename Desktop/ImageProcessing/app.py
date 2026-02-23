import os
import streamlit as st
import json
from google import genai
from google.genai import types
from PIL import Image

# 1. SETUP
# Ensure you run 'set API_KEY=your_key' in your terminal first
api_key = os.environ.get("API_KEY")
if not api_key:
    st.error("🔑 API Key not found! Please set the API_KEY environment variable.")
    st.stop()

client = genai.Client(api_key=api_key)

st.set_page_config(page_title="AI Marketplace Guard Pro", layout="wide")
st.title("🛡️ Universal AI Marketplace Guard")

# 2. DYNAMIC INPUTS
st.sidebar.header("Listing Configuration")
item_title = st.sidebar.text_input("What are you selling? (Title/Model)", "e.g., iPhone 15 Pro Max")
uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "png"])

# Use session_state to remember the suggested categories
if "suggestions" not in st.session_state:
    st.session_state.suggestions = None

if uploaded_file and item_title:
    img = Image.open(uploaded_file)
    st.image(img, width=400)
    
    # --- STEP 1: AUTO-CATEGORY PREDICTION ---
    if st.session_state.suggestions is None:
        with st.spinner("Predicting best categories..."):
            cat_prompt = f"Look at this image and the title '{item_title}'. Suggest the 3 most accurate marketplace categories it belongs to. Return ONLY a JSON list of 3 strings."
            cat_response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[cat_prompt, img],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            st.session_state.suggestions = json.loads(cat_response.text)

    # Display suggestions as buttons
    st.write("### 🏷️ Select the correct category:")
    cols = st.columns(len(st.session_state.suggestions))
    selected_category = None
    
    for idx, cat in enumerate(st.session_state.suggestions):
        if cols[idx].button(f"📁 {cat}", use_container_width=True):
            selected_category = cat

    # --- STEP 2: FULL FORENSIC AUDIT (Triggered by Category Click) ---
    if selected_category:
        st.divider()
        with st.spinner(f"Performing Forensic Audit for '{selected_category}'..."):
            audit_prompt = f"""
            Audit this listing. Category: '{selected_category}', Title: '{item_title}'.
            
            FORENSIC TASKS:
            1. IDENTIFICATION: Does the hardware in the image match the specs of '{item_title}'?
            2. SPOOFING: Is this a photo of a screen? (Check for Moiré patterns).
            3. AUTHENTICITY: Check logo consistency and material quality.
            4. SAFETY: Any prohibited content?

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
                model="gemini-3-flash-preview",
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

            st.write("### Forensic Breakdown")
            st.table({
                "Attribute": ["Category Selected", "Detected As", "Hardware Match", "Screen Spoofing?", "Confidence"],
                "Value": [selected_category, res['detected_model'], not res['mismatch_found'], res['is_photo_of_screen'], f"{res['confidence_score']*100}%"]
            })
            st.info(f"**AI Logic:** {res['technical_reason']}")

            # Reset button to try another image/category
            if st.button("Clear and Scan New Item"):
                st.session_state.suggestions = None
                st.rerun()