from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import httpx
import json
import re
import os

# Load .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use env vars directly

app = FastAPI(title="Job Match Scorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# GROQ API
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(GROQ_API_KEY)
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

APPLY_THRESHOLD = 60
MAX_EXPERIENCE_GAP_MONTHS = 6

# ============================================
# SOFT SKILLS TO IGNORE (don't count in scoring)
# ============================================
SOFT_SKILLS_IGNORE = [
    # Generic terms
    "api", "apis", "frontend", "backend", "full stack", "fullstack", "full-stack",
    "web development", "software development", "application development",
    "build", "develop", "create", "design", "implement", "deploy",
    # Soft skills
    "fast learner", "quick learner", "team player", "communication",
    "problem solving", "problem-solving", "analytical", "leadership",
    "agile", "scrum", "collaboration", "self-motivated", "motivated",
    "detail oriented", "detail-oriented", "time management",
    "critical thinking", "creative", "adaptable", "flexible",
    # Generic tech terms
    "coding", "programming", "development", "engineering", "technical",
    "software", "web", "mobile", "cloud", "data", "database",
    "testing", "debugging", "documentation", "maintenance",
    "scalable", "reliable", "secure", "performance",
]

# ============================================
# RESUME DATA - DHANRAJ PIMPLE
# ============================================
RESUME = {
    "name": "Dhanraj Pimple",
    "email": "dhanrajpimple16@gmail.com",
    "phone": "+91 91468 90521",
    "linkedin": "linkedin.com/in/dhanrajpimple",
    "github": "github.com/dhanrajpimple",
    
    "title": "Full Stack Developer",
    "total_experience_months": 18,
    "total_experience_years": 1.5,
    
    "summary": "Full Stack Developer with 1+ year of professional experience building web applications and automation systems. Proficient in React.js, Node.js, FastAPI, and PostgreSQL with hands-on experience in AWS services and API integrations. Developed multiple client-facing applications and contributed to microservices architecture. Strong problem-solving skills with 500+ DSA problems solved.",
    
    "education": {
        "degree": "Master of Computer Applications (MCA)",
        "institution": "K.K. Wagh Institute of Engineering Education and Research, Nashik",
        "cgpa": "7.5/10",
        "duration": "Nov 2022 - Jun 2024",
        "coursework": ["Data Structures & Algorithms", "Database Management Systems", "Operating Systems", "Web Technologies", "Software Engineering"]
    },
    
    # ONLY TECHNICAL SKILLS (for matching)
    "technical_skills": [
        # Languages
        "JavaScript", "Python", "SQL", "C++", "ES6",
        # Frontend specific
        "React.js", "React", "Remix.js", "Remix", "HTML5", "CSS3", "Tailwind CSS", "Tailwind", "Redux",
        # Backend specific
        "Node.js", "Node", "Express.js", "Express", "FastAPI", "REST", "RESTful", "JWT",
        # Databases specific
        "PostgreSQL", "Postgres", "MySQL", "MongoDB", "Mongo", "Supabase",
        # Cloud specific
        "AWS", "Lambda", "SQS", "S3", "EC2", "SES", "EventBridge",
        "Docker", "Git", "Vercel", "CI/CD",
        # Specific tools/APIs
        "OpenAI", "GPT", "Twilio", "ElevenLabs", "Razorpay", "Postman", "Jira",
        "Procore", "DocuSign",
        # Frameworks/concepts
        "MERN", "Microservices"
    ],
    
    "experience": [
        {
            "title": "Full Stack Developer (Contract)",
            "company": "Palcode.ai",
            "location": "Remote",
            "duration": "Jun 2025 - Dec 2025",
            "months": 7,
            "tech": ["React.js", "Tailwind CSS", "FastAPI", "Python", "PostgreSQL", "AWS", "OpenAI API", "Twilio", "Docker"]
        },
        {
            "title": "Software Developer",
            "company": "ProDT Consulting Services Pvt. Ltd",
            "location": "Pune, India",
            "duration": "Jul 2024 - Mar 2025",
            "months": 9,
            "tech": ["React.js", "Node.js", "Express.js", "Redux", "Supabase", "PostgreSQL", "REST APIs"]
        },
        {
            "title": "Freelance Full Stack Developer",
            "company": "Self-employed",
            "location": "Remote",
            "duration": "Jan 2024 - Present",
            "months": 24,
            "tech": ["Remix.js", "Tailwind CSS", "Supabase", "React.js"]
        }
    ],
    
    "achievements": [
        "Solved 500+ problems across LeetCode, CodeChef, and HackerRank"
    ]
}

TECHNICAL_SKILLS = RESUME['technical_skills']

# ============================================
# API MODELS
# ============================================
class ScoreRequest(BaseModel):
    job_description: str

class ScoreResponse(BaseModel):
    match_score: int
    verdict: str
    experience_match: str
    experience_flag: str
    qualification_match: str
    skills_match: str
    matched_skills: List[str]
    missing_skills: List[str]
    action: str

# ============================================
# EXPERIENCE EXTRACTION - FIXED!
# ============================================
def extract_required_experience(job_text: str) -> dict:
    """Extract years of experience required from job description"""
    job_lower = job_text.lower()
    
    min_years = None
    max_years = None
    
    # FIRST: Check for RANGE patterns (1-3 years, 2-4 years, etc.)
    # This is the most specific - use MIN of range as requirement
    range_pattern = r'(\d+)\s*[-–to]+\s*(\d+)\s*(?:\+)?\s*(?:years?|yrs?)'
    range_matches = re.findall(range_pattern, job_lower)
    
    if range_matches:
        # Take the FIRST range found - min is the lower number
        first_match = range_matches[0]
        min_years = int(first_match[0])
        max_years = int(first_match[1])
    else:
        # No range found, look for single numbers
        # Pattern for "X+ years" or "X years of experience"
        single_patterns = [
            r'(\d+)\+\s*(?:years?|yrs?)',  # 5+ years
            r'minimum\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)',  # minimum 3 years
            r'at\s*least\s*(\d+)\s*(?:years?|yrs?)',  # at least 3 years
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',  # 3 years experience
        ]
        
        for pattern in single_patterns:
            matches = re.findall(pattern, job_lower)
            if matches:
                for match in matches:
                    val = int(match) if isinstance(match, str) else int(match[0])
                    if min_years is None or val < min_years:
                        min_years = val
                break
    
    # Default if nothing found
    if min_years is None:
        min_years = 0
    if max_years is None:
        max_years = min_years + 2
    
    # Check for seniority keywords (only if no explicit years found or to override)
    is_senior = any(word in job_lower for word in ['senior ', 'sr.', 'sr ', ' lead', 'principal', 'staff ', 'architect'])
    is_junior = any(word in job_lower for word in ['junior ', 'jr.', 'jr ', 'entry level', 'entry-level', 'fresher', 'graduate', 'trainee', 'intern '])
    
    # Senior roles need at least 5 years if not specified higher
    if is_senior and min_years < 5:
        min_years = 5
    
    # Junior roles - even if years mentioned, cap the requirement
    if is_junior:
        min_years = min(min_years, 2)
        max_years = min(max_years, 3)
    
    return {
        "min_years": min_years,
        "max_years": max_years,
        "is_senior": is_senior,
        "is_junior": is_junior,
        "has_range": len(range_matches) > 0
    }

def evaluate_experience_match(job_text: str) -> dict:
    """Evaluate if candidate's experience matches job requirement"""
    req = extract_required_experience(job_text)
    candidate_years = RESUME['total_experience_years']
    candidate_months = RESUME['total_experience_months']
    
    # For range requirements (1-3 years), check if candidate is WITHIN range
    if req['has_range']:
        if candidate_years >= req['min_years'] and candidate_years <= req['max_years']:
            return {
                "flag": "GREEN",
                "message": f"✅ Within range - Need {req['min_years']}-{req['max_years']}yr, you have {candidate_years}yr",
                "gap_months": 0
            }
        elif candidate_years > req['max_years']:
            return {
                "flag": "GREEN",
                "message": f"✅ Overqualified - Need {req['min_years']}-{req['max_years']}yr, you have {candidate_years}yr",
                "gap_months": 0
            }
        else:
            gap_months = (req['min_years'] * 12) - candidate_months
            if gap_months <= MAX_EXPERIENCE_GAP_MONTHS:
                return {
                    "flag": "YELLOW",
                    "message": f"⚠️ Slight gap - Need {req['min_years']}-{req['max_years']}yr, you have {candidate_years}yr ({gap_months}mo gap)",
                    "gap_months": gap_months
                }
            else:
                return {
                    "flag": "RED",
                    "message": f"🚫 RED FLAG - Need {req['min_years']}-{req['max_years']}yr, you have {candidate_years}yr ({gap_months}mo gap)",
                    "gap_months": gap_months
                }
    
    # Non-range requirements
    required_months = req['min_years'] * 12
    gap_months = required_months - candidate_months
    
    if req['is_junior'] or req['min_years'] <= 1:
        return {
            "flag": "GREEN",
            "message": f"✅ Perfect fit - Junior/Entry role, you have {candidate_years} years",
            "gap_months": 0
        }
    
    if gap_months <= 0:
        return {
            "flag": "GREEN",
            "message": f"✅ Experience matches - Need {req['min_years']}yr, you have {candidate_years}yr",
            "gap_months": 0
        }
    
    if gap_months <= MAX_EXPERIENCE_GAP_MONTHS:
        return {
            "flag": "YELLOW",
            "message": f"⚠️ Slight gap - Need {req['min_years']}yr, you have {candidate_years}yr ({gap_months}mo gap - acceptable)",
            "gap_months": gap_months
        }
    
    return {
        "flag": "RED",
        "message": f"🚫 RED FLAG - Need {req['min_years']}+ years, you have {candidate_years}yr ({gap_months}mo gap)",
        "gap_months": gap_months
    }

# ============================================
# SKILL MATCHING (Technical only, no soft skills)
# ============================================
def match_technical_skills(job_text: str) -> List[str]:
    """Match only technical skills, ignore soft skills"""
    job_lower = job_text.lower()
    
    # First remove soft skills from job text to avoid false matches
    for soft in SOFT_SKILLS_IGNORE:
        job_lower = job_lower.replace(soft.lower(), " ")
    
    matched = []
    for skill in TECHNICAL_SKILLS:
        skill_lower = skill.lower()
        # Check various forms of the skill
        patterns = [
            r'\b' + re.escape(skill_lower) + r'\b',
            r'\b' + re.escape(skill_lower.replace(".", "")) + r'\b',
            r'\b' + re.escape(skill_lower.replace(".js", "")) + r'\b',
        ]
        for pattern in patterns:
            if re.search(pattern, job_lower):
                # Normalize skill name for display
                display_name = skill
                if display_name not in matched:
                    matched.append(display_name)
                break
    
    return matched

# ============================================
# LLM ANALYSIS
# ============================================
async def analyze_with_llm(job_description: str, exp_eval: dict, matched_skills: List[str]) -> dict:
    """Use Groq LLM for intelligent analysis"""
    
    prompt = f"""Analyze job match. Be STRICT and HONEST.

CANDIDATE PROFILE:
- Name: {RESUME['name']}
- Experience: {RESUME['total_experience_years']} years ({RESUME['total_experience_months']} months) as Full Stack Developer
- Education: MCA (Master of Computer Applications), CGPA 7.5/10
- Technical Skills: {', '.join(TECHNICAL_SKILLS[:25])}
- Achievements: 500+ DSA problems solved

JOB DESCRIPTION:
{job_description[:2500]}

EXPERIENCE EVALUATION (pre-computed):
{exp_eval['message']}
Flag: {exp_eval['flag']}

MATCHED TECHNICAL SKILLS (pre-computed): {', '.join(matched_skills) if matched_skills else 'None'}

Return ONLY this JSON:
{{
    "match_score": <0-100>,
    "qualification_match": "<15 words: Is MCA sufficient? Specific degree needed?>",
    "skills_match": "<15 words: Technical skill overlap analysis>",
    "missing_skills": ["<max 5 TECHNICAL skills candidate LACKS - no soft skills>"],
    "action": "<20 words: If RED flag = say SKIP. Otherwise specific advice>"
}}

IMPORTANT SCORING RULES:
- If experience flag is RED: MAX score is 45
- If experience flag is YELLOW: MAX score is 70
- If experience flag is GREEN: Score based on skill match (use matched skills count)
- DO NOT count soft skills (communication, teamwork, fast learner, etc.) - ONLY technical skills
- Be realistic about technical skill gaps"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 500
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code}")
        
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        analysis = json.loads(content.strip())
        
        # Enforce score limits
        if exp_eval['flag'] == "RED" and analysis['match_score'] > 45:
            analysis['match_score'] = 45
        elif exp_eval['flag'] == "YELLOW" and analysis['match_score'] > 70:
            analysis['match_score'] = 70
            
        return analysis

def fallback_analysis(job_description: str, exp_eval: dict, matched_skills: List[str]) -> dict:
    """Fallback when API unavailable"""
    
    base_score = 35 + len(matched_skills) * 5
    
    if exp_eval['flag'] == "RED":
        base_score = min(base_score, 40)
    elif exp_eval['flag'] == "YELLOW":
        base_score = min(base_score, 65)
    
    score = min(100, max(15, base_score))
    
    return {
        "match_score": score,
        "qualification_match": "MCA degree - generally sufficient for developer roles",
        "skills_match": f"{len(matched_skills)} technical skills matched",
        "missing_skills": ["Enable API for detailed analysis"],
        "action": "SKIP - Experience gap too large" if exp_eval['flag'] == "RED" else f"Highlight: {', '.join(matched_skills[:3])}" if matched_skills else "Review job requirements"
    }

# ============================================
# API ENDPOINTS
# ============================================
@app.get("/")
def root():
    return {"status": "running", "candidate": RESUME['name'], "experience": f"{RESUME['total_experience_years']} years"}

@app.post("/score", response_model=ScoreResponse)
async def calculate_score(request: ScoreRequest):
    if not request.job_description or len(request.job_description.strip()) < 30:
        raise HTTPException(status_code=400, detail="Select more job description text")
    
    try:
        # 1. Evaluate experience match
        exp_eval = evaluate_experience_match(request.job_description)
        
        # 2. Match technical skills only
        matched_skills = match_technical_skills(request.job_description)
        
        # 3. Get LLM analysis
        try:
            analysis = await analyze_with_llm(request.job_description, exp_eval, matched_skills)
        except Exception as e:
            print(f"LLM error: {e}")
            analysis = fallback_analysis(request.job_description, exp_eval, matched_skills)
        
        score = int(analysis.get("match_score", 50))
        verdict = "APPLY" if score >= APPLY_THRESHOLD else "SKIP"
        
        if exp_eval['flag'] == "RED":
            verdict = "SKIP"
        
        return ScoreResponse(
            match_score=score,
            verdict=verdict,
            experience_match=exp_eval['message'],
            experience_flag=exp_eval['flag'],
            qualification_match=analysis.get("qualification_match", ""),
            skills_match=analysis.get("skills_match", ""),
            matched_skills=matched_skills[:8],  # Use our computed list
            missing_skills=analysis.get("missing_skills", [])[:5],
            action=analysis.get("action", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "candidate_experience_months": RESUME['total_experience_months']}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*55)
    print(f"⚡ Job Match Scorer - {RESUME['name']}")
    print(f"📊 Experience: {RESUME['total_experience_years']} years ({RESUME['total_experience_months']} months)")
    print(f"🎯 Apply threshold: {APPLY_THRESHOLD}%")
    print(f"⚠️  Max experience gap: {MAX_EXPERIENCE_GAP_MONTHS} months")
    print("="*55 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
