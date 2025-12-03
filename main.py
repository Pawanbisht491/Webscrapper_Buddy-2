import io
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import feedparser
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
from parse_llm import parse_with_llm
from advance_scrape import generic_fetch, AdvancedScraperError, get_api_key_from_env
import os

# ---------------------- UTILITIES for converting parsed text -> DataFrame and exports ----------------------
def try_to_dataframe(parsed_text):
    """
    Try multiple safe strategies to convert parsed_text to DataFrame:
     1) If it's already in a newline-separated table with tab/| or comma separators -> parse
     2) If it contains HTML table -> read_html
     3) Otherwise last-resort: put whole text in single-column DF
    """
    # 1) try html table
    try:
        dfs = pd.read_html(parsed_text)
        if dfs:
            return dfs[0]
    except Exception:
        pass

    # 2) try CSV-like (tab, pipe, comma)
    lines = [l.strip() for l in parsed_text.splitlines() if l.strip()]
    if not lines:
        return pd.DataFrame()

    # detect separator using the header row heuristics
    header = lines[0]
    for sep in ['\t', '|', ',', ';']:
        if sep in header:
            try:
                df = pd.read_csv(io.StringIO("\n".join(lines)), sep=sep)
                return df
            except Exception:
                pass

    # 3) Try whitespace-split columns (if consistent)
    parts = [row.split() for row in lines]
    if len(parts) >= 2:
        lens = [len(p) for p in parts]
        if len(set(lens)) == 1 and lens[0] > 1:
            df = pd.DataFrame(parts[1:], columns=parts[0])
            return df

    # 4) fallback: single-column DataFrame
    return pd.DataFrame({"text": lines})

def df_to_csv_bytes(df):
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return buf.read()

def df_to_pdf_bytes(df, title="Parsed Table"):
    # Render DataFrame as matplotlib table and save to PDF in-memory
    fig, ax = plt.subplots(figsize=(8.5, max(2, 0.4 * len(df))))
    ax.axis('off')
    ax.set_title(title)
    tbl = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.2)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='pdf', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Webscrapper Buddy",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
#                 BASIC SCRAPER
# =========================================================
def render_basic_scraper():
    st.title("Web_Scraper Buddy — Basic Mode")

    url = st.text_input("Enter Website URL", key="basic_url")

    if st.button("Scrape Site", key="basic_scrape_btn"):
        if not url:
            st.error("Please enter a URL.")
            return

        st.info("Scraping the website...")

        result = scrape_website(url)
        if isinstance(result, str) and result.startswith("ERROR:"):
            st.error(result)
            return

        body_content = extract_body_content(result)
        cleaned_content = clean_body_content(body_content)

        st.session_state.dom_content = cleaned_content

        st.success("Scrape completed!")
        with st.expander("View DOM Content"):
            st.text_area("DOM Content", cleaned_content, height=300)

    # --- parse section (ONLY visible after scraping) ---
    if "dom_content" in st.session_state:
        st.subheader("Describe what you want to parse")
        parse_description = st.text_area(
            "Describe what you want to parse",
            key="basic_parse",
            placeholder="Example: Extract course name, rating, duration, lessons in table format"
        )

        # Provider Selection
        st.subheader("Select AI Provider")
        provider = st.selectbox(
            "Choose Provider",
            ["Gemini (Free)", "Groq", "OpenAI"],
            key="basic_provider"
        )

        provider_key = st.text_input(
            f"Enter {provider} API Key",
            type="password",
            key="basic_api_key"
        )

        provider_map = {
            "Gemini (Free)": "gemini",
            "Groq": "groq",
            "OpenAI": "openai"
        }
        provider_clean = provider_map[provider]

        if st.button("Parse Content", key="basic_parse_btn"):
            if not parse_description.strip():
                st.error("Please describe what you want to parse.")
                return

            if not provider_key.strip():
                st.error("Please enter the API key for the selected provider.")
                return

            st.info("Parsing the content...")

            dom_chunks = split_dom_content(st.session_state.dom_content)

            parsed_result = parse_with_llm(
                provider_clean,
                provider_key.strip(),
                dom_chunks,
                parse_description
            )

            st.subheader("Parsed Output (raw)")
            st.code(parsed_result)

            # Try to convert to DataFrame and provide downloads
            df = try_to_dataframe(parsed_result)
            st.subheader("Parsed table preview")
            st.dataframe(df)

            csv_bytes = df_to_csv_bytes(df)
            pdf_bytes = df_to_pdf_bytes(df, title="Parsed Output - Basic Mode")

            st.download_button(
                "Download CSV (.csv)",
                data=csv_bytes,
                file_name="parsed_basic.csv",
                mime="text/csv",
                key="basic_download_csv"
            )
            st.download_button(
                "Download PDF (.pdf)",
                data=pdf_bytes,
                file_name="parsed_basic.pdf",
                mime="application/pdf",
                key="basic_download_pdf"
            )

# =========================================================
#                 ADVANCED SCRAPER
# =========================================================
def render_advanced_scraper():
    st.title("Web_Scraper Buddy — Advanced Mode")

    url = st.text_input("Enter Website URL", key="adv_url")

    providers = ["ScraperAPI", "ZenRows", "ScrapingBee", "ScrapingDog"]
    provider = st.selectbox("Select Provider", providers)

    api_key = st.text_input("Enter Provider API Key", type="password", key="adv_api_key")

    if st.button("Run Advanced Scrape", key="adv_scrape_btn"):
        if not url:
            st.error("Please enter a URL.")
            return

        provider_map = {
            "ScraperAPI": "scraperapi",
            "ZenRows": "zenrows",
            "ScrapingBee": "scrapingbee",
            "ScrapingDog": "scrapingdog",
        }
        provider_id = provider_map.get(provider)
        provider_key = api_key.strip() or get_api_key_from_env(provider_id)

        if not provider_key:
            st.error("Missing API key for selected provider.")
            return

        st.info("Running advanced scrape...")

        try:
            html = generic_fetch(url, provider_id, api_key=provider_key)
            body_content = extract_body_content(html)
            cleaned_content = clean_body_content(body_content)
            st.session_state.dom_content = cleaned_content

            st.success("Advanced scrape completed!")

            with st.expander("View DOM Content"):
                st.text_area("DOM Content", cleaned_content, height=300)

        except AdvancedScraperError as e:
            st.error(f"Advanced scrape failed: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

    # --- parse section (ONLY visible after scraping) ---
    if "dom_content" in st.session_state:
        st.subheader("Describe what you want to parse")
        parse_description = st.text_area(
            "Describe what you want to parse",
            key="adv_parse",
            placeholder="Example: Extract product name, price, rating in rows"
        )

        # AI Provider section for advanced scraping
        st.subheader("Select AI Provider")
        provider2 = st.selectbox(
            "Choose Provider",
            ["Gemini (Free)", "Groq", "OpenAI"],
            key="adv_provider"
        )

        provider_key2 = st.text_input(
            f"Enter {provider2} API Key",
            type="password",
            key="adv_api_key_llm"
        )

        provider_clean2 = {
            "Gemini (Free)": "gemini",
            "Groq": "groq",
            "OpenAI": "openai"
        }[provider2]

        if st.button("Parse Advanced Content", key="adv_parse_btn"):
            if not parse_description.strip():
                st.error("Please describe what you want to parse.")
                return

            if not provider_key2.strip():
                st.error("Please enter the API key for the selected provider.")
                return

            st.info("Parsing the content...")

            dom_chunks = split_dom_content(st.session_state.dom_content)

            parsed_result = parse_with_llm(
                provider_clean2,
                provider_key2.strip(),
                dom_chunks,
                parse_description
            )

            st.subheader("Parsed Output (raw)")
            st.code(parsed_result)

            # Try to convert to DataFrame and provide downloads
            df = try_to_dataframe(parsed_result)
            st.subheader("Parsed table preview")
            st.dataframe(df)

            csv_bytes = df_to_csv_bytes(df)
            pdf_bytes = df_to_pdf_bytes(df, title="Parsed Output - Advanced Mode")

            st.download_button(
                "Download CSV (.csv)",
                data=csv_bytes,
                file_name="parsed_advanced.csv",
                mime="text/csv",
                key="adv_download_csv"
            )
            st.download_button(
                "Download PDF (.pdf)",
                data=pdf_bytes,
                file_name="parsed_advanced.pdf",
                mime="application/pdf",
                key="adv_download_pdf"
            )

# =========================================================
#                 IT NEWS / HISTORY / FAQ
# =========================================================
def render_it_news():
    st.title("IT News — RSS Reader")

    feed_url = st.text_input(
        "Enter RSS Feed URL",
        " http://indianexpress.com/section/technology/feed/"
    )

    if st.button("Load News"):
        try:
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                st.error("No news found. Check RSS URL.")
                return

            for entry in feed.entries[:10]:
                st.subheader(entry.title)
                st.write(entry.get("summary", "")[:300] + "...")
                st.write(f"🔗 Read more: {entry.link}")
                st.divider()

        except Exception as e:
            st.error(f"Error loading RSS feed: {e}")

def render_history():
    st.title("History")

    if "dom_content" in st.session_state:
        with st.expander("Last DOM Content"):
            st.text_area("DOM Content", st.session_state.dom_content, height=300)
    else:
        st.info("No history found.")

def render_faqs():
    st.title("FAQs")
    with st.expander("What is Webscrapper Buddy?"):
        st.write("A tool to scrape and analyze any website.")
    with st.expander("What is Basic Mode?"):
            st.write("""
**Overview:** Basic Mode is designed for simple websites without heavy security, login walls, 
                bot protection, or JavaScript-loaded content. It uses a normal HTTP request to fetch the page.

**Steps**
1. Enter the website URL.
2. Click "Scrape Site" to fetch and clean the page.
3. View the scraped DOM content in the expander.
4. Describe what you want to parse.
5. Select an AI provider (Gemini, Groq, OpenAI) and enter your API key.
6. Click "Parse Content" to extract results.
7. Download the parsed output as CSV or PDF.
""")
    with st.expander("How do I use Advanced Mode?"):
        st.write("""
**Overview:** Advanced Mode uses external scraping providers (ScraperAPI, ZenRows, ScrapingBee, ScrapingDog).

**Steps:**
1. Enter the website URL.
2. Select a provider (ScraperAPI / ZenRows / ScrapingBee / ScrapingDog).
3. Paste your provider API key (or leave empty if it's set as an environment variable).
4. Click 'Run Advanced Scrape' and check the DOM content shown in the expander.
5. Write your 'Describe what you want to parse' prompt.
6. Choose an AI provider (Gemini, Groq, OpenAI) and enter the API key.
7. Click 'Parse Advanced Content' to get results and download CSV/PDF.
""")
    with st.expander("What is an RSS Feed URL?"):
        st.write("An RSS Feed URL is a special link provided by websites that delivers their latest articles or news in a structured format (XML)." \
        " You can use it to stay updated with new content without visiting the site directly.")
# =========================================================
#                 SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.title("Webscrapper Buddy")
    
    # Yeh automatically state handle karta hai aur dikhne mein accha hai
    menu = option_menu(
        menu_title="",  
        options=["Basic Scraper", "Advanced Scraper", "IT News", "History", "FAQs"],
        icons=["house", "gear", "newspaper", "clock-history", "question-circle"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#fafafa00"},
            "icon": {"color": "orange", "font-size": "25px"},
            
            # REMOVE white hover
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin":"0px",
                "--hover-color": "transparent",   # << REMOVE WHITE HOVER
            },

            "nav-link-selected": {"background-color": "#0036fb"},
        }
    )


# Logic wahi rahega
if menu == "Basic Scraper":
    render_basic_scraper()
elif menu == "Advanced Scraper":
    render_advanced_scraper()
elif menu == "IT News":
    render_it_news()
elif menu == "History":
    render_history()
elif menu == "FAQs":
    render_faqs()