import os
import streamlit as st
import json
from google import genai
from google.genai import types
from PIL import Image

# --- SECURITY CHECK ---
api_key = os.environ.get("API_KEY")
if not api_key:
    st.error("🔑 API Key not found! Run 'set GEMINI_API_KEY=your_key' in your terminal.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- UI SETUP ---
st.set_page_config(page_title="Advanced AI Moderator", layout="wide")
st.title("🛡️ Marketplace AI Guard (Pro)")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("Listing Data")
    category = st.selectbox("Category", ["Mobiles", "Vehicles", "Fashion", "Laptops"])
    claimed_model = st.text_input("Claimed Model", "e.g., iPhone 15 Pro")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])

with col2:
    st.header("Audit Analysis")
    if uploaded_file and claimed_model:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        
        if st.button("Deep Forensic Scan"):
            with st.spinner("Analyzing textures and hardware specs..."):
                # --- THE EDGE-CASE PROMPT ---
                prompt = f"""
                Perform a forensic audit of this listing: '{claimed_model}' in '{category}'.
                
                CHECK FOR THESE EDGE CASES:
                1. SPOOFING: Detect Moiré patterns, screen glare, or pixel grids indicating it's a photo of a screen.
                2. TAMPERING: Check if logos (Apple, Samsung, etc.) look like stickers or are inconsistent with the body.
                3. HARDWARE AUDIT: For {claimed_model}, check for correct camera count, port type (USB-C vs Lightning), and bezel size.
                4. MATERIAL: Ensure the texture matches the claimed quality (e.g., Titanium vs Plastic).

                Return ONLY a JSON object:
                {{
                  "is_safe": bool,
                  "is_real_photo": bool,
                  "model_match": bool,
                  "confidence": 0.0 to 1.0,
                  "detected_features": ["list of hardware found"],
                  "red_flags": ["list any anomalies found"],
                  "final_decision": "APPROVE" | "REVIEW" | "REJECT"
                }}
                """

                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=[prompt, img],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )

                res = json.loads(response.text)

                # --- REAL-TIME DECISION LOGIC ---
                st.subheader("Decision Engine")
                
                # Confidence Thresholding
                if res['confidence'] < 0.7:
                    st.warning(f"⚠️ **LOW CONFIDENCE ({res['confidence']*100}%):** Sending to Human Moderator.")
                    decision_color = "orange"
                elif res['final_decision'] == "APPROVE":
                    st.success(f"✅ **AUTO-APPROVED:** Confirmed as {claimed_model}.")
                    decision_color = "green"
                else:
                    st.error(f"❌ **AUTO-REJECTED:** Potential Fraud or Mismatch.")
                    decision_color = "red"

                # Display Red Flags
                if res['red_flags']:
                    st.write("🚩 **Red Flags Detected:**")
                    for flag in res['red_flags']:
                        st.markdown(f"- {flag}")