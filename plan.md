# Project Specification: Research Roulette 🤪🔬

## 1. Agent Role & Context
You are an expert Python and Streamlit developer. Your task is to build, refine, and maintain the "Research Roulette" web application. This application is a serendipitous research paper discovery tool that breaks users out of their filter bubbles. It uses a chaotic "mood questionnaire" to mathematically generate a random seed, which then fetches a single, random research paper from scientific databases (like arXiv or PubMed E-Utilities). 

The app must be lightweight, capable of running perfectly on a `localhost` environment, and easy to deploy directly from GitHub with a simple `requirements.txt`.

## 2. Tech Stack
* **Frontend & UI State:** Streamlit (`streamlit`)
* **Backend / API Handling:** Python (`requests`, `xml.etree.ElementTree`)
* **Seed Generation:** Python's built-in `hashlib` and `random`

## 3. Core Features to Implement

### A. The "Vibe Check" (Chaos Engine)
A questionnaire that dictates the random seed generation. User inputs must be concatenated, hashed via SHA-256, and converted to an integer to seed Python's `random.seed()`.
* *Example Inputs:* Caffeine levels, social battery, codebase stability (e.g., "Dumpster Fire", "Held by Duct Tape").

### B. Scientific Dials & Controls
The UI must contain the following controls to filter the API requests:
* **Time Dial:** Slider for publication date (e.g., 1 to 10 years back).
* **Complexity Dial:** Slider filtering by abstract length or author count (e.g., "Light Read" vs. "Brain Melter").
* **Domain Toggles:** Multiselect box mapping to specific database categories. 

**Default Domain Toggles to Implement:**
1.  **Computational Biology & Bioinformatics** (e.g., Protein folding, AMP generation, sequence analysis)
2.  **Deep Learning & Machine Learning** (e.g., Foundation models, in-context learning, PINNs)
3.  **Cybersecurity & Binary Exploitation** (e.g., Software security, reverse engineering)
4.  **Hardware & Embedded Systems** (e.g., FPGA architectures, HDL, microcontrollers)

### C. The Fetch Engine
* Construct an HTTP GET request to the arXiv API (and/or PubMed E-Utilities).
* Query based on the selected domain toggles and time dial.
* Retrieve a large batch of papers, filter by the complexity proxy, and use the Chaos Engine's seeded random number to select exactly *one* paper.
* Extract: Title, Abstract, Publication Date, and PDF Link.

## 4. UI/UX Guidelines
* Keep the UI clean and strictly single-page using Streamlit's layout properties (`st.container`, `st.columns`).
* Use `st.spinner` and `st.balloons()` to make the paper selection feel like an event.
* Ensure all database errors or empty query results are handled gracefully with `st.error` or `st.warning`.

## 5. File Structure
```text
research-roulette/
├── app.py             # Main application and logic
├── requirements.txt   # Dependencies (streamlit, requests)
└── README.md          # Localhost setup instructions