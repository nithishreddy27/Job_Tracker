from scraper import fetch_job_listings_for_roles
from notify import send_summary_email
from models import User

def main():
    print("🚀 Starting Enhanced Job Tracker...")
    
    # Get user count
    users = User.get_all_users()
    if not users:
        print("❌ No active users found. Please add users first.")
        return
    
    print(f"👥 Found {len(users)} active users")
    
    # Run the complete scan
    new_jobs = fetch_job_listings_for_roles()
    
    # Send summary
    if new_jobs:
        print(f"✅ Scan complete! Found {len(new_jobs)} new jobs")
        send_summary_email(len(new_jobs), len(users))
    else:
        print("✅ Scan complete! No new jobs found")

if __name__ == "__main__":
    main()
