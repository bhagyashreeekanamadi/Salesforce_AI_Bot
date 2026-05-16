import streamlit as st
import requests
import speech_recognition as sr

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Salesforce Interview AI Bot",
    page_icon="🤖",
    layout="centered"
)

# BACKEND_URL = "http://127.0.0.1:8000"
BACKEND_URL = "https://salesforce-ai-bot-2.onrender.com"


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

    response = requests.get(
        f"{BACKEND_URL}/generate-question"
    )

    data = response.json()

    st.session_state.question = data["question"]

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

                response = requests.post(
                    f"{BACKEND_URL}/evaluate-answer",
                    json=payload
                )

            data = response.json()

            evaluation = data["evaluation"]
            score = data["score"]

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

    # ==========================================
    # VOICE MODE
    # ==========================================

    elif mode == "Voice Mode":

        st.write("Click below and speak your answer.")

        if st.button("🎤 Record Voice Answer"):

            recognizer = sr.Recognizer()

            try:

                with sr.Microphone() as source:

                    st.info("Listening...")

                    audio = recognizer.listen(source)

                voice_text = recognizer.recognize_google(audio)

                st.subheader("🗣 Your Answer")

                st.success(voice_text)

                payload = {
                    "question": st.session_state.question,
                    "answer": voice_text
                }

                with st.spinner("Evaluating Voice Answer..."):

                    response = requests.post(
                        f"{BACKEND_URL}/evaluate-answer",
                        json=payload
                    )

                data = response.json()

                evaluation = data["evaluation"]
                score = data["score"]

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

                st.error(str(e))

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

        response = requests.post(
            f"{BACKEND_URL}/explain-concept",
            json=payload
        )

    explanation = response.json()["explanation"]

    st.subheader("📖 Explanation")

    st.success(explanation)

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "Built with FastAPI + Streamlit | By Bhagyashree Kanamadi"
)
