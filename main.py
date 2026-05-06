import streamlit as st
from datetime import date, timedelta
import calendar
import csv
import io
import random
import textwrap

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Career Compass",
    page_icon="🎓",
    layout="wide"
)

# ==================================================
# CLEAN PROFESSIONAL DESIGN
# ==================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F7FB;
        color: #111827;
        font-family: Arial, sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    h1, h2, h3 {
        color: #111827;
        font-family: Arial, sans-serif;
    }

    p, div, label {
        font-family: Arial, sans-serif;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #2563EB;
        background-color: #2563EB;
        color: white;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #1D4ED8;
        color: white;
        border: 1px solid #1D4ED8;
    }

    .stLinkButton > a {
        border-radius: 10px;
        background-color: #111827;
        color: white !important;
        font-weight: 600;
        text-decoration: none;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
    }

    .calendar-cell {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 10px;
        min-height: 145px;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    }

    .calendar-day {
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
    }

    .event {
        padding: 5px 7px;
        border-radius: 8px;
        margin-bottom: 5px;
        font-size: 12px;
        color: white;
        font-weight: 600;
    }

    .event-blue {
        background-color: #2563EB;
    }

    .event-green {
        background-color: #16A34A;
    }

    .event-purple {
        background-color: #7C3AED;
    }

    .event-orange {
        background-color: #F97316;
    }

    .event-gray {
        background-color: #6B7280;
    }

    .badge {
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
    }

    .badge-yellow {
        background-color: #FEF3C7;
        color: #92400E;
    }

    .badge-blue {
        background-color: #DBEAFE;
        color: #1D4ED8;
    }

    .badge-purple {
        background-color: #EDE9FE;
        color: #6D28D9;
    }

    .badge-green {
        background-color: #DCFCE7;
        color: #15803D;
    }

    .badge-red {
        background-color: #FEE2E2;
        color: #B91C1C;
    }

    .badge-gray {
        background-color: #E5E7EB;
        color: #374151;
    }

    .badge-orange {
        background-color: #FFEDD5;
        color: #C2410C;
    }

    .hero-card {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    #MainMenu, footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# HELPERS
# ==================================================

STATUSES = [
    "To Apply",
    "Applied",
    "Online Assessment",
    "Interview",
    "Offer",
    "Rejected",
    "Withdrawn"
]

PRIORITIES = ["High", "Medium", "Low"]

LOCATIONS = [
    "All",
    "Milan",
    "Rome",
    "Paris",
    "London",
    "Madrid",
    "Berlin",
    "Amsterdam",
    "Dublin",
    "Zurich",
    "Geneva",
    "Luxembourg",
    "Remote"
]

JOB_TYPES = [
    "All",
    "Consulting",
    "Finance",
    "Marketing",
    "Data Analysis",
    "Software Engineering",
    "Product Management",
    "HR",
    "Operations",
    "Business Development",
    "Sales",
    "Supply Chain"
]


def status_badge(status):
    badge_class = {
        "To Apply": "badge-yellow",
        "Applied": "badge-blue",
        "Online Assessment": "badge-purple",
        "Interview": "badge-green",
        "Offer": "badge-green",
        "Rejected": "badge-red",
        "Withdrawn": "badge-gray"
    }.get(status, "badge-gray")

    return f'<span class="badge {badge_class}">{status}</span>'


def priority_badge(priority):
    badge_class = {
        "High": "badge-red",
        "Medium": "badge-orange",
        "Low": "badge-green"
    }.get(priority, "badge-gray")

    return f'<span class="badge {badge_class}">{priority}</span>'


def active_applications():
    return [
        app for app in st.session_state.applications
        if app["status"] not in ["Rejected", "Withdrawn"]
    ]


def rejected_applications():
    return [
        app for app in st.session_state.applications
        if app["status"] == "Rejected"
    ]


def get_nearest_deadline():
    active = active_applications()
    if not active:
        return None
    return min(active, key=lambda app: app["deadline"])


def preparation_checklist(job_title):
    return [
        "Update the CV for this specific role",
        "Adapt the cover letter",
        "Research the company",
        "Review the job description",
        "Prepare examples from previous experience",
        "Practice common interview questions",
        f"Prepare reasons why you want the {job_title} position"
    ]


def safe_link_button(label, url):
    if url and str(url).startswith("http"):
        st.link_button(label, url)
    else:
        st.warning("No valid link available.")


def make_csv_download(applications):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Priority",
        "Job Title",
        "Company",
        "Status",
        "Deadline",
        "Location",
        "Salary",
        "CV Used",
        "Time Spent",
        "Notes",
        "LinkedIn Link"
    ])

    for app in applications:
        writer.writerow([
            app["priority"],
            app["job_title"],
            app["company"],
            app["status"],
            app["deadline"],
            app["location"],
            app["salary"],
            app["cv"],
            app["time_spent"],
            app["notes"],
            app["link"]
        ])

    return output.getvalue().encode("utf-8")


def escape_pdf_text(text):
    text = str(text)
    text = text.replace("\\", "\\\\")
    text = text.replace("(", "\\(")
    text = text.replace(")", "\\)")
    return text


def make_simple_pdf(title, lines):
    pdf_lines = []
    y = 760

    pdf_lines.append("BT")
    pdf_lines.append("/F1 18 Tf")
    pdf_lines.append(f"50 {y} Td")
    pdf_lines.append(f"({escape_pdf_text(title)}) Tj")
    pdf_lines.append("ET")

    y -= 35

    for line in lines:
        wrapped = textwrap.wrap(str(line), width=85)
        for part in wrapped:
            pdf_lines.append("BT")
            pdf_lines.append("/F1 10 Tf")
            pdf_lines.append(f"50 {y} Td")
            pdf_lines.append(f"({escape_pdf_text(part)}) Tj")
            pdf_lines.append("ET")
            y -= 16

            if y < 50:
                break

    content = "\n".join(pdf_lines)
    content_bytes = content.encode("latin-1", errors="replace")

    objects = []

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(
        b"<< /Length " + str(len(content_bytes)).encode() + b" >>\nstream\n"
        + content_bytes + b"\nendstream"
    )

    pdf = b"%PDF-1.4\n"
    offsets = [0]

    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"

    xref_position = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"

    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode()

    pdf += (
        b"trailer\n"
        + f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
        + b"startxref\n"
        + str(xref_position).encode()
        + b"\n%%EOF"
    )

    return pdf


def application_pdf(app):
    lines = [
        f"Job Title: {app['job_title']}",
        f"Company: {app['company']}",
        f"Status: {app['status']}",
        f"Priority: {app['priority']}",
        f"Deadline: {app['deadline']}",
        f"Location: {app['location']}",
        f"Salary: {app['salary']}",
        f"CV Used: {app['cv']}",
        f"Time Spent: {app['time_spent']} hours",
        f"LinkedIn / Application Link: {app['link']}",
        "",
        f"Description: {app['description']}",
        "",
        f"Benefits: {app['benefits']}",
        "",
        f"Required Documents: {app['documents']}",
        "",
        f"Notes: {app['notes']}"
    ]

    return make_simple_pdf(f"{app['job_title']} - {app['company']}", lines)


def autofill_from_link(link):
    link_lower = link.lower()

    if "deloitte" in link_lower or "finance" in link_lower:
        return {
            "job_title": "Finance Intern",
            "company": "Deloitte",
            "location": "Milan",
            "salary": "€1,000/month",
            "job_type": "Finance",
            "description": "Support financial analysis, reporting, Excel modelling, and client presentations.",
            "benefits": "Training, networking events, meal allowance",
            "documents": "CV, cover letter, transcript",
            "notes": "Auto-filled from job link. Review before saving."
        }

    if "loreal" in link_lower or "marketing" in link_lower:
        return {
            "job_title": "Marketing Intern",
            "company": "L'Oréal",
            "location": "Paris",
            "salary": "€1,200/month",
            "job_type": "Marketing",
            "description": "Support campaign analysis, brand strategy, social media planning, and market research.",
            "benefits": "Hybrid work, lunch vouchers, paid vacation",
            "documents": "CV, cover letter",
            "notes": "Auto-filled from job link. Review before saving."
        }

    if "google" in link_lower or "product" in link_lower:
        return {
            "job_title": "Product Management Intern",
            "company": "Google",
            "location": "Dublin",
            "salary": "€1,800/month",
            "job_type": "Product Management",
            "description": "Support product teams with user research, feature prioritization, and product performance analysis.",
            "benefits": "Free meals, wellness support, learning budget",
            "documents": "CV, portfolio, transcript",
            "notes": "Auto-filled from job link. Review before saving."
        }

    if "microsoft" in link_lower or "software" in link_lower:
        return {
            "job_title": "Software Engineering Intern",
            "company": "Microsoft",
            "location": "Berlin",
            "salary": "€1,700/month",
            "job_type": "Software Engineering",
            "description": "Work with engineering teams to build, test, and improve software products.",
            "benefits": "Remote flexibility, mentorship, learning budget",
            "documents": "CV, GitHub profile, transcript",
            "notes": "Auto-filled from job link. Review before saving."
        }

    return {
        "job_title": "Strategy Intern",
        "company": "PwC",
        "location": "Rome",
        "salary": "€1,100/month",
        "job_type": "Consulting",
        "description": "Support strategy consultants with market research, competitor analysis, and business presentations.",
        "benefits": "Hybrid work, training, meal vouchers",
        "documents": "CV, cover letter",
        "notes": "Auto-filled from job link. Review before saving."
    }


def event_color(status):
    if status == "Interview":
        return "event-green"
    if status == "Online Assessment":
        return "event-purple"
    if status == "Offer":
        return "event-orange"
    if status == "Applied":
        return "event-blue"
    return "event-gray"


# ==================================================
# INITIAL DATA
# ==================================================

if "applications" not in st.session_state:
    st.session_state.applications = [
        {
            "job_title": "Marketing Intern",
            "company": "L'Oréal",
            "status": "Applied",
            "priority": "High",
            "deadline": date.today() + timedelta(days=3),
            "location": "Paris",
            "salary": "€1,200/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Marketing%20Intern%20L%27Oreal",
            "cv": "Marketing CV",
            "job_type": "Marketing",
            "description": "Support campaign analysis, social media planning, brand strategy, and market research.",
            "benefits": "Hybrid work, lunch vouchers, paid vacation",
            "documents": "CV, cover letter",
            "notes": "Need to prepare examples of previous marketing projects.",
            "time_spent": 2.5,
            "rejection_reason": "",
            "date_rejected": ""
        },
        {
            "job_title": "Finance Intern",
            "company": "Deloitte",
            "status": "Online Assessment",
            "priority": "High",
            "deadline": date.today() + timedelta(days=5),
            "location": "Milan",
            "salary": "€1,000/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Finance%20Intern%20Deloitte",
            "cv": "Finance CV",
            "job_type": "Finance",
            "description": "Assist with financial analysis, reporting, Excel models, and client presentations.",
            "benefits": "Training, networking events, meal allowance",
            "documents": "CV, transcript, online test",
            "notes": "Online assessment includes numerical reasoning.",
            "time_spent": 3,
            "rejection_reason": "",
            "date_rejected": ""
        },
        {
            "job_title": "Data Analyst Intern",
            "company": "Spotify",
            "status": "Interview",
            "priority": "High",
            "deadline": date.today() + timedelta(days=7),
            "location": "Stockholm",
            "salary": "€1,500/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Data%20Analyst%20Intern%20Spotify",
            "cv": "Data CV",
            "job_type": "Data Analysis",
            "description": "Analyze user data, create dashboards, and support business decisions with insights.",
            "benefits": "Remote flexibility, wellness budget, international environment",
            "documents": "CV, portfolio, technical interview",
            "notes": "Prepare Python, SQL, and dashboard examples.",
            "time_spent": 4,
            "rejection_reason": "",
            "date_rejected": ""
        },
        {
            "job_title": "Consulting Intern",
            "company": "McKinsey",
            "status": "To Apply",
            "priority": "Medium",
            "deadline": date.today() + timedelta(days=2),
            "location": "Madrid",
            "salary": "€1,300/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Consulting%20Intern%20McKinsey",
            "cv": "Consulting CV",
            "job_type": "Consulting",
            "description": "Work with consulting teams on market research, problem solving, and client strategy.",
            "benefits": "Mentorship, travel opportunities, professional training",
            "documents": "CV, cover letter",
            "notes": "Need to adapt CV and write cover letter.",
            "time_spent": 1,
            "rejection_reason": "",
            "date_rejected": ""
        },
        {
            "job_title": "Business Development Intern",
            "company": "Amazon",
            "status": "Applied",
            "priority": "Medium",
            "deadline": date.today() + timedelta(days=10),
            "location": "Luxembourg",
            "salary": "€1,400/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Business%20Development%20Intern%20Amazon",
            "cv": "Business CV",
            "job_type": "Business Development",
            "description": "Support business growth projects, competitor analysis, and process improvement.",
            "benefits": "International office, training, relocation support",
            "documents": "CV, cover letter",
            "notes": "Waiting for response.",
            "time_spent": 2,
            "rejection_reason": "",
            "date_rejected": ""
        },
        {
            "job_title": "HR Intern",
            "company": "Unilever",
            "status": "Rejected",
            "priority": "Low",
            "deadline": date.today() - timedelta(days=4),
            "location": "London",
            "salary": "£1,200/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=HR%20Intern%20Unilever",
            "cv": "HR CV",
            "job_type": "HR",
            "description": "Support recruitment, onboarding, employee engagement, and HR analytics.",
            "benefits": "Flexible working, employee discounts",
            "documents": "CV, cover letter",
            "notes": "Rejected after first screening.",
            "time_spent": 2,
            "rejection_reason": "Lack of direct HR experience.",
            "date_rejected": str(date.today() - timedelta(days=2))
        },
        {
            "job_title": "Operations Intern",
            "company": "Nestlé",
            "status": "To Apply",
            "priority": "Medium",
            "deadline": date.today() + timedelta(days=8),
            "location": "Geneva",
            "salary": "CHF 1,600/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Operations%20Intern%20Nestle",
            "cv": "Operations CV",
            "job_type": "Operations",
            "description": "Assist with supply chain analysis, process optimization, and operational reporting.",
            "benefits": "Paid vacation, training, company events",
            "documents": "CV, cover letter",
            "notes": "Highlight Excel and process analysis skills.",
            "time_spent": 1.5,
            "rejection_reason": "",
            "date_rejected": ""
        },
        {
            "job_title": "Product Management Intern",
            "company": "Google",
            "status": "Rejected",
            "priority": "High",
            "deadline": date.today() - timedelta(days=10),
            "location": "Dublin",
            "salary": "€1,800/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Product%20Management%20Intern%20Google",
            "cv": "Product CV",
            "job_type": "Product Management",
            "description": "Support product teams with user research, feature prioritization, and performance analysis.",
            "benefits": "Free meals, wellness support, learning budget",
            "documents": "CV, portfolio, online assessment",
            "notes": "Rejected after online assessment.",
            "time_spent": 5,
            "rejection_reason": "Online assessment score was not high enough.",
            "date_rejected": str(date.today() - timedelta(days=6))
        },
        {
            "job_title": "Supply Chain Intern",
            "company": "P&G",
            "status": "Applied",
            "priority": "Medium",
            "deadline": date.today() + timedelta(days=12),
            "location": "Geneva",
            "salary": "CHF 1,500/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Supply%20Chain%20Intern%20P%26G",
            "cv": "Operations CV",
            "job_type": "Supply Chain",
            "description": "Support logistics, demand planning, and supply chain performance analysis.",
            "benefits": "Training, international team, paid vacation",
            "documents": "CV, cover letter",
            "notes": "Good match with operations coursework.",
            "time_spent": 2,
            "rejection_reason": "",
            "date_rejected": ""
        },
        {
            "job_title": "Software Engineering Intern",
            "company": "Microsoft",
            "status": "To Apply",
            "priority": "Low",
            "deadline": date.today() + timedelta(days=15),
            "location": "Berlin",
            "salary": "€1,700/month",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Software%20Engineering%20Intern%20Microsoft",
            "cv": "Tech CV",
            "job_type": "Software Engineering",
            "description": "Build, test, and improve software features with engineering teams.",
            "benefits": "Remote flexibility, mentorship, learning budget",
            "documents": "CV, GitHub profile",
            "notes": "Requires stronger technical portfolio.",
            "time_spent": 0.5,
            "rejection_reason": "",
            "date_rejected": ""
        }
    ]

if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "Giulia",
        "surname": "Student",
        "birthday": date(2003, 1, 1),
        "university": "University Student",
        "degree": "Business and Management",
        "graduation_year": "2026",
        "email": "giulia@example.com",
        "phone": "+39 000 000 0000",
        "linkedin": "https://www.linkedin.com/",
        "portfolio": "",
        "experience": "Marketing project, finance coursework, group consulting project.",
        "skills": "Excel, PowerPoint, Python, communication, teamwork, financial analysis",
        "interests": "Consulting, Finance, Marketing, Data Analysis",
        "preferred_locations": "Milan, Paris, London, Remote",
        "preferred_job_types": "Consulting, Finance, Marketing"
    }

if "cvs" not in st.session_state:
    st.session_state.cvs = [
        {
            "name": "Finance CV",
            "job_type": "Finance",
            "upload_date": str(date.today() - timedelta(days=20)),
            "notes": "Best for finance, accounting, and investment roles.",
            "default": True,
            "file_name": "finance_cv.pdf"
        },
        {
            "name": "Marketing CV",
            "job_type": "Marketing",
            "upload_date": str(date.today() - timedelta(days=15)),
            "notes": "Best for marketing, branding, and communication roles.",
            "default": False,
            "file_name": "marketing_cv.pdf"
        },
        {
            "name": "Consulting CV",
            "job_type": "Consulting",
            "upload_date": str(date.today() - timedelta(days=12)),
            "notes": "Best for consulting, strategy, and business analyst roles.",
            "default": False,
            "file_name": "consulting_cv.pdf"
        },
        {
            "name": "Data CV",
            "job_type": "Data Analysis",
            "upload_date": str(date.today() - timedelta(days=8)),
            "notes": "Best for data analyst roles using Python, SQL, and Excel.",
            "default": False,
            "file_name": "data_cv.pdf"
        }
    ]

if "profile_photo" not in st.session_state:
    st.session_state.profile_photo = None

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.markdown(
    """
    <div style="padding: 10px 0 20px 0;">
        <h2 style="margin-bottom:4px; color:#111827;">🎓 Career Compass</h2>
        <p style="font-size:14px; color:#6B7280; margin-top:0;">
            Internship application hub
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Applications",
        "Calendar",
        "CV Library",
        "Profile",
        "Job Suggestions",
        "Rejection History",
        "Settings"
    ]
)

st.sidebar.divider()

nearest = get_nearest_deadline()

if nearest:
    st.sidebar.subheader("⏰ Next Deadline")
    st.sidebar.write(f"**{nearest['job_title']}**")
    st.sidebar.write(nearest["company"])
    st.sidebar.write(nearest["deadline"].strftime("%d %B %Y"))

    with st.sidebar.expander("Preparation checklist"):
        for item in preparation_checklist(nearest["job_title"]):
            st.checkbox(item, key=f"sidebar_{nearest['company']}_{item}")

# ==================================================
# HOME
# ==================================================

if page == "Home":
    st.markdown(
        """
        <div class="hero-card">
            <h1 style="margin:0; font-size:38px;">Career Compass</h1>
            <p style="margin-top:10px; font-size:17px; color:#4B5563; max-width:900px;">
                Organize your internship applications, track deadlines, manage CV versions,
                prepare for interviews, and keep LinkedIn job links in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    all_apps = st.session_state.applications
    active = active_applications()
    rejected = rejected_applications()
    interviews = [app for app in all_apps if app["status"] == "Interview"]
    offers = [app for app in all_apps if app["status"] == "Offer"]

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Total", len(all_apps))
    col2.metric("Active", len(active))
    col3.metric("Interviews", len(interviews))
    col4.metric("Offers", len(offers))
    col5.metric("Rejections", len(rejected))

    if nearest:
        days_left = (nearest["deadline"] - date.today()).days
        col6.metric("Closest Deadline", f"{days_left} days")
    else:
        col6.metric("Closest Deadline", "None")

    st.divider()

    tips = [
        "Small progress is still progress. Apply to one role today.",
        "Customize your CV for each role instead of sending the same version everywhere.",
        "Before an interview, prepare three examples from your experience.",
        "Track rejection reasons: they can help improve your next application.",
        "Apply early. Many roles close before the official deadline."
    ]

    st.info(f"💡 Daily motivation: {random.choice(tips)}")

    st.subheader("Closest Deadline Reminder")

    if nearest:
        st.warning(
            f"Your closest deadline is **{nearest['job_title']} at {nearest['company']}** "
            f"on **{nearest['deadline'].strftime('%d %B %Y')}**."
        )

        with st.expander("Open preparation plan"):
            st.write("### Preparation Checklist")
            for item in preparation_checklist(nearest["job_title"]):
                st.checkbox(item, key=f"home_{nearest['company']}_{item}")

            st.write("### Notes")
            st.write(nearest["notes"])

            safe_link_button("Open LinkedIn / Job Page", nearest["link"])
    else:
        st.success("No upcoming deadlines.")

    st.divider()

    st.subheader("Active Applications Overview")

    st.markdown("**Priority | Job Title | Company | Status | Closest Deadline | Location**")

    for app in active[:6]:
        with st.container(border=True):
            c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 2, 2, 2])
            c1.markdown(priority_badge(app["priority"]), unsafe_allow_html=True)
            c2.write(f"**{app['job_title']}**")
            c3.write(app["company"])
            c4.markdown(status_badge(app["status"]), unsafe_allow_html=True)
            c5.write(app["deadline"].strftime("%d %B %Y"))
            c6.write(app["location"])

# ==================================================
# APPLICATIONS
# ==================================================

elif page == "Applications":
    st.title("Application Tracker")

    tab1, tab2 = st.tabs(["Applications Table", "Add New Application"])

    with tab1:
        search = st.text_input(
            "Search applications by job title, company, location, status, or notes"
        ).lower()

        st.download_button(
            "Download full applications table as CSV",
            data=make_csv_download(st.session_state.applications),
            file_name="applications.csv",
            mime="text/csv"
        )

        st.subheader("Active Applications")
        st.markdown(
            "**Priority | Job Title | Company | Status | Closest Deadline | Location | Salary | CV Used | Time Spent**"
        )

        visible_apps = []

        for index, app in enumerate(st.session_state.applications):
            if app["status"] in ["Rejected", "Withdrawn"]:
                continue

            searchable_text = " ".join([
                app["job_title"],
                app["company"],
                app["status"],
                app["location"],
                app["notes"],
                app["job_type"]
            ]).lower()

            if search and search not in searchable_text:
                continue

            visible_apps.append((index, app))

        if not visible_apps:
            st.warning("No applications found with your search.")

        for i, app in visible_apps:
            with st.container(border=True):
                c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
                    [1, 2, 2, 2, 2, 1.5, 1.5, 1.5, 1]
                )

                c1.markdown(priority_badge(app["priority"]), unsafe_allow_html=True)
                c2.write(f"**{app['job_title']}**")
                c3.write(app["company"])
                c4.markdown(status_badge(app["status"]), unsafe_allow_html=True)
                c5.write(app["deadline"].strftime("%d %B %Y"))
                c6.write(app["location"])
                c7.write(app["salary"])
                c8.write(app["cv"])
                c9.write(f"{app['time_spent']}h")

                with st.expander("Click to view full application details"):
                    st.write("### Job Description")
                    st.write(app["description"])

                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.write(f"**Company:** {app['company']}")
                        st.write(f"**Location:** {app['location']}")
                        st.write(f"**Job Type:** {app['job_type']}")
                        st.write(f"**Salary:** {app['salary']}")
                        st.write(f"**Benefits / Vacations:** {app['benefits']}")
                        st.write(f"**Required Documents:** {app['documents']}")

                    with col_b:
                        st.write(f"**Status:** {app['status']}")
                        st.write(f"**Priority:** {app['priority']}")
                        st.write(f"**Deadline:** {app['deadline'].strftime('%d %B %Y')}")
                        st.write(f"**CV Used:** {app['cv']}")
                        st.write(f"**Time Spent:** {app['time_spent']} hours")
                        st.write(f"**Notes:** {app['notes']}")

                    safe_link_button("Apply on LinkedIn / Open Job Page", app["link"])

                    st.download_button(
                        "Download this application as PDF",
                        data=application_pdf(app),
                        file_name=f"{app['company']}_{app['job_title']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{i}"
                    )

                    st.divider()
                    st.write("### Edit Application")

                    new_status = st.selectbox(
                        "Status",
                        STATUSES,
                        index=STATUSES.index(app["status"]),
                        key=f"edit_status_{i}"
                    )

                    new_priority = st.selectbox(
                        "Priority",
                        PRIORITIES,
                        index=PRIORITIES.index(app["priority"]),
                        key=f"edit_priority_{i}"
                    )

                    new_deadline = st.date_input(
                        "Deadline",
                        value=app["deadline"],
                        key=f"edit_deadline_{i}"
                    )

                    new_time = st.number_input(
                        "Time spent in hours",
                        min_value=0.0,
                        step=0.5,
                        value=float(app["time_spent"]),
                        key=f"edit_time_{i}"
                    )

                    new_notes = st.text_area(
                        "Notes",
                        value=app["notes"],
                        key=f"edit_notes_{i}"
                    )

                    c_save, c_reject, c_offer, c_delete = st.columns(4)

                    if c_save.button("Save Changes", key=f"save_{i}"):
                        old_status = st.session_state.applications[i]["status"]

                        st.session_state.applications[i]["status"] = new_status
                        st.session_state.applications[i]["priority"] = new_priority
                        st.session_state.applications[i]["deadline"] = new_deadline
                        st.session_state.applications[i]["time_spent"] = new_time
                        st.session_state.applications[i]["notes"] = new_notes

                        if new_status == "Offer" and old_status != "Offer":
                            st.balloons()
                            st.success("Congratulations! Offer received.")

                        st.success("Application updated.")
                        st.rerun()

                    if c_reject.button("Mark as Rejected", key=f"reject_{i}"):
                        st.session_state.applications[i]["status"] = "Rejected"
                        st.session_state.applications[i]["rejection_reason"] = "Reason not specified."
                        st.session_state.applications[i]["date_rejected"] = str(date.today())
                        st.success("Application moved to rejection history.")
                        st.rerun()

                    if c_offer.button("Mark as Offer", key=f"offer_{i}"):
                        st.session_state.applications[i]["status"] = "Offer"
                        st.balloons()
                        st.success("Congratulations! Offer received.")
                        st.rerun()

                    if c_delete.button("Delete", key=f"delete_{i}"):
                        st.session_state.applications.pop(i)
                        st.warning("Application deleted.")
                        st.rerun()

    with tab2:
        st.subheader("Add New Application")

        pasted_link = st.text_input("Paste LinkedIn or job application link")

        if st.button("Auto-fill from Job Link"):
            st.session_state.autofill = autofill_from_link(pasted_link)
            st.success("Information extracted. Please review and edit before saving.")

        autofill = st.session_state.get("autofill", {})

        with st.form("add_application_form"):
            c1, c2 = st.columns(2)

            job_title = c1.text_input("Job Title", value=autofill.get("job_title", ""))
            company = c2.text_input("Company", value=autofill.get("company", ""))

            status = c1.selectbox("Status", STATUSES)
            priority = c2.selectbox("Priority", PRIORITIES)

            deadline = c1.date_input("Closest Deadline", value=date.today() + timedelta(days=7))
            location = c2.selectbox(
                "Location",
                [loc for loc in LOCATIONS if loc != "All"],
                index=0
            )

            salary = c1.text_input("Salary", value=autofill.get("salary", ""))
            job_type = c2.selectbox(
                "Job Type",
                [job for job in JOB_TYPES if job != "All"],
                index=0
            )

            link = st.text_input("LinkedIn / Application Link", value=pasted_link)

            cv_options = [cv["name"] for cv in st.session_state.cvs]
            cv_used = st.selectbox("CV Used", cv_options)

            description = st.text_area("Job Description", value=autofill.get("description", ""))
            benefits = st.text_area("Benefits / Vacations / Other Info", value=autofill.get("benefits", ""))
            documents = st.text_area("Required Documents", value=autofill.get("documents", ""))
            notes = st.text_area("Notes", value=autofill.get("notes", ""))

            time_spent = st.number_input("Time Spent in Hours", min_value=0.0, step=0.5)

            submitted = st.form_submit_button("Save Application")

            if submitted:
                st.session_state.applications.append(
                    {
                        "job_title": job_title,
                        "company": company,
                        "status": status,
                        "priority": priority,
                        "deadline": deadline,
                        "location": location,
                        "salary": salary,
                        "link": link,
                        "cv": cv_used,
                        "job_type": job_type,
                        "description": description,
                        "benefits": benefits,
                        "documents": documents,
                        "notes": notes,
                        "time_spent": time_spent,
                        "rejection_reason": "",
                        "date_rejected": ""
                    }
                )

                if "autofill" in st.session_state:
                    del st.session_state.autofill

                st.success("Application added successfully.")
                st.rerun()

# ==================================================
# CALENDAR
# ==================================================

elif page == "Calendar":
    st.title("Calendar")

    st.write("View application deadlines, interviews, online assessments, offer responses, and follow-up reminders.")

    search_event = st.text_input("Search calendar events by job title, company, status, or location").lower()

    today = date.today()
    selected_year = st.selectbox("Year", [today.year, today.year + 1], index=0)
    selected_month = st.selectbox(
        "Month",
        list(range(1, 13)),
        index=today.month - 1,
        format_func=lambda month: calendar.month_name[month]
    )

    filtered_events = []

    for app in active_applications():
        text = " ".join([
            app["job_title"],
            app["company"],
            app["status"],
            app["location"]
        ]).lower()

        if search_event and search_event not in text:
            continue

        if app["deadline"].year == selected_year and app["deadline"].month == selected_month:
            filtered_events.append(app)

    month_matrix = calendar.monthcalendar(selected_year, selected_month)

    st.markdown("### " + calendar.month_name[selected_month] + f" {selected_year}")

    header_cols = st.columns(7)
    for col, day_name in zip(header_cols, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        col.markdown(f"**{day_name}**")

    for week in month_matrix:
        cols = st.columns(7)

        for col, day_num in zip(cols, week):
            with col:
                if day_num == 0:
                    st.markdown('<div class="calendar-cell"></div>', unsafe_allow_html=True)
                else:
                    events_today = [
                        app for app in filtered_events
                        if app["deadline"].day == day_num
                    ]

                    html = f'<div class="calendar-cell"><div class="calendar-day">{day_num}</div>'

                    for event in events_today:
                        color = event_color(event["status"])
                        html += (
                            f'<div class="event {color}">'
                            f'{event["company"]}: {event["status"]}'
                            f'</div>'
                        )

                    html += "</div>"
                    st.markdown(html, unsafe_allow_html=True)

    st.divider()

    st.subheader("Calendar Event Details")

    if not filtered_events:
        st.warning("No matching calendar events found.")
    else:
        for app in sorted(filtered_events, key=lambda item: item["deadline"]):
            with st.expander(
                f"{app['deadline'].strftime('%d %B %Y')} - {app['job_title']} at {app['company']}"
            ):
                st.write(f"**Event type:** {app['status']}")
                st.write(f"**Location:** {app['location']}")
                st.write(f"**Notes:** {app['notes']}")

                st.write("### Preparation checklist")
                for item in preparation_checklist(app["job_title"]):
                    st.checkbox(item, key=f"calendar_{app['company']}_{item}")

                safe_link_button("Open full job page", app["link"])

# ==================================================
# CV LIBRARY
# ==================================================

elif page == "CV Library":
    st.title("CV Library")

    st.write("Upload, store, edit, delete, and organize different CV versions.")

    for i, cv in enumerate(st.session_state.cvs):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

            c1.write(f"**{cv['name']}**")
            c2.write(cv["job_type"])
            c3.write(f"Uploaded: {cv['upload_date']}")
            c4.write("⭐ Default" if cv["default"] else "")

            with st.expander("View or edit CV"):
                new_name = st.text_input("CV Name", value=cv["name"], key=f"cv_name_{i}")
                new_type = st.selectbox(
                    "Job Type",
                    [job for job in JOB_TYPES if job != "All"],
                    index=[job for job in JOB_TYPES if job != "All"].index(cv["job_type"])
                    if cv["job_type"] in [job for job in JOB_TYPES if job != "All"] else 0,
                    key=f"cv_type_{i}"
                )
                new_notes = st.text_area("Notes", value=cv["notes"], key=f"cv_notes_{i}")

                uploaded_replacement = st.file_uploader(
                    "Upload replacement CV file",
                    type=["pdf", "docx"],
                    key=f"replace_cv_{i}"
                )

                if cv["file_name"]:
                    st.write(f"Current file: **{cv['file_name']}**")

                c_save, c_default, c_delete = st.columns(3)

                if c_save.button("Save CV Changes", key=f"save_cv_{i}"):
                    st.session_state.cvs[i]["name"] = new_name
                    st.session_state.cvs[i]["job_type"] = new_type
                    st.session_state.cvs[i]["notes"] = new_notes

                    if uploaded_replacement is not None:
                        st.session_state.cvs[i]["file_name"] = uploaded_replacement.name
                        st.session_state.cvs[i]["upload_date"] = str(date.today())

                    st.success("CV updated.")
                    st.rerun()

                if c_default.button("Mark as Default", key=f"default_cv_{i}"):
                    for existing_cv in st.session_state.cvs:
                        existing_cv["default"] = False

                    st.session_state.cvs[i]["default"] = True
                    st.success("Default CV updated.")
                    st.rerun()

                if c_delete.button("Delete CV", key=f"delete_cv_{i}"):
                    st.session_state.cvs.pop(i)
                    st.warning("CV deleted.")
                    st.rerun()

    st.divider()

    st.subheader("Add New CV")

    with st.form("add_cv_form"):
        cv_name = st.text_input("CV Name")

        job_type = st.selectbox(
            "Job Type",
            [job for job in JOB_TYPES if job != "All"]
        )

        uploaded_cv = st.file_uploader(
            "Upload CV File",
            type=["pdf", "docx"]
        )

        cv_notes = st.text_area("Notes")
        make_default = st.checkbox("Set as default CV")

        submit_cv = st.form_submit_button("Add CV")

        if submit_cv:
            if make_default:
                for existing_cv in st.session_state.cvs:
                    existing_cv["default"] = False

            st.session_state.cvs.append(
                {
                    "name": cv_name,
                    "job_type": job_type,
                    "upload_date": str(date.today()),
                    "notes": cv_notes,
                    "default": make_default,
                    "file_name": uploaded_cv.name if uploaded_cv else "No file uploaded"
                }
            )

            st.success("CV added.")
            st.rerun()

# ==================================================
# PROFILE
# ==================================================

elif page == "Profile":
    st.title("Student Profile")

    profile = st.session_state.profile

    photo = st.file_uploader("Upload profile photo", type=["png", "jpg", "jpeg"])

    if photo is not None:
        st.session_state.profile_photo = photo

    if st.session_state.profile_photo is not None:
        st.image(st.session_state.profile_photo, width=160)

    with st.form("profile_form"):
        c1, c2 = st.columns(2)

        name = c1.text_input("Name", value=profile["name"])
        surname = c2.text_input("Surname", value=profile["surname"])

        birthday = c1.date_input("Birthday", value=profile["birthday"])
        university = c2.text_input("University", value=profile["university"])

        degree = c1.text_input("Degree", value=profile["degree"])
        graduation_year = c2.text_input("Graduation Year", value=profile["graduation_year"])

        email = c1.text_input("Email", value=profile["email"])
        phone = c2.text_input("Phone Number", value=profile["phone"])

        linkedin = st.text_input("LinkedIn Profile URL", value=profile["linkedin"])
        portfolio = st.text_input("Portfolio URL", value=profile["portfolio"])

        experience = st.text_area("Previous Work Experience", value=profile["experience"])
        skills = st.text_area("Main Skills", value=profile["skills"])
        interests = st.text_area("Career Interests", value=profile["interests"])

        preferred_locations = st.text_area("Preferred Locations", value=profile["preferred_locations"])
        preferred_job_types = st.text_area("Preferred Job Types", value=profile["preferred_job_types"])

        save_profile = st.form_submit_button("Save Profile")

        if save_profile:
            st.session_state.profile = {
                "name": name,
                "surname": surname,
                "birthday": birthday,
                "university": university,
                "degree": degree,
                "graduation_year": graduation_year,
                "email": email,
                "phone": phone,
                "linkedin": linkedin,
                "portfolio": portfolio,
                "experience": experience,
                "skills": skills,
                "interests": interests,
                "preferred_locations": preferred_locations,
                "preferred_job_types": preferred_job_types
            }

            st.success("Profile saved.")

    st.divider()

    safe_link_button("Open LinkedIn Profile", st.session_state.profile["linkedin"])

# ==================================================
# JOB SUGGESTIONS
# ==================================================

elif page == "Job Suggestions":
    st.title("Job Suggestions")

    st.write(
        "Suggestions are based on your profile, skills, previous experience, preferred locations, and rejection history."
    )

    suggestions = [
        {
            "job_title": "Junior Business Analyst Intern",
            "company": "Accenture",
            "location": "Milan",
            "job_type": "Consulting",
            "industry": "Consulting",
            "mode": "Hybrid",
            "match": 92,
            "deadline": date.today() + timedelta(days=14),
            "salary": "€1,100/month",
            "description": "A strong match for students interested in consulting, business analysis, and digital transformation.",
            "skills": "Excel, PowerPoint, analytical thinking",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Junior%20Business%20Analyst%20Intern%20Accenture"
        },
        {
            "job_title": "Marketing Strategy Intern",
            "company": "Danone",
            "location": "Paris",
            "job_type": "Marketing",
            "industry": "Consumer Goods",
            "mode": "Hybrid",
            "match": 86,
            "deadline": date.today() + timedelta(days=9),
            "salary": "€1,200/month",
            "description": "Suitable for students interested in branding, consumer behavior, and market research.",
            "skills": "Communication, marketing, research",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Marketing%20Strategy%20Intern%20Danone"
        },
        {
            "job_title": "Financial Planning Intern",
            "company": "P&G",
            "location": "Geneva",
            "job_type": "Finance",
            "industry": "Consumer Goods",
            "mode": "In person",
            "match": 84,
            "deadline": date.today() + timedelta(days=11),
            "salary": "CHF 1,500/month",
            "description": "Good fit for students with finance, Excel, and analytical skills.",
            "skills": "Excel, finance, reporting",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Financial%20Planning%20Intern%20P%26G"
        },
        {
            "job_title": "People Operations Intern",
            "company": "Booking.com",
            "location": "Amsterdam",
            "job_type": "HR",
            "industry": "Technology",
            "mode": "Hybrid",
            "match": 71,
            "deadline": date.today() + timedelta(days=20),
            "salary": "€1,300/month",
            "description": "Recommended with lower priority because of previous rejection history in HR roles.",
            "skills": "Communication, HR, organization",
            "link": "https://www.linkedin.com/jobs/search/?keywords=People%20Operations%20Intern%20Booking"
        },
        {
            "job_title": "Software Engineering Intern",
            "company": "Microsoft",
            "location": "Berlin",
            "job_type": "Software Engineering",
            "industry": "Technology",
            "mode": "Remote",
            "match": 68,
            "deadline": date.today() + timedelta(days=18),
            "salary": "€1,700/month",
            "description": "Good for students with Python, web development, or software project experience.",
            "skills": "Python, problem solving, Git",
            "link": "https://www.linkedin.com/jobs/search/?keywords=Software%20Engineering%20Intern%20Microsoft"
        }
    ]

    c1, c2, c3 = st.columns(3)

    location_filter = c1.selectbox("Location", LOCATIONS)
    job_type_filter = c2.selectbox("Job Type", JOB_TYPES)
    min_match = c3.slider("Minimum Match Percentage", 0, 100, 70)

    c4, c5, c6 = st.columns(3)

    industry_filter = c4.selectbox(
        "Industry",
        ["All", "Consulting", "Consumer Goods", "Technology", "Finance"]
    )

    mode_filter = c5.selectbox(
        "Work Mode",
        ["All", "Remote", "Hybrid", "In person"]
    )

    deadline_limit = c6.date_input(
        "Show jobs before deadline",
        value=date.today() + timedelta(days=60)
    )

    if min_match < 50:
        st.error("Minimum match is under 50%. Results may be less relevant.")
    else:
        st.success("Minimum match is 50% or above. Suggestions should be more relevant.")

    filtered = []

    for suggestion in suggestions:
        if suggestion["match"] < min_match:
            continue

        if location_filter != "All" and suggestion["location"] != location_filter:
            continue

        if job_type_filter != "All" and suggestion["job_type"] != job_type_filter:
            continue

        if industry_filter != "All" and suggestion["industry"] != industry_filter:
            continue

        if mode_filter != "All" and suggestion["mode"] != mode_filter:
            continue

        if suggestion["deadline"] > deadline_limit:
            continue

        filtered.append(suggestion)

    if not filtered:
        st.warning("No matching job suggestions found. Try lowering the match percentage or changing the filters.")

    for suggestion in filtered:
        with st.container(border=True):
            c_a, c_b, c_c = st.columns([2, 2, 1])

            c_a.write(f"**{suggestion['job_title']}**")
            c_a.write(suggestion["company"])

            c_b.write(f"📍 {suggestion['location']}")
            c_b.write(f"Deadline: {suggestion['deadline'].strftime('%d %B %Y')}")
            c_b.write(f"Mode: {suggestion['mode']}")

            c_c.metric("Match", f"{suggestion['match']}%")

            with st.expander("View suggestion details"):
                st.write(suggestion["description"])
                st.write(f"**Required skills:** {suggestion['skills']}")
                st.write(f"**Salary:** {suggestion['salary']}")
                st.write("Some recommendations are adjusted based on your rejection history.")

                safe_link_button("Open exact LinkedIn job page", suggestion["link"])

                if st.button("Add to Application Tracker", key=f"suggestion_{suggestion['company']}"):
                    default_cv = "Default CV"

                    for cv in st.session_state.cvs:
                        if cv["default"]:
                            default_cv = cv["name"]

                    st.session_state.applications.append(
                        {
                            "job_title": suggestion["job_title"],
                            "company": suggestion["company"],
                            "status": "To Apply",
                            "priority": "Medium",
                            "deadline": suggestion["deadline"],
                            "location": suggestion["location"],
                            "salary": suggestion["salary"],
                            "link": suggestion["link"],
                            "cv": default_cv,
                            "job_type": suggestion["job_type"],
                            "description": suggestion["description"],
                            "benefits": "Not specified",
                            "documents": "CV, cover letter",
                            "notes": "Saved from job suggestions.",
                            "time_spent": 0.0,
                            "rejection_reason": "",
                            "date_rejected": ""
                        }
                    )

                    st.success("Suggestion added to application tracker.")
                    st.rerun()

# ==================================================
# REJECTION HISTORY
# ==================================================

elif page == "Rejection History":
    st.title("Rejection History")

    rejected = rejected_applications()

    if not rejected:
        st.success("No rejected applications yet.")
    else:
        st.write("Rejected applications are hidden from the main table and stored here.")

        with st.expander("Open Rejection Archive", expanded=True):
            for i, app in enumerate(st.session_state.applications):
                if app["status"] != "Rejected":
                    continue

                with st.container(border=True):
                    st.write(f"**{app['job_title']} at {app['company']}**")
                    st.write(f"**Date rejected:** {app['date_rejected']}")
                    st.write(f"**Reason:** {app['rejection_reason']}")
                    st.write(f"**CV used:** {app['cv']}")
                    st.write(f"**Notes:** {app['notes']}")

                    safe_link_button("Open original job page", app["link"])

                    if st.button("Restore to Active Applications", key=f"restore_{i}"):
                        st.session_state.applications[i]["status"] = "Applied"
                        st.session_state.applications[i]["rejection_reason"] = ""
                        st.session_state.applications[i]["date_rejected"] = ""
                        st.success("Application restored.")
                        st.rerun()

# ==================================================
# SETTINGS
# ==================================================

elif page == "Settings":
    st.title("Settings")

    st.write("Customize your Career Compass experience.")

    st.checkbox("Enable deadline reminders", value=True)
    st.checkbox("Enable motivational messages", value=True)
    st.checkbox("Enable calendar notifications", value=True)
    st.checkbox("Use rejection history to improve suggestions", value=True)
    st.checkbox("Show salary information when available", value=True)
    st.checkbox("Open applications through LinkedIn links", value=True)

    st.divider()

    st.subheader("Default CV")

    default_cv_names = [cv["name"] for cv in st.session_state.cvs]
    current_default = 0

    for index, cv in enumerate(st.session_state.cvs):
        if cv["default"]:
            current_default = index

    selected_default = st.selectbox(
        "Choose default CV",
        default_cv_names,
        index=current_default
    )

    if st.button("Save Default CV"):
        for cv in st.session_state.cvs:
            cv["default"] = cv["name"] == selected_default

        st.success("Default CV saved.")

    st.divider()

    st.subheader("About this app")

    st.write(
        """
        Career Compass is a Streamlit prototype for students managing internship and job applications.

        It includes application tracking, LinkedIn job links, CV storage, CV upload,
        profile photo upload, calendar deadlines, rejection history, job suggestions,
        motivational messages, time tracking, priority levels, search filters,
        CSV export, PDF export, and confetti when an offer is received.
        """
    )