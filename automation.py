import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime
from notifier import send_telegram_msg

SENIORITY_BLACKLIST = [
    "senior", "sr.", "sr ", "lead", "principal", "staff", "manager",
    "director", "head of", "vp ", "vice president",
    " ii", " iii", " iv", " 2", " 3",
    "experienced", "mid-level"
]

ROLE_BLACKLIST = [
    "support", "kyc", "verification", "customer service",
    "voice", "bpo", "telecall"
]

TECH_KEYWORDS = [
    "SQL", "Python", "Power BI", "Tableau", "Data Analysis",
    "Data Science", "ETL", "Dashboard", "Machine Learning",
    "Analytics", "Excel", "Looker", "Spark", "BigQuery"
]

def is_entry_level(title: str) -> bool:
    title_lower = title.lower()
    if any(word in title_lower for word in SENIORITY_BLACKLIST):
        return False
    return True  # neutral titles like "Data Analyst" are fine


def is_technical(row) -> bool:
    """Check title AND description — description is often None on scraped jobs."""
    title = str(row.get("title", ""))
    description = str(row.get("description", ""))

    # Title alone is enough — "Data Analyst" is inherently technical
    title_is_technical = any(
        kw.lower() in title.lower() for kw in TECH_KEYWORDS + [
            "analyst", "engineer", "scientist", "intelligence", "analytics"
        ]
    )
    # Description is a bonus check, not a hard requirement
    desc_is_technical = any(kw.lower() in description.lower() for kw in TECH_KEYWORDS)

    return title_is_technical or desc_is_technical  # ✅ OR not AND


def run_omni_channel_search():
    queries = [
        "Junior Data Analyst",
        "Associate Data Analyst",
        "Data Analyst Intern",
        "Junior Data Scientist",
        "Associate Business Intelligence Analyst",
        "Business Intelligence Intern",
        "Junior Data Engineer",
        "Associate Product Analyst",
        "Growth Analyst",
        "Decision Science Associate",
        "Quantitative Analyst",
        "Analytics Trainee",
        "Data Analyst fresher",
        "Entry Level Data Analyst",
    ]

    locations = ["Bengaluru, India", "Hyderabad, India", "Pune, India"]

    all_jobs = []

    for query in queries:
        for location in locations:
            print(f"Scraping '{query}' in {location}...")
            try:
                jobs = scrape_jobs(
                    site_name=["linkedin", "indeed"],
                    search_term=query,
                    location=location,
                    results_wanted=15,
                    hours_old=72,
                    country_indeed="India",
                )
                if jobs is not None and not jobs.empty:
                    all_jobs.append(jobs)
                    print(f"  → {len(jobs)} found")
            except Exception as e:
                print(f"  ⚠️ Error for '{query}' in {location}: {e}")

    if not all_jobs:
        print("No jobs found.")
        return

    df = pd.concat(all_jobs).drop_duplicates(subset=["job_url"])
    print(f"\nRaw after dedup:         {len(df)}")

    # Filter 1 — BPO / support roles
    df = df[~df["title"].str.contains("|".join(ROLE_BLACKLIST), case=False, na=False)]
    print(f"After role blacklist:     {len(df)}")

    # Filter 2 — Seniority (title only)
    df = df[df["title"].apply(is_entry_level)]
    print(f"After seniority filter:   {len(df)}")

    # Filter 3 — Technical (title OR description, not just description)
    df["is_technical"] = df.apply(is_technical, axis=1)
    final_list = df[df["is_technical"]].copy()
    print(f"After technical filter:   {len(final_list)}")
    print(f"\n✅ Sending {len(final_list)} roles to Telegram")

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"Daily_Hunt_{date_str}.csv"
    final_list[["title", "company", "location", "job_url", "date_posted"]].to_csv(
        filename, index=False
    )
    print(f"Saved → {filename}")

    print("\n--- Manual niche board checks ---")
    print("Wellfound:  https://wellfound.com/jobs?role=Data+Analyst&location=Bengaluru&experience=0-1")
    print("Instahyre:  https://www.instahyre.com/jobs-in-bangalore/?skills=SQL,Python&exp=0")

    send_telegram_msg(final_list)


if __name__ == "__main__":
    run_omni_channel_search()