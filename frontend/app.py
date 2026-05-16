import streamlit as st
import requests

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

# BACKEND_URL = "http://127.0.0.1:8000"

BACKEND_URL = "https://salesforce-ai-bot-2.onrender.com"

# ==========================================
# SAFE JSON RESPONSE FUNCTION
# ==========================================

def safe_json_response(response):

    try:
        return response.json()

    except Exception:

        st.error("Backend returned invalid response")

        st.write("Status Code:", response.status_code)

        st.write("Response Text:")

        st.code(response.text)

        return None

# ==========================================
# TITLE
# ==========================================

st.title("🤖 Salesforce Interview AI Chatbot")

st.write(
    "Practice Salesforce interviews using AI."
)

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

    try:

        response = requests.get(
            f"{BACKEND_URL}/generate-question",
            timeout=30
        )

        data = safe_json_response(response)

        if data and "question" in data:

            st.session_state.question = data["question"]

        else:

            st.error("Failed to generate question.")

    except Exception as e:

        st.error(f"Request Failed: {str(e)}")

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

            try:

                with st.spinner("Evaluating Answer..."):

                    response = requests.post(
                        f"{BACKEND_URL}/evaluate-answer",
                        json=payload,
                        timeout=60
                    )

                data = safe_json_response(response)

                if data:

                    evaluation = data.get("evaluation", "No evaluation")
                    score = data.get("score", 0)

                    # ==========================================
                    # SCORE DISPLAY
                    # ==========================================

                    st.subheader("📊 Interview Score")

                    st.progress(score / 100)

                    st.metric(
                        label="Score",
                        value=f"{score}/100"
                    )

                    # ==========================================
                    # FEEDBACK DISPLAY
                    # ==========================================

                    st.subheader("📝 AI Feedback")

                    st.success(evaluation)

            except Exception as e:

                st.error(f"Request Failed: {str(e)}")

    # ==========================================
    # VOICE MODE
    # ==========================================

    elif mode == "Voice Mode":

        st.info(
            "🎤 Voice Interview Feature is currently in progress and under implementation."
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

    try:

        with st.spinner("Generating Explanation..."):

            response = requests.post(
                f"{BACKEND_URL}/explain-concept",
                json=payload,
                timeout=60
            )

        data = safe_json_response(response)

        if data:

            explanation = data.get(
                "explanation",
                "No explanation generated."
            )

            st.subheader("📖 Explanation")

            st.success(explanation)

    except Exception as e:

        st.error(f"Request Failed: {str(e)}")

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "Built with FastAPI + Streamlit | By Bhagyashree Kanamadi"
)
