import streamlit as st
import os
import time
import threading
import tempfile
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import all original modules
from modules.question_generator import generate_questions
from modules.speech_analyzer import record_audio, transcribe_audio, analyze_speech
from modules.emotion_detector import analyze_emotions_realtime, analyze_emotion_summary
from modules.answer_evaluator import evaluate_answer
from modules.feedback_generator import generate_final_feedback

# Import new modules
from modules.resume_parser import extract_text_from_pdf, parse_resume_with_ai, generate_resume_based_questions
from modules.company_prep import generate_company_questions, get_all_companies, COMPANY_PROFILES
from modules.followup_generator import decide_followup
from modules.progress_tracker import init_database, save_session, get_all_sessions, create_progress_charts, get_progress_stats, get_improvement_tips

# Initialize database
init_database()

# Page config
st.set_page_config(
    page_title="AI Interview Coach Pro",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        color: #2E86AB;
        padding: 20px;
    }
    .sub-header {
        font-size: 18px;
        text-align: center;
        color: #888;
        margin-bottom: 30px;
    }
    .question-box {
        background: #1a1a2e;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #2E86AB;
        font-size: 20px;
        font-weight: bold;
        margin: 10px 0;
        color: white;
    }
    .followup-box {
        background: #1a2e1a;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #28a745;
        font-size: 18px;
        font-weight: bold;
        margin: 10px 0;
        color: white;
    }
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    .company-box {
        background: #2e1a1a;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid #dc3545;
        margin: 10px 0;
        color: white;
    }
    .strength-box {
        background: #d4edda;
        padding: 12px 15px;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        margin: 5px 0;
        color: #155724;
    }
    .improve-box {
        background: #fff3cd;
        padding: 12px 15px;
        border-radius: 8px;
        border-left: 5px solid #ffc107;
        margin: 5px 0;
        color: #856404;
    }
    .action-box {
        background: #d1ecf1;
        padding: 12px 15px;
        border-radius: 8px;
        border-left: 5px solid #17a2b8;
        margin: 5px 0;
        color: #0c5460;
    }
    .tip-box {
        background: #2e2e1a;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid #ffc107;
        margin: 10px 0;
        color: white;
    }
    .ready-box {
        background: #1a2e1a;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid #28a745;
        margin: 10px 0;
        color: white;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)


def go_next_question():
    """Callback to move to next question"""
    cq = st.session_state.current_q
    for key in [f"speech_{cq}", f"transcript_{cq}",
                f"emotion_data_{cq}", f"evaluated_{cq}",
                f"followup_{cq}", f"followup_q_{cq}",
                f"followup_count_{cq}", f"ready_to_evaluate_{cq}"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.current_q += 1


def go_final_report():
    """Callback to go to final report"""
    st.session_state.current_q += 1


def main():
    st.markdown('<div class="main-header">🎯 AI Interview Coach Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Resume-Powered • Company-Specific • Dynamic Follow-ups • Progress Tracking</div>', unsafe_allow_html=True)
    st.divider()

    # ===== SIDEBAR =====
    with st.sidebar:
        st.title("⚙️ Settings")

        candidate_name = st.text_input("👤 Your Name", placeholder="e.g. Aishwarya")
        job_role = st.text_input("💼 Job Role", placeholder="e.g. Data Scientist")

        st.markdown("### 🏢 Target Company")
        indian_it, product = get_all_companies()
        all_companies = ["None (General)"] + indian_it + product
        selected_company = st.selectbox("Select Company", all_companies)
        company = None if selected_company == "None (General)" else selected_company

        if company and company in COMPANY_PROFILES:
            profile = COMPANY_PROFILES[company]
            st.markdown(f'<div class="tip-box">💡 <b>{company} Tip:</b><br>{profile["tip"]}</div>', unsafe_allow_html=True)

        st.divider()

        interview_type = st.selectbox("📋 Interview Type", ["HR", "Technical", "Behavioral", "Mixed"])
        num_questions = st.slider("❓ Questions", 1, 10, 3)
        answer_duration = st.slider("⏱️ Duration (sec)", 15, 120, 30)
        emotion_tracking = st.toggle("📷 Emotion Tracking", value=True)
        followup_enabled = st.toggle("🔄 AI Follow-ups", value=True)

        st.divider()

        st.markdown("### 📄 Upload Resume")
        resume_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
        use_resume = st.toggle("Use Resume for Questions", value=True if resume_file else False)

        st.divider()

        st.markdown("### 📊 Navigation")
        page = st.radio("Go to", ["🎯 Interview", "📊 Progress Dashboard"])

    # ===== PROGRESS DASHBOARD =====
    if page == "📊 Progress Dashboard":
        st.markdown("## 📊 Progress Dashboard")
        st.divider()

        stats = get_progress_stats(candidate_name if candidate_name else None)

        if not stats:
            st.info("👈 Complete at least one interview session to see your progress!")
            return

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("🎯 Avg Score", f"{stats['avg_score']}/100")
        with col2:
            st.metric("🏆 Best Score", f"{stats['best_score']}/100")
        with col3:
            st.metric("📅 Sessions", stats['total_sessions'])
        with col4:
            st.metric("📝 Questions", stats['total_questions_practiced'])
        with col5:
            improvement = stats['score_improvement']
            st.metric("📈 Improvement", f"+{improvement}" if improvement > 0 else str(improvement))

        st.divider()

        fig1, fig2, fig3, fig4 = create_progress_charts(candidate_name if candidate_name else None)

        if fig1:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                st.plotly_chart(fig2, use_container_width=True)

            col3, col4 = st.columns(2)
            with col3:
                st.plotly_chart(fig3, use_container_width=True)
            with col4:
                st.plotly_chart(fig4, use_container_width=True)

        st.divider()
        st.markdown("### 💡 Personalized Improvement Tips")
        tips = get_improvement_tips(candidate_name if candidate_name else None)
        for tip in tips:
            st.markdown(f'<div class="tip-box">{tip}</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📅 Session History")
        df = get_all_sessions(candidate_name if candidate_name else None)
        if not df.empty:
            st.dataframe(
                df[['date', 'candidate_name', 'job_role', 'company',
                    'overall_score', 'avg_wpm', 'avg_confidence',
                    'total_questions', 'total_followups']],
                use_container_width=True
            )
        return

    # ===== INTERVIEW PAGE =====
    if not job_role or not candidate_name:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("### 📄 Resume-Based Questions")
            st.write("Upload your resume and get questions based on YOUR actual experience!")
        with col2:
            st.markdown("### 🏢 Company-Specific Prep")
            st.write("Practice with real interview styles of TCS, Google, Amazon and more!")
        with col3:
            st.markdown("### 🔄 Dynamic Follow-ups")
            st.write("AI probes deeper just like a real interviewer would!")
        with col4:
            st.markdown("### 📊 Progress Tracking")
            st.write("Track improvement over time with beautiful charts!")
        st.info("👈 Enter your Name and Job Role in the sidebar to get started!")
        return

    # Process resume
    resume_data = None
    if resume_file and use_resume:
        if not st.session_state.get("resume_processed"):
            with st.spinner("📄 Reading and analyzing your resume..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(resume_file.read())
                    tmp_path = tmp.name
                resume_text = extract_text_from_pdf(tmp_path)
                resume_data = parse_resume_with_ai(resume_text)
                st.session_state.resume_data = resume_data
                st.session_state.resume_processed = True
                os.unlink(tmp_path)
            st.success(f"✅ Resume analyzed! Welcome {resume_data['name']}!")
        else:
            resume_data = st.session_state.get("resume_data")

    # Start Interview Button
    if st.button("🚀 Start Mock Interview", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["resume_data", "resume_processed"]:
                del st.session_state[key]
        st.session_state.started = True
        st.session_state.questions = []
        st.session_state.current_q = 0
        st.session_state.results = []
        st.session_state.start_time = time.time()
        st.rerun()

    # Generate Questions
    if st.session_state.get("started") and not st.session_state.get("questions"):
        with st.spinner("🤖 Generating personalized questions..."):
            if resume_data and use_resume and company:
                questions, _ = generate_company_questions(company, job_role, resume_data, num_questions)
                st.session_state.question_source = f"📄 Resume + 🏢 {company} Style"
            elif resume_data and use_resume:
                questions = generate_resume_based_questions(resume_data, job_role, num_questions)
                st.session_state.question_source = "📄 Resume-Based Questions"
            elif company:
                questions, _ = generate_company_questions(company, job_role, None, num_questions)
                st.session_state.question_source = f"🏢 {company} Style Questions"
            else:
                questions = generate_questions(job_role, interview_type, num_questions)
                st.session_state.question_source = "🎯 General Questions"
            st.session_state.questions = questions
        st.success(f"✅ {len(questions)} questions generated!")
        st.rerun()

    # ===== INTERVIEW FLOW =====
    if st.session_state.get("questions"):
        questions = st.session_state.questions
        current_q = st.session_state.get("current_q", 0)

        if current_q < len(questions):

            # Progress
            st.progress(
                current_q / len(questions),
                text=f"Question {current_q + 1} of {len(questions)} — {st.session_state.get('question_source', '')}"
            )

            # Company info bar
            if company and company in COMPANY_PROFILES:
                profile = COMPANY_PROFILES[company]
                rounds = " → ".join(profile['rounds'])
                st.markdown(f'<div class="company-box">🏢 <b>{company} Interview</b> | Rounds: {rounds}</div>', unsafe_allow_html=True)

            question = questions[current_q]
            in_followup = st.session_state.get(f"followup_{current_q}", False)
            followup_question = st.session_state.get(f"followup_q_{current_q}", None)
            followup_count = st.session_state.get(f"followup_count_{current_q}", 0)

            if in_followup and followup_question:
                st.markdown(f"### 🔄 Follow-up Question:")
                st.markdown(f'<div class="followup-box">🤖 {followup_question}</div>', unsafe_allow_html=True)
                current_display_question = followup_question
            else:
                st.markdown(f"### ❓ Question {current_q + 1}:")
                st.markdown(f'<div class="question-box">{question}</div>', unsafe_allow_html=True)
                current_display_question = question

            st.divider()

            # ===== RECORDING SECTION =====
            if not st.session_state.get(f"ready_to_evaluate_{current_q}") and not st.session_state.get(f"evaluated_{current_q}"):

                st.markdown("### 🎯 Record Your Answer + Emotion Analysis")
                st.info(f"⏱️ You have {answer_duration} seconds — Speak clearly and look at the camera!")

                if st.button(
                    "🎤📷 Start Recording + Emotion Analysis",
                    type="primary",
                    use_container_width=True,
                    key=f"start_{current_q}_{followup_count}"
                ):
                    results_store = {}

                    def record_thread():
                        audio_path = record_audio(duration=answer_duration)
                        transcript = transcribe_audio(audio_path)
                        speech = analyze_speech(transcript)
                        results_store["transcript"] = transcript
                        results_store["speech"] = speech

                    def emotion_thread():
                        if emotion_tracking:
                            emotion_log = analyze_emotions_realtime(duration=answer_duration)
                            emotion_summary = analyze_emotion_summary(emotion_log)
                            results_store["emotion"] = emotion_summary
                        else:
                            results_store["emotion"] = None

                    with st.spinner(f"🎤 Recording + 📷 Analyzing for {answer_duration} seconds... Speak now!"):
                        t1 = threading.Thread(target=record_thread)
                        t2 = threading.Thread(target=emotion_thread)
                        t1.start()
                        t2.start()
                        t1.join()
                        t2.join()

                    st.session_state[f"speech_{current_q}"] = results_store.get("speech", {})
                    st.session_state[f"transcript_{current_q}"] = results_store.get("transcript", "")
                    st.session_state[f"emotion_data_{current_q}"] = results_store.get("emotion", None)
                    st.success("✅ Recording complete!")
                    st.rerun()

            # ===== SHOW TRANSCRIPT + EMOTION RESULTS =====
            if st.session_state.get(f"transcript_{current_q}"):
                speech = st.session_state[f"speech_{current_q}"]
                emotion = st.session_state.get(f"emotion_data_{current_q}")
                transcript = st.session_state[f"transcript_{current_q}"]

                st.divider()
                st.markdown("### 📝 Your Answer:")
                st.write(transcript)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🗣️ Pace", f"{speech.get('wpm', 0)} WPM")
                with col2:
                    st.metric("⚠️ Fillers", f"{speech.get('total_fillers', 0)}")
                with col3:
                    st.metric("📝 Words", f"{speech.get('word_count', 0)}")
                st.write(f"**Pace Feedback:** {speech.get('pace_feedback', '')}")

                if emotion:
                    st.divider()
                    st.markdown("### 🎭 Live Emotion Analysis:")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🏆 Emotion", emotion['dominant_emotion'].upper())
                    with col2:
                        st.metric("💪 Confidence", f"{emotion['confidence_score']}/100")
                    for emo, pct in sorted(
                        emotion['emotion_percentages'].items(),
                        key=lambda x: x[1], reverse=True
                    ):
                        st.progress(int(pct), text=f"{emo.capitalize()}: {pct}%")

                # ===== FOLLOW-UP CHECK =====
                if followup_enabled and not st.session_state.get(f"ready_to_evaluate_{current_q}"):
                    st.divider()
                    if st.button(
                        "🤖 Check if Follow-up Needed",
                        use_container_width=True,
                        key=f"check_followup_{current_q}_{followup_count}"
                    ):
                        with st.spinner("🤖 AI analyzing your answer..."):
                            decision = decide_followup(
                                current_display_question,
                                transcript,
                                job_role,
                                company,
                                followup_count
                            )

                        if decision['needs_followup'] and decision['followup_question'] and followup_count < 3:
                            st.warning(f"🔍 Follow-up needed! {decision['reason']}")
                            if decision['what_was_missing']:
                                st.info(f"💡 What you missed: {decision['what_was_missing']}")
                            st.session_state[f"followup_{current_q}"] = True
                            st.session_state[f"followup_q_{current_q}"] = decision['followup_question']
                            st.session_state[f"followup_count_{current_q}"] = followup_count + 1
                            for k in [f"transcript_{current_q}", f"speech_{current_q}", f"emotion_data_{current_q}"]:
                                if k in st.session_state:
                                    del st.session_state[k]
                            st.rerun()
                        else:
                            st.success("✅ Great answer! No follow-up needed!")
                            st.session_state[f"ready_to_evaluate_{current_q}"] = True
                            st.session_state[f"followup_{current_q}"] = False
                            st.rerun()

            # ===== EVALUATE SECTION =====
            if st.session_state.get(f"ready_to_evaluate_{current_q}") or not followup_enabled:
                if st.session_state.get(f"transcript_{current_q}"):
                    speech = st.session_state[f"speech_{current_q}"]
                    emotion = st.session_state.get(f"emotion_data_{current_q}")
                    transcript = st.session_state[f"transcript_{current_q}"]

                    st.divider()
                    st.markdown(f'<div class="ready-box">✅ Your answer was satisfactory! Click below to get your score!</div>', unsafe_allow_html=True)
                    st.markdown("### 🧠 Get AI Evaluation")

                    if not st.session_state.get(f"evaluated_{current_q}"):
                        if st.button(
                            "🧠 Evaluate My Answer",
                            type="primary",
                            use_container_width=True,
                            key=f"eval_{current_q}"
                        ):
                            with st.spinner("🧠 Evaluating your answer..."):
                                evaluation = evaluate_answer(question, transcript, job_role)
                            with st.spinner("📊 Generating feedback..."):
                                feedback = generate_final_feedback(
                                    job_role, question, speech, emotion, evaluation
                                )
                            st.session_state.results.append({
                                "question": question,
                                "speech": speech,
                                "emotion": emotion,
                                "evaluation": evaluation,
                                "feedback": feedback,
                                "followup_count": followup_count
                            })
                            st.session_state[f"evaluated_{current_q}"] = True
                            st.rerun()

                    # ===== SHOW EVALUATION RESULTS =====
                    if st.session_state.get(f"evaluated_{current_q}") and st.session_state.results:
                        result = st.session_state.results[-1]
                        evaluation = result["evaluation"]
                        feedback = result["feedback"]

                        st.success("✅ Evaluation complete!")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📝 Content", f"{evaluation['content_score']}/10")
                        with col2:
                            st.metric("💬 Clarity", f"{evaluation['clarity_score']}/10")
                        with col3:
                            st.metric("⭐ Answer", f"{evaluation['overall_score']}/10")
                        with col4:
                            st.metric("🎯 Interview", f"{feedback['overall_score']}/100")

                        st.markdown("**✅ Strengths:**")
                        for s in feedback['top_strengths']:
                            if s:
                                st.markdown(f'<div class="strength-box">✅ {s}</div>', unsafe_allow_html=True)

                        st.markdown("**⚠️ Improvements:**")
                        for i in feedback['critical_improvements']:
                            if i:
                                st.markdown(f'<div class="improve-box">⚠️ {i}</div>', unsafe_allow_html=True)

                        st.info(f"💬 Coach: \"{feedback['encouragement']}\"")

                        # ===== NEXT QUESTION BUTTON =====
                        st.divider()
                        if current_q + 1 < len(questions):
                            st.button(
                                f"➡️ Next Question ({current_q + 2} of {len(questions)})",
                                type="primary",
                                use_container_width=True,
                                on_click=go_next_question,
                                key=f"next_{current_q}"
                            )
                        else:
                            st.button(
                                "🏆 View Final Report",
                                type="primary",
                                use_container_width=True,
                                on_click=go_final_report,
                                key=f"final_{current_q}"
                            )

        else:
            # ===== FINAL REPORT =====
            st.balloons()
            st.markdown("## 🎉 Interview Complete!")
            st.divider()

            results = st.session_state.get("results", [])

            if results:
                scores = []
                for r in results:
                    try:
                        scores.append(int(r["feedback"]["overall_score"]))
                    except:
                        pass

                avg_score = int(sum(scores) / len(scores)) if scores else 0
                duration = int((time.time() - st.session_state.get("start_time", time.time())) / 60)

                st.markdown(f'<div class="score-box">🎯 Overall Score: {avg_score}/100</div>', unsafe_allow_html=True)
                st.divider()

                if avg_score >= 85:
                    st.markdown("### 🌟 Performance: Expert")
                elif avg_score >= 70:
                    st.markdown("### ✅ Performance: Proficient")
                elif avg_score >= 55:
                    st.markdown("### 📈 Performance: Developing")
                else:
                    st.markdown("### 🌱 Performance: Beginner")

                # Calculate averages safely
                total_followups = sum(r.get("followup_count", 0) for r in results)
                avg_content = sum(int(r["evaluation"]["content_score"]) for r in results) / len(results)
                avg_clarity = sum(int(r["evaluation"]["clarity_score"]) for r in results) / len(results)
                avg_wpm = sum(r["speech"].get("wpm", 0) for r in results) / len(results)
                avg_fillers = sum(r["speech"].get("total_fillers", 0) for r in results) / len(results)
                avg_confidence = sum(
                    r["emotion"]["confidence_score"] if r["emotion"] else 0
                    for r in results
                ) / len(results)
                dominant_emotion = results[0]["emotion"]["dominant_emotion"] if results[0].get("emotion") else "neutral"

                # Save session to database
                session_data = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "candidate_name": candidate_name,
                    "job_role": job_role,
                    "company": company or "General",
                    "interview_type": interview_type,
                    "overall_score": avg_score,
                    "avg_content_score": round(avg_content, 1),
                    "avg_clarity_score": round(avg_clarity, 1),
                    "avg_wpm": int(avg_wpm),
                    "avg_filler_words": int(avg_fillers),
                    "avg_confidence": int(avg_confidence),
                    "dominant_emotion": dominant_emotion,
                    "total_questions": len(results),
                    "total_followups": total_followups,
                    "resume_used": resume_data is not None,
                    "duration_minutes": duration,
                    "questions": [
                        {
                            "question_number": idx + 1,
                            "question_text": r["question"],
                            "answer_transcript": r["speech"].get("transcript", ""),
                            "content_score": int(r["evaluation"]["content_score"]),
                            "clarity_score": int(r["evaluation"]["clarity_score"]),
                            "overall_score": int(r["evaluation"]["overall_score"]),
                            "interview_score": int(r["feedback"]["overall_score"]),
                            "wpm": r["speech"].get("wpm", 0),
                            "filler_words": r["speech"].get("total_fillers", 0),
                            "emotion": r["emotion"]["dominant_emotion"] if r["emotion"] else "neutral",
                            "confidence": r["emotion"]["confidence_score"] if r["emotion"] else 0,
                            "followup_count": r.get("followup_count", 0)
                        }
                        for idx, r in enumerate(results)
                    ]
                }

                if not st.session_state.get("session_saved"):
                    save_session(session_data)
                    st.session_state.session_saved = True
                    st.success("✅ Session saved to Progress Tracker!")

                # Question breakdown
                st.divider()
                st.markdown("### 📋 Question Breakdown:")
                for idx, result in enumerate(results):
                    with st.expander(f"📌 Q{idx+1}: {result['question'][:70]}..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**📊 Scores:**")
                            st.write(f"• Content   : {result['evaluation']['content_score']}/10")
                            st.write(f"• Clarity   : {result['evaluation']['clarity_score']}/10")
                            st.write(f"• Answer    : {result['evaluation']['overall_score']}/10")
                            st.write(f"• Interview : {result['feedback']['overall_score']}/100")
                            st.write(f"• Follow-ups: {result.get('followup_count', 0)}")
                        with col2:
                            st.markdown("**🎤 Speech & Emotion:**")
                            st.write(f"• Pace      : {result['speech']['wpm']} WPM")
                            st.write(f"• Fillers   : {result['speech']['total_fillers']}")
                            if result['emotion']:
                                st.write(f"• Emotion   : {result['emotion']['dominant_emotion'].upper()}")
                                st.write(f"• Confidence: {result['emotion']['confidence_score']}/100")

                        st.markdown("**✅ Strengths:**")
                        for s in result['feedback']['top_strengths']:
                            if s:
                                st.markdown(f'<div class="strength-box">✅ {s}</div>', unsafe_allow_html=True)

                        st.markdown("**⚠️ Improvements:**")
                        for i in result['feedback']['critical_improvements']:
                            if i:
                                st.markdown(f'<div class="improve-box">⚠️ {i}</div>', unsafe_allow_html=True)

                        st.markdown("**📋 Action Plan:**")
                        for a in result['feedback']['action_plan']:
                            if a:
                                st.markdown(f'<div class="action-box">📌 {a}</div>', unsafe_allow_html=True)

                        st.info(f"💬 Coach: \"{result['feedback']['encouragement']}\"")

                # Summary table
                st.divider()
                st.markdown("### 📊 Score Summary:")
                import pandas as pd
                summary = []
                for idx, r in enumerate(results):
                    summary.append({
                        "Q": f"Q{idx+1}",
                        "Content": f"{r['evaluation']['content_score']}/10",
                        "Clarity": f"{r['evaluation']['clarity_score']}/10",
                        "Score": f"{r['feedback']['overall_score']}/100",
                        "WPM": r['speech']['wpm'],
                        "Fillers": r['speech']['total_fillers'],
                        "Follow-ups": r.get('followup_count', 0)
                    })
                st.dataframe(pd.DataFrame(summary), use_container_width=True)

                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 New Interview", type="primary", use_container_width=True):
                        for key in list(st.session_state.keys()):
                            if key not in ["resume_data", "resume_processed"]:
                                del st.session_state[key]
                        st.rerun()
                with col2:
                    if st.button("📊 View Progress Dashboard", use_container_width=True):
                        st.info("👈 Click 'Progress Dashboard' in the sidebar!")


if __name__ == "__main__":
    main()
