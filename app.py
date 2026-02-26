import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import re
from urllib.parse import urljoin
import os

# --- 1. Configuration & API Initialization ---
# It is highly recommended to use st.secrets for production security.
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_KEY_MISSING")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def clean_html(raw_html):
    """
    Cleans HTML to reduce noise and save tokens for LLM processing.
    Removes non-essential tags while preserving structural information.
    """
    soup = BeautifulSoup(raw_html, 'html.parser')
    for tag in soup(['script', 'style', 'svg', 'img', 'noscript', 'meta', 'link']):
        tag.decompose()
    return str(soup)

# --- 2. Core AI & Logic Components ---

def find_login_link_with_ai(compressed_html, raw_html):
    """
    Advanced Link Detection:
    1. Regex Scan: Finds URLs hidden in JS/JSON (Essential for NYTimes/CNN/Amazon).
    2. DOM Scan: Searches for keywords in <a> tags and aria-labels.
    3. AI Reasoning: Semantic fallback if rule-based methods fail.
    """
    # Strategy 1: Regex Hunt (Deep scan in raw source for hidden strings)
    url_pattern = re.compile(r'["\'](https?://[^\s"\'<>]+(?:auth/login|myaccount|signin|account/login|/login)[^\s"\'<>]*?)["\']')
    matches = url_pattern.findall(raw_html)
    for match in matches:
        if not any(ext in match.lower() for ext in ['.js', '.css', '.png', '.jpg']):
            return match

    # Strategy 2: Standard DOM Parsing (BS4)
    soup = BeautifulSoup(compressed_html, 'html.parser')
    keywords = ['log in', 'login', 'sign in', 'signin', 'my account', 'auth']
    for a_tag in soup.find_all('a', href=True):
        href_val = a_tag['href'].lower()
        text_val = a_tag.get_text(separator=' ', strip=True).lower()
        if any(kw in href_val or kw in text_val for kw in keywords):
            if not any(trap in href_val for trap in ['logout', 'help', 'search', 'newsletter']):
                return a_tag['href']

    # Strategy 3: AI Semantic Reasoning
    prompt = f"""
    You are an expert web navigator. Find the Login/Sign-in URL from this HTML.
    Focus on 'href' or 'data-url' attributes.
    Return ONLY the raw URL string. If not found, return "NOT_FOUND".
    
    HTML Snippet:
    {compressed_html[:80000]}
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

def extract_form_with_ai(compressed_html):
    """
    LLM Extraction: Precisely extracts the authentication HTML block.
    """
    prompt = f"""
    You are an AI automation agent. 
    Extract the raw HTML snippet for the login form or authentication container.
    
    Rules:
    1. Return ONLY raw HTML.
    2. Exclude search bars, footers, and site navigation.
    3. If not found, return "NOT_FOUND".
    
    HTML Content:
    {compressed_html[:80000]}
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

# --- 3. Agent Workflow ---

def run_agent_workflow(start_url):
    """
    Streamlined Logic:
    1. Scan Main Page for Login URL.
    2. Navigate to that URL.
    3. Extract the final HTML snippet.
    """
    try:
        # High-stealth headers to bypass basic WAF
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Step 1: Discover Entry Point
        st.info(f"🕵️ Scanning main page: {start_url}")
        response = requests.get(start_url, headers=headers, timeout=12)
        response.raise_for_status()
        
        login_href = find_login_link_with_ai(clean_html(response.text), response.text)
        
        if login_href == "NOT_FOUND":
            return "ERROR: Agent could not identify a login entry point.", start_url

        # Step 2: Navigate to identified URL
        target_url = urljoin(start_url, login_href)
        st.success(f"🔗 Entry point identified: {target_url}")
        
        st.info("🚀 Extracting authentication module...")
        response2 = requests.get(target_url, headers=headers, timeout=12)
        response2.raise_for_status()
        
        # Step 3: Final Extraction
        final_html_snippet = extract_form_with_ai(clean_html(response2.text))
        
        return final_html_snippet, target_url

    except Exception as e:
        return f"ERROR: Execution failed. {str(e)}", start_url

# --- 4. Streamlit UI Interface ---

st.set_page_config(page_title="AI Auth Scraper", page_icon="🤖", layout="centered")

st.title("Autonomous AI Web Scraper 🤖")
st.markdown("Automated detection of login portals and HTML snippet extraction.")

# Sidebar for Suggested Links
with st.sidebar:
    st.header("Suggested Test Links")
    st.markdown("Click below to copy a link:")
    st.code("https://www.amazon.com/")
    st.code("https://stackoverflow.com/questions")
    st.code("https://edition.cnn.com/")
    st.code("https://www.box.com/home")
    st.code("https://news.yahoo.com")

input_url = st.text_input("Enter Website URL:", placeholder="https://www.nytimes.com")

if st.button("🚀 Start Extraction", type="primary"):
    if input_url:
        with st.spinner("Agent is analyzing the web structure..."):
            snippet, final_url = run_agent_workflow(input_url)
            
            st.divider()
            
            if snippet.startswith("ERROR"):
                st.error(snippet)
            else:
                st.subheader("✅ Extracted HTML Snippet")
                # This is the primary output as requested
                st.code(snippet, language='html')
                
                with st.expander("Process Details"):
                    st.write(f"**Target URL:** `{final_url}`")
    else:
        st.warning("Please enter a valid URL.")
