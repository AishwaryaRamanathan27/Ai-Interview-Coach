from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_final_feedback(job_role, question, speech_analysis, emotion_summary, answer_evaluation):
    """
    Generate comprehensive final feedback combining all analyses
    """

    # Prepare emotion data safely
    dominant_emotion = "neutral"
    confidence_score = 0
    emotion_breakdown = ""

    if emotion_summary:
        dominant_emotion = emotion_summary.get("dominant_emotion", "neutral")
        confidence_score = emotion_summary.get("confidence_score", 0)
        emotion_breakdown = str(emotion_summary.get("emotion_percentages", {}))

    prompt = f"""
    You are an expert interview coach. Based on the complete interview analysis below,
    generate a comprehensive final feedback report.

    Job Role: {job_role}
    Question Asked: {question}

    === SPEECH ANALYSIS ===
    Transcript: {speech_analysis.get('transcript', '')}
    Word Count: {speech_analysis.get('word_count', 0)}
    Speaking Pace: {speech_analysis.get('wpm', 0)} WPM
    Pace Feedback: {speech_analysis.get('pace_feedback', '')}
    Filler Words: {speech_analysis.get('filler_words', {})}
    Total Fillers: {speech_analysis.get('total_fillers', 0)}

    === EMOTION ANALYSIS ===
    Dominant Emotion: {dominant_emotion}
    Confidence Score: {confidence_score}/100
    Emotion Breakdown: {emotion_breakdown}

    === ANSWER EVALUATION ===
    Content Score: {answer_evaluation.get('content_score', 0)}/10
    Clarity Score: {answer_evaluation.get('clarity_score', 0)}/10
    STAR Method Used: {answer_evaluation.get('star_method', 'No')}
    Overall Score: {answer_evaluation.get('overall_score', 0)}/10

    Based on ALL the above, provide:

    1. OVERALL_INTERVIEW_SCORE: Score out of 100
    2. PERFORMANCE_LEVEL: Beginner / Developing / Proficient / Expert
    3. TOP_STRENGTHS: 3 best things about this candidate
    4. CRITICAL_IMPROVEMENTS: 3 most important things to improve
    5. ACTION_PLAN: 3 specific actions to take before next interview
    6. ENCOURAGEMENT: One motivating sentence for the candidate

    Format EXACTLY like this:
    OVERALL_INTERVIEW_SCORE: [number]/100
    PERFORMANCE_LEVEL: [level]
    TOP_STRENGTHS: [point1] | [point2] | [point3]
    CRITICAL_IMPROVEMENTS: [point1] | [point2] | [point3]
    ACTION_PLAN: [action1] | [action2] | [action3]
    ENCOURAGEMENT: [sentence]
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content
    return parse_feedback(raw)


def parse_feedback(raw_text):
    """
    Parse feedback response into dictionary
    """
    result = {
        "overall_score": 0,
        "performance_level": "Developing",
        "top_strengths": [],
        "critical_improvements": [],
        "action_plan": [],
        "encouragement": "",
        "raw": raw_text
    }

    try:
        lines = raw_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if "OVERALL_INTERVIEW_SCORE" in line:
                result["overall_score"] = line.split(":")[1].strip().split("/")[0]
            elif "PERFORMANCE_LEVEL" in line:
                result["performance_level"] = line.split(":")[1].strip()
            elif "TOP_STRENGTHS" in line:
                parts = line.split(":")[1].strip().split("|")
                result["top_strengths"] = [p.strip() for p in parts if p.strip()]
            elif "CRITICAL_IMPROVEMENTS" in line:
                parts = line.split(":")[1].strip().split("|")
                result["critical_improvements"] = [p.strip() for p in parts if p.strip()]
            elif "ACTION_PLAN" in line:
                parts = line.split(":")[1].strip().split("|")
                result["action_plan"] = [p.strip() for p in parts if p.strip()]
            elif "ENCOURAGEMENT" in line:
                result["encouragement"] = line.split(":")[1].strip()
    except Exception as e:
        print(f"⚠️ Parsing warning: {e}")

    return result


def print_final_report(feedback, speech_analysis, emotion_summary, answer_evaluation, job_role, question):
    """
    Print complete final interview report
    """
    print("\n" + "="*55)
    print("       🏆 FINAL INTERVIEW PERFORMANCE REPORT")
    print("="*55)

    print(f"\n👤 Job Role   : {job_role}")
    print(f"❓ Question   : {question}")

    print(f"\n🎯 OVERALL SCORE    : {feedback['overall_score']}/100")
    print(f"📈 PERFORMANCE LEVEL: {feedback['performance_level']}")

    # Score breakdown
    print(f"\n📊 Score Breakdown:")
    print(f"   • Answer Quality : {answer_evaluation.get('overall_score', 0)}/10")
    print(f"   • Speech Clarity : {'✅ Good' if int(speech_analysis.get('wpm', 0)) <= 150 else '⚠️ Too Fast'}")
    print(f"   • Filler Words   : {speech_analysis.get('total_fillers', 0)} detected")
    if emotion_summary:
        print(f"   • Confidence     : {emotion_summary.get('confidence_score', 0)}/100")
        print(f"   • Dominant Emotion: {emotion_summary.get('dominant_emotion', 'N/A').upper()}")

    print(f"\n✅ Top Strengths:")
    for s in feedback['top_strengths']:
        print(f"   • {s}")

    print(f"\n⚠️ Critical Improvements:")
    for i in feedback['critical_improvements']:
        print(f"   • {i}")

    print(f"\n📋 Action Plan (Do Before Next Interview):")
    for idx, a in enumerate(feedback['action_plan'], 1):
        print(f"   {idx}. {a}")

    print(f"\n💬 Coach Says:")
    print(f"   \"{feedback['encouragement']}\"")

    print("\n" + "="*55)
    print("       Keep practicing — you're improving every day!")
    print("="*55)


# Test the module
if __name__ == "__main__":
    print("🏆 AI Interview Feedback Generator")
    print("="*55)

    # Sample test data
    job_role = "Software Engineer"
    question = "Tell me about yourself"

    speech_analysis = {
        "transcript": "I am a software engineer with 2 years of experience in Python and Java.",
        "word_count": 85,
        "wpm": 130,
        "pace_feedback": "✅ Perfect pace",
        "filler_words": {"um": 2},
        "total_fillers": 2
    }

    emotion_summary = {
        "dominant_emotion": "neutral",
        "confidence_score": 65,
        "emotion_percentages": {"neutral": 60.5, "sad": 27.9, "fear": 9.3, "happy": 2.3}
    }

    answer_evaluation = {
        "content_score": 6,
        "clarity_score": 8,
        "star_method": "No",
        "overall_score": 7,
        "strengths": ["Clear introduction", "Mentioned technical skills"],
        "improvements": ["Add specific examples", "Mention career goals"],
        "tips": ["Use STAR method", "Quantify achievements"]
    }

    print("\n⏳ Generating final feedback report...")
    feedback = generate_final_feedback(
        job_role, question,
        speech_analysis, emotion_summary, answer_evaluation
    )

    print_final_report(
        feedback, speech_analysis,
        emotion_summary, answer_evaluation,
        job_role, question
    )
