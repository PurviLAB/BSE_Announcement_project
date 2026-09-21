from bse_api import get_latest_announcement
from downloader import download_pdf
from email_service import send_email
import os


# ============================================================
# COMPANIES TO MONITOR
# ============================================================

COMPANIES = {
    "Home First Finance Company India Limited": "543259",
    "Gokak Textiles Limited": "532957",
    "HDFC Bank Limited": "500180",
    "Jana Small Finance Bank Limited": "544118",
}

TRACKER_FILE = "sent_announcements.txt"


# ============================================================
# READ PREVIOUSLY SENT NEWS IDs
# ============================================================

if os.path.exists(TRACKER_FILE):

    with open(TRACKER_FILE, "r") as f:
        sent_news = {
            line.strip()
            for line in f
            if line.strip()
        }

else:
    sent_news = set()


# ============================================================
# CHECK ALL COMPANIES
# ============================================================

for company_name, scrip_code in COMPANIES.items():

    print()
    print("=" * 70)
    print("Checking:", company_name)
  
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # Get latest announcement
        # ----------------------------------------------------

        announcement = get_latest_announcement(
            scrip_code
        )

        news_id = str(
            announcement["news_id"]
        )


        # ----------------------------------------------------
        # Skip already sent announcement
        # ----------------------------------------------------

        if news_id in sent_news:

            print(
                "Announcement already emailed."
            )

            print(
                "Skipping email..."
            )

            continue


        # ----------------------------------------------------
        # Get company name
        # ----------------------------------------------------

        display_company = (
            announcement.get("company")
            or company_name
        )


        # ----------------------------------------------------
        # Get headline
        # ----------------------------------------------------

        headline = (
            announcement.get("headline")
            or "New BSE Announcement"
        )


        # ----------------------------------------------------
        # Display announcement
        # ----------------------------------------------------

        print()
        print("LATEST ANNOUNCEMENT")
        print("-" * 70)

        print(
            "Company  :",
            display_company
        )

        print(
            "Headline :",
            headline
        )

        print(
            "Date     :",
            announcement.get("date")
        )

        print(
            "Category :",
            announcement.get("category")
        )


        # ----------------------------------------------------
        # Download PDF
        # ----------------------------------------------------

        pdf_file, working_url = download_pdf(
            announcement["pdf_urls"],
            announcement["pdf_name"]
        )

        print(
            "Downloaded:",
            pdf_file
        )


        # ====================================================
        # EMAIL SUBJECT
        # ====================================================

        subject = (
            f"New Announcement - "
            f"{display_company} - "
            f"{headline}"
        )


        # ====================================================
        # EMAIL BODY
        # ====================================================

        body = f"""
New Announcement

Company:
{display_company}

BSE Scrip Code:
{scrip_code}

Headline:
{headline}

Date:
{announcement.get("date")}

Category:
{announcement.get("category")}

Subcategory:
{announcement.get("subcategory")}

PDF Link:
{working_url}
"""


        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        print()
        print("Sending email...")
        print("Subject:", subject)

        send_email(
            subject=subject,
            body=body,
            attachment=pdf_file
        )


        # ----------------------------------------------------
        # Save NEWSID after successful email
        # ----------------------------------------------------

        with open(
            TRACKER_FILE,
            "a"
        ) as f:

            f.write(
                news_id + "\n"
            )


        sent_news.add(
            news_id
        )


        print()
        print("NEWSID saved.")
        print("Email sent successfully!")


    except Exception as e:

        print()
        print(
            f"ERROR for {company_name}:"
        )

        print(e)

        # Continue checking the next company
        continue


# ============================================================
# FINISHED
# ============================================================

print()
print("=" * 70)
print("BSE ANNOUNCEMENT MONITORING COMPLETED")
print("=" * 70)