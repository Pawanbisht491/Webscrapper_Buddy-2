# advanced_scraper.py
import os
import requests
from urllib.parse import urlencode, quote_plus

DEFAULT_TIMEOUT = 30

class AdvancedScraperError(Exception):
    pass

def _get(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.RequestException as e:
        raise AdvancedScraperError(str(e))

def fetch_with_scraperapi(url, api_key, timeout=DEFAULT_TIMEOUT):
    """
    ScraperAPI: https://www.scraperapi.com/docs/
    Simple usage: https://api.scraperapi.com?api_key=API_KEY&url={url}
    """
    endpoint = "https://api.scraperapi.com"
    params = {"api_key": api_key, "url": url, "render": "false"}
    return _get(endpoint, params=params, timeout=timeout)

def fetch_with_scrapingbee(url, api_key, render_js=False, timeout=DEFAULT_TIMEOUT):
    """
    ScrapingBee: https://www.scrapingbee.com/documentation/
    Example endpoint: https://app.scrapingbee.com/api/v1?api_key=API_KEY&url={url}
    """
    endpoint = "https://app.scrapingbee.com/api/v1"
    params = {"api_key": api_key, "url": url}
    if render_js:
        params["render_js"] = "true"
    return _get(endpoint, params=params, timeout=timeout)

def fetch_with_scrapingdog(url, api_key, timeout=DEFAULT_TIMEOUT):
    """
    ScrapingDog example:
    https://www.scrapingdog.com/docs/api
    endpoint (example): https://api.scrapingdog.com/scrape?api_key=API_KEY&url={url}
    """
    endpoint = "https://api.scrapingdog.com/scrape"
    params = {"api_key": api_key, "url": url}
    return _get(endpoint, params=params, timeout=timeout)

def fetch_with_zenrows(url, api_key, timeout=DEFAULT_TIMEOUT):
    """
    ZenRows example:
    https://www.zenrows.com/docs
    endpoint: https://api.zenrows.com/v1/?apikey=API_KEY&url={url}
    """
    endpoint = "https://api.zenrows.com/v1/"
    params = {"apikey": api_key, "url": url}
    return _get(endpoint, params=params, timeout=timeout)

def generic_fetch(url, provider, api_key=None, timeout=DEFAULT_TIMEOUT, **options):
    """
    provider: one of ["scraperapi","scrapingbee","scrapingdog","zenrows"]
    api_key: required for advanced providers (pass as string)
    options: provider-specific flags, e.g. render_js=True
    Returns HTML text or raises AdvancedScraperError on failure.
    """
    if provider is None or provider.lower() in ("none", "basic"):
        raise AdvancedScraperError("No provider selected. Use the basic scraper or select a provider.")

    p = provider.lower()
    if not api_key:
        raise AdvancedScraperError("API key is required for provider: " + provider)

    if p == "scraperapi":
        return fetch_with_scraperapi(url, api_key, timeout=timeout)
    elif p == "scrapingbee":
        return fetch_with_scrapingbee(url, api_key, render_js=options.get("render_js", False), timeout=timeout)
    elif p == "scrapingdog":
        return fetch_with_scrapingdog(url, api_key, timeout=timeout)
    elif p == "zenrows":
        return fetch_with_zenrows(url, api_key, timeout=timeout)
    else:
        raise AdvancedScraperError(f"Unknown provider: {provider}")

# Optional small helper to read API key from env if user prefers that flow
def get_api_key_from_env(provider):
    # map provider to env name convention
    env_map = {
        "scraperapi": "SCRAPERAPI_KEY",
        "scrapingbee": "SCRAPINGBEE_KEY",
        "scrapingdog": "SCRAPINGDOG_KEY",
        "zenrows": "ZENROWS_KEY",
    }
    return os.getenv(env_map.get(provider.lower(), ""), "")