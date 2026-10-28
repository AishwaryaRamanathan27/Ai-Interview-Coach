import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time

# Load Whisper model (only loads once)
print("⏳ Loading Whisper model...")
model = whisper.load_model("base")
print("✅ Whisper model loaded!")

def record_audio(duration=60, sample_rate=16000):
    """
    Record audio from microphone
    """
    print(f"\n🎤 Recording started... Speak now! (max {duration} seconds)")
    print("Press Ctrl+C to stop recording early\n")

    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.int16
    )

    try:
        sd.wait()
    except KeyboardInterrupt:
        sd.stop()
        print("\n⏹ Recording stopped early!")

    # Save as WAV file
    wav.write("outputs/recorded_answer.wav", sample_rate, audio_data)
    print("✅ Audio recorded and saved!")
    return "outputs/recorded_answer.wav"


def transcribe_audio(audio_path):
    """
    Convert speech to text using Whisper
    """
    print("\n⏳ Transcribing your answer...")
    result = model.transcribe(audio_path)
    transcript = result["text"].strip()
    print("✅ Transcription complete!")
    return transcript


def analyze_speech(transcript):
    """
    Analyze speech for filler words and pace
    """
    # Count filler words
    filler_words = ["um", "uh", "like", "you know", "basically",
                    "actually", "literally", "right", "so", "well"]

    transcript_lower = transcript.lower()
    filler_count = {}
    total_fillers = 0

    for word in filler_words:
        count = transcript_lower.count(word)
        if count > 0:
            filler_count[word] = count
            total_fillers += count

    # Calculate word count and pace
    words = transcript.split()
    word_count = len(words)

    # Estimate duration from word count (average 130 wpm)
    estimated_duration_mins = word_count / 130
    wpm = int(word_count / estimated_duration_mins) if estimated_duration_mins > 0 else 0

    # Generate pace feedback
    if wpm < 100:
        pace_feedback = "🐢 Too slow — try to speak more confidently"
    elif wpm <= 150:
        pace_feedback = "✅ Perfect pace — clear and professional"
    elif wpm <= 180:
        pace_feedback = "⚡ Slightly fast — try to slow down a bit"
    else:
        pace_feedback = "🚀 Too fast — slow down significantly"

    return {
        "transcript": transcript,
        "word_count": word_count,
        "wpm": wpm,
        "pace_feedback": pace_feedback,
        "filler_words": filler_count,
        "total_fillers": total_fillers
    }


def print_speech_report(analysis):
    """
    Print a clean speech analysis report
    """
    print("\n" + "="*45)
    print("       📊 SPEECH ANALYSIS REPORT")
    print("="*45)

    print(f"\n📝 Transcript:\n{analysis['transcript']}")

    print(f"\n📈 Speech Stats:")
    print(f"   • Word Count     : {analysis['word_count']} words")
    print(f"   • Speaking Pace  : {analysis['wpm']} WPM")
    print(f"   • Pace Feedback  : {analysis['pace_feedback']}")

    print(f"\n⚠️  Filler Words Found: {analysis['total_fillers']} total")
    if analysis['filler_words']:
        for word, count in analysis['filler_words'].items():
            print(f"   • '{word}' used {count} time(s)")
    else:
        print("   • No filler words detected! 🎉")

    print("\n" + "="*45)


# Test the module
if __name__ == "__main__":
    print("🎤 AI Interview Speech Analyzer")
    print("="*45)
    print("This will record your answer and analyze it")
    print("\nWhen ready, press Enter to start recording...")
    input()

    # Record audio
    audio_path = record_audio(duration=30)

    # Transcribe
    transcript = transcribe_audio(audio_path)

    # Analyze
    analysis = analyze_speech(transcript)

    # Print report
    print_speech_report(analysis)