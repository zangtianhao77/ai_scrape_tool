import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import time
from urllib.parse import urljoin

# set up API Key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY" 
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def clean_html(raw_html):
    """Clean HTML to save tokens while preserving structure and links."""
    soup = BeautifulSoup(raw_html, 'html.parser')
    for tag in soup(['script', 'style', 'svg', 'img', 'noscript', 'meta']):
        tag.decompose()
    return str(soup)

def extract_form_with_ai(compressed_html):
    """Core extraction logic: Looks for the form in the given HTML."""
    prompt = f"""
    You are an AI web automation agent.
    Identify and extract the HTML snippet containing the Username and Password authentication section (e.g., login form, auth div).
    
    Rules:
    1. Return ONLY the raw HTML snippet.
    2. Do not include markdown formatting.
    3. If no authentication component is found, return exactly: "NOT_FOUND"
    
    HTML Content:
    {compressed_html[:80000]}
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

def find_login_link_with_ai(compressed_html):
    """Reasoning logic: Looks for a login/sign-in link if the form is missing."""
    prompt = f"""
    You are an AI web navigator. This page does not contain a login form.
    Your task is to find the URL/href for the login or sign-in page.
    Look for `<a>` tags with text like "Log in", "Sign in", "Login", etc.
    
    Rules:
    1. Return ONLY the raw value of the `href` attribute (e.g., "/login" or "https://example.com/signin").
    2. Do not return any other text or markdown.
    3. If no such link exists, return exactly: "NOT_FOUND"
    
    HTML Content:
    {compressed_html[:80000]}
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

def agentic_auto_navigate_and_extract(start_url):
    """The Agent Workflow: Extract -> If failed -> Find Link -> Navigate -> Extract"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # --- Step 1: Check the starting URL ---
        st.info(f"🕵️ Agent Step 1: Analyzing starting URL: {start_url}")
        response = requests.get(start_url, headers=headers, timeout=10)
        response.raise_for_status()
        compressed_html = clean_html(response.text)
        
        form_snippet = extract_form_with_ai(compressed_html)
        
        if form_snippet != "NOT_FOUND":
            st.success("🎯 Direct hit! Login form found on the starting page.")
            return form_snippet, start_url
            
        # --- Step 2: Form not found, looking for a login link ---
        st.warning("⚠️ No form found on the starting page. Agent is looking for a login link...")
        login_href = find_login_link_with_ai(compressed_html)
        
        if login_href != "NOT_FOUND":
            # Convert relative URL (like "/login") to absolute URL
            absolute_login_url = urljoin(start_url, login_href)
            st.info(f"🔗 Agent Step 2: Login link found! Navigating to: {absolute_login_url}")
            
            # --- Step 3: Fetch the new URL and extract the form ---
            response2 = requests.get(absolute_login_url, headers=headers, timeout=10)
            response2.raise_for_status()
            compressed_html2 = clean_html(response2.text)
            
            final_snippet = extract_form_with_ai(compressed_html2)
            
            if final_snippet != "NOT_FOUND":
                st.success("🎯 Success! Form extracted after auto-navigation.")
                return final_snippet, absolute_login_url
            else:
                return "Failed to find form even after navigating to the login page.", absolute_login_url
        
        return "Agent could not find a login form or a login link on the provided page.", start_url

    except Exception as e:
        return f"Error processing URL: {e}", start_url

# --- Streamlit UI Integration Example ---
st.title("Autonomous AI Web Scraper 🤖")
st.markdown("Suggested Test URL:")
st.markdown("https://stackoverflow.com/questions")
st.markdown("https://edition.cnn.com/")
st.markdown("https://login.salesforce.com/")
st.markdown("https://www.nytimes.com/")
st.markdown("https://account.box.com/login")
test_url = st.text_input("Enter an URL: ")

if st.button("Start AI Agent"):
    if test_url:
        with st.spinner("AI Agent is working..."):
            snippet, final_url = agentic_auto_navigate_and_extract(test_url)
            st.write(f"**Final Evaluated URL:** {final_url}")
            st.subheader("Extracted HTML Snippet:")
            if snippet.startswith("Error") or snippet.startswith("Failed") or snippet.startswith("Agent"):
                st.error(snippet)
            else:
                st.code(snippet, language='html')