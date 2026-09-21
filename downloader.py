import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bseindia.com/",
    "Accept": "application/pdf,*/*"
}


def download_pdf(pdf_urls, filename):
    """
    Tries multiple BSE PDF URLs until one works.

    Returns:
        filename
        working_url
    """

    session = requests.Session()

    # Visit homepage first to establish a session
    session.get(
        "https://www.bseindia.com/",
        headers=HEADERS,
        timeout=30
    )

    last_error = None

    for url in pdf_urls:
        try:
            print(f"Trying: {url}")

            response = session.get(
                url,
                headers=HEADERS,
                timeout=30,
                allow_redirects=True
            )

            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)

                print("✅ PDF downloaded successfully")

                return filename, url

            else:
                print(f"Failed ({response.status_code})")

        except Exception as e:
            last_error = e
            print(e)

    raise Exception(
        f"Unable to download PDF.\nLast Error: {last_error}"
    )