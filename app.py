import streamlit as st
import openai
from dotenv import load_dotenv
import os
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Optional
import json

# Load environment variables
load_dotenv()

# Fetch credentials from environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

openai_client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

class WebResearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.discovered_urls = []  # Track all discovered URLs
    
    def scrape_website(self, url: str, max_length: int = 5000) -> Dict[str, str]:
        """Scrape content from a website and discover relevant URLs"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Discover relevant URLs (news, about, careers, etc.)
            self._discover_relevant_urls(soup, url)
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return {
                "url": url,
                "content": text,
                "title": soup.title.string if soup.title else "No title",
                "status": "success"
            }
        except Exception as e:
            return {
                "url": url,
                "content": "",
                "title": "",
                "status": f"error: {str(e)}"
            }
    
    def _discover_relevant_urls(self, soup, base_url):
        """Discover relevant URLs from the webpage"""
        relevant_keywords = ['news', 'blog', 'press', 'careers', 'about', 'investor', 'media', 'announcement']
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                link_text = link.get_text().lower()
                
                # Check if URL or link text contains relevant keywords
                if any(keyword in full_url.lower() or keyword in link_text for keyword in relevant_keywords):
                    if full_url not in self.discovered_urls:
                        self.discovered_urls.append({
                            'url': full_url,
                            'text': link.get_text().strip(),
                            'category': self._categorize_url(full_url, link_text)
                        })
    
    def _categorize_url(self, url, link_text):
        """Categorize URLs based on content"""
        url_lower = url.lower()
        text_lower = link_text.lower()
        
        if any(word in url_lower or word in text_lower for word in ['news', 'press', 'announcement']):
            return 'News'
        elif any(word in url_lower or word in text_lower for word in ['career', 'job', 'hire']):
            return 'Careers'
        elif any(word in url_lower or word in text_lower for word in ['investor', 'financial', 'funding']):
            return 'Investor Relations'
        elif any(word in url_lower or word in text_lower for word in ['about', 'company', 'management']):
            return 'Company Info'
        else:
            return 'General'
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Simulate web search - in production, you'd use Google Custom Search API"""
        # This would be replaced with actual search API results
        # For now, return mock results with realistic URLs
        mock_results = [
            {
                "title": f"{query} - Recent News",
                "url": f"https://www.businesswire.com/news/{query.lower().replace(' ', '-')}",
                "snippet": f"Latest developments regarding {query}...",
                "category": "News"
            },
            {
                "title": f"{query} - Company Updates",
                "url": f"https://www.prnewswire.com/news/{query.lower().replace(' ', '-')}",
                "snippet": f"Press releases and announcements about {query}...",
                "category": "Press Release"
            }
        ]
        return mock_results

class IntelligenceAgent:
    def __init__(self, openai_client, web_researcher):
        self.openai_client = openai_client
        self.web_researcher = web_researcher
        self.source_links = {}  # Track links for each insight type
    
    def analyze_relevance(self, content: str, user_requirements: str, url: str) -> Dict[str, any]:
        """Use LLM to analyze if content is relevant to user requirements"""
        prompt = f"""
        Analyze the following content and determine its relevance to the user requirements.
        
        User Requirements: {user_requirements}
        Source URL: {url}
        
        Content: {content[:2000]}...
        
        Provide a JSON response with:
        - "relevance_score": 0-10 (10 being highly relevant)
        - "relevant_insights": list of relevant insights found with their categories (e.g., "Recent Hires", "Funding", "Growth")
        - "missing_info": list of information not found in content
        - "recommendation": whether to use this source or search elsewhere
        - "best_for": list of insight types this source is best suited for
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert content analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            result['source_url'] = url
            return result
        except Exception as e:
            return {
                "relevance_score": 0,
                "relevant_insights": [],
                "missing_info": ["Analysis failed"],
                "recommendation": "search_elsewhere",
                "best_for": [],
                "source_url": url
            }
    
    def generate_insights_table_with_links(self, company_info: Dict, research_results: List[Dict]) -> str:
        """Generate insights table with source links"""
        
        # Build source mapping
        source_mapping = {}
        for result in research_results:
            if result.get('relevant_insights'):
                for insight in result['relevant_insights']:
                    insight_type = self._extract_insight_type(insight)
                    if insight_type not in source_mapping:
                        source_mapping[insight_type] = []
                    source_mapping[insight_type].append({
                        'source': result['source'],
                        'url': result.get('url', ''),
                        'relevance': result.get('relevance_score', 0)
                    })
        
        # Add discovered URLs from web research
        for url_info in self.web_researcher.discovered_urls:
            category = self._map_category_to_insight(url_info['category'])
            if category not in source_mapping:
                source_mapping[category] = []
            source_mapping[category].append({
                'source': f"Company Website - {url_info['category']}",
                'url': url_info['url'],
                'relevance': 8  # High relevance for company's own pages
            })
        
        # Combine all information for LLM
        all_content = f"Company: {company_info['company']}\n"
        all_content += f"Country: {company_info['country']}\n"
        all_content += f"Research Topic: {company_info['research_topic']}\n"
        all_content += f"Requirements: {company_info['prompt']}\n\n"
        
        all_content += "Available Sources with URLs:\n"
        for insight_type, sources in source_mapping.items():
            all_content += f"\n{insight_type}:\n"
            for source in sources:
                all_content += f"- {source['source']}: {source['url']}\n"
        
        for result in research_results:
            all_content += f"\nSource: {result['source']}\n"
            all_content += f"Content: {result['content'][:800]}...\n"
        
        system_prompt = """You are an enterprise research assistant. Create a comprehensive insights table with these columns:
        - Insight Type
        - Recommended Source (with URL)
        - Reason
        
        For the Recommended Source column, format as: "Source Name - URL" (e.g., "Company Website - https://example.com/news")
        
        Focus on: Account Intelligence, Recent Hires, Recent Initiatives, Growth Insights, Funding, Senior Management Hires.
        Output ONLY a markdown table format with proper URLs included."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": all_content}
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            # Fallback table generation
            return self._generate_fallback_table(source_mapping)
    
    def _extract_insight_type(self, insight: str) -> str:
        """Extract insight type from insight description"""
        insight_lower = insight.lower()
        if any(word in insight_lower for word in ['hire', 'recruit', 'employee', 'staff']):
            return 'Recent Hires'
        elif any(word in insight_lower for word in ['funding', 'investment', 'capital', 'financial']):
            return 'Funding'
        elif any(word in insight_lower for word in ['growth', 'expansion', 'market', 'revenue']):
            return 'Growth Insights'
        elif any(word in insight_lower for word in ['initiative', 'project', 'partnership', 'acquisition']):
            return 'Recent Initiatives'
        elif any(word in insight_lower for word in ['management', 'executive', 'leadership', 'ceo', 'cto']):
            return 'Senior Management'
        else:
            return 'Account Intelligence'
    
    def _map_category_to_insight(self, category: str) -> str:
        """Map URL categories to insight types"""
        mapping = {
            'News': 'Recent Initiatives',
            'Careers': 'Recent Hires',
            'Investor Relations': 'Funding',
            'Company Info': 'Account Intelligence',
            'General': 'Growth Insights'
        }
        return mapping.get(category, 'Account Intelligence')
    
    def _generate_fallback_table(self, source_mapping: Dict) -> str:
        """Generate fallback table if LLM fails"""
        table_rows = []
        table_rows.append("| Insight Type | Recommended Source | Reason |")
        table_rows.append("|---|---|---|")
        
        for insight_type, sources in source_mapping.items():
            if sources:
                best_source = max(sources, key=lambda x: x['relevance'])
                source_with_url = f"{best_source['source']} - {best_source['url']}"
                reason = f"High relevance source with detailed information about {insight_type.lower()}"
                table_rows.append(f"| {insight_type} | {source_with_url} | {reason} |")
        
        return "\n".join(table_rows)

def display_enhanced_table(df):
    """Display table with clickable links"""
    # Process the dataframe to make URLs clickable
    if 'Recommended Source' in df.columns:
        def make_clickable(text):
            if ' - http' in text:
                parts = text.split(' - http')
                if len(parts) == 2:
                    source_name = parts[0]
                    url = 'http' + parts[1]
                    return f'<a href="{url}" target="_blank">{source_name}</a>'
            return text
        
        df_display = df.copy()
        df_display['Recommended Source'] = df_display['Recommended Source'].apply(make_clickable)
        
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.dataframe(df, use_container_width=True)

def main():
    st.title("🔍 Enhanced Account Intelligence App")
    st.markdown("*Powered by AI-driven web research with clickable source links*")
    
    # Initialize components
    web_researcher = WebResearcher()
    intelligence_agent = IntelligenceAgent(openai_client, web_researcher)
    
    with st.form(key="enhanced_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company = st.text_input("Company Name", placeholder="e.g., Royal Cup, Inc.")
            country = st.text_input("Country", placeholder="e.g., United States")
            research_topic = st.text_input("Research Topic", placeholder="e.g., NEWS, PARTNERSHIPS")
        
        with col2:
            search_queries = st.text_area("Search Queries", placeholder="e.g., Recent Initiatives, New Hires")
            support_urls = st.text_area("Company URLs (comma separated)", 
                                      placeholder="https://www.company.com, https://company.com/news")
            prompt = st.text_area("Intelligence Requirements", 
                                placeholder="Account Insights, Buyer Intent, Growth Insights, Recent Hires, Funding")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("🚀 Generate Intelligence Report", use_container_width=True)
    
    if submit_button and company:
        with st.spinner("🔍 Researching and analyzing information..."):
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Analyze company website(s)
            status_text.text("📊 Analyzing company website(s)...")
            progress_bar.progress(20)
            
            research_results = []
            
            if support_urls.strip():
                urls = [url.strip() for url in support_urls.split(',') if url.strip()]
                
                for i, url in enumerate(urls):
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    
                    status_text.text(f"🌐 Scraping {urlparse(url).netloc}...")
                    website_data = web_researcher.scrape_website(url)
                    
                    if website_data['status'] == 'success':
                        user_requirements = f"{research_topic} {search_queries} {prompt}"
                        relevance_analysis = intelligence_agent.analyze_relevance(
                            website_data['content'], user_requirements, url
                        )
                        
                        research_results.append({
                            "source": f"Company Website ({urlparse(url).netloc})",
                            "content": website_data['content'],
                            "relevance_score": relevance_analysis.get('relevance_score', 0),
                            "relevant_insights": relevance_analysis.get('relevant_insights', []),
                            "url": url
                        })
            
            progress_bar.progress(80)
            
            # Step 2: Generate insights with links
            status_text.text("🧠 Generating intelligence insights with source links...")
            
            company_info = {
                "company": company,
                "country": country,
                "research_topic": research_topic,
                "search_queries": search_queries,
                "prompt": prompt
            }
            
            insights_table = intelligence_agent.generate_insights_table_with_links(company_info, research_results)
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.success("🎯 Intelligence Report Generated Successfully!")
            
            # Show discovered URLs
            if web_researcher.discovered_urls:
                with st.expander("🔗 Discovered Relevant URLs"):
                    for url_info in web_researcher.discovered_urls[:10]:  # Show first 10
                        st.write(f"**{url_info['category']}:** [{url_info['text']}]({url_info['url']})")
            
            # Display main results with clickable links
            st.subheader("📋 Account Intelligence Report")
            
            # Parse and display table with links
            if "|" in insights_table and "Insight Type" in insights_table:
                try:
                    lines = insights_table.strip().split('\n')
                    table_lines = [line for line in lines if '|' in line and line.strip()]
                    
                    if len(table_lines) >= 3:
                        table_content = '\n'.join(table_lines)
                        df = pd.read_csv(io.StringIO(table_content), sep='|', skipinitialspace=True)
                        df = df.dropna(axis=1, how='all')
                        df = df.iloc[1:]  # Remove separator row
                        df.columns = df.columns.str.strip()
                        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                        
                        # Display with clickable links
                        display_enhanced_table(df)
                    else:
                        st.markdown(insights_table)
                except Exception as e:
                    st.error(f"Error parsing table: {e}")
                    st.markdown(insights_table)
            else:
                st.markdown(insights_table)

if __name__ == "__main__":
    main()
