import requests
from datetime import datetime, timedelta


# ============================================================
# BSE API
# ============================================================

BASE_URL = (
    "https://api.bseindia.com/"
    "BseIndiaAPI/api/AnnSubCategoryGetData/w"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.bseindia.com/",
    "Origin": "https://www.bseindia.com",
}


# ============================================================
# SESSION
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# DATE PARSER
# ============================================================

def parse_date(value):

    if not value:
        return datetime.min

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except Exception:
        pass

    try:
        return datetime.strptime(
            value[:19],
            "%Y-%m-%dT%H:%M:%S"
        )
    except Exception:
        return datetime.min


# ============================================================
# GET LATEST ANNOUNCEMENT
# ============================================================

def get_latest_announcement(scrip_code):

    scrip_code = str(scrip_code)

    print(
        f"Checking BSE announcements for {scrip_code}"
    )

    # --------------------------------------------------------
    # Open BSE website first
    # --------------------------------------------------------

    try:
        session.get(
            "https://www.bseindia.com/",
            timeout=30
        )
    except Exception:
        pass

    # --------------------------------------------------------
    # Date range - last 30 days
    #
    # BSE requires YYYYMMDD
    # --------------------------------------------------------

    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)

    from_date_string = from_date.strftime("%Y%m%d")
    to_date_string = to_date.strftime("%Y%m%d")

    print(
        f"Date range: {from_date_string} "
        f"to {to_date_string}"
    )

    # --------------------------------------------------------
    # BSE request
    # --------------------------------------------------------

    params = {
        "pageno": 1,
        "strCat": -1,
        "strPrevDate": from_date_string,
        "strScrip": scrip_code,
        "strSearch": "P",
        "strToDate": to_date_string,
        "strType": "C"
    }

    try:

        response = session.get(
            BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as e:

        raise Exception(
            f"BSE API connection error: {e}"
        )

    # --------------------------------------------------------
    # JSON response
    # --------------------------------------------------------

    try:

        data = response.json()

    except Exception:

        raise Exception(
            "BSE returned an invalid JSON response."
        )

    print(
        "BSE Status:",
        data.get("Status")
    )

    if data.get("Message"):

        print(
            "BSE Message:",
            data.get("Message")
        )

    # --------------------------------------------------------
    # Get announcements
    # --------------------------------------------------------

    announcements = data.get(
        "Table",
        []
    )

    # --------------------------------------------------------
    # Check alternative response keys
    # --------------------------------------------------------

    if not announcements:

        for key in [
            "Table1",
            "Table2",
            "Data",
            "data",
            "results"
        ]:

            value = data.get(key)

            if isinstance(value, list) and value:

                announcements = value
                break

    # --------------------------------------------------------
    # No announcements
    # --------------------------------------------------------

    if not announcements:

        raise Exception(
            f"No announcements found for BSE Scrip Code "
            f"{scrip_code} between "
            f"{from_date_string} and {to_date_string}"
        )

    print(
        f"Announcements found: {len(announcements)}"
    )

    # --------------------------------------------------------
    # Sort newest first
    # --------------------------------------------------------

    announcements.sort(
        key=lambda x: parse_date(
            x.get("NEWS_DT", "")
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # Latest announcement
    # --------------------------------------------------------

    latest = announcements[0]

    news_id = latest.get("NEWSID")
    headline = latest.get("HEADLINE")
    news_date = latest.get("NEWS_DT")
    category = latest.get("CATEGORYNAME")
    subcategory = latest.get("SUBCATNAME")
    company = latest.get("SLONGNAME")
    pdf_name = latest.get("ATTACHMENTNAME", "")

    # --------------------------------------------------------
    # PDF URLs
    # --------------------------------------------------------

    pdf_urls = []

    if pdf_name:

        live_url = (
            "https://www.bseindia.com/"
            "xml-data/corpfiling/AttachLive/"
            + pdf_name
        )

        historical_url = (
            "https://www.bseindia.com/"
            "xml-data/corpfiling/AttachHis/"
            + pdf_name
        )

        pdf_urls = [
            live_url,
            historical_url
        ]

    # --------------------------------------------------------
    # Return announcement
    # --------------------------------------------------------

    return {
        "news_id": news_id,
        "headline": headline,
        "date": news_date,
        "category": category,
        "subcategory": subcategory,
        "company": company,
        "pdf_name": pdf_name,
        "pdf_urls": pdf_urls,
        "scrip_code": scrip_code
    }


# ============================================================
# TEST BSE API
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("BSE ANNOUNCEMENT TEST")
    print("=" * 70)

    SCRIP_CODE = "500180"

    try:

        announcement = get_latest_announcement(
            SCRIP_CODE
        )

        print()
        print("=" * 70)
        print("LATEST ANNOUNCEMENT")
        print("=" * 70)

        print(
            "Company    :",
            announcement["company"]
        )

        print(
            "NEWS ID    :",
            announcement["news_id"]
        )

        print(
            "Headline   :",
            announcement["headline"]
        )

        print(
            "Date       :",
            announcement["date"]
        )

        print(
            "Category   :",
            announcement["category"]
        )

        print(
            "Subcategory:",
            announcement["subcategory"]
        )

        print(
            "PDF Name   :",
            announcement["pdf_name"]
        )

        print()
        print("PDF URLs:")

        for url in announcement["pdf_urls"]:

            print(url)

    except Exception as e:

        print()
        print("ERROR:")
        print(e)