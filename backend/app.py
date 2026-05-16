from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
# from openai import OpenAI
from dotenv import load_dotenv

import os
import re

# ==========================================
# LOAD ENV VARIABLES
# ==========================================

load_dotenv()

# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY")
# )

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI()

# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are an expert Salesforce Interview Evaluator.

Evaluate candidate answers professionally.

Return:
1. Score out of 100
2. Strengths
3. Missing Points
4. Improvement Suggestions
5. Final Feedback

Keep feedback beginner friendly.
"""

# ==========================================
# REQUEST MODELS
# ==========================================

class AnswerRequest(BaseModel):
    question: str
    answer: str

class ConceptRequest(BaseModel):
    concept: str

# ==========================================
# GENERATE QUESTION API
# ==========================================

@app.get("/generate-question")

def generate_question():

    response = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": "Generate  Salesforce interview questions."
            },
            {
                "role": "user",
                "content": "Generate one Salesforce interview question."
            }
        ]
    )

    return {
        "question": response.choices[0].message.content
    }

# ==========================================
# EVALUATE ANSWER API
# ==========================================

@app.post("/evaluate-answer")

def evaluate_answer(request: AnswerRequest):

    # ==========================================
    # HANDLE EMPTY ANSWERS
    # ==========================================

    if not request.answer.strip():

        return {
            "evaluation": """
Score: 0/100

Strengths:
- No answer provided

Missing Points:
- Candidate did not attempt the question

Improvements:
- Try answering the question
- Explain concepts in simple words
- Practice Salesforce fundamentals

Final Feedback:
No valid answer was submitted.
""",
            "score": 0
        }

    # ==========================================
    # VERY SHORT ANSWERS
    # ==========================================

    if len(request.answer.strip()) < 10:

        return {
            "evaluation": """
Score: 10/100

Strengths:
- Attempted the question

Missing Points:
- Answer is too short
- Missing technical explanation

Improvements:
- Add examples
- Explain concepts clearly
- Include Salesforce terminology

Final Feedback:
The answer needs more detail and clarity.
""",
            "score": 10
        }

    # ==========================================
    # LLM EVALUATION
    # ==========================================

    evaluation_prompt = f"""
    Interview Question:
    {request.question}

    Candidate Answer:
    {request.answer}

    Evaluate the answer strictly.

    Scoring Rules:
    - Blank answer = 0
    - Very short answer = below 30
    - Partial answer = 40-60
    - Good answer = 70-85
    - Excellent detailed answer = 90+

    Format:

    Score: X/100

    Strengths:
    - ...

    Missing Points:
    - ...

    Improvements:
    - ...

    Final Feedback:
    ...
    """

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": evaluation_prompt
            }
        ]
    )

    evaluation = response.choices[0].message.content

    # ==========================================
    # EXTRACT SCORE
    # ==========================================

    score_match = re.search(r"(\d+)/100", evaluation)

    score = 0

    if score_match:
        score = int(score_match.group(1))

    return {
        "evaluation": evaluation,
        "score": score
    }


# ==========================================
# EXPLAIN CONCEPT API
# ==========================================

@app.post("/explain-concept")

def explain_concept(request: ConceptRequest):

    response = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": "Explain Salesforce concepts clearly for beginners."
            },
            {
                "role": "user",
                "content": f"Explain Salesforce concept: {request.concept}"
            }
        ]
    )

    return {
        "explanation": response.choices[0].message.content
    }