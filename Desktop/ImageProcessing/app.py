import os
import streamlit as st
import json
import time
from google import genai
from google.genai import types 
from PIL import Image

# 1. SETUP WITH IMPROVED RESILIENCE
api_key = os.environ.get("API_KEY")

# Increased timeout and attempts for better stability
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=30.0, 
        retry_options=types.HttpRetryOptions(
            attempts=3, # Fewer retries here because we will handle the fallback manually
            initial_delay=3.0,
            http_status_codes=[503, 504, 429]
        )
    )
)

st.set_page_config(page_title="AI Marketplace Guard Pro", layout="wide")
st.title("🛡️ Universal AI Marketplace Guard")

# --- HELPER FUNCTION FOR FALLBACK LOGIC ---
def call_gemini_with_fallback(prompt, img):
    """Tries 2.0 first, falls back to 1.5 if 2.0 is overloaded."""
    for model_name in ["gemini-2.0-flash", "gemini-1.5-flash","gemini-flash-latest"]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt, img],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            if "503" in str(e) or "overloaded" in str(e).lower():
                st.warning(f"⚠️ {model_name} is busy. Trying fallback engine...")
                time.sleep(1) # Small rest
                continue
            raise e
    return None

# 2. DYNAMIC INPUTS
st.sidebar.header("Listing Configuration")
item_title = st.sidebar.text_input("Product Title/Model", placeholder="e.g., iPhone 15 Pro Max")
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])

# Persistent State Management
if "suggestions" not in st.session_state:
    st.session_state.suggestions = None
if "audit_result" not in st.session_state:
    st.session_state.audit_result = None

if uploaded_file and item_title:
    img = Image.open(uploaded_file)
    st.image(img, width=400)
    
    # --- STEP 1: AUTO-CATEGORY PREDICTION ---
    if st.session_state.suggestions is None:
        with st.spinner("Analyzing categories..."):
            try:
                cat_prompt = f"Identify 3 marketplace categories for '{item_title}'. Return ONLY a JSON list of 3 strings."
                st.session_state.suggestions = call_gemini_with_fallback(cat_prompt, img)
            except Exception as e:
                st.error("🔌 All AI servers are currently busy. Please try again in a moment.")
                st.stop()

    if st.session_state.suggestions:
        st.write("### 🏷️ Select the correct category:")
        cols = st.columns(len(st.session_state.suggestions))
        
        for idx, cat in enumerate(st.session_state.suggestions):
            if cols[idx].button(f"📁 {cat}", key=f"btn_{cat}", use_container_width=True):
                # --- STEP 2: FULL FORENSIC AUDIT ---
                with st.spinner(f"Auditing for '{cat}'..."):
                    try:
                        audit_prompt = f"""
                        Audit this listing. Category: '{cat}', Title: '{item_title}'.
                        Return JSON: {{
                          "decision": "APPROVE" | "REJECT" | "FLAG_FOR_HUMAN",
                          "confidence_score": 0.0,
                          "detected_model": "string",
                          "mismatch_found": bool,
                          "safety_violation": bool,
                          "is_photo_of_screen": bool,
                          "technical_reason": "string"
                        }}
                        """
                        st.session_state.audit_result = call_gemini_with_fallback(audit_prompt, img)
                        st.session_state.last_category = cat
                    except Exception:
                        st.error("Audit server busy. Please click the category again.")

    # --- DISPLAY PERSISTENT RESULTS ---
    if st.session_state.audit_result:
        res = st.session_state.audit_result
        st.divider()
        
        if res['decision'] == "APPROVE":
            st.success(f"✅ **APPROVED**")
        elif res['decision'] == "FLAG_FOR_HUMAN":
            st.warning(f"⚠️ **FLAGGED FOR REVIEW**")
        else:
            st.error(f"❌ **REJECTED**")

        st.table({
            "Attribute": ["Category", "Detected As", "Hardware Match", "Screen Spoofing?", "Confidence"],
            "Value": [st.session_state.get('last_category'), res['detected_model'], not res['mismatch_found'], res['is_photo_of_screen'], f"{res['confidence_score']*100}%"]
        })
        st.info(f"**AI Logic:** {res['technical_reason']}")