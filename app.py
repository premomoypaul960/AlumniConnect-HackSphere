import streamlit as st
import pandas as pd
import os
from google import genai
from streamlit_option_menu import option_menu
import time
from datetime import date

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AlumniConnect", layout="wide")

# --- CUSTOM CSS FOR MODERN UI ---
custom_css = """
<style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .viewerBadge_container {display: none !important;}
    [data-testid="stViewerBadge"] {display: none !important;}
    
    /* Make Expanders look like modern cards */
    div[data-testid="stExpander"] {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: none !important;
        margin-bottom: 10px;
    }
    
    /* Enhance the Analytics Dashboard Metrics */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #0D47A1;
    }
    
    /* Style the Primary Buttons */
    button[kind="primary"] {
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    /* Clean up the tabs */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 600 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# --- DATABASES ---
DB_FILE = "users_db.csv"
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=[
        "Email", "Password", "Name", "Role", "GradYear", "Skills", 
        "Department", "Projects", "Resume", 
        "Company", "JobRole", "Industry", "Experience"
    ])
    df.to_csv(DB_FILE, index=False)

# AUTO-MIGRATE JOBS DB (Adds new columns without breaking old data)
JOBS_DB_FILE = "jobs_db.csv"
new_job_cols = {"Job Type": "Full-time", "Eligibility": "N/A", "Required Skills": "N/A", "Deadline": str(date.today())}

if not os.path.exists(JOBS_DB_FILE):
    df_jobs = pd.DataFrame(columns=["Job Title", "Company", "Posted By (Email)", "Application Link"] + list(new_job_cols.keys()))
    df_jobs.to_csv(JOBS_DB_FILE, index=False)
else:
    df_jobs = pd.read_csv(JOBS_DB_FILE)
    changed = False
    for col, default_val in new_job_cols.items():
        if col not in df_jobs.columns:
            df_jobs[col] = default_val
            changed = True
    if changed:
        df_jobs.to_csv(JOBS_DB_FILE, index=False)

REFERRALS_DB_FILE = "referrals_db.csv"
if not os.path.exists(REFERRALS_DB_FILE):
    df_refs = pd.DataFrame(columns=["Job Title", "Applicant Name", "Applicant Email", "Alumni Email", "Status"])
    df_refs.to_csv(REFERRALS_DB_FILE, index=False)

# --- HELPER: EMAIL NOTIFICATION SIMULATOR ---
def send_mock_email(to_email, subject):
    st.toast(f"📧 Sending email to {to_email}...", icon="📨")
    time.sleep(1)
    st.success(f"**Email Notification Successfully Delivered to {to_email}**  \n*Subject: {subject}*")


# --- DYNAMIC NAVIGATION MENU ---
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.png", use_container_width=True)
        except FileNotFoundError:
            pass 

    st.markdown("<h2 style='text-align: center; color: #0D47A1; margin-top: -15px;'>NIT Jamshedpur</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>AlumniConnect</p>", unsafe_allow_html=True)
    st.write("---")

    if st.session_state.logged_in:
        user_role = st.session_state.user_info['Role']
        if user_role == 'Student':
            options = ["My Workspace", "Network Directory", "Opportunity Portal", "Resume Builder", "AI Career Assistant", "Analytics", "Logout"]
            icons = ["person-badge", "people", "briefcase", "file-earmark-text", "robot", "bar-chart", "box-arrow-left"]
        else:
            options = ["My Workspace", "Network Directory", "Opportunity Portal", "Review Referrals", "Analytics", "Logout"]
            icons = ["person-badge", "people", "briefcase", "envelope-paper", "bar-chart", "box-arrow-left"]
    else:
        options = ["Home", "Login / Register"]
        icons = ["house", "box-arrow-in-right"]

    page = option_menu(
        menu_title=None,
        options=options,
        icons=icons,
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#0D47A1", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#e0e0e0"},
            "nav-link-selected": {"background-color": "#0D47A1", "color": "white", "font-weight": "normal"},
        }
    )
    
    st.write("---")
    st.markdown("<div style='text-align: center; font-size: 13px; color: gray;'>Built for <b>HACKSPHERE</b></div>", unsafe_allow_html=True)


# --- PAGE: HOME ---
if page == "Home":
    st.title("🎓 Welcome to AlumniConnect")
    st.markdown("### The Official Network for NIT Jamshedpur")
    st.write("Connect, grow, and succeed together. AlumniConnect bridges the gap between current students and successful alumni, creating a closed-loop ecosystem for referrals and mentorship.")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.info("#### For Students\n* 🔍 **Discover Alumni:** Find mentors in your target industry.\n* 💼 **Get Referrals:** Apply for exclusive job opportunities.\n* 🤖 **AI Career Assistant:** Optimize your resume instantly.")
    with col2:
        st.success("#### For Alumni\n* 🤝 **Give Back:** Guide the next generation of engineers.\n* 📢 **Post Opportunities:** Share jobs and referrals directly.\n* 🏆 **Climb the Leaderboard:** Earn points for your contributions.")


# --- PAGE: AUTHENTICATION ---
elif page == "Login / Register":
    st.title("🔐 Access Portal")
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    with tab1:
        st.subheader("Login to your Workspace")
        login_email = st.text_input("College Email ID")
        login_pass = st.text_input("Password", type="password")
        if st.button("Secure Login", use_container_width=True):
            df = pd.read_csv(DB_FILE)
            user = df[(df["Email"] == login_email) & (df["Password"] == login_pass)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_info = user.iloc[0].to_dict()
                st.rerun() 
            else:
                st.error("Invalid email or password.")
                
    with tab2:
        st.subheader("Register New Profile")
        department, projects, resume, company, job_role, industry, experience = "", "", "", "", "", "", ""
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Official College Email ID", key="reg_email")
            password = st.text_input("Create Password", type="password", key="reg_pass")
            name = st.text_input("Full Name")
        with col2:
            skills = st.text_input("Top Skills (comma-separated)")
            grad_year = st.number_input("Graduation Year", min_value=2000, max_value=2030, value=2026)
        
        st.write("---")
        current_year = 2026
        role = "Student" if grad_year > current_year else "Alumni"
        
        if role == "Student":
            col3, col4 = st.columns(2)
            with col3:
                department = st.text_input("Department")
                projects = st.text_input("Key Projects")
            with col4:
                resume = st.text_input("Resume Link")
        else:
            col3, col4 = st.columns(2)
            with col3:
                company = st.text_input("Current Company")
                job_role = st.text_input("Job Role")
            with col4:
                industry = st.text_input("Industry")
                experience = st.text_input("Years of Experience")
        
        st.write("---")
        if st.button("🚀 Register Profile", use_container_width=True):
            if "@" not in email or password == "":
                st.error("Please provide a valid email and password!")
            else:
                new_user = pd.DataFrame([[email, password, name, role, grad_year, skills, department, projects, resume, company, job_role, industry, experience]], columns=pd.read_csv(DB_FILE).columns)
                df_existing = pd.read_csv(DB_FILE)
                pd.concat([df_existing, new_user], ignore_index=True).to_csv(DB_FILE, index=False)
                st.success(f"🎉 Successfully registered as a **{role}**! Head to the Login tab.")


# --- PAGE: MY WORKSPACE ---
elif page == "My Workspace":
    user = st.session_state.user_info
    badge = "✅ Verified Alumni" if user['Role'] == 'Alumni' else "🎓 Student Profile"
    
    st.markdown(f"""
        <div style="background-color:#0D47A1;padding:20px;border-radius:10px;margin-bottom:20px;">
            <h1 style="color:white;margin:0;">{user['Name']}</h1>
            <h4 style="color:#E0E0E0;margin:0;">{badge} • Class of {user['GradYear']}</h4>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("### Contact & Core")
        st.info(f"📧 **Email:** {user['Email']}")
        st.info(f"🛠️ **Skills:** {user['Skills']}")
    with col2:
        if user['Role'] == 'Student':
            st.write("### 🎓 Academic Profile")
            st.success(f"**Department:** {user['Department']}")
            st.success(f"**Key Projects:** {user['Projects']}")
            st.success(f"**Resume Link:** {user['Resume']}")
        else:
            st.write("### 💼 Professional Profile")
            st.success(f"**Company:** {user['Company']}")
            st.success(f"**Job Role:** {user['JobRole']}")
            st.success(f"**Industry:** {user['Industry']}")
            st.success(f"**Experience:** {user['Experience']}")

    st.write("---")
    with st.expander("✏️ Manage & Update Profile"):
        new_skills = st.text_input("Update Skills", value=user['Skills'])
        if user['Role'] == 'Student':
            new_proj = st.text_input("Update Projects", value=user['Projects'])
            new_res = st.text_input("Update Resume Link", value=user['Resume'])
        else:
            new_comp = st.text_input("Update Company", value=user['Company'])
            new_role = st.text_input("Update Job Role", value=user['JobRole'])

        if st.button("Save Changes"):
            df = pd.read_csv(DB_FILE)
            idx = df.index[df['Email'] == user['Email']].tolist()[0]
            df.at[idx, 'Skills'] = new_skills
            if user['Role'] == 'Student':
                df.at[idx, 'Projects'] = new_proj
                df.at[idx, 'Resume'] = new_res
            else:
                df.at[idx, 'Company'] = new_comp
                df.at[idx, 'JobRole'] = new_role
            df.to_csv(DB_FILE, index=False)
            st.session_state.user_info = df.iloc[idx].to_dict()
            st.success("Profile updated successfully!")
            st.rerun()
            
    # FEATURE RESTORED: ACCOUNT DELETION
    st.write("---")
    with st.expander("⚠️ Danger Zone: Delete Account"):
        st.warning("Deleting your account is permanent. It will instantly remove your profile, job postings, and referral requests from the platform.")
        delete_confirm = st.text_input("Type 'DELETE' to confirm:")
        
        if st.button("🗑️ Permanently Delete My Account"):
            if delete_confirm == "DELETE":
                user_email = user['Email']
                
                # 1. Remove user from users database
                df_users = pd.read_csv(DB_FILE)
                df_users = df_users[df_users['Email'] != user_email]
                df_users.to_csv(DB_FILE, index=False)
                
                # 2. Cascade delete: Remove any jobs posted by this user
                df_jobs = pd.read_csv(JOBS_DB_FILE)
                df_jobs = df_jobs[df_jobs['Posted By (Email)'] != user_email]
                df_jobs.to_csv(JOBS_DB_FILE, index=False)
                
                # 3. Cascade delete: Remove any referrals made BY or TO this user
                df_refs = pd.read_csv(REFERRALS_DB_FILE)
                df_refs = df_refs[(df_refs['Applicant Email'] != user_email) & (df_refs['Alumni Email'] != user_email)]
                df_refs.to_csv(REFERRALS_DB_FILE, index=False)
                
                # 4. Log out and refresh
                st.session_state.logged_in = False
                st.session_state.user_info = None
                st.rerun()
            else:
                st.error("Please type 'DELETE' exactly as shown to confirm.")


# --- PAGE: LOGOUT ---
elif page == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()


# --- PAGE: NETWORK DIRECTORY ---
elif page == "Network Directory":
    st.title("🌐 Network Directory")
    df = pd.read_csv(DB_FILE)
    tab1, tab2, tab3 = st.tabs(["💼 Alumni Profiles", "🎓 Student Profiles", "🏆 Top Contributors"])
    
    with tab1:
        search_alumni = st.text_input("Search Alumni by Name, Company, or Skill:")
        alumni_df = df[df["Role"] == "Alumni"]
        if search_alumni:
            mask = alumni_df.apply(lambda row: row.astype(str).str.contains(search_alumni, case=False).any(), axis=1)
            alumni_df = alumni_df[mask]
        
        for index, row in alumni_df.iterrows():
            with st.expander(f"👤 {row['Name']} ✅ | {row['JobRole']} at {row['Company']}"):
                colA, colB = st.columns(2)
                with colA:
                    st.write(f"**Email:** {row['Email']}")
                    st.write(f"**Class of:** {row['GradYear']}")
                with colB:
                    st.write(f"**Industry:** {row['Industry']}")
                    st.write(f"**Experience:** {row['Experience']}")
                st.write(f"**Core Skills:** {row['Skills']}")

    with tab2:
        search_students = st.text_input("Search Students by Name, Department, or Skill:")
        student_df = df[df["Role"] == "Student"]
        if search_students:
            mask = student_df.apply(lambda row: row.astype(str).str.contains(search_students, case=False).any(), axis=1)
            student_df = student_df[mask]
        for index, row in student_df.iterrows():
            with st.expander(f"🎓 {row['Name']} | {row['Department']}"):
                colA, colB = st.columns(2)
                with colA:
                    st.write(f"**Email:** {row['Email']}")
                    st.write(f"**Core Skills:** {row['Skills']}")
                with colB:
                    st.write(f"**Key Projects:** {row['Projects']}")
                    st.write(f"**Resume Link:** {row['Resume']}")
                    
    with tab3:
        st.markdown("🥇 **Top Alumni Leaderboard**")
        jobs_df = pd.read_csv(JOBS_DB_FILE)
        if not jobs_df.empty:
            contribution_counts = jobs_df["Posted By (Email)"].value_counts().reset_index()
            contribution_counts.columns = ["Email", "Jobs Posted"]
            contribution_counts["Points"] = contribution_counts["Jobs Posted"] * 10
            leaderboard = pd.merge(contribution_counts, df[["Email", "Name"]], on="Email", how="left")
            for index, row in leaderboard.iterrows():
                st.success(f"{index+1}. **{row['Name']}** - {row['Points']} Points ({row['Jobs Posted']} Jobs)")


# --- PAGE: ANALYTICS DASHBOARD ---
elif page == "Analytics":
    st.title("📈 Placement & Network Analytics")
    st.write("Live insights into the AlumniConnect ecosystem.")
    
    df = pd.read_csv(DB_FILE)
    alumni_df = df[df['Role'] == 'Alumni']
    student_df = df[df['Role'] == 'Student']
    jobs_df = pd.read_csv(JOBS_DB_FILE)
    refs_df = pd.read_csv(REFERRALS_DB_FILE)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Alumni", len(alumni_df))
    col2.metric("Total Students", len(student_df))
    col3.metric("Live Opportunities", len(jobs_df))
    col4.metric("Referrals Processed", len(refs_df[refs_df['Status'] != 'Pending']))

    st.write("---")
    colA, colB = st.columns(2)
    
    with colA:
        st.write("### 🏢 Alumni Distribution by Industry")
        if not alumni_df.empty:
            st.bar_chart(alumni_df['Industry'].value_counts())
            
    with colB:
        st.write("### 💻 Student Distribution by Department")
        if not student_df.empty:
            st.bar_chart(student_df['Department'].value_counts())


# --- PAGE: RESUME BUILDER (STUDENT ONLY) ---
elif page == "Resume Builder":
    st.title("📄 Auto-Resume Builder")
    st.write("Generate a clean, text-based resume instantly using your profile data.")
    user = st.session_state.user_info
    
    st.write("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**Add Extra Details**")
        phone = st.text_input("Phone Number")
        github = st.text_input("GitHub Profile Link")
        linkedin = st.text_input("LinkedIn Profile Link")
        bio = st.text_area("Professional Summary")
        
    with col2:
        st.markdown("### 👁️ Resume Preview")
        resume_markdown = f"""
# {user['Name']}
📧 {user['Email']} | 📱 {phone}
🔗 [GitHub]({github}) | 🔗 [LinkedIn]({linkedin})

---

### **PROFESSIONAL SUMMARY**
{bio}

### **EDUCATION**
**NIT Jamshedpur**
*B.Tech in {user['Department']}* | Expected Graduation: {user['GradYear']}

### **TECHNICAL SKILLS**
* {user['Skills']}

### **KEY PROJECTS**
* {user['Projects']}

### **LINKS**
* Portfolio/Resume: {user['Resume']}
        """
        st.markdown(f"<div style='border: 1px solid gray; padding: 20px; border-radius: 5px; background-color: white; color: black;'>{resume_markdown}</div>", unsafe_allow_html=True)
        

# --- PAGE: AI CAREER ASSISTANT ---
elif page == "AI Career Assistant":
    st.title("🤖 AI Career Assistant")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.write("---")
    student_resume = st.text_area("Paste your current skills or resume text here:", value=st.session_state.user_info['Skills'])
    target_role = st.text_input("What job role or company are you targeting?")
    
    if st.button("Generate Resume Optimization & Referral Message"):
        if not api_key:
            st.error("Please enter your API Key first!")
        elif not student_resume or not target_role:
            st.warning("Please fill in your skills and target role.")
        else:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""I am a student with these skills: {student_resume}. I want to apply for a {target_role} role. 
                1. Give me a brief skill gap analysis. 
                2. Write a short referral request message I can send to an alumni."""
                with st.spinner("Analyzing profile..."):
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")


# --- PAGE: OPPORTUNITY PORTAL (PRIORITY RANKING ALGORITHM) ---
elif page == "Opportunity Portal":
    st.title("💼 Referral & Opportunity Portal")
    
    users_df = pd.read_csv(DB_FILE)
    jobs_df = pd.read_csv(JOBS_DB_FILE)
    
    # 1. ALUMNI POSTING INTERFACE
    if st.session_state.user_info['Role'] == 'Alumni':
        with st.expander("📌 Post a New Opportunity"):
            job_title = st.text_input("Job Title")
            job_type = st.selectbox("Job Type", ["Full-time", "Internship", "Referral Opportunity"])
            job_company = st.text_input("Company", value=st.session_state.user_info['Company'])
            
            col_req1, col_req2 = st.columns(2)
            with col_req1:
                eligibility = st.text_input("Eligibility (e.g., 2026 Batch, B.Tech CSE)")
                deadline = st.date_input("Application Deadline")
            with col_req2:
                req_skills = st.text_input("Required Skills")
                app_link = st.text_input("Application or Referral Link")
                
            posted_by = st.text_input("Your Email", value=st.session_state.user_info['Email'], disabled=True)
            
            if st.button("Post Job"):
                if job_title and job_company:
                    new_job = pd.DataFrame([[job_title, job_company, posted_by, app_link, job_type, eligibility, req_skills, str(deadline)]], columns=jobs_df.columns)
                    pd.concat([jobs_df, new_job], ignore_index=True).to_csv(JOBS_DB_FILE, index=False)
                    st.success("Opportunity posted successfully! You earned Contribution Points.")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields.")
    
    # 2. ALGORITHMIC JOB SORTING & DISPLAY
    st.write("### Current Openings")
    if not jobs_df.empty:
        refs_df_for_stats = pd.read_csv(REFERRALS_DB_FILE)
        
        stats = []
        for email in jobs_df['Posted By (Email)'].unique():
            user_match = users_df[users_df['Email'] == email]
            seniority = (2026 - user_match['GradYear'].values[0]) if not user_match.empty else 0
            contrib = len(jobs_df[jobs_df['Posted By (Email)'] == email]) * 10
            
            alumni_refs = refs_df_for_stats[refs_df_for_stats['Alumni Email'] == email]
            success_rate = (len(alumni_refs[alumni_refs['Status'] == 'Referred']) / len(alumni_refs) * 100) if not alumni_refs.empty else 0.0
            
            stats.append({'Posted By (Email)': email, 'Seniority': seniority, 'Contrib': contrib, 'SuccessRate': success_rate})
        
        stats_df = pd.DataFrame(stats)
        ranked_jobs = pd.merge(jobs_df.reset_index(), stats_df, on='Posted By (Email)', how='left')
        
        ranked_jobs = ranked_jobs.sort_values(
            by=['Company', 'Job Title', 'Seniority', 'SuccessRate', 'Contrib'], 
            ascending=[True, True, False, False, False]
        )
        
        for _, row in ranked_jobs.iterrows():
            original_index = row['index']
            
            badge_html = f"<span style='color: #2e7d32; font-weight: bold;'>[🏅 Prioritized Referrer: {row['SuccessRate']:.0f}% Success Rate]</span>" if row['SuccessRate'] > 0 else ""
            
            st.markdown(f"""
            <div style='border: 1px solid #e0e0e0; padding: 15px; border-radius: 8px; margin-bottom: 10px; background-color: #f9fbfd;'>
                <h4 style='margin-bottom: 5px; color: #0D47A1;'>{row['Job Title']} ({row['Job Type']}) @ {row['Company']}</h4>
                <p style='margin: 0; font-size: 14px; color: #333;'>
                    <b>Eligibility:</b> {row['Eligibility']} | <b>Skills required:</b> {row['Required Skills']} <br>
                    <b>Deadline:</b> {row['Deadline']} | <a href="{row['Application Link']}" target="_blank">External Link</a>
                </p>
                <p style='margin-top: 8px; font-size: 13px; color: gray;'>
                    Posted by: {row['Posted By (Email)']} {badge_html}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.user_info['Role'] == 'Student':
                if st.button(f"Request Referral for {row['Job Title']}", key=f"req_{original_index}"):
                    refs_df = pd.read_csv(REFERRALS_DB_FILE)
                    new_ref = pd.DataFrame([[row['Job Title'], st.session_state.user_info['Name'], st.session_state.user_info['Email'], row['Posted By (Email)'], "Pending"]], columns=refs_df.columns)
                    pd.concat([refs_df, new_ref], ignore_index=True).to_csv(REFERRALS_DB_FILE, index=False)
                    st.success(f"Referral request sent to {row['Posted By (Email)']}!")
                    
            # FEATURE RESTORED: MANUAL JOB DELETION
            elif st.session_state.user_info['Role'] == 'Alumni' and row['Posted By (Email)'] == st.session_state.user_info['Email']:
                if st.button("🗑️ Delete Opportunity", key=f"del_{original_index}"):
                    jobs_df.drop(original_index).to_csv(JOBS_DB_FILE, index=False)
                    st.success("Opportunity removed from the portal.")
                    st.rerun()
    else:
        st.info("No opportunities posted yet.")

    # 3. REFERRAL TRACKING DASHBOARD
    if st.session_state.user_info['Role'] == 'Student':
        st.write("---")
        st.write("### 📍 Referral Tracking Dashboard")
        refs_df = pd.read_csv(REFERRALS_DB_FILE)
        my_apps = refs_df[refs_df["Applicant Email"] == st.session_state.user_info['Email']]
        
        if not my_apps.empty:
            for index, row in my_apps.iterrows():
                if row['Status'] == 'Pending':
                    st.warning(f"**{row['Job Title']}** (Sent to {row['Alumni Email']}) - ⏳ PENDING REVIEW")
                    st.progress(33)
                elif row['Status'] == 'Referred':
                    st.success(f"**{row['Job Title']}** (Sent to {row['Alumni Email']}) - ✅ SUCCESSFULLY REFERRED")
                    st.progress(100)
                else:
                    st.error(f"**{row['Job Title']}** (Sent to {row['Alumni Email']}) - ❌ DECLINED")
        else:
            st.info("You haven't requested any referrals yet.")


# --- PAGE: REVIEW REFERRALS (ALUMNI ONLY) ---
elif page == "Review Referrals":
    st.title("📥 Manage Referral Requests")
    
    refs_df = pd.read_csv(REFERRALS_DB_FILE)
    users_df = pd.read_csv(DB_FILE)
    my_requests = refs_df[refs_df["Alumni Email"] == st.session_state.user_info['Email']]
    
    if not my_requests.empty:
        for index, row in my_requests.iterrows():
            with st.expander(f"{row['Applicant Name']} - {row['Job Title']} | Status: {row['Status']}"):
                student_match = users_df[users_df["Email"] == row['Applicant Email']]
                if not student_match.empty:
                    student_info = student_match.iloc[0]
                    colA, colB = st.columns(2)
                    with colA:
                        st.write(f"**Applicant:** {student_info['Name']}")
                        st.write(f"**Email:** {student_info['Email']}")
                    with colB:
                        st.write(f"**Skills:** {student_info['Skills']}")
                        st.write(f"**Resume Link:** {student_info['Resume']}")
                
                if row['Status'] == 'Pending':
                    st.write("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Accept & Refer", key=f"acc_{index}", use_container_width=True):
                            actual_index = my_requests.index[my_requests.index == index].tolist()[0]
                            refs_df.at[actual_index, 'Status'] = 'Referred'
                            refs_df.to_csv(REFERRALS_DB_FILE, index=False)
                            
                            # FEATURE RESTORED: AUTO-DELETE JOB UPON ACCEPTANCE
                            jobs_df = pd.read_csv(JOBS_DB_FILE)
                            mask = (jobs_df['Job Title'] == row['Job Title']) & (jobs_df['Posted By (Email)'] == st.session_state.user_info['Email'])
                            jobs_df[~mask].to_csv(JOBS_DB_FILE, index=False)
                            
                            send_mock_email(to_email=row['Applicant Email'], subject=f"Great News! Your referral for {row['Job Title']} was accepted!")
                            time.sleep(2) 
                            st.rerun()
                            
                    with col2:
                        if st.button("❌ Decline", key=f"dec_{index}", use_container_width=True):
                            actual_index = my_requests.index[my_requests.index == index].tolist()[0]
                            refs_df.at[actual_index, 'Status'] = 'Declined'
                            refs_df.to_csv(REFERRALS_DB_FILE, index=False)
                            
                            send_mock_email(to_email=row['Applicant Email'], subject=f"Update on your referral request for {row['Job Title']}")
                            time.sleep(2)
                            st.rerun()
    else:
        st.info("You have no pending referral requests at the moment.")
