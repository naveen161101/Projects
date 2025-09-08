
---

# 🔍 How to Build an AI-Powered Enhanced Account Intelligence App with Clickable Source Links

In today's data-driven world, sales and research teams need actionable account intelligence fast and reliably. Imagine an AI-powered web research tool that not only scrapes company websites but also analyzes the data, scores its relevance, and generates actionable insights — complete with clickable links to every source for full traceability.

Welcome to the **Enhanced Account Intelligence App**.

---

## 🚀 What Is the Enhanced Account Intelligence App?

This web app leverages Azure OpenAI, advanced web scraping techniques, and an elegant Streamlit interface to deliver enterprise-ready intelligence reports. It helps researchers generate meaningful insights on companies such as recent hires, funding news, growth trends, and more — by simply providing company names, search topics, and URLs.

---

## 🌟 Key Features

### 1️⃣ AI-Driven Account Intelligence
- Automated insights summarized into a traceable markdown table.
- Uses Azure OpenAI to analyze scraped content intelligently.
- Delivers relevance scoring and recommendations per source.

### 2️⃣ Smart Web & Company Site Scraper
- Scrapes and parses key sections (news, press, careers).
- Auto-discovers relevant URLs.
- Handles errors gracefully, ensuring robust scraping.

### 3️⃣ Relevance Evaluation
- Each page is rated for its relevance to your research needs.
- Customizable intelligence goals (e.g., "Growth Insights," "Recent Hires").

### 4️⃣ User-Friendly Reports
- Interactive markdown tables or pandas DataFrame views in Streamlit.
- Clickable URLs for verifying all sources.
- Expandable URL explorer for manual URL review.

### 5️⃣ Secure and Configurable
- API keys managed through .env.
- Streamlit frontend for a clean, efficient experience.

---

## ⚙️ Installation Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/naveen161101/Projects.git
cd Enhanced Account Intelligence App
```

### 2️⃣ Install Dependencies
Python 3.8+ is recommended.

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables
Create a .env file:
```bash
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_API_BASE=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_OPENAI_API_VERSION=2023-03-15-preview
```

### 4️⃣ Run the App
```bash
streamlit run app.py
```

---

## 🧱 How It Works

- **Web Scraping**: Automatically scrapes the company's official pages and discovers relevant URLs.
- **URL Categorization**: Automatically categorizes URLs (e.g., News, Careers).
- **LLM Relevance Scoring**: Azure OpenAI analyzes content against user requirements.
- **Insight Table Generation**: Generates a table showing insights with clickable sources.
- **Interactive UI**: Presents an intuitive Streamlit interface to interact with insights.

---

## 🎯 Example Output

| Insight Type    | Recommended Source                                 | Reason                             |
| --------------- | -------------------------------------------------- | ---------------------------------- |
| Recent Hires    | [Company Careers](https://example.com/careers)     | High relevance for new hires       |
| Growth Insights | [BusinessWire News](https://businesswire.com/news) | Detailed coverage of recent growth |

---

## ⚡ Example Usage Flow

- Enter company details: name, country, research topic.
- Specify search queries like "Recent Initiatives" or "New Hires."
- Optionally provide official URLs.
- View generated table with clickable source links.
- Expand discovered URL explorer to manually check other resources.

---

## 🧱 Architecture Overview

- **app.py**: Entry point, Streamlit-based UI.
- **WebResearcher class**: Handles web scraping and URL discovery.
- **IntelligenceAgent class**: Uses Azure OpenAI for relevance scoring and table generation.

---

## 🛠 Attributions

- [Streamlit](https://streamlit.io/) for web UI.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing.
- [OpenAI Azure API](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) for LLM-based analysis.

---

## 📚 License

Educational and research use only. For commercial use, contact the author.

---

## 💡 Support

Found an issue or want to contribute? Feel free to open issues or PRs in the GitHub repo.

---

This app empowers researchers and analysts to turn unstructured web data into actionable, reliable insights with full traceability.

👉 Ready to boost your account intelligence workflow? Check out the [GitHub repository](https://github.com/naveen161101/Projects) and start exploring now.

---
