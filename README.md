# ⚡ Job Match Scorer - Chrome Extension

A Chrome extension that analyzes job descriptions and tells you whether to **APPLY** or **SKIP** based on your resume match. Uses AI (Groq's Llama 3.1) for intelligent analysis.

![Score Example](https://img.shields.io/badge/Match-75%25-green) ![Verdict](https://img.shields.io/badge/Verdict-APPLY-brightgreen)

## ✨ Features

- 🎯 **Instant Match Score** - Get 0-100% match score
- ✅ **Clear Verdict** - APPLY (≥60%) or SKIP (<60%)
- 📅 **Experience Check** - Flags if you're under/overqualified
- 💻 **Skills Analysis** - Shows matched & missing technical skills
- 🚫 **Smart Filtering** - Ignores soft skills, only counts real tech skills
- 💡 **Action Advice** - What to highlight or why to skip

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Get Free Groq API Key

1. Go to **[https://console.groq.com/keys](https://console.groq.com/keys)**
2. Sign up / Login (free)
3. Click **"Create API Key"**
4. Copy your API key (starts with `gsk_...`)

### Step 2: Setup Backend

#### Option A: Using Environment Variable (Recommended)

1. Create a `.env` file in the `product` folder:
```
GROQ_API_KEY=gsk_your_api_key_here
```

2. Install dependencies:
```bash
pip install fastapi uvicorn httpx python-dotenv
```

3. Run the server:
```bash
python main.py
```

#### Option B: Hardcode API Key

1. Open `main.py`
2. Find this line (around line 28):
```python
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```
3. Replace with:
```python
GROQ_API_KEY = "gsk_your_api_key_here"
```
4. Run: `python main.py`

You should see:
```
⚡ Job Match Scorer - Your Name
📊 Experience: X.X years
🎯 Apply threshold: 60%
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Add Your Resume

1. Open `main.py`
2. Find the `RESUME = {` section (around line 55)
3. Update with YOUR information:

```python
RESUME = {
    "name": "Your Full Name",
    "email": "your.email@example.com",
    "phone": "+1 234 567 8900",
    "linkedin": "linkedin.com/in/yourprofile",
    "github": "github.com/yourusername",
    
    "title": "Your Job Title",  # e.g., "Software Engineer", "Data Scientist"
    "total_experience_months": 24,  # Your total experience in MONTHS
    "total_experience_years": 2.0,  # Same in years (for display)
    
    "education": {
        "degree": "Your Degree",  # e.g., "B.Tech Computer Science"
        "institution": "Your University",
        "cgpa": "8.5/10",  # or "3.5/4.0"
        "duration": "2018 - 2022"
    },
    
    # ADD YOUR TECHNICAL SKILLS HERE
    # Only add skills you actually know - these are matched against job descriptions
    "technical_skills": [
        # Languages
        "Python", "JavaScript", "Java", "SQL",
        # Frameworks
        "React", "Node.js", "Django", "Spring Boot",
        # Databases
        "PostgreSQL", "MongoDB", "MySQL", "Redis",
        # Cloud
        "AWS", "Docker", "Kubernetes", "GCP",
        # Tools
        "Git", "Jenkins", "Terraform",
        # Add more of YOUR skills...
    ],
    
    "experience": [
        {
            "title": "Your Job Title",
            "company": "Company Name",
            "duration": "Jan 2023 - Present",
            "months": 12,  # Duration in months
            "tech": ["React", "Node.js", "PostgreSQL"]  # Tech used
        },
        # Add more jobs...
    ],
    
    "achievements": [
        "Your achievement 1",
        "Your achievement 2"
    ]
}
```

### Step 4: Load Chrome Extension

1. Open Chrome and go to: `chrome://extensions/`
2. Enable **"Developer mode"** (toggle in top-right corner)
3. Click **"Load unpacked"**
4. Select the `frontend` folder from this project
5. The extension icon ⚡ should appear in your toolbar

---

## 📖 How to Use

1. **Start the backend** (keep it running):
   ```bash
   python main.py
   ```

2. **Go to any job posting** (LinkedIn, Indeed, Glassdoor, etc.)

3. **Select the job description text** with your mouse
   - Select requirements, qualifications, responsibilities sections
   - The more text, the better analysis

4. **Click the extension icon** or use the floating **⚡ Check Match** button

5. **View your results**:
   - **Score**: 0-100% match
   - **Verdict**: APPLY ✅ or SKIP ❌
   - **Experience**: GREEN/YELLOW/RED flag
   - **Skills**: What you have vs what's missing
   - **Action**: What to do next

---

## 🎯 Understanding the Results

### Score Thresholds
| Score | Verdict | Meaning |
|-------|---------|---------|
| 60-100% | **APPLY** ✅ | Good match, worth applying |
| 0-59% | **SKIP** ❌ | Poor match, save your time |

### Experience Flags
| Flag | Meaning |
|------|---------|
| 🟢 **GREEN** | Your experience matches or exceeds requirement |
| 🟡 **YELLOW** | Slight gap (≤6 months) - still worth trying |
| 🔴 **RED** | Large gap (>6 months) - auto-SKIP |

### Experience Examples (if you have 1.5 years)
- Job needs "1-3 years" → **GREEN** ✅ (you're within range)
- Job needs "2 years" → **YELLOW** ⚠️ (6 month gap, acceptable)
- Job needs "3+ years" → **RED** 🚫 (18 month gap, too big)
- Job says "Senior" → **RED** 🚫 (senior = 5+ years usually)

---

## 🛠️ Project Structure

```
product/
├── main.py              # Backend API (FastAPI)
├── .env                 # Your API key (create this)
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── frontend/            # Chrome extension
    ├── manifest.json    # Extension config
    ├── popup.html       # Extension popup UI
    ├── popup.js         # Popup logic
    ├── content.js       # Floating button on pages
    └── background.js    # API communication
```

---

## 📋 Requirements

- Python 3.8+
- Google Chrome browser
- Free Groq API key

### Python Packages
```bash
pip install fastapi uvicorn httpx python-dotenv
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

---

## ❓ Troubleshooting

### "Cannot connect to server"
- Make sure `python main.py` is running
- Check it's on `http://localhost:8000`

### "GROQ_API_KEY not set"
- Create `.env` file with your key
- Or hardcode it in `main.py`

### Extension not working
- Reload extension in `chrome://extensions/`
- Check if backend is running
- Try selecting more text

### Score seems wrong
- Select more job description text
- Make sure your skills in `main.py` match what you know
- Update your experience months accurately

---

## 🔒 Privacy

- Your resume stays LOCAL (in `main.py`)
- Job text is sent to Groq API for analysis
- No data is stored or logged
- API key is only used for Groq calls

---

## 📄 License

MIT License - Free to use and modify

---

## 🤝 Contributing

1. Fork the repo
2. Make your changes
3. Submit a pull request

---

**Made with ❤️ to save time on job applications**

