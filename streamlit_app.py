import streamlit as st
import google.generativeai as genai
import json
import time
from google.api_core.exceptions import ResourceExhausted

# CONFIG
apikey = st.secrets['API_KEY']
genai.configure(api_key=apikey)

generation_config = {
    "temperature": 0.4,
    "top_p": 0.9,
    "top_k": 20,
    "max_output_tokens": 120,  # lower = cheaper
}

model = genai.GenerativeModel(
    model_name="gemini-3.1-flash-lite-preview",
    generation_config=generation_config,
)
print("API CALL")
# SESSION 
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": (
                "Your name is Larry AI developed by COSENTIAL: COSMOS AI DIVISION.\n"
                "If appropriate, recommend books based on the conversation.\n"
                "Only return JSON when recommending a book in this format Return ONLY valid JSON. No extra text before or after. No explanations.:\n"
                '{"type":"book","title":"...","author":"...","description":"...","image":"REAL_URL"}'
            )
        }
    ])

if "processing" not in st.session_state:
    st.session_state.processing = False

# UI
st.title("Larry AI")
st.caption("Powered by COSENTIAL: COSMOS AI DIVISION")

def right_aligned(msg):
    st.markdown(
        f'<div style="text-align:right;padding:8px;">{msg}</div>',
        unsafe_allow_html=True
    )

# AI
def generate_response(prompt):
    try:
        time.sleep(0.5)  # small cooldown

        response = st.session_state.chat.send_message(prompt)
        text = response.text.strip()

        # Try JSON parse (only if it's a book)
        try:
            data = json.loads(text)
            if isinstance(data, dict) and data.get("type") == "book":
                return data
        except:
            pass

        return {"type": "text", "content": text}

    except ResourceExhausted:
        return {"type": "error", "content": "⚠️ Quota exceeded. Try later."}

    except Exception as e:
        return {"type": "error", "content": str(e)}

# RENDER
def render_response(data):
    if data["type"] == "book":
        st.markdown("### 📚 Book Recommendation")

        left, right = st.columns([1, 1.2])

        image_url = data.get("image", "")
        if not isinstance(image_url, str) or not image_url.startswith("http"):
            image_url = "https://via.placeholder.com/150?text=No+Image"

        with left:
            st.image(image_url, use_container_width=True)

        with right:
            st.markdown(f"**{data.get('title','Unknown')}**")
            st.markdown(f"✍️ *{data.get('author','Unknown')}*")
            st.write(data.get("description", ""))

    else:
        st.chat_message("assistant").markdown(data.get("content", ""))

# HISTORY
for msg in st.session_state.messages[-6:]:  
    if msg["role"] == "user":
        right_aligned(msg["content"])
    else:
        render_response(msg["data"])

# INPUT
prompt = st.chat_input("Ask something...")

if prompt and not st.session_state.processing:
    st.session_state.processing = True

    right_aligned(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    placeholder = st.chat_message("assistant").empty()
    placeholder.markdown("Thinking...")

    data = generate_response(prompt)

    placeholder.empty()
    render_response(data)

    st.session_state.messages.append({
        "role": "assistant",
        "data": data
    })

    st.session_state.processing = False
