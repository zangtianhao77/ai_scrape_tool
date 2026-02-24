# 🤖 AI-Powered Web Authentication Scraper

## 📌 Project Objective

This repository contains the solution for the AI Engineer Technical Assessment. The primary objective is to design, build, and deliver an AI-powered tool capable of web scraping, component detection, and functional delivery.

Unlike traditional rule-based web scrapers that rely on brittle CSS selectors or XPath, this application leverages Large Language Models (LLMs) to perform semantic DOM analysis and Agentic auto-navigation, ensuring highly robust extraction across modern, complex web architectures.

## ✨ Core Features

* **Dynamic URL Input (UI):** Provides a clean Streamlit interface that allows users to input any website URL dynamically.


* **LLM-Powered Component Detection:** Scrapes the HTML markup and uses an AI model to intelligently locate the Username and Password authentication section (e.g., `<input type="password">`, `<form>` tags, login divs).


* **Agentic Auto-Navigation:** If a user inputs a homepage or content URL instead of a direct login page, the built-in AI Agent performs multi-step reasoning to locate the "Log in" or "Sign in" link, dynamically navigates to the target page, and performs the extraction.
* **Structured HTML Output:** The application accurately displays or returns the raw HTML snippet containing the login form. If no component exists or the page is entirely blocked by anti-bot systems, it gracefully states that none was found.


* **Multi-Domain Validation:** Pre-configured to test against five different websites (including news media, SaaS, and developer communities) to demonstrate generalization.



## 🧠 Architecture & Technical Trade-offs

In modern web development, frontend frameworks often generate dynamic, non-semantic class names, making traditional scraping libraries (like `BeautifulSoup` alone) unreliable.

By framing this extraction task as an **LLM Context Analysis** problem:

1. **Robustness:** The AI understands the semantic meaning of authentication interfaces regardless of the underlying tag structures or language.
2. **Token Optimization:** A preprocessing pipeline strips noisy tags (`<script>`, `<style>`, `<svg>`) before passing the DOM to the LLM, strictly managing context window limits and reducing API costs.

### Limitations & Future Work

Currently, the scraper relies on HTTP requests to fetch the initial HTML markup. Enterprise websites often deploy strict anti-bot mechanisms (e.g., Cloudflare, Datadome) that intercept basic requests, returning a CAPTCHA challenge instead of the actual DOM.

* **Future Improvement:** For a production-grade AI Agent, the underlying fetch mechanism should be upgraded to a headless browser (e.g., Playwright or Selenium) to execute JavaScript, render Single Page Applications (SPAs), and bypass basic bot protections.

---

## 🚀 Local Setup Instructions

If you prefer to run the application locally instead of using the deployed version, please follow these clear setup instructions.

**1. Clone the repository**

```bash
git clone <your-repository-url>
cd <your-project-directory>

```

**2. Create and activate a virtual environment**

```bash
# Mac/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

```

**3. Install dependencies**

```bash
pip install -r requirements.txt

```

*(Dependencies include: `streamlit`, `requests`, `beautifulsoup4`, `openai`)*

**4. Configure Environment Variables**
Open the application file and replace the placeholder API key with your actual OpenAI API Key:

```python
OPENAI_API_KEY = "sk-your-actual-api-key-here" 

```

**5. Run the Application**

```bash
streamlit run app.py

```

The application will automatically open in your default web browser at `http://localhost:8501`.

---

## 🧪 Sample Test Cases

The application has been configured to test against the following diverse URLs, which include both direct login pages and complex content pages that challenge the Agent's extraction and navigation logic:

1. **Stack Overflow (Developer Q&A):** `https://stackoverflow.com/questions`
2. **CNN (News Media):** `https://edition.cnn.com/`
3. **Salesforce (Enterprise SaaS):** `https://login.salesforce.com/`
4. **The New York Times (News Media):** `https://www.nytimes.com/`
5. **Box (Cloud Storage SaaS):** `https://account.box.com/login`
