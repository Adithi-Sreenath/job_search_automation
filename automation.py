# pip install python-jobspy pandas requests
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime
from notifier import send_telegram_msg
import requests


def run_omni_channel_search():
    # 1. Target Titles (Strictly Entry Level / No Experience)
    # FIXED: Added missing commas and corrected "Quantitative"
    queries = [
        "Strategy and Operations Analyst", 
        "Associate Product Analyst",
        "Decision Science Associate",
        "Junior Data Scientist",
        "Analytics Engineer Trainee",
        "Product operations analyst",
        "junior data engineer",
        "Associate data analyst", # Fixed missing comma
        "data analyst intern",
        "Associate Business Intelligence",
        "Business Intelligence intern",
        "junior data analyst",
        "Quantitative Analyst", # Fixed typo
        "Growth analyst"
    ]
    
    all_jobs = []
    
    # 2. Scrape Aggregators (LinkedIn, Indeed, Glassdoor, Google Jobs)
    for query in queries:
        print(f"Scouting {query}...")
        try:
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "glassdoor", "google"],
                search_term=query,
                location="Bengaluru, India",
                results_wanted=15, # Keeping it lean for speed
                hours_old=24, 
                country_seniority_filter="entry_level"
            )
            all_jobs.append(jobs)
        except Exception as e:
            print(f"Error scouting {query}: {e}")

    if not all_jobs:
        print("No jobs found in this run.")
        return

    df = pd.concat(all_jobs).drop_duplicates(subset=['job_url'])

    # 3. Apply the "Engineering" Filter (Excluding Support/KYC/BPO)
    # Added "telecall" and "voice" to keep it strictly technical
    blacklist = ["support", "kyc", "verification", "customer service", "voice", "bpo", "telecall"]
    df = df[~df['title'].str.contains('|'.join(blacklist), case=False, na=False)]

    # 4. Filter for Technical Stack (Ensures you don't get 'Excel-only' roles)
    tech_filter = ["SQL", "Python", "Power BI", "Models", "Data Analysis", "Data Science", "Data Engineer", "ETL", "Dashboards"]
    df['is_technical'] = df['description'].str.contains('|'.join(tech_filter), case=False, na=False)
    final_list = df[df['is_technical'] == True]

    # 5. Generate Output
    print(f"Done! Found {len(final_list)} fresh technical roles.")
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"Daily_Hunt_{date_str}.csv"
    final_list[['title', 'company', 'job_url']].to_csv(filename, index=False)
    
    # 6. Summary of Niche Boards (Manual Check needed for these)
    print("\n--- Manual Check Niche Boards ---")
    print("Wellfound: https://wellfound.com/jobs?role=Data+Analyst&location=Bengaluru&experience=0-1")
    print("Instahyre: https://www.instahyre.com/jobs-in-bangalore/?skills=SQL,Python&exp=0")
    # 6. Trigger Notification
    send_telegram_msg(final_list)

# Run the system
if __name__ == "__main__":
    run_omni_channel_search()