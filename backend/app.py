from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

import os
import re

# ==========================================
# LOAD ENV VARIABLES
# ==========================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ==========================================
# GROQ CLIENT
# ==========================================

client = Groq(
    api_key=GROQ_API_KEY
)

# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI()

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# HEALTH CHECK APIs
# ==========================================

@app.get("/")
def root():
    return {"message": "Salesforce AI Backend Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

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

    try:

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "system",
                    "content": "Generate Salesforce interview questions."
                },
                {
                    "role": "user",
                    "content": "Generate one Salesforce interview question."
                }
            ],

            temperature=0.7,
            max_tokens=100
        )

        question = response.choices[0].message.content.strip()

        return {
            "question": question
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# ==========================================
# EVALUATE ANSWER API
# ==========================================

@app.post("/evaluate-answer")
def evaluate_answer(request: AnswerRequest):

    try:

        # ==========================================
        # EMPTY ANSWER
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
- Practice Salesforce basics

Final Feedback:
No valid answer submitted.
                """,

                "score": 0
            }

        # ==========================================
        # VERY SHORT ANSWER
        # ==========================================

        if len(request.answer.strip()) < 10:

            return {
                "evaluation": """
Score: 10/100

Strengths:
- Attempted the question

Missing Points:
- Technical explanation missing

Improvements:
- Add examples
- Explain concepts clearly
- Include Salesforce terminology

Final Feedback:
Answer needs more detail.
                """,

                "score": 10
            }

        # ==========================================
        # PROMPT
        # ==========================================

        evaluation_prompt = f"""
Interview Question:
{request.question}

Candidate Answer:
{request.answer}

Evaluate strictly.

Scoring Rules:
- Blank answer = 0
- Very short answer = below 30
- Partial answer = 40-60
- Good answer = 70-85
- Excellent answer = 90+

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
            ],

            temperature=0.5,
            max_tokens=400
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

    except Exception as e:

        return {
            "evaluation": f"Error: {str(e)}",
            "score": 0
        }

# ==========================================
# EXPLAIN CONCEPT API
# ==========================================

@app.post("/explain-concept")
def explain_concept(request: ConceptRequest):

    try:

        response = client.chat.completions.create(

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
            ],

            temperature=0.5,
            max_tokens=300
        )

        explanation = response.choices[0].message.content

        return {
            "explanation": explanation
        }

    except Exception as e:

        return {
            "explanation": f"Error: {str(e)}"
        }
