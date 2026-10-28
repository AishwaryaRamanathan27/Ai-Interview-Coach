import cv2
import time
import numpy as np

def analyze_emotions_realtime(duration=30):
    try:
        from deepface import DeepFace
    except Exception as e:
        print(f"❌ DeepFace import error: {e}")
        return []

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot open webcam!")
        return None

    print(f"\n📷 Webcam opened! Analyzing emotions for {duration} seconds...")
    print("👀 Look at the camera naturally as if in an interview")
    print("Press 'Q' to stop early\n")

    emotion_log = []
    start_time = time.time()
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        elapsed = time.time() - start_time
        if elapsed > duration:
            break

        frame_count += 1

        if frame_count % 15 == 0:
            try:
                result = DeepFace.analyze(
                    frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True
                )
                dominant = result[0]["dominant_emotion"]
                emotion_log.append(dominant)

                cv2.putText(
                    frame,
                    f"Emotion: {dominant.upper()}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 255, 0), 2
                )

                remaining = int(duration - elapsed)
                cv2.putText(
                    frame,
                    f"Time left: {remaining}s",
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 0), 2
                )

                print(f"  🎭 Detected: {dominant.upper()}")

            except Exception:
                pass

        cv2.imshow("AI Interview Coach - Emotion Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n⏹ Stopped early!")
            break

    cap.release()
    cv2.destroyAllWindows()
    return emotion_log


def analyze_emotion_summary(emotion_log):
    if not emotion_log:
        return None

    emotion_counts = {}
    for emotion in emotion_log:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    total = len(emotion_log)
    emotion_percentages = {
        e: round((c / total) * 100, 1)
        for e, c in emotion_counts.items()
    }

    dominant = max(emotion_counts, key=emotion_counts.get)
    neutral_pct = emotion_percentages.get("neutral", 0)
    happy_pct = emotion_percentages.get("happy", 0)
    fear_pct = emotion_percentages.get("fear", 0)
    angry_pct = emotion_percentages.get("angry", 0)

    confidence_score = min(100, int(neutral_pct * 0.5 + happy_pct * 1.0))

    if confidence_score >= 70:
        confidence_feedback = "✅ Very confident and calm — excellent!"
    elif confidence_score >= 50:
        confidence_feedback = "🙂 Moderately confident — good job!"
    elif confidence_score >= 30:
        confidence_feedback = "😐 Slightly nervous — try to relax more"
    else:
        confidence_feedback = "😰 Very nervous — practice more mock interviews"

    tips = []
    if fear_pct > 30:
        tips.append("😰 High nervousness detected — take deep breaths")
    if angry_pct > 20:
        tips.append("😠 Some tension detected — try to stay calm")
    if happy_pct > 40:
        tips.append("😊 Great positivity — keep smiling naturally!")
    if neutral_pct > 60:
        tips.append("😐 Good composure — calm and professional!")
    if not tips:
        tips.append("👍 Good emotional balance throughout!")

    return {
        "emotion_counts": emotion_counts,
        "emotion_percentages": emotion_percentages,
        "dominant_emotion": dominant,
        "confidence_score": confidence_score,
        "confidence_feedback": confidence_feedback,
        "tips": tips,
        "total_frames": total
    }


def print_emotion_report(summary):
    print("\n" + "="*45)
    print("       🎭 EMOTION ANALYSIS REPORT")
    print("="*45)
    print(f"\n🏆 Dominant Emotion : {summary['dominant_emotion'].upper()}")
    print(f"💪 Confidence Score : {summary['confidence_score']}/100")
    print(f"📊 Feedback         : {summary['confidence_feedback']}")
    print(f"\n📈 Emotion Breakdown:")
    for emotion, pct in sorted(
        summary['emotion_percentages'].items(),
        key=lambda x: x[1], reverse=True
    ):
        bar = "█" * int(pct / 5)
        print(f"   {emotion:<10} {bar:<20} {pct}%")
    print(f"\n💡 Tips:")
    for tip in summary['tips']:
        print(f"   {tip}")
    print("\n" + "="*45)


# Test the module
if __name__ == "__main__":
    print("🎭 AI Interview Emotion Detector")
    print("="*45)
    print("This will open your webcam and detect emotions")
    print("\nWhen ready, press Enter to start...")
    input()

    emotion_log = analyze_emotions_realtime(duration=30)

    if emotion_log:
        summary = analyze_emotion_summary(emotion_log)
        print_emotion_report(summary)
    else:
        print("❌ No emotions detected. Check your webcam!")
