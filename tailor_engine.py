import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


RESUME_AND_LETTER_PROMPT = """
You are an elite technical recruiter and career strategist helping university students and early-career candidates land interviews at top companies.

Your task is to take:
1. The student's current resume profile.
2. The target company name and role.
3. The target job description.
4. Target location.

And produce:
1. A tailored, ATS-optimized resume following the classic "Jake's Resume Template" structure in crisp Black & White formatting.
2. A compelling, professional Application Letter (Cover Letter) tailored specifically for this company and role.
3. A 4-Category Enterprise ATS Diagnostic Breakdown (Overall, Skills, Impact, Format, Brevity).
4. AI Mock Interview Preparation (3 Technical Questions, 2 Company Culture / Behavioral Questions with answer tips).
5. "Before vs. After" Bullet Point Transformations (showing how raw bullets were elevated into Google XYZ format).
6. A professional LinkedIn Headline and About summary tailored for this career trajectory.

CRITICAL RULES:
1. TRUTHFULNESS & ANTI-HALLUCINATION: NEVER fabricate degrees, companies, jobs, or work experiences that the student didn't provide. Only re-frame, elevate, and highlight their real skills, projects, and coursework.
2. JAKE'S TEMPLATE STRUCTURE: Standard sections: Education, Technical Skills, Experience, Projects, Certifications/Awards.
3. GOOGLE XYZ BULLETS: Rewrite bullet points following "Accomplished [X] as measured by [Y], by doing [Z]". Use strong active verbs (e.g., Engineered, Spearheaded, Accelerated, Implemented, Streamlined).

Respond strictly in valid JSON matching this schema:
{
  "ats_assessment": {
    "match_score": 93,
    "breakdown": {
      "skills_match_score": 96,
      "impact_metric_score": 91,
      "format_compliance_score": 99,
      "brevity_score": 94
    },
    "target_company": "Company Name",
    "target_role": "Role Title",
    "location": "Location",
    "key_matched_keywords": ["keyword1", "keyword2", "keyword3"],
    "missing_or_recommended_keywords": ["keyword4", "keyword5"],
    "tailoring_summary": "Explanation of changes made and why it appeals to this employer."
  },
  "personal_info": {
    "name": "Student Full Name",
    "email": "email@example.com",
    "phone": "Phone number or blank",
    "location": "City, State",
    "linkedin": "linkedin url or blank",
    "github": "github url or blank",
    "portfolio": "portfolio or blank"
  },
  "education": [
    {
      "institution": "University Name",
      "location": "City, State",
      "degree": "Bachelor of Science in Computer Science",
      "dates": "Expected May 2026",
      "gpa": "GPA if present",
      "relevant_coursework": ["Course 1", "Course 2", "Course 3"]
    }
  ],
  "skills": {
    "Languages": ["Python", "Java", "C++", "SQL"],
    "Frameworks & Developer Tools": ["React", "FastAPI", "Docker", "Git", "AWS"],
    "Core Competencies": ["Data Structures & Algorithms", "Distributed Systems", "RESTful APIs"]
  },
  "experience": [
    {
      "role": "Software Engineering Intern",
      "company": "Company Name",
      "location": "City, State",
      "dates": "June 2024 – Aug 2024",
      "bullets": [
        "Action verb + Task + Quantifiable Result / Tech used.",
        "Second high-impact bullet point."
      ]
    }
  ],
  "projects": [
    {
      "title": "Project Name",
      "tech_stack": "Python, FastAPI, PostgreSQL",
      "dates": "Jan 2024 – Present",
      "bullets": [
        "Accomplished [X] by doing [Z], resulting in [Y] performance improvement.",
        "Engineered backend microservices handling concurrent requests."
      ]
    }
  ],
  "certifications_or_awards": [
    "Dean's Honors List",
    "Hackathon 1st Place Winner"
  ],
  "application_letter": {
    "recipient": "Hiring Team",
    "company": "Target Company",
    "role": "Role Title",
    "date": "October 31, 2026",
    "opening": "Opening paragraph stating the role applied for and genuine enthusiasm for the company mission.",
    "body_paragraph_1": "Paragraph connecting student's technical background and top project directly to the role requirements.",
    "body_paragraph_2": "Paragraph demonstrating problem-solving, collaboration, and eagerness to contribute.",
    "closing": "Closing paragraph reiterating enthusiasm, availability, and requesting an interview."
  },
  "bullet_transformations": [
    {
      "context": "Project / Work Title",
      "original_bullet": "Unoptimized draft or brief statement.",
      "elevated_bullet": "Google XYZ bullet with action verb and metrics.",
      "impact_enhancement": "Explanation of what was enhanced (e.g. quantified latency reduction)."
    }
  ],
  "interview_prep": {
    "technical_questions": [
      {
        "question": "Realistic technical question based on their tailored projects?",
        "focus_area": "System Architecture / Concurrency",
        "answer_strategy": "Key technical talking points the student should mention."
      }
    ],
    "behavioral_questions": [
      {
        "question": "Behavioral question tied to the target company culture?",
        "company_value": "Customer Obsession / Ownership",
        "answer_strategy": "STAR method guidance."
      }
    ]
  },
  "linkedin_suite": {
    "headline": "Punchy 1-2 line headline with keywords.",
    "about_summary": "3-sentence professional bio connecting university studies to company domain."
  },
  "recruiter_outreach": {
    "linkedin_connection_note": "Concise connection request note under 300 characters referencing common tech or interest in their team.",
    "cold_email_subject": "Brief subject line e.g. Software Engineer Candidate - [Candidate Name]",
    "cold_email_body": "Concise 3-paragraph outreach email to hiring manager emphasizing impact, relevant stack, and humble call to action.",
    "thank_you_note": "Thoughtful post-interview thank you email referencing key technical discussions."
  }
}
"""

RECOMMENDATION_PROMPT = """
You are a senior tech talent scout and career advisor.
Analyze the student's resume profile and target location preference.
Recommend 4 to 5 high-profile, real-world companies and specific student/intern/new-grad roles where this candidate has the highest competitive advantage.

For EACH company:
1. "company_name": Official company name (e.g. Stripe, Datadog, Palantir, Cloudflare, Figma, Ramp).
2. "website_url": The exact official company website (e.g. "https://stripe.com", "https://datadoghq.com", "https://palantir.com", etc.).
3. "headquarters": Accurate real-world headquarters location (e.g. "South San Francisco, CA & Dublin", "New York, NY", "Denver, CO", "San Francisco, CA").
4. "target_locations": Accurate real-world office hubs and remote options that fit the student's location preference (e.g. "San Francisco, CA • Seattle, WA • Remote US").
5. "work_policy": Real-world policy (e.g. "Hybrid (3 days in office)", "Remote Friendly", "In-Person").
6. "role_title": Realistic role title suitable for a student/intern/junior (e.g. "Software Engineering Intern - Infrastructure & APIs").
7. "industry": Industry tag (e.g. "Fintech / Core Infrastructure", "Observability & Cloud", "Enterprise AI & Defense").
8. "fit_score": Match percentage between 88 and 98 based on actual tech stack match.
9. "company_overview": 2-3 engaging sentences describing what the company builds, their engineering scale, and why developers love working there.
10. "match_reason": Concise sentence connecting the student's specific projects/skills to what this company builds.
11. "skills_match": List of 3-5 overlapping skills.
12. "job_description": Realistic 2-paragraph job description with key responsibilities and qualifications for tailoring.

Respond strictly in valid JSON matching this schema:
{
  "recommendations": [
    {
      "company_name": "Stripe",
      "website_url": "https://stripe.com",
      "headquarters": "South San Francisco, CA & Dublin, Ireland",
      "target_locations": "San Francisco, CA • Seattle, WA • Remote (US/Canada)",
      "work_policy": "Hybrid / Remote Available",
      "role_title": "Software Engineering Intern - Infrastructure & APIs",
      "industry": "Fintech & Developer Infrastructure",
      "fit_score": 95,
      "company_overview": "Stripe builds economic infrastructure for the internet, powering payments and financial services for millions of businesses worldwide. Their engineering culture emphasizes reliability, developer ergonomics, and distributed scale.",
      "match_reason": "Your backend API development, Python/FastAPI projects, and interest in high-availability systems directly align with Stripe's payments infrastructure team.",
      "skills_match": ["Python", "API Design", "Distributed Systems", "AWS"],
      "job_description": "We are seeking Software Engineering Interns to join our Infrastructure team in San Francisco, CA or Remote. You will design, build, and deploy high-availability services and RESTful APIs that process millions of transactions per second. Required: Strong foundation in data structures, algorithms, and backend services in Python, Java, or Go. Familiarity with databases and cloud infrastructure."
    }
  ]
}
"""


def recommend_companies_for_student(
    resume_text: str,
    target_location: str = "Any",
    target_role: str = "",
    api_key: str = None,
    model: str = "gpt-4o-mini"
) -> list:
    """
    Analyzes student resume & target location preference.
    Returns 4-5 verified company recommendations with real URLs, exact HQ/hubs, and job descriptions.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key or key.strip() == "":
        raise ValueError("OpenAI API Key is missing. Please set OPENAI_API_KEY in .env.")

    client = OpenAI(api_key=key.strip())

    role_line = f"DESIRED ROLE / FOCUS: {target_role}\n" if target_role else ""

    user_prompt = f"""
TARGET LOCATION PREFERENCE: {target_location or 'Any location / Remote'}
{role_line}
--- STUDENT RESUME PROFILE ---
{resume_text}

Recommend 4-5 best-fit companies and roles for this candidate with official website URLs, accurate headquarters and tech hubs, and full job descriptions.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": RECOMMENDATION_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.4
    )

    raw_content = response.choices[0].message.content
    try:
        data = json.loads(raw_content)
        return data.get("recommendations", [])
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse recommendations JSON: {e}\nRaw output: {raw_content[:300]}")


def tailor_resume_and_letter(
    resume_text: str,
    job_description: str,
    company_name: str = "",
    role_title: str = "",
    location: str = "",
    career_level: str = "student",
    user_details: dict = None,
    api_key: str = None,
    model: str = "gpt-4o-mini"
) -> dict:
    """
    Calls OpenAI GPT to tailor the candidate's resume (Jake's Template B&W),
    craft an Application Letter, generate 4-Category ATS Breakdown, Keyword Match & Gap Matrix,
    Recruiter Outreach Suite, Before/After Diff, Mock Interview Questions, and LinkedIn Suite.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key or key.strip() == "":
        raise ValueError("OpenAI API Key is missing. Please set OPENAI_API_KEY in .env.")

    client = OpenAI(api_key=key.strip())

    details = user_details or {}
    contact_instruction = ""
    if details:
        parts = []
        if details.get("name"): parts.append(f"Full Name: {details['name']}")
        if details.get("email"): parts.append(f"Email: {details['email']}")
        if details.get("phone"): parts.append(f"Phone: {details['phone']}")
        if details.get("linkedin"): parts.append(f"LinkedIn: {details['linkedin']}")
        if details.get("github"): parts.append(f"GitHub: {details['github']}")
        if details.get("portfolio"): parts.append(f"Portfolio: {details['portfolio']}")
        if details.get("target_role"): parts.append(f"Preferred Target Role: {details['target_role']}")
        if parts:
            contact_instruction = "EXACT CANDIDATE CONTACT DETAILS (Use these exact values in personal_info):\n" + "\n".join(parts) + "\n"

    level_instruction = (
        "CANDIDATE STAGE: Student / New Grad. Prioritize Education, coursework, academic achievements, and foundational projects."
        if career_level == "student"
        else "CANDIDATE STAGE: Experienced Professional. Prioritize Work Experience, architectural decisions, business impact, and leadership. Place Education at the bottom."
    )

    user_prompt = f"""
TARGET COMPANY: {company_name or 'Target Employer'}
TARGET ROLE: {role_title or details.get('target_role') or 'Target Role'}
TARGET LOCATION: {location or 'Not specified'}
{level_instruction}
{contact_instruction}
--- TARGET JOB DESCRIPTION ---
{job_description}

--- CANDIDATE'S CURRENT RESUME / PROFILE ---
{resume_text}

Generate the complete enterprise application suite (Jake's Resume, Application Letter, 4-Category ATS breakdown with matched and missing keywords, Recruiter Outreach suite, Before vs After comparisons, Interview prep, and LinkedIn suite).
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": RESUME_AND_LETTER_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    raw_content = response.choices[0].message.content
    try:
        data = json.loads(raw_content)
        data["career_level"] = career_level

        # Guarantee user contact overrides if provided
        p = data.setdefault("personal_info", {})
        if details.get("name"): p["name"] = details["name"]
        if details.get("email"): p["email"] = details["email"]
        if details.get("phone"): p["phone"] = details["phone"]
        if details.get("linkedin"): p["linkedin"] = details["linkedin"]
        if details.get("github"): p["github"] = details["github"]
        if details.get("portfolio"): p["portfolio"] = details["portfolio"]

        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse GPT response as JSON: {e}\nRaw output: {raw_content[:300]}")


def tune_bullet(
    bullet_text: str,
    mode: str,
    target_role: str = "",
    tech_stack: str = "",
    api_key: str = None,
    model: str = "gpt-4o-mini"
) -> str:
    """
    Refines a single resume bullet point on demand.
    Modes:
      - 'add_metrics': Infuses realistic, quantifiable metrics/data/scale.
      - 'more_technical': Emphasizes architectural depth, libraries, frameworks, performance.
      - 'more_concise': Trims words to a punchy, crisp single-line ATS bullet under 22 words.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key or key.strip() == "":
        raise ValueError("OpenAI API Key is missing.")

    client = OpenAI(api_key=key.strip())

    mode_prompts = {
        "add_metrics": "Enhance this bullet with realistic quantifiable impact (e.g. latency reduced by X%, throughput increased, X active users, test coverage). Do not sound artificial.",
        "more_technical": "Make this bullet more technically rigorous by specifying tools, algorithms, protocols, data structures, or engineering patterns.",
        "more_concise": "Make this bullet extremely concise, punchy, and readable in under 20 words, strictly starting with an active power verb."
    }

    directive = mode_prompts.get(mode, "Refine this bullet using the Google XYZ formula (Accomplished X by doing Z as measured by Y).")

    prompt = f"""
You are an expert technical resume editor.
ORIGINAL BULLET: "{bullet_text}"
TARGET ROLE: {target_role or 'Software Engineer'}
RELEVANT TECH: {tech_stack or 'Modern tech stack'}

GOAL: {directive}
RULES:
1. Return ONLY the single refined bullet point text.
2. Do not enclose in quotes.
3. Do not include markdown bullet symbols (* or -).
4. Never invent degrees or unrelated companies.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=120
    )

    refined = response.choices[0].message.content.strip().strip('"').strip("'").lstrip("•-* ")
    return refined

