from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_questions(job_role, interview_type="HR", num_questions=5):
    """
    Generate interview questions based on job role and interview type
    """
    prompt = f"""
    You are an expert interviewer. Generate {num_questions} {interview_type} 
    interview questions for a {job_role} position.
    
    Rules:
    - Number each question (1. 2. 3. etc.)
    - Make questions realistic and professional
    - For Technical: focus on skills and problem solving
    - For HR: focus on behavior, teamwork, communication
    - Keep each question clear and concise
    
    Generate exactly {num_questions} questions only. No extra text.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract and split questions
    raw = response.choices[0].message.content
    questions = [q.strip() for q in raw.strip().split("\n") if q.strip()]
    return questions


# Test the module
if __name__ == "__main__":
    print("🎯 AI Interview Question Generator")
    print("=" * 40)

    job_role = input("Enter Job Role (e.g. Software Engineer): ")
    interview_type = input("Enter Interview Type (HR / Technical): ")

    print(f"\n📋 Generating {interview_type} questions for {job_role}...\n")

    questions = generate_questions(job_role, interview_type)

    for q in questions:
        print(q)