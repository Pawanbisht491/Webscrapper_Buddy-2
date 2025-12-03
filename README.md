# **Webscrapper Buddy 🕸️🤖**

A Streamlit-based smart web scraping and AI-powered data extraction tool.
Supports **Basic Scraping**, **Advanced Scraping Providers**, **LLM Parsing**, **CSV/PDF export**, **RSS News Reader**, and **History Tracking**.

---

## 🚀 **Features**

### **🟢 Basic Scraper**

Scrapes any publicly accessible website using simple HTTP requests.

* Fetches raw HTML from URL
* Extracts `<body>` content
* Cleans it by removing scripts/styles
* Splits DOM into chunks for LLM parsing
* Uses AI (Gemini/Groq/OpenAI) to extract structured information
* Export results as **CSV or PDF**

(Uses scraping logic from **scrape.py** )

---

### **🔵 Advanced Scraper**

Handles sites with stronger protection using external scraping APIs:

* ScraperAPI
* ZenRows
* ScrapingBee
* ScrapingDog

The tool allows selecting a provider + entering API keys.
Automatically handles request failures with custom error classes.

(Provider logic implemented in **advance_scrape.py** )

---

### **🤖 AI Parsing Engine (LLM Parser)**

Extracts structured data using:

* Gemini (Free)
* Groq (Llama 3)
* OpenAI (GPT-4o-mini)

LLM parsing works chunk-by-chunk and merges results intelligently.

(LLM parsing logic from **parse_llm.py** )

---

### **📊 Data Export**

After parsing, results can be automatically converted into tables:

* Smart detection of HTML tables, CSV-like text, whitespace tables, etc.
* Downloads:

  * **CSV export**
  * **PDF export using matplotlib**

(Export helpers in **main.py** )

---

### **📰 IT News Reader (RSS Mode)**

Reads any RSS feed using `feedparser` and shows top headlines.

---

### **🕘 History**

Stores last scraped DOM in session state.

---

### **❓ FAQs Page**

Explains Basic Mode, Advanced Mode, and RSS usage.

---

## 🏗️ **Tech Stack**

### **Backend / Core**

* Python
* Requests
* BeautifulSoup4
* lxml / html5lib

### **Frontend**

* Streamlit
* streamlit-option-menu

### **AI Providers**

* Gemini API
* Groq API
* OpenAI API

### **Other Tools**

* Pandas
* Matplotlib
* feedparser

(Full dependency list from **requirements.txt** )

---

## 📦 Installation

```bash
git clone https://github.com/<your-username>/Webscrapper_Buddy.git
cd Webscrapper_Buddy

pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
streamlit run main.py
```

---

## 🔐 Environment Variables (Optional)

If you prefer storing API keys in environment variables:

| Provider    | Environment Variable |
| ----------- | -------------------- |
| ScraperAPI  | `SCRAPERAPI_KEY`     |
| ZenRows     | `ZENROWS_KEY`        |
| ScrapingBee | `SCRAPINGBEE_KEY`    |
| ScrapingDog | `SCRAPINGDOG_KEY`    |

(Handled in `get_api_key_from_env()` from **advance_scrape.py** )

---

## 📂 Project Structure

```
Webscrapper_Buddy/
│
├── main.py                # Main Streamlit UI (Basic, Advanced, RSS, History, FAQ)
├── scrape.py              # Basic scraper utilities
├── advance_scrape.py      # Advanced scraping provider integration
├── parse_llm.py           # AI parsing logic using Gemini/Groq/OpenAI
├── requirements.txt       # Dependencies
└── README.md
```

---

## 📝 Future Improvements

* Add login/session scraping
* Add browser-based scraping (Playwright/Selenium)
* Add image/PDF extraction
* Add custom XPath/CSS selector extraction

---

## ❤️ Contribution

Pull requests are welcome!

---

If you'd like, I can also generate:

✅ A shorter GitHub-friendly README
✅ A version with screenshots
✅ A "Deploy to Streamlit Cloud" badge

Just tell me!
