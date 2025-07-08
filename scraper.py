# Scraper.py

import requests
from bs4 import BeautifulSoup
from config import CONFIG
from models import Job, User
from notify import send_batched_job_alerts
import time
from collections import defaultdict
from telegram_bot import send_job_to_telegram
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
import re

def parse_job_date(date_str):
    """
    Parse various date formats and return a datetime object.
    Returns None if parsing fails.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip()
    if not date_str:
        return None
    
    # Handle relative dates first
    date_str_lower = date_str.lower()
    now = datetime.now()
    
    # Handle "today", "just now", "yesterday" etc.
    if any(keyword in date_str_lower for keyword in ["today", "just now", "now"]):
        return now
    
    if "yesterday" in date_str_lower:
        return now - timedelta(days=1)
    
    # Handle "X days ago", "X hours ago" etc.
    time_ago_match = re.search(r'(\d+)\s*(day|hour|minute|week|month)s?\s*ago', date_str_lower)
    if time_ago_match:
        number = int(time_ago_match.group(1))
        unit = time_ago_match.group(2)
        
        if unit == 'minute':
            return now - timedelta(minutes=number)
        elif unit == 'hour':
            return now - timedelta(hours=number)
        elif unit == 'day':
            return now - timedelta(days=number)
        elif unit == 'week':
            return now - timedelta(weeks=number)
        elif unit == 'month':
            return now - relativedelta(months=number)
    
    # Handle ordinal numbers (20th, 1st, 2nd, 3rd, etc.)
    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    
    # Remove extra spaces
    date_str = ' '.join(date_str.split())
    
    # Try common date formats
    date_formats = [
        "%m/%d/%Y",     # 01/20/2025
        "%d/%m/%Y",     # 20/01/2025
        "%m/%d/%y",     # 01/20/25
        "%d/%m/%y",     # 20/01/25
        "%B %d, %Y",    # January 20, 2025
        "%b %d, %Y",    # Jan 20, 2025
        "%d %B %Y",     # 20 January 2025
        "%d %b %Y",     # 20 Jan 2025
        "%B %d",        # January 20 (current year)
        "%b %d",        # Jan 20 (current year)
        "%d %B",        # 20 January (current year)
        "%d %b",        # 20 Jan (current year)
        "%Y-%m-%d",     # 2025-01-20
        "%d-%m-%Y",     # 20-01-2025
        "%m-%d-%Y",     # 01-20-2025
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # If no year specified, assume current year
            if parsed_date.year == 1900:
                parsed_date = parsed_date.replace(year=now.year)
            return parsed_date
        except ValueError:
            continue
    
    # Try using dateutil parser as last resort
    try:
        parsed_date = parser.parse(date_str, fuzzy=True)
        return parsed_date
    except (ValueError, TypeError):
        pass
    
    return None


def fetch_job_listings_for_roles():
    """Fetch job listings for all user roles"""
    all_roles = User.get_all_unique_roles()
    if not all_roles:
        print("❌ No user roles found in database")
        return []
    
    print(f"🔍 Found {len(all_roles)} unique roles to search for")
    all_new_jobs = []
    global_user_job_map = defaultdict(list)
    
    for role in all_roles:
        print(f"\n🎯 Searching for role: {role}")
        role_jobs, user_job_map_for_role = fetch_jobs_for_specific_role(role)
        all_new_jobs.extend(role_jobs)
        
        # Merge user_job_map
        for email, job_pairs in user_job_map_for_role.items():
            global_user_job_map[email].extend(job_pairs)
        
        time.sleep(2)  # Rate limiting

    print("✅ Finished fetching all roles.")
    print(f"📬 Sending alerts to {len(global_user_job_map)} users")
    send_batched_job_alerts(global_user_job_map)
    
    return all_new_jobs

def is_recent_job(date_str, days_threshold=1):
    """
    Check if a job posting is recent (within the specified days threshold).
    Returns True if recent, False otherwise.
    """
    if not date_str:
        # If no date, assume it might be recent to be safe
        return True
    
    parsed_date = parse_job_date(date_str)
    if parsed_date is None:
        # If we can't parse the date, assume it might be recent
        return True
    
    # Check if the parsed date is within the threshold
    threshold_date = datetime.now() - timedelta(days=days_threshold)
    return parsed_date >= threshold_date

def fetch_jobs_for_specific_role(role):
    """Fetch jobs for a specific role from all sources"""
    role_jobs = []
    user_job_map = defaultdict(list)

    for source in CONFIG["SOURCES"]:
        print(f"🔍 Scraping {source['name']} for {role}...")
        
        try:
            url = source["url"].format(role=role.replace(" ", "%20"))
            res = requests.get(url, timeout=10)
            
            if res.status_code != 200:
                print(f"⚠️ HTTP {res.status_code} for {source['name']}")
                continue
            
            if source["type"] == "html_section":
                jobs = scrape_html_jobs(res, source, role)
            elif source["type"] == "json_selection":
                jobs = scrape_json_jobs(res, source, role)
            else:
                jobs = []
            
            print(f"📝 Found {len(jobs)} jobs from {source['name']}")

            for job_data in jobs:
                if is_valid_job(job_data):
                    try:
                        if Job.save_job(job_data):
                            role_jobs.append(job_data)
                            print(f"✅ New job saved: {job_data['title'][:50]}... at {job_data['company']}")

                            matching_users = User.find_matching_users(
                                job_data['title'], 
                                job_data['location']
                            )

                            date_str = job_data.get('date_posted', '')
                            try:
                                if is_recent_job(date_str, days_threshold=1):
                                    send_job_to_telegram(job_data)
                                    print(f"Job sent to Telegram. Date: {date_str}")
                                else:
                                    print(f"Job too old, skipping. Date: {date_str}")

                            except Exception as e:
                                print(f"⚠️ Could not parse job date: {e}")

                            for user in matching_users:
                                user_job_map[user['email']].append((user, job_data))
                        else:
                            print(f"⚠️ Job already exists or failed to save: {job_data['title'][:50]}...")
                    except Exception as e:
                        print(f"❌ Error processing job {job_data.get('title', 'Unknown')}: {e}")
                        continue

        except Exception as e:
            print(f"❌ Failed to scrape {source['name']} for {role}: {e}")
            continue

    return role_jobs, user_job_map

def scrape_html_jobs(response, source, role):
    """Scrape HTML-based job listings"""
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.select(source["selectors"]["container"])
        job_list = []
        
        for job in jobs:
            try:
                title = get_text(job, source["selectors"]["title"])
                location = get_text(job, source["selectors"]["location"])
                
                if title and location:
                    # Get company name safely
                    company = source["selectors"]["company"] if isinstance(source["selectors"]["company"], str) else get_text(job, source["selectors"]["company"])
                    
                    job_obj = {
                        "title": str(title).strip(),
                        "company": str(company).strip() if company else "Unknown",
                        "location": str(location).strip(),
                        "date_posted": str(get_text(job, source["selectors"]["date_posted"])).strip(),
                        "source": str(source["name"]).strip(),
                        "search_role": str(role).strip()
                    }
                    job_list.append(job_obj)
            except Exception as e:
                print(f"⚠️ Error processing individual job: {e}")
                continue
        
        return job_list
    except Exception as e:
        print(f"❌ Error scraping HTML jobs: {e}")
        return []

def scrape_json_jobs(response, source, role):
    """Scrape JSON-based job listings"""
    try:
        data = response.json()
        jobs = data.get(source['selectors']['field'], [])
        job_list = []
        
        for job in jobs:
            try:
                title = job.get(source['selectors']['title'])
                location = job.get(source['selectors']['location'])
                
                if title and location:
                    company = job.get("company_name", source["selectors"]['company'])
                    
                    job_obj = {
                        "title": str(title).strip(),
                        "company": str(company).strip() if company else "Unknown",
                        "location": str(location).strip(),
                        "date_posted": str(job.get(source['selectors']['date_posted'], "")).strip(),
                        "source": str(source["name"]).strip(),
                        "search_role": str(role).strip()
                    }
                    job_list.append(job_obj)
            except Exception as e:
                print(f"⚠️ Error processing individual JSON job: {e}")
                continue
        
        return job_list
    except Exception as e:
        print(f"❌ JSON parsing error: {e}")
        return []

def get_text(job_elem, selector):
    """Extract text from HTML element"""
    try:
        if isinstance(selector, str) and not selector.startswith('.') and not selector.startswith('#') and not selector.startswith('['):
            return str(selector).strip()  # It's a hardcoded value
        
        if job_elem is None:
            return ""
            
        elem = job_elem.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            # Clean the text
            text = text.replace('\x00', '').replace('\n', ' ').replace('\r', ' ')
            return text[:200]  # Limit length
        return ""
    except Exception as e:
        print(f"⚠️ Selector error for '{selector}': {e}")
        return ""

def is_valid_job(job_data):
    """Validate job data"""
    try:
        if not isinstance(job_data, dict):
            return False
            
        required_fields = ['title', 'company', 'location']
        for field in required_fields:
            if field not in job_data:
                return False
            if not job_data[field] or str(job_data[field]).strip() == "":
                return False
        
        # Check for reasonable length limits
        if len(str(job_data['title'])) > 200:
            return False
        if len(str(job_data['company'])) > 100:
            return False
        if len(str(job_data['location'])) > 100:
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error validating job data: {e}")
        return False
