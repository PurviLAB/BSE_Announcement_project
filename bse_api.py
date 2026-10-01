import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin


BASE_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.bseindia.com/",
    "Origin": "https://www.bseindia.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}


# ============================================================
# HELPER - GET VALUE FROM DICTIONARY
# ============================================================

def get_value(data, *keys):
    """
    Return the first non-empty value from the supplied keys.
    """

    for key in keys:
        value = data.get(key)

        if value is not None and str(value).strip() != "":
            return value

    return ""


# ============================================================
# CREATE PDF URL
# ============================================================

def create_pdf_url(attachment_name):
    """
    Convert BSE ATTACHMENTNAME into a PDF URL.
    """

    if not attachment_name:
        return ""

    attachment_name = str(attachment_name).strip()

    # If BSE already gives a complete URL
    if attachment_name.startswith("http://"):
        return attachment_name

    if attachment_name.startswith("https://"):
        return attachment_name

    # BSE attachment names normally point to AttachLive
    return (
        "https://www.bseindia.com/"
        "xml-data/corpfiling/AttachLive/"
        + attachment_name
    )


# ============================================================
# NORMALIZE BSE ANNOUNCEMENT
# ============================================================

def normalize_announcement(item):
    """
    Convert the raw BSE response into a common format
    used by app.py.
    """

    news_id = get_value(
        item,
        "NEWSID",
        "NewsID",
        "news_id",
        "NEWS_ID"
    )

    scrip_code = get_value(
        item,
        "SCRIP_CD",
        "SCRIPCODE",
        "ScripCode",
        "scrip_code"
    )

    company = get_value(
        item,
        "SLONGNAME",
        "LONG_NAME",
        "COMPANYNAME",
        "company"
    )

    headline = get_value(
        item,
        "HEADLINE",
        "NEWSSUB",
        "NEWS_SUB",
        "headline"
    )

    date = get_value(
        item,
        "NEWS_DT",
        "DT_TM",
        "DissemDT",
        "News_submission_dt",
        "date"
    )

    category = get_value(
        item,
        "CATEGORYNAME",
        "CATEGORY",
        "category"
    )

    subcategory = get_value(
        item,
        "SUBCATNAME",
        "SUBCATEGORYNAME",
        "SUBCATEGORY",
        "subcategory"
    )

    attachment_name = get_value(
        item,
        "ATTACHMENTNAME",
        "AttachmentName",
        "attachment_name"
    )

    pdf_url = create_pdf_url(attachment_name)

    # Sometimes MORE can contain a PDF/document URL.
    more = get_value(
        item,
        "MORE",
        "more"
    )

    if not pdf_url and more:
        more_text = str(more).strip()

        if "http://" in more_text or "https://" in more_text:
            parts = more_text.replace('"', " ").split()

            for part in parts:
                if part.startswith("http://") or part.startswith("https://"):
                    if ".pdf" in part.lower():
                        pdf_url = part.strip()
                        break

    # Use NEWSID as the safest unique filename component.
    safe_news_id = str(news_id).replace("/", "_").replace("\\", "_")

    pdf_name = (
        f"{safe_news_id}.pdf"
        if safe_news_id
        else "bse_announcement.pdf"
    )

    return {
        "news_id": str(news_id).strip(),
        "scrip_code": str(scrip_code).strip(),
        "company": str(company).strip(),
        "headline": str(headline).strip(),
        "date": str(date).strip(),
        "category": str(category).strip(),
        "subcategory": str(subcategory).strip(),
        "pdf_urls": [pdf_url] if pdf_url else [],
        "pdf_name": pdf_name,
        "raw": item,
    }


# ============================================================
# GET ALL ANNOUNCEMENTS FOR A COMPANY
# ============================================================

def get_announcements(
    scrip_code,
    days_back=7,
    max_pages=20
):
    """
    Fetch multiple announcements for a company.

    The program looks back `days_back` days so that if the
    daily program misses one run, it can still find the
    announcement later.

    BSE returns announcement data page-by-page, therefore
    multiple pages are requested.
    """

    scrip_code = str(scrip_code).strip()

    today = datetime.now().date()
    from_date = today - timedelta(days=days_back)

    str_prev_date = from_date.strftime("%Y%m%d")
    str_to_date = today.strftime("%Y%m%d")

    all_announcements = []
    seen_ids = set()

    session = requests.Session()
    session.headers.update(HEADERS)

    print(
        f"Fetching BSE announcements for {scrip_code} "
        f"from {str_prev_date} to {str_to_date}"
    )

    for page_no in range(1, max_pages + 1):

        params = {
            "pageno": page_no,
            "strCat": "-1",
            "subcategory": "-1",
            "strPrevDate": str_prev_date,
            "strScrip": scrip_code,
            "strSearch": "P",
            "strToDate": str_to_date,
            "strType": "C",
        }

        try:

            response = session.get(
                BASE_URL,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

        except Exception as e:

            print(
                f"Error fetching BSE page {page_no} "
                f"for {scrip_code}: {e}"
            )

            break

        # ----------------------------------------------------
        # BSE ERROR MESSAGE
        # ----------------------------------------------------

        if isinstance(data, dict):

            status = data.get("Status")

            if status is False:

                print(
                    "BSE Status:",
                    status
                )

                print(
                    "BSE Message:",
                    data.get("Message")
                )

                break

        # ----------------------------------------------------
        # GET TABLE
        # ----------------------------------------------------

        table = []

        if isinstance(data, dict):

            table = data.get("Table", [])

        if not table:

            print(
                f"No more announcements after page {page_no}."
            )

            break

        print(
            f"Page {page_no}: "
            f"{len(table)} announcements"
        )

        # ----------------------------------------------------
        # PROCESS PAGE
        # ----------------------------------------------------

        for item in table:

            if not isinstance(item, dict):
                continue

            announcement = normalize_announcement(item)

            news_id = announcement["news_id"]

            # Ignore records without NEWSID
            if not news_id:
                continue

            # Avoid duplicate records across pages
            if news_id in seen_ids:
                continue

            # Confirm company/scrip when BSE returns it
            item_scrip = announcement["scrip_code"]

            if item_scrip and item_scrip != scrip_code:
                continue

            seen_ids.add(news_id)

            all_announcements.append(
                announcement
            )

        # ----------------------------------------------------
        # STOP WHEN PAGE IS SMALL
        # ----------------------------------------------------
        #
        # Normally this means we reached the last page.
        # We still allow the next page if needed.
        # The empty page above is the final safeguard.
        # ----------------------------------------------------

    session.close()

    # --------------------------------------------------------
    # SORT OLDEST -> NEWEST
    # --------------------------------------------------------
    #
    # This means if 4 announcements were missed, the oldest
    # one is emailed first, followed by the newer ones.
    # --------------------------------------------------------

    def sort_key(item):

        return (
            item.get("date", ""),
            item.get("news_id", "")
        )

    all_announcements.sort(
        key=sort_key
    )

    print(
        f"Total announcements found for {scrip_code}: "
        f"{len(all_announcements)}"
    )

    return all_announcements


# ============================================================
# BACKWARD-COMPATIBLE FUNCTION
# ============================================================

def get_latest_announcement(scrip_code):
    """
    Kept for compatibility with older versions of app.py.

    Returns the newest announcement only.
    The new app.py uses get_announcements() instead.
    """

    announcements = get_announcements(
        scrip_code,
        days_back=7
    )

    if not announcements:
        return None

    return announcements[-1]
