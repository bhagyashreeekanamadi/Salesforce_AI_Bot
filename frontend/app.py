import streamlit as st
import requests
import time

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Salesforce Interview AI Bot",
    page_icon="🤖",
    layout="centered"
)

# ==========================================
# BACKEND URL
# ==========================================

BACKEND_URL = "https://salesforce-ai-bot-2.onrender.com"

# ==========================================
# SAFE JSON RESPONSE
# ==========================================

def safe_json_response(response):

    if response.status_code != 200:

        st.error(f"Backend Error: {response.status_code}")

        st.code(response.text)

        return None

    try:
        return response.json()

    except Exception:

        st.error("Invalid JSON Response")

        st.code(response.text)

        return None

# ==========================================
# RETRY REQUEST
# ==========================================

def make_request(method, endpoint, payload=None):

    for i in range(3):

        try:

            if method == "GET":

                response = requests.get(
                    f"{BACKEND_URL}{endpoint}",
                    timeout=60
                )

            else:

                response = requests.post(
                    f"{BACKEND_URL}{endpoint}",
                    json=payload,
                    timeout=60
                )

            return response

        except Exception:

            time.sleep(5)

    return None

# ==========================================
# TITLE
# ==========================================

st.title("🤖 Salesforce Interview AI Chatbot")

st.write("Practice Salesforce interviews using AI.")

# ==========================================
# SESSION STATE
# ==========================================

if "question" not in st.session_state:
    st.session_state.question = ""

# ==========================================
# GENERATE QUESTION
# ==========================================

st.subheader("🎯 Interview Question")

if st.button("Generate Question"):

    with st.spinner("Generating Question..."):

        response = make_request(
            "GET",
            "/generate-question"
        )

    if response:

        data = safe_json_response(response)

        if data and "question" in data:

            st.session_state.question = data["question"]

        else:

            st.error("Failed to generate question.")

    else:

        st.error("Backend unavailable.")

# ==========================================
# DISPLAY QUESTION
# ==========================================

if st.session_state.question:

    st.info(st.session_state.question)

    # ==========================================
    # INTERVIEW MODE
    # ==========================================

    mode = st.radio(
        "Choose Interview Mode",
        ["Typing Mode", "Voice Mode"]
    )

    # ==========================================
    # TYPING MODE
    # ==========================================

    if mode == "Typing Mode":

        typed_answer = st.text_area(
            "Type Your Answer",
            height=200
        )

        if st.button("Submit Typed Answer"):

            payload = {
                "question": st.session_state.question,
                "answer": typed_answer
            }

            with st.spinner("Evaluating Answer..."):

                response = make_request(
                    "POST",
                    "/evaluate-answer",
                    payload
                )

            if response:

                data = safe_json_response(response)

                if data:

                    evaluation = data.get(
                        "evaluation",
                        "No evaluation"
                    )

                    score = data.get(
                        "score",
                        0
                    )

                    # ==========================================
                    # SCORE
                    # ==========================================

                    st.subheader("📊 Interview Score")

                    st.progress(score / 100)

                    st.metric(
                        label="Score",
                        value=f"{score}/100"
                    )

                    # ==========================================
                    # FEEDBACK
                    # ==========================================

                    st.subheader("📝 AI Feedback")

                    st.success(evaluation)

            else:

                st.error("Backend unavailable.")

    # ==========================================
    # VOICE MODE
    # ==========================================

    elif mode == "Voice Mode":

        st.info(
            "🎤 Voice Interview Feature is under implementation."
        )

# ==========================================
# EXPLAIN CONCEPT
# ==========================================

st.markdown("---")

st.subheader("📘 Explain Salesforce Concept")

concept = st.text_input(
    "Enter Salesforce Concept"
)

if st.button("Explain Concept"):

    payload = {
        "concept": concept
    }

    with st.spinner("Generating Explanation..."):

        response = make_request(
            "POST",
            "/explain-concept",
            payload
        )

    if response:

        data = safe_json_response(response)

        if data:

            explanation = data.get(
                "explanation",
                "No explanation generated."
            )

            st.subheader("📖 Explanation")

            st.success(explanation)

    else:

        st.error("Backend unavailable.")

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "Built with FastAPI + Streamlit + Groq | By Bhagyashree Kanamadi"
)
