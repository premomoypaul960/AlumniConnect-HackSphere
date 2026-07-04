# 🎓 AlumniConnect 

**The Official Opportunity & Referral Network for NIT Jamshedpur**  
*Built for the Hacksphere Hackathon*

---

## 🚀 Overview

AlumniConnect is a closed-loop, intelligent web application designed to bridge the gap between ambitious students and established alumni. Instead of getting lost in the noise of massive platforms like LinkedIn, students can request direct, verified job referrals from alumni who actually want to hire from their alma mater. 

This platform moves beyond a simple job board by introducing a **Priority Ranking Algorithm** that dynamically sorts opportunities based on an alum's reliability, seniority, and contribution history, creating a high-trust ecosystem.

## ✨ Key Features

### 👨‍🎓 For Students
* **Live Opportunity Portal:** Browse internships and full-time roles posted directly by alumni.
* **Referral Tracking Dashboard:** Track the real-time status of your referral requests (Pending, Accepted, Declined).
* **AI Career Assistant:** Powered by Google Gemini 2.5 Flash, get instant skill-gap analysis and auto-generated cover letters based on your profile.
* **Auto-Resume Builder:** Instantly generate a clean, markdown-formatted resume using your saved academic and project data.

### 💼 For Alumni
* **Opportunity Posting:** Post exclusive roles and referral opportunities for current students.
* **Referral Management:** Review applicant skills and resumes in one click, and accept or decline requests.
* **Gamified Leaderboard:** Earn Contribution Points for every job posted and climb the top contributors leaderboard.
* **Smart Auto-Deletion:** Once a referral is accepted, the specific job posting is automatically closed and removed from the portal.

### 🧠 The Algorithm (Algorithmic Job Sorting)
To ensure students apply to the most reliable opportunities, the portal does not just list jobs chronologically. It uses a Pandas-driven algorithm to dynamically rank identical job postings based on:
1. **Referral Success Rate:** Alumni who frequently accept requests rank higher.
2. **Seniority:** Calculated by graduation year.
3. **Contribution Score:** Total jobs posted on the platform.

## 🛠️ Tech Stack
* **Language:** Python
* **Framework:** Streamlit
* **Data Processing & Logic:** Pandas 
* **AI Integration:** Google Gemini API 
* **UI/UX:** Custom HTML & CSS (Keyframe animations, modern card layouts, hover states)
* **Database:** Local CSV state management (`users_db.csv`, `jobs_db.csv`, `referrals_db.csv`)

## 💻 How to Run Locally

If you want to run this project on your local machine, follow these steps:

**1. Clone the repository**
`git clone https://github.com/YOUR_GITHUB_USERNAME/alumniconnect-hacksphere.git`
`cd alumniconnect-hacksphere`

**2. Install dependencies**
Make sure you have Python installed, then run:
`pip install streamlit pandas google-genai streamlit-option-menu`

**3. Run the application**
`streamlit run app.py`

## 👨‍💻 Author
**Premomoy**  
Electrical Engineering Student | NIT Jamshedpur
