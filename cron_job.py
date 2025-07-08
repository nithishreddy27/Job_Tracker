import schedule
import time
from run import main
from datetime import datetime
from scraper import fetch_job_listings_for_roles  # make sure this import is correct

def job():
    print(f"\n⏰ Cron job started at {datetime.now()}")
    main()
    print(f"⏰ Cron job completed at {datetime.now()}\n")

def test_job():
    print(f"\n🧪 Test job (fetch_job_listings_for_roles) started at {datetime.now()}")
    # fetch_job_listings_for_roles()
    main()
    print(f"🧪 Test job completed at {datetime.now()}\n")

# Schedule the production jobs
schedule.every(6).hours.do(job)
schedule.every().day.at("09:00").do(job)
schedule.every().day.at("18:00").do(job)

# TESTING: Schedule fetch_job_listings_for_roles every 5 minutes
# schedule.every(5).minutes.do(test_job)

print("🤖 Cron job scheduler started...")
print("📅 Jobs scheduled:")
print("   • Every 6 hours")
print("   • Daily at 9:00 AM")
print("   • Daily at 6:00 PM")
print("🧪 Test job scheduled: Every 5 minutes")
print("⏰ Waiting for scheduled times...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
