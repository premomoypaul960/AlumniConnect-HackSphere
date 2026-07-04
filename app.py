import streamlit as st
import pandas as pd
import os
from google import genai
from streamlit_option_menu import option_menu

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AlumniConnect", layout="wide")

# --- CUSTOM CSS TO HIDE STREAMLIT BRANDING & CLOUD BADGE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            .viewerBadge_container {display: none !important;}
            .viewerBadge_link {display: none !important;}
            [data-testid="stViewerBadge"] {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- SESSION STATE (LOGIN MEMORY) ---
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

JOBS_DB_FILE = "jobs_db.csv"
if not os.path.exists(JOBS_DB_FILE):
    df_jobs = pd.DataFrame(columns=["Job Title", "Company", "Posted By (Email)", "Application Link"])
    df_jobs.to_csv(JOBS_DB_FILE, index=False)

REFERRALS_DB_FILE = "referrals_db.csv"
if not os.path.exists(REFERRALS_DB_FILE):
    df_refs = pd.DataFrame(columns=["Job Title", "Applicant Name", "Applicant Email", "Alumni Email", "Status"])
    df_refs.to_csv(REFERRALS_DB_FILE, index=False)


# --- DYNAMIC NAVIGATION MENU WITH SECURITY RULES ---
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.png", use_container_width=True)
        except FileNotFoundError:
            pass 

    st.markdown("<h2 style='text-align: center; color: #0D47A1; margin-top: -15px;'>NIT Jamshedpur</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>AlumniConnect Portal</p>", unsafe_allow_html=True)
    st.write("---")

    if st.session_state.logged_in:
        user_role = st.session_state.user_info['Role']
        
        if user_role == 'Student':
            options = ["My Workspace", "Network Directory", "AI Career Assistant", "Opportunity Portal", "Logout"]
            icons = ["person-badge", "people", "robot", "briefcase", "box-arrow-left"]
        else:
            options = ["My Workspace", "Network Directory", "Opportunity Portal", "Review Referrals", "Logout"]
            icons = ["person-badge", "people", "briefcase", "envelope-paper", "box-arrow-left"]
    else:
        options = ["Login / Register"]
        icons = ["box-arrow-in-right"]

    page = option_menu(
        menu_title=None,
        options=options,
        icons=icons,
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#0D47A1", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#e0e0e0"},
            "nav-link-selected": {"background-color": "#0D47A1", "color": "white", "font-weight": "normal"},
        }
    )
    
    st.write("---")
    st.markdown("<div style='text-align: center; font-size: 13px; color: gray;'>Built for <b>HACKSPHERE</b><br>Code. Create. Conquer.</div>", unsafe_allow_html=True)


# --- PAGE 0: AUTHENTICATION ---
if page == "Login / Register":
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
                new_user = pd.DataFrame([[
                    email, password, name, role, grad_year, skills, 
                    department, projects, resume, company, job_role, industry, experience
                ]], columns=pd.read_csv(DB_FILE).columns)
                
                df_existing = pd.read_csv(DB_FILE)
                df_updated = pd.concat([df_existing, new_user], ignore_index=True)
                df_updated.to_csv(DB_FILE, index=False)
                st.success(f"🎉 Successfully registered as a **{role}**! Head to the Login tab.")


# --- PAGE 1: MY WORKSPACE (MANAGE PROFILE) ---
elif page == "My Workspace":
    user = st.session_state.user_info
    
    st.markdown(f"""
        <div style="background-color:#0D47A1;padding:20px;border-radius:10px;margin-bottom:20px;">
            <h1 style="color:white;margin:0;">{user['Name']}</h1>
            <h4 style="color:#E0E0E0;margin:0;">{user['Role']} Profile • Class of {user['GradYear']}</h4>
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
        st.write("Update your details below.")
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


# --- LOGOUT LOGIC ---
elif page == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()


# --- PAGE 2: NETWORK DIRECTORY ---
elif page == "Network Directory":
    st.title("🌐 Network Directory")
    st.markdown("Discover and connect with verified Alumni and Students.")
    
    df = pd.read_csv(DB_FILE)
    
    tab1, tab2, tab3 = st.tabs(["💼 Alumni Profiles", "🎓 Student Profiles", "🏆 Top Contributors"])
    
    with tab1:
        search_alumni = st.text_input("Search Alumni by Name, Company, or Skill:")
        alumni_df = df[df["Role"] == "Alumni"]
        
        if search_alumni:
            mask = alumni_df.apply(lambda row: row.astype(str).str.contains(search_alumni, case=False).any(), axis=1)
            alumni_df = alumni_df[mask]
            
        st.write(f"Found **{len(alumni_df)}** Alumni")
        
        for index, row in alumni_df.iterrows():
            with st.expander(f"👤 {row['Name']} | {row['JobRole']} at {row['Company']}"):
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
            
        st.write(f"Found **{len(student_df)}** Students")
        
        for index, row in student_df.iterrows():
            with st.expander(f"🎓 {row['Name']} | {row['Department']} (Class of {row['GradYear']})"):
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
            
            rank = 1
            for index, row in leaderboard.iterrows():
                st.success(f"{rank}. **{row['Name']}** - {row['Points']} Points ({row['Jobs Posted']} Jobs Posted)")
                rank += 1
        else:
            st.write("No contributions yet.")


# --- PAGE 3: AI CAREER ASSISTANT (STUDENTS ONLY) ---
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
                prompt = f"""
                I am a student with these skills: {student_resume}. 
                I want to apply for a {target_role} role. 
                1. Give me a brief skill gap analysis. 
                2. Write a short referral request message I can send to an alumni.
                """
                with st.spinner("Analyzing profile..."):
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.success("Analysis Complete!")
                    st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")


# --- PAGE 4: OPPORTUNITY PORTAL ---
elif page == "Opportunity Portal":
    st.title("💼 Referral & Opportunity Portal")
    
    users_df = pd.read_csv(DB_FILE)
    jobs_df = pd.read_csv(JOBS_DB_FILE)
    
    if st.session_state.user_info['Role'] == 'Alumni':
        with st.expander("📌 Post a New Opportunity"):
            job_title = st.text_input("Job Title")
            job_company = st.text_input("Company", value=st.session_state.user_info['Company'])
            posted_by = st.text_input("Your Email", value=st.session_state.user_info['Email'], disabled=True)
            app_link = st.text_input("Application or Referral Link")
            
            if st.button("Post Job"):
                if job_title and job_company:
                    new_job = pd.DataFrame([[job_title, job_company, posted_by, app_link]], 
                                           columns=jobs_df.columns)
                    pd.concat([jobs_df, new_job], ignore_index=True).to_csv(JOBS_DB_FILE, index=False)
                    st.success("Opportunity posted successfully! You earned 10 Contribution Points!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields.")
    
    st.write("### Current Openings")
    if not jobs_df.empty:
        for index, row in jobs_df.iterrows():
            with st.container():
                st.info(f"**{row['Job Title']}** at **{row['Company']}**  \n*Posted by: {row['Posted By (Email)']}*  \nLink: {row['Application Link']}")
                if st.session_state.user_info['Role'] == 'Student':
                    if st.button(f"Request Referral for {row['Job Title']}", key=f"req_{index}"):
                        refs_df = pd.read_csv(REFERRALS_DB_FILE)
                        new_ref = pd.DataFrame([[row['Job Title'], st.session_state.user_info['Name'], st.session_state.user_info['Email'], row['Posted By (Email)'], "Pending"]], 
                                               columns=refs_df.columns)
                        pd.concat([refs_df, new_ref], ignore_index=True).to_csv(REFERRALS_DB_FILE, index=False)
                        st.success(f"Referral request sent to {row['Posted By (Email)']}!")
    else:
        st.info("No opportunities posted yet.")


# --- PAGE 5: REVIEW REFERRALS (ALUMNI ONLY) ---
elif page == "Review Referrals":
    st.title("📥 Review Referral Requests")
    st.write("Review and manage incoming requests from students.")
    
    refs_df = pd.read_csv(REFERRALS_DB_FILE)
    my_requests = refs_df[refs_df["Alumni Email"] == st.session_state.user_info['Email']]
    
    if not my_requests.empty:
        st.dataframe(my_requests[["Job Title", "Applicant Name", "Applicant Email", "Status"]], hide_index=True, use_container_width=True)
    else:
        st.info("You have no pending referral requests at the moment.")
