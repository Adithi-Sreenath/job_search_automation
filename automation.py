# pip install python-jobspy pandas requests
from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import requests

def run_omni_channel_search():
    # 1. Target Titles (Strictly Entry Level / No Experience)
    queries = [
        "Strategy and Operations Analyst", 
        "Associate Product Analyst",
        "Decision Science Associate",
        "Junior Data Scientist",
        "Analytics Engineer Trainee",
        "Product operations analyst",
        "junior data engineer",
        "Associate data analyst"
        "data analyst intern",
        "Associate Business Intelligence",
        "Business Intelligence intern",
        "junior data analyst",
        "Qunatitative Analyst",
        "Growth analyst"
    ]
    
    # 2. Scrape Aggregators (LinkedIn, Indeed, Glassdoor, Google Jobs)
    all_jobs = []
    for query in queries:
        print(f"Scouting {query}...")
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "glassdoor", "google"],
            search_term=query,
            location="Bengaluru, India",
            results_wanted=20,
            hours_old=24, # We only want the fresh daily drops
            country_seniority_filter="entry_level"
        )
        all_jobs.append(jobs)

    df = pd.concat(all_jobs).drop_duplicates(subset=['job_url'])

    # 3. Apply the "Engineering" Filter (Excluding Support/KYC)
    blacklist = ["support", "kyc", "verification", "customer service", "voice", "bpo"]
    df = df[~df['title'].str.contains('|'.join(blacklist), case=False)]

    # 4. Filter for your Specific Tech Stack (SQL/Python/Git)
    # This ensures you aren't looking at "Excel-only" roles
    tech_filter = ["SQL", "Python", "Power BI", "Models", "Data Analysis", "Data Science", "Data Engineer", "ETL", "Dashboards"]
    df['is_technical'] = df['description'].str.contains('|'.join(tech_filter), case=False)
    final_list = df[df['is_technical'] == True]

    # 5. Generate Niche Board Direct Links (Naukri, Instahyre, Wellfound)
    # These sites don't allow easy scraping, so we generate the "Filtered Search URL"
    niche_links = {
        "Wellfound (Startups)": "https://wellfound.com/jobs?role=Data+Analyst&location=Bengaluru&experience=0-1",
        "Instahyre (Tech)": "https://www.instahyre.com/jobs-in-bangalore/?skills=SQL,Python&exp=0",
        "FreshersHunt (MNC Drives)": "https://freshershunt.in/category/jobs-by-batch/2026-batch/"
    }

    # 6. Output Results
    print(f"Done! Found {len(final_list)} fresh technical roles.")
    final_list[['title', 'company', 'job_url']].to_csv(f"Daily_Hunt_{datetime.now().strftime('%Y-%m-%d')}.csv")

# Run the system
run_omni_channel_search()