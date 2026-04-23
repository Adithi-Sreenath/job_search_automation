import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime
from notifier import send_telegram_msg

# ✅ Seniority blacklist — drop anything that looks senior/mid-level
SENIORITY_BLACKLIST = [
    "senior", "sr.", "sr ", "lead", "principal", "staff", "manager",
    "director", "head of", "vp ", "vice president",
    "ii", "iii", "iv", "2", "3",          # "Data Engineer II", "Analyst 2"
    "experienced", "mid-level", "5+ years", "7+ years", "8+ years"
]

# ✅ Role blacklist — non-technical / BPO / irrelevant
ROLE_BLACKLIST = [
    "support", "kyc", "verification", "customer service",
    "voice", "bpo", "telecall", "sales", "marketing"
]

# ✅ Entry-level signal whitelist — title must contain at least one of these
ENTRY_LEVEL_SIGNALS = [
    "junior", "jr", "associate", "intern", "trainee",
    "entry", "fresher", "graduate", "assistant", "apprentice"
]

# ✅ Tech stack must appear in description
TECH_KEYWORDS = [
    "SQL", "Python", "Power BI", "Tableau", "Data Analysis",
    "Data Science", "ETL", "Dashboard", "Machine Learning", "Excel"
]

def is_entry_level(title: str) -> bool:
    title_lower = title.lower()

    # Hard reject if any seniority word found
    if any(word in title_lower for word in SENIORITY_BLACKLIST):
        return False

    # Accept if any entry-level signal found
    if any(word in title_lower for word in ENTRY_LEVEL_SIGNALS):
        return True

    # For neutral titles like "Data Analyst" (no junior/senior) — allow through
    # These are often genuinely open to freshers in India
    return True


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
        "Quantitative Analyst fresher",
        "Analytics Trainee",
        "Data Analyst fresher",           # ← "fresher" keyword helps on Indian job boards
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
            except Exception as e:
                print(f"  ⚠️ Error for '{query}' in {location}: {e}")

    if not all_jobs:
        print("No jobs found.")
        return

    df = pd.concat(all_jobs).drop_duplicates(subset=["job_url"])
    print(f"Raw jobs after dedup: {len(df)}")

    # ── FILTER 1: Drop role blacklist (BPO, support etc.) ──────────────────
    df = df[~df["title"].str.contains("|".join(ROLE_BLACKLIST), case=False, na=False)]

    # ── FILTER 2: Drop senior/mid-level by title ────────────────────────────
    df = df[df["title"].apply(is_entry_level)]
    print(f"After seniority filter: {len(df)}")

    # ── FILTER 3: Must mention technical stack in description ───────────────
    df["is_technical"] = df["description"].str.contains(
        "|".join(TECH_KEYWORDS), case=False, na=False
    )
    final_list = df[df["is_technical"]].copy()
    print(f"✅ Final qualified fresher roles: {len(final_list)}")

    # ── OUTPUT ───────────────────────────────────────────────────────────────
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