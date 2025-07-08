from pymongo import MongoClient
from config import CONFIG
from datetime import datetime
import hashlib
import copy
client = MongoClient(CONFIG["MONGO_URI"])
db = client[CONFIG["DB_NAME"]]
jobs_collection = db[CONFIG["COLLECTION_NAME"]]
users_collection = db[CONFIG["USERS_COLLECTION_NAME"]]

class User:
    @staticmethod
    def create_user(email, job_roles, job_types, locations):
        """Create a new user with preferences"""
        user_data = {
            "email": email,
            "job_roles": job_roles,
            "job_types": job_types,
            "locations": locations,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "active": True
        }
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            # Update existing user
            users_collection.update_one(
                {"email": email},
                {"$set": {
                    "job_roles": job_roles,
                    "job_types": job_types,
                    "locations": locations,
                    "updated_at": datetime.now()
                }}
            )
            return "updated"
        else:
            users_collection.insert_one(user_data)
            return "created"
    
    @staticmethod
    def get_all_users():
        """Get all active users"""
        return list(users_collection.find({"active": True}))
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        return users_collection.find_one({"email": email})
    
    @staticmethod
    def get_all_unique_roles():
        """Get all unique job roles from all users"""
        pipeline = [
            {"$unwind": "$job_roles"},
            {"$group": {"_id": "$job_roles"}},
            {"$sort": {"_id": 1}}
        ]
        return [doc["_id"] for doc in users_collection.aggregate(pipeline)]
    
    @staticmethod
    def find_matching_users(job_title, job_location, job_type="full-time"):
        """Find users who match the job criteria"""
        base_query = {
            "active": True,
            "$or": [
                {"job_roles": {"$regex": job_title, "$options": "i"}},
                {"job_roles": {"$in": [role for role in CONFIG["JOB_ROLES"] if role.lower() in job_title.lower()]}}
            ]
        }

        if job_location and job_location != "Remote":
            location_query = {
                "$or": [
                    {"locations": {"$regex": job_location, "$options": "i"}},
                    {"locations": "Remote"}
                ]
            }
            query = {
                "$and": [copy.deepcopy(base_query), location_query]
            }
        else:
            query = base_query

        return list(users_collection.find(query))
    
    
class Job:
    @staticmethod
    def create_job_hash(title, company, location, date_posted):
        """Create a unique hash for job identification"""
        # Clean and normalize the data before hashing
        title = str(title).strip() if title else ""
        company = str(company).strip() if company else ""
        location = str(location).strip() if location else ""
        date_posted = str(date_posted).strip() if date_posted else ""
        
        job_string = f"{title}_{company}_{location}_{date_posted}"
        return hashlib.md5(job_string.encode('utf-8')).hexdigest()
    
    @staticmethod
    def job_exists(job_hash):
        """Check if job already exists in database"""
        try:
            return jobs_collection.find_one({"job_hash": job_hash}) is not None
        except Exception as e:
            print(f"❌ Error checking job existence: {e}")
            return False
    
    @staticmethod
    def clean_job_data(job_data):
        """Clean job data to prevent BSON encoding issues"""
        cleaned_data = {}
        
        # Define allowed fields and their types
        allowed_fields = {
            "title": str,
            "company": str,
            "location": str,
            "date_posted": str,
            "source": str,
            "search_role": str,
            "job_hash": str,
            "created_at": datetime
        }
        
        # Clean each field
        for field, expected_type in allowed_fields.items():
            if field in job_data:
                try:
                    if expected_type == str:
                        # Convert to string and clean
                        value = str(job_data[field]).strip() if job_data[field] else ""
                        # Remove any problematic characters
                        value = value.replace('\x00', '').replace('\n', ' ').replace('\r', ' ')
                        cleaned_data[field] = value[:500]  # Limit length
                    elif expected_type == datetime:
                        cleaned_data[field] = job_data[field]
                except Exception as e:
                    print(f"⚠️ Error cleaning field {field}: {e}")
                    if expected_type == str:
                        cleaned_data[field] = ""
        
        return cleaned_data
    
    @staticmethod
    def save_job(job_data):

        """Save job to database with proper error handling"""
        try:
            # Clean the job data first
            cleaned_data = Job.clean_job_data(job_data)
            
            # Create job hash
            job_hash = Job.create_job_hash(
                cleaned_data.get("title", ""),
                cleaned_data.get("company", ""),
                cleaned_data.get("location", ""),
                cleaned_data.get("date_posted", "")
            )
            
            # Check if job already exists
            if not Job.job_exists(job_hash):
                cleaned_data["job_hash"] = job_hash
                cleaned_data["created_at"] = datetime.now()
                
                # Insert with error handling
                result = jobs_collection.insert_one(cleaned_data)
                if result.inserted_id:
                    return True
                else:
                    print("❌ Failed to insert job - no ID returned")
                    return False
            else:
                print(f"⚠️ Job already exists: {cleaned_data.get('title', 'Unknown')}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving job: {e}")
            print(f"❌ Job data: {job_data}")
            return False
        
