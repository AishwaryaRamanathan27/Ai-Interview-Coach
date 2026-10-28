from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def evaluate_answer(question, transcript, job_role):
    """
    Evaluate candidate's answer using Groq AI
    """
    prompt = f"""
    You are an expert interview coach evaluating a candidate's answer.

    Job Role: {job_role}
    Interview Question: {question}
    Candidate's Answer: {transcript}

    Please evaluate the answer and provide:

    1. CONTENT SCORE (out of 10): How relevant and complete is the answer?
    2. CLARITY SCORE (out of 10): How clear and structured is the answer?
    3. STAR METHOD (Yes/No): Did the candidate use Situation, Task, Action, Result format?
    4. KEY STRENGTHS: 2-3 things the candidate did well
    5. IMPROVEMENTS NEEDED: 2-3 specific things to improve
    6. BETTER ANSWER TIPS: 2-3 tips to make the answer stronger
    7. OVERALL SCORE (out of 10): Combined score

    Format your response EXACTLY like this:
    CONTENT_SCORE: [number]/10
    CLARITY_SCORE: [number]/10
    STAR_METHOD: [Yes/No]
    STRENGTHS: [point1] | [point2] | [point3]
    IMPROVEMENTS: [point1] | [point2] | [point3]
    TIPS: [tip1] | [tip2] | [tip3]
    OVERALL_SCORE: [number]/10
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content
    return parse_evaluation(raw)


def parse_evaluation(raw_text):
    """
    Parse the evaluation response into a dictionary
    """
    result = {
        "content_score": 0,
        "clarity_score": 0,
        "star_method": "No",
        "strengths": [],
        "improvements": [],
        "tips": [],
        "overall_score": 0,
        "raw": raw_text
    }

    try:
        lines = raw_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if "CONTENT_SCORE" in line:
                result["content_score"] = line.split(":")[1].strip().split("/")[0]
            elif "CLARITY_SCORE" in line:
                result["clarity_score"] = line.split(":")[1].strip().split("/")[0]
            elif "STAR_METHOD" in line:
                result["star_method"] = line.split(":")[1].strip()
            elif "STRENGTHS" in line:
                parts = line.split(":")[1].strip().split("|")
                result["strengths"] = [p.strip() for p in parts if p.strip()]
            elif "IMPROVEMENTS" in line:
                parts = line.split(":")[1].strip().split("|")
                result["improvements"] = [p.strip() for p in parts if p.strip()]
            elif "TIPS" in line:
                parts = line.split(":")[1].strip().split("|")
                result["tips"] = [p.strip() for p in parts if p.strip()]
            elif "OVERALL_SCORE" in line:
                result["overall_score"] = line.split(":")[1].strip().split("/")[0]

        # If still empty, print raw for debugging
        if not result["strengths"] and not result["improvements"]:
            print("\n🔍 Raw AI Response (for debugging):")
            print(raw_text)

    except Exception as e:
        print(f"⚠️ Parsing warning: {e}")
        print(f"Raw response: {raw_text}")

    return result


def print_evaluation_report(evaluation, question):
    """
    Print a clean evaluation report
    """
    print("\n" + "="*50)
    print("       🧠 ANSWER EVALUATION REPORT")
    print("="*50)

    print(f"\n❓ Question: {question}")

    print(f"\n📊 Scores:")
    print(f"   • Content Score  : {evaluation['content_score']}/10")
    print(f"   • Clarity Score  : {evaluation['clarity_score']}/10")
    print(f"   • STAR Method    : {evaluation['star_method']}")
    print(f"   • Overall Score  : {evaluation['overall_score']}/10")

    print(f"\n✅ Strengths:")
    for s in evaluation['strengths']:
        if s:
            print(f"   • {s}")

    print(f"\n⚠️ Improvements Needed:")
    for i in evaluation['improvements']:
        if i:
            print(f"   • {i}")

    print(f"\n💡 Tips for Better Answer:")
    for t in evaluation['tips']:
        if t:
            print(f"   • {t}")

    print("\n" + "="*50)


# Test the module
if __name__ == "__main__":
    print("🧠 AI Interview Answer Evaluator")
    print("="*50)

    job_role = input("Enter Job Role (e.g. Software Engineer): ")
    question = input("Enter Interview Question: ")

    print("\nEnter your answer (press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    transcript = " ".join(lines)

    print("\n⏳ Evaluating your answer...")
    evaluation = evaluate_answer(question, transcript, job_role)
    print_evaluation_report(evaluation, question)
