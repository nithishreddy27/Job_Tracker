
# config.py

CONFIG = {
    "SOURCES": [
        {
            "name": "Walmart Careers",
            "url": "https://careers.walmart.com/api/search?q={role}&page=1&sort=rank&expand=department,brand,type,rate&jobCareerArea=0000015e-b97d-d143-af5e-bd7da8ca0000&type=jobs",
            "type": "html_section",
            "selectors": {
                "container": "li.search-result.job-listing",
                "title": ".job-listing__title",
                "company": ".job-listing-logo",
                "location": ".job-listing__location",
                "date_posted": ".job-listing__created"
            }
        },
        {
            "name": "Amazon Careers",
            "url": "https://www.amazon.jobs/en/search.json?radius=24km&facets%5B%5D=normalized_country_code&facets%5B%5D=normalized_state_name&facets%5B%5D=normalized_city_name&facets%5B%5D=location&facets%5B%5D=business_category&facets%5B%5D=category&facets%5B%5D=schedule_type_id&facets%5B%5D=employee_class&facets%5B%5D=normalized_location&facets%5B%5D=job_function_id&facets%5B%5D=is_manager&facets%5B%5D=is_intern&offset=0&result_limit=10&sort=relevant&latitude=&longitude=&loc_group_id=&loc_query=&base_query={role}&city=&country=&region=&county=&query_options=&",
            "type": "json_selection",
            "selectors": {
                "title": "title",
                "company": "Amazon",
                "location": "location",
                "date_posted": "posted_date",
                "field": "jobs"
            }
        },
        {
            "name": "Verizon Careers",
            "url": "https://mycareer.verizon.com/jobs/?search={role}&location=",
            "type": "html_section",
            "selectors": {
                "container": ".card.card-job",
                "title": ".card-title",
                "company": "Verizon",
                "location": ".list-inline-item",
                "date_posted": ".list-inline-item"
            }
        },
        {
            "name": "Apple Careers",
            "url": "https://jobs.apple.com/en-us/search?search={role}&sort=relevance&location=united-states-USA",
            "type": "html_section",
            "selectors": {
                "container": ".job-title.job-list-item",
                "title": ".link-inline",
                "company": "Apple",
                "location": ".job-title-location span",
                "date_posted": ".job-posted-date"
            }
        },
          
    ],
    "MONGO_URI": "mongodb+srv://nithishreddygade:WsVhXD4PNm5cUPMc@database.awx894c.mongodb.net/",
    "DB_NAME": "job_tracker",
    "COLLECTION_NAME": "jobs",
    "USERS_COLLECTION_NAME": "users",
    "EMAIL": {
        "sender": "nithishreddygade@gmail.com",
        "password": "uluz bddd bjro clcw"
    },
    "JOB_ROLES": [
        "full stack developer",
        "frontend developer",
        "backend developer",
        "data scientist",
        "machine learning engineer",
        "devops engineer",
        "software engineer",
        "product manager",
        "ui/ux designer",
        "mobile developer"
    ],
    "JOB_TYPES": ["full-time", "intern", "contract", "part-time"],
    "LOCATIONS": [
        "New York, NY",
        "San Francisco, CA",
        "Seattle, WA",
        "Austin, TX",
        "Chicago, IL",
        "Boston, MA",
        "Los Angeles, CA",
        "Remote",
        "Denver, CO",
        "Atlanta, GA"
    ],
      "TELEGRAM": {
        "BOT_TOKEN": "7369620106:AAHHJdXULA_dkyTntUIn9wouNjpSS1Jcvjk",
        "CHANNEL_ID": "@usa_jobs_alert"
    }
}
