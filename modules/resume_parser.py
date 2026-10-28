import pdfplumber
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_text_from_pdf(pdf_path):
    """
    Extract raw text from PDF resume
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        print(f"✅ Resume text extracted! ({len(text)} characters)")
        return text
    except Exception as e:
        print(f"❌ Error extracting PDF: {e}")
        return ""


def parse_resume_with_ai(resume_text):
    """
    Use Groq AI to extract structured info from resume
    """
    prompt = f"""
    You are an expert resume analyzer. Extract structured information from this resume.

    Resume Text:
    {resume_text[:3000]}

    Extract and return EXACTLY in this format:
    NAME: [candidate name]
    EMAIL: [email address]
    PHONE: [phone number]
    EXPERIENCE_YEARS: [total years of experience]
    CURRENT_ROLE: [current or most recent job title]
    CURRENT_COMPANY: [current or most recent company]
    SKILLS: [skill1, skill2, skill3, skill4, skill5]
    PROJECTS: [project1 name | project2 name | project3 name]
    EDUCATION: [degree, institution]
    ACHIEVEMENTS: [achievement1 | achievement2]
    PREVIOUS_COMPANIES: [company1, company2, company3]

    Return ONLY the formatted data above. Nothing else.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    return parse_resume_data(raw)


def parse_resume_data(raw_text):
    """
    Parse AI response into structured dictionary
    """
    data = {
        "name": "Candidate",
        "email": "",
        "phone": "",
        "experience_years": "0",
        "current_role": "",
        "current_company": "",
        "skills": [],
        "projects": [],
        "education": "",
        "achievements": [],
        "previous_companies": []
    }

    try:
        lines = raw_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if "NAME:" in line:
                data["name"] = line.split("NAME:")[1].strip()
            elif "EMAIL:" in line:
                data["email"] = line.split("EMAIL:")[1].strip()
            elif "PHONE:" in line:
                data["phone"] = line.split("PHONE:")[1].strip()
            elif "EXPERIENCE_YEARS:" in line:
                data["experience_years"] = line.split("EXPERIENCE_YEARS:")[1].strip()
            elif "CURRENT_ROLE:" in line:
                data["current_role"] = line.split("CURRENT_ROLE:")[1].strip()
            elif "CURRENT_COMPANY:" in line:
                data["current_company"] = line.split("CURRENT_COMPANY:")[1].strip()
            elif "SKILLS:" in line:
                skills_raw = line.split("SKILLS:")[1].strip()
                data["skills"] = [s.strip() for s in skills_raw.split(",")]
            elif "PROJECTS:" in line:
                projects_raw = line.split("PROJECTS:")[1].strip()
                data["projects"] = [p.strip() for p in projects_raw.split("|")]
            elif "EDUCATION:" in line:
                data["education"] = line.split("EDUCATION:")[1].strip()
            elif "ACHIEVEMENTS:" in line:
                ach_raw = line.split("ACHIEVEMENTS:")[1].strip()
                data["achievements"] = [a.strip() for a in ach_raw.split("|")]
            elif "PREVIOUS_COMPANIES:" in line:
                comp_raw = line.split("PREVIOUS_COMPANIES:")[1].strip()
                data["previous_companies"] = [c.strip() for c in comp_raw.split(",")]
    except Exception as e:
        print(f"⚠️ Parsing warning: {e}")

    return data


def generate_resume_based_questions(resume_data, job_role, num_questions=5):
    """
    Generate personalized interview questions based on resume
    """
    skills = ", ".join(resume_data.get("skills", []))
    projects = ", ".join(resume_data.get("projects", []))
    achievements = ", ".join(resume_data.get("achievements", []))
    experience = resume_data.get("experience_years", "0")
    current_role = resume_data.get("current_role", "")
    current_company = resume_data.get("current_company", "")

    prompt = f"""
    You are an expert interviewer. Generate {num_questions} highly personalized
    interview questions based on THIS candidate's actual resume.

    Candidate Profile:
    - Name: {resume_data.get('name', 'Candidate')}
    - Current Role: {current_role} at {current_company}
    - Experience: {experience} years
    - Key Skills: {skills}
    - Projects: {projects}
    - Achievements: {achievements}
    - Target Job Role: {job_role}

    Rules:
    - Reference their ACTUAL skills, projects and experience
    - Ask about specific technologies they mentioned
    - Ask about their real achievements
    - Make questions feel like a REAL interview
    - Number each question (1. 2. 3. etc.)
    - No extra text, just questions

    Generate exactly {num_questions} personalized questions.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    questions = [q.strip() for q in raw.strip().split("\n") if q.strip() and q[0].isdigit()]
    return questions


def print_resume_summary(resume_data):
    """
    Print extracted resume summary
    """
    print("\n" + "="*50)
    print("       📄 RESUME ANALYSIS SUMMARY")
    print("="*50)
    print(f"👤 Name            : {resume_data['name']}")
    print(f"📧 Email           : {resume_data['email']}")
    print(f"💼 Current Role    : {resume_data['current_role']}")
    print(f"🏢 Company         : {resume_data['current_company']}")
    print(f"⏳ Experience      : {resume_data['experience_years']} years")
    print(f"🎓 Education       : {resume_data['education']}")
    print(f"\n🛠️  Skills:")
    for skill in resume_data['skills']:
        print(f"   • {skill}")
    print(f"\n📁 Projects:")
    for project in resume_data['projects']:
        print(f"   • {project}")
    print(f"\n🏆 Achievements:")
    for ach in resume_data['achievements']:
        print(f"   • {ach}")
    print("="*50)


# Test the module
if __name__ == "__main__":
    print("📄 AI Resume Parser & Question Generator")
    print("="*50)

    pdf_path = input("Enter path to your resume PDF: ")

    if not os.path.exists(pdf_path):
        print("❌ File not found! Check the path.")
    else:
        print("\n⏳ Extracting resume text...")
        resume_text = extract_text_from_pdf(pdf_path)

        print("⏳ Analyzing resume with AI...")
        resume_data = parse_resume_with_ai(resume_text)

        print_resume_summary(resume_data)

        job_role = input("\nEnter Target Job Role: ")
        print(f"\n⏳ Generating personalized questions for {job_role}...")
        questions = generate_resume_based_questions(resume_data, job_role)

        print(f"\n🎯 Personalized Interview Questions:")
        print("="*50)
        for q in questions:
            print(q)
        print("="*50)
