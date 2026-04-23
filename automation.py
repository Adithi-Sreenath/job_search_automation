import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime
from notifier import send_telegram_msg

def run_omni_channel_search():
    queries = [
        "Strategy and Operations Analyst",
        "Associate Product Analyst",
        "Decision Science Associate",
        "Junior Data Scientist",
        "Analytics Engineer Trainee",
        "Product Operations Analyst",
        "Junior Data Engineer",
        "Associate Data Analyst",
        "Data Analyst Intern",
        "Associate Business Intelligence",
        "Business Intelligence Intern",
        "Junior Data Analyst",
        "Quantitative Analyst",
        "Growth Analyst"
    ]

    locations = ["Bengaluru, India", "Hyderabad, India", "Pune, India"]

    all_jobs = []

    for query in queries:
        for location in locations:
            print(f"Scraping '{query}' in {location}...")
            try:
                jobs = scrape_jobs(
                    site_name=["linkedin", "indeed"],
                    search_term=query,           # ✅ FIX 1: Use the loop variable
                    location=location,           # ✅ FIX 2: Single string, not a list
                    results_wanted=15,
                    hours_old=72,
                    country_indeed="India",      # ✅ FIX 3: Target India on Indeed
                    # Removed: is_remote, job_type (unreliable params)
                )
                if jobs is not None and not jobs.empty:
                    all_jobs.append(jobs)
            except Exception as e:
                print(f"  ⚠️ Error for '{query}' in {location}: {e}")

    if not all_jobs:
        print("No jobs found in this run.")
        return

    df = pd.concat(all_jobs).drop_duplicates(subset=["job_url"])
    print(f"Total raw jobs after dedup: {len(df)}")

    # Filter out non-technical / BPO / support roles
    blacklist = ["support", "kyc", "verification", "customer service", "voice", "bpo", "telecall"]
    df = df[~df["title"].str.contains("|".join(blacklist), case=False, na=False)]

    # Filter for technical stack mentions in description
    tech_keywords = ["SQL", "Python", "Power BI", "Tableau", "Data Analysis",
                     "Data Science", "Data Engineer", "ETL", "Dashboard", "Machine Learning"]
    df["is_technical"] = df["description"].str.contains("|".join(tech_keywords), case=False, na=False)
    final_list = df[df["is_technical"]]

    print(f"✅ Found {len(final_list)} qualified technical roles.")

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"Daily_Hunt_{date_str}.csv"
    final_list[["title", "company", "location", "job_url", "date_posted"]].to_csv(filename, index=False)
    print(f"Saved to {filename}")

    print("\n--- Also check these niche boards manually ---")
    print("Wellfound:  https://wellfound.com/jobs?role=Data+Analyst&location=Bengaluru&experience=0-1")
    print("Instahyre:  https://www.instahyre.com/jobs-in-bangalore/?skills=SQL,Python&exp=0")

    send_telegram_msg(final_list)

if __name__ == "__main__":
    run_omni_channel_search()