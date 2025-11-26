# TrackMyCareer-AI

TrackMyCareer-AI is an AI-powered career intelligence platform that analyzes resumes, identifies skill gaps, recommends suitable roles, and generates a personalized roadmap to help users reach their dream job faster.

## 🚀 Live Demo
**[Click here to use TrackMyCareer AI](https://trackmycareer-ai-1.onrender.com)**  


## Features

### 1. AI Resume Analysis
- Upload resume (PDF or text)
- Extracts:
  - Skills  
  - Education  
  - Experience  
  - Keywords  
- Generates an ATS Score (0–100)
- Detects missing skills for the selected dream role
- Computes a career readiness score  
  Example: “You are 46% away from your dream job.”

---

### 2. Dream Role Skill-Gap Breakdown
- Shows skills you already have
- Highlights skills you are missing
- Prioritizes which skills to learn first
- Provides a personalized step-by-step learning roadmap

---

### 3. Smart Role Recommendations
- Finds roles that match the user’s current skillset
- Displays match percentage for each role
- Helps users choose realistic and achievable roles

---

### 4. Modern & Premium UI
- Dark futuristic UI
- Animated 3D geometric background
- Soft gradients and smooth transitions
- Simple, distraction-free user flow

---

### 5. Outputs Provided by the Website
- Extracted resume text
- ATS score out of 100
- Skill-match percentage for dream role
- Missing skills list
- Skills user already has
- Career readiness score (“X% away from dream job”)
- Recommended roles with match %
- Personalized career roadmap
- Complete result page summarizing all insights

---

## Screenshots

### 1. Landing Page
<img width="1919" height="983" alt="Screenshot 2025-11-18 205750" src="https://github.com/user-attachments/assets/eb80ce75-b828-46a5-b763-5fe1d0eb7fab" />


### 2. Onboarding / Resume Upload Page
<img width="1848" height="940" alt="Screenshot 2025-11-18 205820" src="https://github.com/user-attachments/assets/54d2768e-ca03-4401-8469-c7b4a24fff93" />



---

## Tech Stack

### Frontend
- React.js  
- Tailwind CSS  
- Framer Motion  
- Axios  

### Backend
- FastAPI (Python)  
- Resume parser  
- Skill extractor  
- ATS score engine  
- Role recommender  

### AI
- Google Gemini API (future upgrade: model fine-tuning)

### Deployment
- GitHub  
- Vercel / Render  

---


## 📂 Folder Structure

```
TrackMyCareer-AI/
│── backend/
│   ├── main.py
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   ├── ats_matcher.py
│   ├── role_recommender.py
│   └── ai_helper.py
│
│── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   └── styles/
│   └── public/
│
└── README.md
```


---

## How It Works

1. User uploads resume  
2. Backend extracts text + skills  
3. AI processes and generates:
   - ATS score  
   - Skill gaps  
   - Matching roles  
   - Dream role readiness percentage  
4. All results returned to frontend  
5. User sees a full personalized career roadmap

---

## Roadmap
- Add AI interview preparation  
- Add skill-based learning paths  
- Add progress tracking  
- Light/dark theme toggle  
- Career dashboard with analytics  

---

## Contributing
Pull requests are welcome.  
For major changes, open an issue first to discuss the update.

---





⭐ If you like this project, consider giving it a star on GitHub!
