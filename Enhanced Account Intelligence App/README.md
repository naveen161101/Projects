# 🔍 Enhanced Account Intelligence App

An AI-powered web research tool that delivers actionable account intelligence, with **clickable links to all sources** for maximum traceability and insight validation.

---

## Features

### 🚀 AI-Driven Account Intelligence

- **Automated Insights Table**: Get key intelligence (Recent Hires, Funding, Growth, Initiatives, Senior Management, Account Intelligence) packaged in a **clear, traceable markdown table with clickable source links**.
- **Enterprise-Ready LLM Integration**: Uses Azure OpenAI and a tailored prompting strategy to extract, evaluate, and summarize insights from scraped web pages and news.

### 🌐 Smart Web & Company Site Scraper

- **Web Scraping with Context**: Pulls and parses relevant company website sections (news, press, careers, about, IR). Automatically discovers and categorizes pages likely to contain intelligence.
- **Safe and Robust**: Gracefully handles and reports errors for unreachable or problematic web pages.

### 💡 Relevance Evaluation

- **LLM-Powered Content Analysis**: Each scraped page is rated for relevance and value for your research goals; unhelpful sources are deprioritized.
- **Customizable Requirements**: User can define their intelligence needs (e.g., "Growth Insights," "Recent Initiatives," "Buyer Intent") and get only the most relevant info.

### 📊 User-Friendly Intelligence Reports

- **Interactive Next-Gen Table**: All results are rendered as a markdown table or clickable pandas dataframe (Streamlit), so you can instantly verify every fact.
- **Expandable URL Explorer**: See all discovered and categorized URLs for manual review.

### 🔒 Secure & Configurable

- **.env Support**: Credentials and API endpoints read from environment variables.
- **Streamlit Frontend**: Clean, beautiful, efficient online interface for your intelligence workflow.

---

## Installation

1. **Clone the repo:**
```bash
git clone https://github.com/naveen161101/Projects.git
cd Enhanced Account Intelligence App

2. **Install dependencies:**  
Python 3.8+ is recommended.

pip install -r requirements.txt

text

3. **Setup environment variables:**  
Create a `.env` file with your Azure OpenAI info:

AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_API_BASE=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_OPENAI_API_VERSION=2023-03-15-preview

text

4. **Run the App:**

streamlit run app.py

or whatever the main file is named
text

---

## Usage

1. **Describe Your Need**: Enter company name, country, research topic (e.g., NEWS), search queries (e.g., "Recent Hires"), and intelligence requirements (e.g., "Growth Insights, Buyer Intent").
2. **Add URLs** *(optional)*: Enter official company URLs or news/press page links for deep analysis.
3. **Review Results**:  
- Clickable URLs to **verify every source**.
- Expandable panel for all discovered relevant company URLs.

---

## Example Output

| Insight Type            | Recommended Source                                              | Reason                                         |
|-------------------------|---------------------------------------------------------------|------------------------------------------------|
| Recent Hires            | Company Website - https://example.com/careers                 | High relevance for hiring news                 |
| Growth Insights         | BusinessWire - https://businesswire.com/news/company-growth   | Direct recent growth coverage                  |

---

## How It Works

1. **Web Scraping**: Collects main site and important company webpage text.
2. **URL Discovery**: Auto-extracts and categorizes news/investor/press/careers/company info pages.
3. **LLM Relevance Scoring**: Every page is summarized and scored for user-specified insight types by Azure OpenAI.
4. **Results Table**: Highlights best-matching insight types with recommended sources; all links are **clickable** and reasoned.
5. **Streamlit UI**: Presents insights in an interactive, user-friendly table.

---

## Key Files

- `app.py` (or main file): Entrypoint, Streamlit UI logic.
- `WebResearcher` class: Scrapes, discovers URLs, and categories.
- `IntelligenceAgent` class: LLM-based relevance analysis, insight extraction, table generation.
- `.env`: API credentials (never check into GitHub!).

---

## Attributions

- [Streamlit](https://streamlit.io/) for ultra-fast web UIs.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing.
- [OpenAI](https://openai.com/) & [Azure Cognitive Services](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/) for state-of-the-art language models.

---

## License

This project is for educational and research use. For commercial use or custom licensing, please contact the author.

---

## Support

Feel free to open issues or PRs for improvements!
