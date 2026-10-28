from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def decide_followup(question, answer, job_role, company=None, followup_count=0):
    """
    AI decides whether a follow-up question is needed
    and generates one if necessary
    """

    company_context = f"for {company} interview" if company else ""

    prompt = f"""
    You are an expert interviewer {company_context}.

    Original Question: {question}
    Candidate's Answer: {answer}
    Job Role: {job_role}
    Follow-ups asked so far: {followup_count}

    Analyze the candidate's answer and decide:
    1. Is the answer complete and satisfactory?
    2. Did they miss any important points?
    3. Can you probe deeper into something interesting they said?
    4. Have they already answered too many follow-ups? (max 3)

    Rules:
    - If answer is complete and followup_count >= 2: return NO
    - If answer is vague or incomplete: return YES with follow-up
    - If they mentioned something interesting: probe deeper
    - If they used STAR method well: return NO
    - Keep follow-up questions short and specific

    Respond EXACTLY in this format:
    NEEDS_FOLLOWUP: [YES/NO]
    REASON: [why follow-up is needed or not]
    FOLLOWUP_QUESTION: [the follow-up question if needed, or NONE]
    WHAT_WAS_MISSING: [what the candidate missed, or NONE]
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    return parse_followup_decision(raw)


def parse_followup_decision(raw_text):
    """
    Parse follow-up decision from AI response
    """
    result = {
        "needs_followup": False,
        "reason": "",
        "followup_question": None,
        "what_was_missing": None
    }

    try:
        lines = raw_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if "NEEDS_FOLLOWUP:" in line:
                value = line.split("NEEDS_FOLLOWUP:")[1].strip()
                result["needs_followup"] = value.upper() == "YES"
            elif "REASON:" in line:
                result["reason"] = line.split("REASON:")[1].strip()
            elif "FOLLOWUP_QUESTION:" in line:
                value = line.split("FOLLOWUP_QUESTION:")[1].strip()
                result["followup_question"] = None if value == "NONE" else value
            elif "WHAT_WAS_MISSING:" in line:
                value = line.split("WHAT_WAS_MISSING:")[1].strip()
                result["what_was_missing"] = None if value == "NONE" else value
    except Exception as e:
        print(f"⚠️ Parsing warning: {e}")

    return result


def generate_hint(question, answer, job_role):
    """
    Generate a hint if candidate is struggling
    """
    prompt = f"""
    The candidate is struggling to answer this interview question.
    Give them a helpful hint without giving away the full answer.

    Question: {question}
    Their Answer So Far: {answer}
    Job Role: {job_role}

    Provide:
    HINT: [A helpful hint to guide them]
    KEY_POINTS: [2-3 key points they should mention]

    Keep it encouraging and brief.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    return parse_hint(raw)


def parse_hint(raw_text):
    """
    Parse hint from AI response
    """
    result = {
        "hint": "",
        "key_points": []
    }

    try:
        lines = raw_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if "HINT:" in line:
                result["hint"] = line.split("HINT:")[1].strip()
            elif "KEY_POINTS:" in line:
                points = line.split("KEY_POINTS:")[1].strip()
                result["key_points"] = [p.strip() for p in points.split("|")]
    except Exception as e:
        print(f"⚠️ Parsing warning: {e}")

    return result


def run_dynamic_interview(question, job_role, company=None):
    """
    Run a complete dynamic interview for one question
    with AI-decided follow-ups
    """
    print("\n" + "="*55)
    print(f"❓ Question: {question}")
    print("="*55)

    conversation = []
    followup_count = 0
    current_question = question

    while True:
        # Get candidate answer
        print(f"\n💬 Your Answer (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        answer = " ".join(lines)

        if not answer.strip():
            print("⚠️ Please provide an answer!")
            continue

        conversation.append({
            "question": current_question,
            "answer": answer,
            "is_followup": followup_count > 0
        })

        # AI decides if follow-up needed
        print("\n⏳ AI is analyzing your answer...")
        decision = decide_followup(
            current_question,
            answer,
            job_role,
            company,
            followup_count
        )

        print(f"\n🤖 AI Analysis: {decision['reason']}")

        if decision['needs_followup'] and decision['followup_question']:
            followup_count += 1
            print(f"\n🔍 Follow-up Question {followup_count}:")
            print(f"   {decision['followup_question']}")

            if decision['what_was_missing']:
                print(f"\n💡 Hint: You missed — {decision['what_was_missing']}")

            current_question = decision['followup_question']
        else:
            print("\n✅ Great answer! Moving on...")
            break

        if followup_count >= 3:
            print("\n✅ Maximum follow-ups reached. Moving on...")
            break

    return conversation, followup_count


# Test the module
if __name__ == "__main__":
    print("🤖 AI Follow-up Question Generator")
    print("="*55)

    job_role = input("Enter Job Role: ")
    company = input("Enter Company (or press Enter to skip): ").strip()
    company = company if company else None

    question = input("Enter Interview Question: ")

    conversation, total_followups = run_dynamic_interview(
        question, job_role, company
    )

    print("\n" + "="*55)
    print("       📊 CONVERSATION SUMMARY")
    print("="*55)
    print(f"Total Follow-ups: {total_followups}")
    print(f"\nFull Conversation:")
    for idx, turn in enumerate(conversation):
        label = "Follow-up" if turn['is_followup'] else "Main Question"
        print(f"\n[{label} {idx+1}]")
        print(f"Q: {turn['question']}")
        print(f"A: {turn['answer'][:100]}...")
    print("="*55)
    