from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Company profiles with interview styles
COMPANY_PROFILES = {
    # Indian IT Companies
    "TCS": {
        "full_name": "Tata Consultancy Services",
        "type": "Indian IT",
        "interview_style": "Aptitude + Technical + HR rounds",
        "focus_areas": ["Coding basics", "SQL", "Java/Python", "Communication", "Teamwork"],
        "known_for": "Large scale projects, process-driven culture, work-life balance",
        "tip": "TCS focuses heavily on communication skills and basic coding. They love candidates who are adaptable and team players.",
        "rounds": ["Aptitude Test", "Technical Interview", "Managerial Round", "HR Round"],
        "favorite_questions": [
            "Tell me about yourself",
            "Why do you want to join TCS?",
            "Where do you see yourself in 5 years?",
            "Explain OOP concepts",
            "Write a program to reverse a string"
        ]
    },
    "Infosys": {
        "full_name": "Infosys Limited",
        "type": "Indian IT",
        "interview_style": "Aptitude + Technical + HR",
        "focus_areas": ["Problem solving", "Communication", "Python/Java", "DBMS", "OS concepts"],
        "known_for": "Training programs, global exposure, innovation culture",
        "tip": "Infosys values problem-solving ability and communication. Focus on explaining your thought process clearly.",
        "rounds": ["Online Test", "Technical Round 1", "Technical Round 2", "HR Round"],
        "favorite_questions": [
            "Explain your final year project",
            "What is polymorphism?",
            "Difference between SQL and NoSQL",
            "How do you handle work pressure?",
            "Write a program to find factorial"
        ]
    },
    "Wipro": {
        "full_name": "Wipro Limited",
        "type": "Indian IT",
        "interview_style": "Online Test + Technical + HR",
        "focus_areas": ["Verbal ability", "Logical reasoning", "Coding", "Core CS concepts"],
        "known_for": "Diversity, sustainability focus, global delivery",
        "tip": "Wipro focuses on logical reasoning and verbal ability in addition to technical skills. Practice aptitude tests.",
        "rounds": ["NLTH Test", "Technical Interview", "HR Interview"],
        "favorite_questions": [
            "What are your strengths and weaknesses?",
            "Explain SDLC",
            "What is cloud computing?",
            "Describe a challenging situation you overcame",
            "Why Wipro?"
        ]
    },
    "HCL": {
        "full_name": "HCL Technologies",
        "type": "Indian IT",
        "interview_style": "Technical + HR focused",
        "focus_areas": ["Core technical skills", "Project experience", "Communication", "Attitude"],
        "known_for": "Employee-first culture, infrastructure services, digital transformation",
        "tip": "HCL values technical depth and positive attitude. Be confident about your projects and skills.",
        "rounds": ["Technical Round", "HR Round"],
        "favorite_questions": [
            "Walk me through your projects",
            "What programming languages do you know?",
            "Explain your internship experience",
            "How do you stay updated with technology?",
            "What is your greatest achievement?"
        ]
    },

    # Product Companies
    "Google": {
        "full_name": "Google LLC",
        "type": "Product Company",
        "interview_style": "DSA + System Design + Behavioral",
        "focus_areas": ["Data Structures", "Algorithms", "System Design", "Problem Solving", "Googleyness"],
        "known_for": "Innovation, open culture, cutting-edge technology, best perks",
        "tip": "Google focuses heavily on DSA and problem-solving. Practice LeetCode medium/hard problems. Think out loud during coding.",
        "rounds": ["Phone Screen", "Technical Round 1", "Technical Round 2", "System Design", "Behavioral"],
        "favorite_questions": [
            "Implement a LRU Cache",
            "Design Google Search",
            "Find the shortest path in a graph",
            "Tell me about a time you failed",
            "How would you design YouTube?"
        ]
    },
    "Amazon": {
        "full_name": "Amazon.com Inc",
        "type": "Product Company",
        "interview_style": "Leadership Principles + DSA + System Design",
        "focus_areas": ["Leadership Principles", "STAR method", "DSA", "System Design", "Customer obsession"],
        "known_for": "Leadership Principles, customer focus, fast-paced environment, ownership",
        "tip": "Amazon LOVES the STAR method and Leadership Principles. Prepare 2 stories for each of their 16 Leadership Principles.",
        "rounds": ["Online Assessment", "Phone Screen", "Loop Interviews (4-5 rounds)"],
        "favorite_questions": [
            "Tell me about a time you took ownership",
            "Describe a situation where you disagreed with your manager",
            "How do you handle tight deadlines?",
            "Design Amazon's recommendation system",
            "Tell me about a time you failed and what you learned"
        ]
    },
    "Microsoft": {
        "full_name": "Microsoft Corporation",
        "type": "Product Company",
        "interview_style": "Coding + Behavioral + Culture fit",
        "focus_areas": ["DSA", "OOP", "System Design", "Growth mindset", "Collaboration"],
        "known_for": "Growth mindset culture, work-life balance, diverse teams, Azure cloud",
        "tip": "Microsoft values growth mindset and collaboration. Show enthusiasm for learning and teamwork in every answer.",
        "rounds": ["Online Assessment", "Technical Rounds (3-4)", "As-Appropriate Round"],
        "favorite_questions": [
            "Implement binary search",
            "Design a parking lot system",
            "Tell me about a time you learned something new quickly",
            "How do you handle conflict in a team?",
            "What is your approach to debugging?"
        ]
    }
}


def get_company_profile(company_name):
    """
    Get company profile by name
    """
    for key, profile in COMPANY_PROFILES.items():
        if key.lower() == company_name.lower():
            return key, profile
    return None, None


def get_all_companies():
    """
    Get list of all available companies
    """
    indian_it = [k for k, v in COMPANY_PROFILES.items() if v["type"] == "Indian IT"]
    product = [k for k, v in COMPANY_PROFILES.items() if v["type"] == "Product Company"]
    return indian_it, product


def generate_company_questions(company_name, job_role, resume_data=None, num_questions=5):
    """
    Generate company-specific interview questions
    """
    company_key, profile = get_company_profile(company_name)

    if not profile:
        return [], None

    focus_areas = ", ".join(profile["focus_areas"])
    rounds = ", ".join(profile["rounds"])
    resume_context = ""

    if resume_data:
        skills = ", ".join(resume_data.get("skills", []))
        projects = ", ".join(resume_data.get("projects", []))
        resume_context = f"""
        Candidate Skills: {skills}
        Candidate Projects: {projects}
        Experience: {resume_data.get('experience_years', '0')} years
        """

    prompt = f"""
    You are an expert interviewer from {profile['full_name']}.
    Generate {num_questions} interview questions exactly matching {company_name}'s interview style.

    Company: {company_name} ({profile['full_name']})
    Interview Style: {profile['interview_style']}
    Focus Areas: {focus_areas}
    Interview Rounds: {rounds}
    Job Role: {job_role}
    {resume_context}

    Important:
    - Match {company_name}'s actual interview culture
    - For Amazon: include Leadership Principle based questions
    - For Google: include DSA and system design questions
    - For TCS/Infosys/Wipro/HCL: include basic technical + HR questions
    - Make questions realistic and challenging
    - Number each question (1. 2. 3. etc.)

    Generate exactly {num_questions} questions only.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    questions = [q.strip() for q in raw.strip().split("\n") if q.strip() and q[0].isdigit()]
    return questions, profile


def print_company_profile(company_name, profile):
    """
    Print company interview profile
    """
    print("\n" + "="*55)
    print(f"       🏢 {company_name} INTERVIEW PROFILE")
    print("="*55)
    print(f"🏢 Company     : {profile['full_name']}")
    print(f"📋 Type        : {profile['type']}")
    print(f"🎯 Style       : {profile['interview_style']}")
    print(f"\n📌 Interview Rounds:")
    for idx, round_name in enumerate(profile['rounds'], 1):
        print(f"   {idx}. {round_name}")
    print(f"\n🎯 Focus Areas:")
    for area in profile['focus_areas']:
        print(f"   • {area}")
    print(f"\n💡 Expert Tip:")
    print(f"   {profile['tip']}")
    print("="*55)


# Test the module
if __name__ == "__main__":
    print("🏢 Company Specific Interview Prep")
    print("="*55)

    # Show available companies
    indian_it, product = get_all_companies()
    print("\n🇮🇳 Indian IT Companies:")
    for c in indian_it:
        print(f"   • {c}")
    print("\n🌐 Product Companies:")
    for c in product:
        print(f"   • {c}")

    company = input("\nEnter Company Name: ")
    job_role = input("Enter Job Role: ")

    print(f"\n⏳ Loading {company} interview profile...")
    questions, profile = generate_company_questions(company, job_role)

    if profile:
        print_company_profile(company, profile)

        print(f"\n🎯 {company} Style Interview Questions:")
        print("="*55)
        for q in questions:
            print(f"\n{q}")
        print("="*55)
    else:
        print(f"❌ Company '{company}' not found!")
        print("Available: TCS, Infosys, Wipro, HCL, Google, Amazon, Microsoft")
