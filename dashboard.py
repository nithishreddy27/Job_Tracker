# # dashboard.py

import streamlit as st
from pymongo import MongoClient
from config import CONFIG
from scraper import fetch_job_listings_for_roles
from models import User, Job
from user_manager import show_user_management
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd

# MongoDB Connection
client = MongoClient(CONFIG["MONGO_URI"])
db = client[CONFIG["DB_NAME"]]
jobs_collection = db[CONFIG["COLLECTION_NAME"]]
users_collection = db[CONFIG["USERS_COLLECTION_NAME"]]

# Streamlit Page Config
st.set_page_config(page_title="Enhanced Job Tracker Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.title("🚀 Job Tracker Pro")
page = st.sidebar.selectbox("Choose a page", ["📊 Dashboard", "👥 User Management", "🔍 Job Search"])

if page == "📊 Dashboard":
    st.title("📊 Job Tracker Dashboard")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_jobs = jobs_collection.count_documents({})
        st.metric("Total Jobs", total_jobs)
    
    with col2:
        total_users = users_collection.count_documents({"active": True})
        st.metric("Active Users", total_users)
    
    with col3:
        today_jobs = jobs_collection.count_documents({
            "created_at": {"$gte": datetime.now() - timedelta(days=1)}
        })
        st.metric("Jobs Today", today_jobs)
    
    with col4:
        unique_companies = len(jobs_collection.distinct("company"))
        st.metric("Companies", unique_companies)
    
    # Manual scrape button
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Run Complete Scan", type="primary"):
            with st.spinner("Scanning all job sources for all user roles..."):
                new_jobs = fetch_job_listings_for_roles()
                if new_jobs:
                    st.success(f"✅ Scan complete! Found {len(new_jobs)} new jobs and sent notifications.")
                else:
                    st.info("✅ Scan complete! No new jobs found.")
    
    with col2:
        st.info("💡 This will search all job sources for all user-selected roles and send personalized emails.")
    
    # Recent jobs
    st.markdown("---")
    st.subheader("📋 Recent Jobs")
    
    recent_jobs = list(jobs_collection.find().sort("created_at", -1).limit(20))
    
    if recent_jobs:
        for job in recent_jobs:
            with st.expander(f"{job['title']} at {job['company']} - {job['location']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Title:** {job['title']}")
                    st.write(f"**Company:** {job['company']}")
                    st.write(f"**Location:** {job['location']}")
                with col2:
                    st.write(f"**Source:** {job['source']}")
                    st.write(f"**Date Posted:** {job.get('date_posted', 'N/A')}")
                    st.write(f"**Added:** {job.get('created_at', 'N/A')}")
    else:
        st.info("No jobs found. Run a scan to start collecting jobs!")

elif page == "👥 User Management":
    show_user_management()

elif page == "🔍 Job Search":
    st.title("🔍 Job Search & Filters")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sources = ["All"] + list(jobs_collection.distinct("source"))
        selected_source = st.selectbox("Source", sources)
    
    with col2:
        companies = ["All"] + list(jobs_collection.distinct("company"))
        selected_company = st.selectbox("Company", companies)
    
    with col3:
        locations = ["All"] + list(jobs_collection.distinct("location"))
        selected_location = st.selectbox("Location", locations)
    
    # Search
    search_term = st.text_input("🔍 Search jobs", placeholder="Enter job title, company, or keywords...")
    
    # Build query
    query = {}
    if selected_source != "All":
        query["source"] = selected_source
    if selected_company != "All":
        query["company"] = selected_company
    if selected_location != "All":
        query["location"] = selected_location
    if search_term:
        query["$or"] = [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"company": {"$regex": search_term, "$options": "i"}},
            {"location": {"$regex": search_term, "$options": "i"}}
        ]
    
    # Get jobs
    jobs = list(jobs_collection.find(query).sort("created_at", -1))
    
    st.subheader(f"📄 Found {len(jobs)} job(s)")
    
    if jobs:
        for job in jobs:
            with st.expander(f"{job['title']} at {job['company']} ({job['location']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Title:** {job['title']}")
                    st.markdown(f"**Company:** {job['company']}")
                    st.markdown(f"**Location:** {job['location']}")
                with col2:
                    st.markdown(f"**Source:** {job['source']}")
                    st.markdown(f"**Date Posted:** {job.get('date_posted', 'N/A')}")
                    st.markdown(f"**Search Role:** {job.get('search_role', 'N/A')}")
    else:
        st.info("No jobs found with the selected filters.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Enhanced Job Tracker Pro 🚀")
st.sidebar.caption("Made by Nithish Reddy")
