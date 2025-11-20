# TrackMyCareer-AI

TrackMyCareer-AI is an **AI-powered career guidance platform** that analyzes resumes, identifies skill gaps, recommends suitable roles, and provides a personalized roadmap to help users reach their dream job faster.

🌐 **Live Demo Coming Soon**

---

## 🚀 Features

### **1. AI Resume Analysis**
- Upload your resume (PDF/text)
- Extracts skills, experience, and keywords
- Computes your **ATS score** out of 100  
- Identifies **missing skills** for your selected dream role  
- Tells you **how far you are from your dream job** (e.g., “You are 46% away from your goal”)

### **2. Smart Role Recommendations**
- Recommends roles based on your current skillset
- Shows how well you match each role

### **3. Dream Role Skill Gap Breakdown**
- Highlights skills you already have
- Highlights skills you need to learn
- Suggests what to learn next

### **4. Beautiful, Modern UI**
- Dark, futuristic theme  
- Animated 3D geometric background  
- Smooth, premium transitions  

---

## 📸 Screenshots

### **1️⃣ Landing Page**
![Landing Page](/mnt/data/Screenshot 2025-11-18 205750.png)

---

### **2️⃣ Onboarding / Resume Upload Page**
![Onboarding Page](/mnt/data/Screenshot 2025-11-18 205820.png)

---

## 🛠️ Tech Stack

### **Frontend**
- React.js
- Tailwind CSS
- Framer Motion (animations)
- Axios

### **Backend**
- FastAPI (Python)
- Resume parsing module  
- Skill extraction with AI  
- ATS score calculator  
- Role recommender

### **AI**
- Google Gemini API (future upgrade: LLM fine‑tuning)

### **DevOps**
- GitHub
- Render / Vercel (deployment)

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

## 🧠 How It Works

1. User uploads resume  
2. Backend extracts text + skills  
3. AI analyzes and computes:
   - ATS score  
   - Skill gaps  
   - Matching roles  
   - Dream role readiness (%)  
4. Results returned to frontend  
5. User gets a complete **career roadmap**

---

## 🛣️ Roadmap

- [ ] Add AI interview preparation  
- [ ] Add skill‑based learning paths  
- [ ] Store user history & track progress  
- [ ] Add dark/light theme toggle  
- [ ] Add dashboard analytics  

---

## 🤝 Contributing

Pull requests are welcome!  
For major changes, open an issue first to discuss what you’d like to change.

---

## 📧 Contact

For queries or collaborations:  
**Sarayu Tallady**  
Developer & Creator, TrackMyCareer-AI  

---

⭐ If you like this project, consider giving it a star on GitHub!
