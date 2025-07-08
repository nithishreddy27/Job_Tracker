# # notify.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import CONFIG
from datetime import datetime

def send_batched_job_alerts(user_job_map):
    """Send one email per user containing all matched jobs"""
    print("insdide batched job alerts")
    for email, user_jobs in user_job_map.items():
        try:
            if not user_jobs:
                continue
            
            user = user_jobs[0][0]  # All entries have same user
            job_listings = user_jobs  # List of tuples (user, job_data)
            
            # Email subject
            subject = f"🎯 {len(job_listings)} New Job(s) Matching Your Preferences"
            
            # Construct body
            body = f"""
            Hi there! 👋

            Here are the new jobs that match your preferences:

            """
            for _, job_data in job_listings:
                body += f"""
            🏢 Company: {job_data['company']}
            📝 Title: {job_data['title']}
            📍 Location: {job_data['location']}
            📅 Posted: {job_data['date_posted']}
            🔍 Source: {job_data['source']}

            ---
            """

            body += f"""
            • Your selected roles: {', '.join(user['job_roles'])}
            • Your selected locations: {', '.join(user['locations'])}

            Happy job hunting! 🚀

            ---
            Job Tracker Bot
            """

            # Send email
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = CONFIG["EMAIL"]["sender"]
            msg["To"] = email
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(CONFIG["EMAIL"]["sender"], CONFIG["EMAIL"]["password"])
                server.send_message(msg)
                print(f"✅ Batched email sent to {email}")
        
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")

def send_summary_email(total_jobs, total_users):
    """Send summary email to admin"""
    try:
        subject = f"📊 Job Tracker Summary - {total_jobs} jobs processed"
        
        body = f"""
Job Tracker Summary:

📊 **Total Jobs Processed:** {total_jobs}
👥 **Total Active Users:** {total_users}
⏰ **Scan Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
Job Tracker System
        """
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = CONFIG["EMAIL"]["sender"]
        msg["To"] = CONFIG["EMAIL"]["sender"]  # Send to admin
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(CONFIG["EMAIL"]["sender"], CONFIG["EMAIL"]["password"])
            server.send_message(msg)
            print("✅ Summary email sent to admin")
            
    except Exception as e:
        print(f"❌ Failed to send summary email: {e}")
