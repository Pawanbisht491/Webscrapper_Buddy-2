import requests
from bs4 import BeautifulSoup

def scrape_website(url, timeout=20):
    """
    Simple, Streamlit-friendly scraper that fetches raw HTML
    using requests instead of Selenium.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()   # throw error on 4xx/5xx
        return response.text

    except requests.exceptions.RequestException as e:
        return f"ERROR: Failed to scrape the website.\nDetails: {e}"


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    return str(body_content) if body_content else ""


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    # remove <script> and <style>
    for tag in soup(["script", "style"]):
        tag.extract()

    # clean text
    cleaned = soup.get_text(separator="\n")
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())

    return cleaned


def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i:i + max_length]
        for i in range(0, len(dom_content), max_length)
    ]
