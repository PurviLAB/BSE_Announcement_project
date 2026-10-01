from bse_api import get_announcements
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


# ============================================================
# SETTINGS
# ============================================================

TRACKER_FILE = "sent_announcements.txt"

# Look back 7 days.
#
# This is intentional.
# If the program does not run for 1 or 2 days, it can still
# find the missed announcement.
#
# sent_announcements.txt prevents duplicate emails.
DAYS_BACK = 7


# ============================================================
# READ PREVIOUSLY SENT NEWS IDs
# ============================================================

def load_sent_news():

    if not os.path.exists(TRACKER_FILE):

        return set()

    try:

        with open(
            TRACKER_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return {
                line.strip()
                for line in f
                if line.strip()
            }

    except Exception as e:

        print(
            "Error reading tracker file:",
            e
        )

        return set()


# ============================================================
# SAVE NEWS ID
# ============================================================

def save_news_id(news_id):

    with open(
        TRACKER_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            str(news_id) + "\n"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load tracker ONCE when program starts
    # --------------------------------------------------------

    sent_news = load_sent_news()

    print()
    print("=" * 80)
    print("BSE ANNOUNCEMENT MONITOR")
    print("=" * 80)

    print(
        f"Previously sent announcements: "
        f"{len(sent_news)}"
    )

    print(
        f"Checking last {DAYS_BACK} days"
    )

    print("=" * 80)


    # ========================================================
    # CHECK EVERY COMPANY
    # ========================================================

    for company_name, scrip_code in COMPANIES.items():

        print()
        print()
        print("=" * 80)
        print("Checking:", company_name)
        print("BSE Scrip:", scrip_code)
        print("=" * 80)

        try:

            # ------------------------------------------------
            # GET ALL RECENT ANNOUNCEMENTS
            # ------------------------------------------------

            announcements = get_announcements(
                scrip_code,
                days_back=DAYS_BACK
            )

            if not announcements:

                print(
                    "No announcements found."
                )

                continue


            # ------------------------------------------------
            # FIND UNSENT ANNOUNCEMENTS
            # ------------------------------------------------

            unsent = []

            for announcement in announcements:

                news_id = str(
                    announcement.get(
                        "news_id",
                        ""
                    )
                ).strip()

                if not news_id:

                    continue

                if news_id in sent_news:

                    print(
                        f"Already sent: {news_id}"
                    )

                    continue

                unsent.append(
                    announcement
                )


            # ------------------------------------------------
            # NOTHING NEW
            # ------------------------------------------------

            if not unsent:

                print()
                print(
                    "No new announcements to email."
                )

                continue


            print()
            print(
                f"New announcements found: "
                f"{len(unsent)}"
            )


            # =================================================
            # EMAIL EACH UNSENT ANNOUNCEMENT
            # =================================================

            for announcement in unsent:

                news_id = str(
                    announcement["news_id"]
                ).strip()

                display_company = (
                    announcement.get(
                        "company"
                    )
                    or company_name
                )

                headline = (
                    announcement.get(
                        "headline"
                    )
                    or "New BSE Announcement"
                )

                date = announcement.get(
                    "date",
                    ""
                )

                category = announcement.get(
                    "category",
                    ""
                )

                subcategory = announcement.get(
                    "subcategory",
                    ""
                )

                pdf_urls = announcement.get(
                    "pdf_urls",
                    []
                )

                pdf_name = announcement.get(
                    "pdf_name",
                    f"{news_id}.pdf"
                )


                # =============================================
                # DISPLAY
                # =============================================

                print()
                print("-" * 80)
                print(
                    "PROCESSING ANNOUNCEMENT"
                )
                print("-" * 80)

                print(
                    "NEWSID     :",
                    news_id
                )

                print(
                    "Company    :",
                    display_company
                )

                print(
                    "Scrip Code :",
                    scrip_code
                )

                print(
                    "Headline   :",
                    headline
                )

                print(
                    "Date       :",
                    date
                )

                print(
                    "Category   :",
                    category
                )

                print(
                    "Subcategory:",
                    subcategory
                )


                # =============================================
                # CHECK PDF
                # =============================================

                if not pdf_urls:

                    print()
                    print(
                        "WARNING: No PDF attachment found."
                    )

                    print(
                        "Skipping this announcement."
                    )

                    print(
                        "NEWSID will NOT be saved."
                    )

                    continue


                # =============================================
                # DOWNLOAD PDF
                # =============================================

                try:

                    pdf_file, working_url = download_pdf(
                        pdf_urls,
                        pdf_name
                    )

                except Exception as e:

                    print()
                    print(
                        "PDF DOWNLOAD FAILED"
                    )

                    print(
                        "NEWSID:",
                        news_id
                    )

                    print(
                        "Error:",
                        e
                    )

                    print(
                        "NEWSID will NOT be saved."
                    )

                    continue


                print()
                print(
                    "Downloaded:",
                    pdf_file
                )


                # =============================================
                # EMAIL SUBJECT
                # =============================================

                subject = (
                    f"New Announcement - "
                    f"{display_company} - "
                    f"{headline}"
                )


                # =============================================
                # EMAIL BODY
                # =============================================

                body = f"""
New Announcement

Company:
{display_company}

BSE Scrip Code:
{scrip_code}

NEWS ID:
{news_id}

Headline:
{headline}

Date:
{date}

Category:
{category}

Subcategory:
{subcategory}

PDF Link:
{working_url}
"""


                # =============================================
                # SEND EMAIL
                # =============================================

                print()
                print(
                    "Sending email..."
                )

                print(
                    "Subject:",
                    subject
                )

                try:

                    send_email(
                        subject=subject,
                        body=body,
                        attachment=pdf_file
                    )

                except Exception as e:

                    print()
                    print(
                        "EMAIL FAILED"
                    )

                    print(
                        "NEWSID:",
                        news_id
                    )

                    print(
                        "Error:",
                        e
                    )

                    print(
                        "NEWSID will NOT be saved."
                    )

                    continue


                # =============================================
                # EMAIL SUCCESS
                # =============================================
                #
                # IMPORTANT:
                #
                # Only save NEWSID AFTER successful email.
                #
                # Therefore:
                #
                # email failed -> not saved
                # email succeeded -> saved
                #
                # This prevents losing announcements.
                # =============================================

                save_news_id(
                    news_id
                )

                sent_news.add(
                    news_id
                )

                print()
                print(
                    "NEWSID saved:",
                    news_id
                )

                print(
                    "Email sent successfully!"
                )


        except Exception as e:

            # ------------------------------------------------
            # COMPANY ERROR
            # ------------------------------------------------

            print()
            print(
                f"ERROR for {company_name}:"
            )

            print(
                type(e).__name__,
                ":",
                e
            )

            print(
                "Continuing with next company..."
            )

            continue


    # ========================================================
    # FINISHED
    # ========================================================

    print()
    print()
    print("=" * 80)
    print(
        "BSE ANNOUNCEMENT MONITORING COMPLETED"
    )
    print("=" * 80)

    print(
        "Total NEWSIDs saved:",
        len(sent_news)
    )

    print("=" * 80)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()
