import sqlite3
import os
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Database path
DB_PATH = "database/interview_progress.db"


def init_database():
    """
    Initialize SQLite database and create tables
    """
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            candidate_name TEXT,
            job_role TEXT,
            company TEXT,
            interview_type TEXT,
            overall_score INTEGER,
            avg_content_score REAL,
            avg_clarity_score REAL,
            avg_wpm INTEGER,
            avg_filler_words INTEGER,
            avg_confidence INTEGER,
            dominant_emotion TEXT,
            total_questions INTEGER,
            total_followups INTEGER,
            resume_used INTEGER DEFAULT 0,
            duration_minutes INTEGER,
            notes TEXT
        )
    """)

    # Questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question_number INTEGER,
            question_text TEXT,
            answer_transcript TEXT,
            content_score INTEGER,
            clarity_score INTEGER,
            overall_score INTEGER,
            interview_score INTEGER,
            wpm INTEGER,
            filler_words INTEGER,
            emotion TEXT,
            confidence INTEGER,
            followup_count INTEGER,
            used_star_method INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    # Skills tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            skill_name TEXT,
            score INTEGER,
            date TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


def save_session(session_data):
    """
    Save complete interview session to database
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert session
    cursor.execute("""
        INSERT INTO sessions (
            date, candidate_name, job_role, company,
            interview_type, overall_score, avg_content_score,
            avg_clarity_score, avg_wpm, avg_filler_words,
            avg_confidence, dominant_emotion, total_questions,
            total_followups, resume_used, duration_minutes, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_data.get("date", datetime.now().strftime("%Y-%m-%d %H:%M")),
        session_data.get("candidate_name", "Candidate"),
        session_data.get("job_role", ""),
        session_data.get("company", "General"),
        session_data.get("interview_type", "Mixed"),
        session_data.get("overall_score", 0),
        session_data.get("avg_content_score", 0),
        session_data.get("avg_clarity_score", 0),
        session_data.get("avg_wpm", 0),
        session_data.get("avg_filler_words", 0),
        session_data.get("avg_confidence", 0),
        session_data.get("dominant_emotion", "neutral"),
        session_data.get("total_questions", 0),
        session_data.get("total_followups", 0),
        1 if session_data.get("resume_used") else 0,
        session_data.get("duration_minutes", 0),
        session_data.get("notes", "")
    ))

    session_id = cursor.lastrowid

    # Insert individual questions
    for q in session_data.get("questions", []):
        cursor.execute("""
            INSERT INTO questions (
                session_id, question_number, question_text,
                answer_transcript, content_score, clarity_score,
                overall_score, interview_score, wpm, filler_words,
                emotion, confidence, followup_count, used_star_method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            q.get("question_number", 0),
            q.get("question_text", ""),
            q.get("answer_transcript", ""),
            q.get("content_score", 0),
            q.get("clarity_score", 0),
            q.get("overall_score", 0),
            q.get("interview_score", 0),
            q.get("wpm", 0),
            q.get("filler_words", 0),
            q.get("emotion", "neutral"),
            q.get("confidence", 0),
            q.get("followup_count", 0),
            1 if q.get("used_star_method") else 0
        ))

    conn.commit()
    conn.close()
    print(f"✅ Session saved! Session ID: {session_id}")
    return session_id


def get_all_sessions(candidate_name=None):
    """
    Get all sessions from database
    """
    conn = sqlite3.connect(DB_PATH)

    query = "SELECT * FROM sessions"
    if candidate_name:
        query += f" WHERE candidate_name = '{candidate_name}'"
    query += " ORDER BY date DESC"

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_session_questions(session_id):
    """
    Get all questions for a specific session
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT * FROM questions WHERE session_id = {session_id}",
        conn
    )
    conn.close()
    return df


def get_progress_stats(candidate_name=None):
    """
    Calculate progress statistics
    """
    df = get_all_sessions(candidate_name)

    if df.empty:
        return None

    stats = {
        "total_sessions": len(df),
        "avg_score": round(df['overall_score'].mean(), 1),
        "best_score": df['overall_score'].max(),
        "latest_score": df['overall_score'].iloc[0],
        "score_improvement": 0,
        "avg_wpm": round(df['avg_wpm'].mean(), 1),
        "avg_confidence": round(df['avg_confidence'].mean(), 1),
        "total_questions_practiced": df['total_questions'].sum(),
        "companies_practiced": df['company'].nunique(),
        "most_practiced_role": df['job_role'].mode()[0] if not df.empty else "N/A"
    }

    # Calculate improvement
    if len(df) >= 2:
        first_score = df['overall_score'].iloc[-1]
        latest_score = df['overall_score'].iloc[0]
        stats["score_improvement"] = latest_score - first_score

    return stats


def create_progress_charts(candidate_name=None):
    """
    Create progress visualization charts
    """
    df = get_all_sessions(candidate_name)

    if df.empty:
        return None, None, None, None

    # Reverse for chronological order
    df_chrono = df.iloc[::-1].reset_index(drop=True)

    # Chart 1 — Score Progress Over Time
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_chrono['date'],
        y=df_chrono['overall_score'],
        mode='lines+markers',
        name='Overall Score',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=10)
    ))
    fig1.update_layout(
        title='📈 Interview Score Progress Over Time',
        xaxis_title='Date',
        yaxis_title='Score (/100)',
        yaxis=dict(range=[0, 100]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # Chart 2 — Skills Radar Chart
    categories = ['Content', 'Clarity', 'Confidence', 'Speech Pace', 'Overall']
    latest = df.iloc[0]

    # Normalize WPM to 0-10 scale (ideal is 130 WPM)
    wpm_score = min(10, max(0, 10 - abs(latest['avg_wpm'] - 130) / 13))

    values = [
        min(10, latest['avg_content_score']),
        min(10, latest['avg_clarity_score']),
        min(10, latest['avg_confidence'] / 10),
        wpm_score,
        min(10, latest['overall_score'] / 10)
    ]

    fig2 = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#2E86AB'
    ))
    fig2.update_layout(
        title='🎯 Latest Session Skills Radar',
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # Chart 3 — Score by Company
    if df['company'].nunique() > 1:
        company_avg = df.groupby('company')['overall_score'].mean().reset_index()
        fig3 = px.bar(
            company_avg,
            x='company',
            y='overall_score',
            title='🏢 Average Score by Company',
            color='overall_score',
            color_continuous_scale='Blues'
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
    else:
        fig3 = go.Figure()
        fig3.update_layout(title='🏢 Practice more companies to see comparison!')

    # Chart 4 — Emotion Distribution
    emotion_counts = df['dominant_emotion'].value_counts().reset_index()
    emotion_counts.columns = ['emotion', 'count']
    fig4 = px.pie(
        emotion_counts,
        values='count',
        names='emotion',
        title='🎭 Emotion Distribution Across Sessions',
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    return fig1, fig2, fig3, fig4


def get_improvement_tips(candidate_name=None):
    """
    Generate improvement tips based on history
    """
    df = get_all_sessions(candidate_name)

    if df.empty:
        return ["Complete your first interview session to get personalized tips!"]

    tips = []

    avg_score = df['overall_score'].mean()
    avg_wpm = df['avg_wpm'].mean()
    avg_fillers = df['avg_filler_words'].mean()
    avg_confidence = df['avg_confidence'].mean()

    if avg_score < 60:
        tips.append("📚 Focus on preparing structured answers using the STAR method")
    if avg_score >= 60 and avg_score < 75:
        tips.append("📈 Good progress! Add more specific examples and metrics to your answers")
    if avg_score >= 75:
        tips.append("🌟 Excellent performance! Focus on system design and advanced topics")
    if avg_wpm > 160:
        tips.append("🐢 Slow down your speaking pace — aim for 130-150 WPM")
    if avg_wpm < 100:
        tips.append("⚡ Try to speak with more confidence and increase your pace slightly")
    if avg_fillers > 5:
        tips.append("🎯 Reduce filler words — practice pausing instead of saying 'um' or 'uh'")
    if avg_confidence < 50:
        tips.append("💪 Work on your confidence — practice in front of mirror daily")

    if not tips:
        tips.append("✅ You're doing great! Keep practicing consistently")

    return tips


def print_progress_report(candidate_name=None):
    """
    Print progress report in terminal
    """
    stats = get_progress_stats(candidate_name)

    if not stats:
        print("❌ No sessions found! Complete an interview first.")
        return

    print("\n" + "="*55)
    print("       📊 PROGRESS TRACKER REPORT")
    print("="*55)
    print(f"👤 Candidate        : {candidate_name or 'All'}")
    print(f"📅 Total Sessions   : {stats['total_sessions']}")
    print(f"🎯 Average Score    : {stats['avg_score']}/100")
    print(f"🏆 Best Score       : {stats['best_score']}/100")
    print(f"📈 Latest Score     : {stats['latest_score']}/100")

    improvement = stats['score_improvement']
    if improvement > 0:
        print(f"📈 Improvement      : +{improvement} points 🎉")
    elif improvement < 0:
        print(f"📉 Change           : {improvement} points")
    else:
        print(f"➡️  Change           : No change yet")

    print(f"\n🎤 Avg Speaking Pace : {stats['avg_wpm']} WPM")
    print(f"💪 Avg Confidence   : {stats['avg_confidence']}/100")
    print(f"📝 Questions Done   : {stats['total_questions_practiced']}")
    print(f"🏢 Companies Tested : {stats['companies_practiced']}")

    print(f"\n💡 Improvement Tips:")
    tips = get_improvement_tips(candidate_name)
    for tip in tips:
        print(f"   • {tip}")

    print("="*55)


# Test the module
if __name__ == "__main__":
    print("📊 Progress Tracker Module")
    print("="*55)

    # Initialize database
    init_database()

    # Save a test session
    test_session = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "candidate_name": "Aishwarya",
        "job_role": "Data Scientist",
        "company": "Amazon",
        "interview_type": "Technical",
        "overall_score": 72,
        "avg_content_score": 7.5,
        "avg_clarity_score": 8.0,
        "avg_wpm": 130,
        "avg_filler_words": 2,
        "avg_confidence": 65,
        "dominant_emotion": "neutral",
        "total_questions": 3,
        "total_followups": 2,
        "resume_used": True,
        "duration_minutes": 15,
        "notes": "Good performance overall",
        "questions": [
            {
                "question_number": 1,
                "question_text": "Tell me about your Mental Health project",
                "answer_transcript": "I built a mental health detection system...",
                "content_score": 7,
                "clarity_score": 8,
                "overall_score": 7,
                "interview_score": 72,
                "wpm": 128,
                "filler_words": 2,
                "emotion": "neutral",
                "confidence": 65,
                "followup_count": 2,
                "used_star_method": False
            },
            {
                "question_number": 2,
                "question_text": "How do you handle missing data?",
                "answer_transcript": "I use imputation techniques...",
                "content_score": 8,
                "clarity_score": 8,
                "overall_score": 8,
                "interview_score": 78,
                "wpm": 132,
                "filler_words": 1,
                "emotion": "happy",
                "confidence": 70,
                "followup_count": 0,
                "used_star_method": False
            }
        ]
    }

    print("\n⏳ Saving test session...")
    session_id = save_session(test_session)

    print("\n⏳ Generating progress report...")
    print_progress_report("Aishwarya")

    print("\n✅ Progress Tracker is working!")
    print("Charts will be visible in the Streamlit app!")
