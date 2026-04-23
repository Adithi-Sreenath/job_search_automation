import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_telegram_msg(df):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("⚠️ Telegram credentials missing in .env")
        return

    if df.empty:
        message = "📉 No new technical roles found in Bengaluru today."
    else:
        # Get top 8 roles to stay within Telegram character limits
        top_jobs = df.head(8)
        message = f"🚀 **{len(df)} New Technical Roles Found!**\n\n"
        
        for _, row in top_jobs.iterrows():
            job_entry = (
                f"🔹 **{row['title']}**\n"
                f"🏢 {row['company']}\n"
                f"🔗 [Apply Here]({row['job_url']})\n"
                f"--- \n"
            )
            message += job_entry

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram notification sent!")
        else:
            print(f"❌ Failed to send Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")