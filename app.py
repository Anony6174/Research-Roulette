import streamlit as st
import hashlib
import random
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import socket
import urllib3.util.connection as urllib3_cn

# Force IPv4 because IPv6 is broken in some environments and causes arXiv API to timeout
def allowed_gai_family():
    return socket.AF_INET
urllib3_cn.allowed_gai_family = allowed_gai_family

# --- CONFIGURATION ---
st.set_page_config(page_title="Research Roulette", page_icon="🤪🔬", layout="wide")

DOMAIN_MAPPINGS = {
    "AI for Science (AI4Science)": ["cs.AI", "cs.LG", "q-bio.BM", "q-bio.CB", "physics.comp-ph", "stat.ML"],
    "Computer Science": ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.CR", "cs.DS", "cs.SE", "cs.RO", "cs.SY"],
    "Computational Biology": ["q-bio.BM", "q-bio.CB", "q-bio.GN", "q-bio.MN", "q-bio.NC", "q-bio.TO", "q-bio.PE", "q-bio.QM"],
    "Mathematics": ["math.AP", "math.CO", "math.PR", "math.ST", "math.NT", "math.AG"],
    "Physics": ["physics.comp-ph", "physics.data-an", "quant-ph", "astro-ph.CO", "cond-mat.mtrl-sci", "hep-th"],
    "Statistics": ["stat.ML", "stat.AP", "stat.ME", "stat.CO", "stat.TH"],
    "Quantitative Finance": ["q-fin.CP", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.PR", "q-fin.RM", "q-fin.ST", "q-fin.TR"],
    "Electrical Eng & Systems Science": ["eess.AS", "eess.IV", "eess.SP", "eess.SY"],
    "Economics": ["econ.EM", "econ.GN", "econ.TH"],
    "Cybersecurity & Binary Exploitation": ["cs.CR"],
    "Hardware & Embedded Systems": ["cs.AR", "eess.SY"]
}

# --- CHAOS ENGINE ---
def generate_seed(inputs):
    """Hashes a list of string inputs to generate a stable integer seed."""
    combined = "".join(str(i) for i in inputs)
    hash_obj = hashlib.sha256(combined.encode())
    return int(hash_obj.hexdigest(), 16)

# --- FETCH ENGINE ---
def fetch_papers(categories, max_years_back):
    """Fetches papers from arXiv based on selected categories and time limit."""
    if not categories:
        return []
    
    # Build query
    all_subcategories = []
    for cat in categories:
        all_subcategories.extend(DOMAIN_MAPPINGS[cat])
    
    # Remove duplicates and sort to ensure deterministic selection
    all_subcategories = sorted(list(set(all_subcategories)))
    
    # Randomly pick ONE subcategory using the seeded RNG
    chosen_subcat = random.choice(all_subcategories)
            
    # Use the arXiv RSS feed which is immune to the severe rate-limiting of the main API
    url = f"https://rss.arxiv.org/rss/{chosen_subcat}"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from arXiv RSS: {e}")
        return []

    root = ET.fromstring(response.content)
    
    papers = []
    
    dc_ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
    
    for item in root.findall('.//item'):
        title_raw = item.find('title').text.strip() if item.find('title') is not None else "Unknown Title"
        summary_html = item.find('description').text.strip() if item.find('description') is not None else ""
        published = item.find('pubDate').text.strip() if item.find('pubDate') is not None else "Unknown Date"
        
        creator_elem = item.find('dc:creator', dc_ns)
        authors = creator_elem.text.split(', ') if creator_elem is not None and creator_elem.text else ["Unknown Authors"]
        
        link = item.find('link').text.strip() if item.find('link') is not None else ""
        pdf_link = link.replace('/abs/', '/pdf/') if link else ""
        
        papers.append({
            "title": title_raw,
            "summary": summary_html,
            "published": published,
            "authors": authors,
            "pdf_link": pdf_link,
            "abstract_length": len(summary_html)
        })
            
    return papers

# --- UI LAYOUT ---
st.title("🤪🔬 Research Roulette")
st.markdown("Break out of your filter bubble! Let your *vibes* dictate the next paper you read.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. The Vibe Check")
    st.markdown("Your answers mathematically generate a chaotic random seed.")
    
    caffeine = st.select_slider(
        "Caffeine Level",
        options=["Decaf", "1 Cup", "Jitters", "Seeing Sounds", "I am Speed"]
    )
    
    social_battery = st.select_slider(
        "Social Battery",
        options=["Dead", "1%", "Low Power Mode", "Charged", "Overclocked"]
    )
    
    codebase_stability = st.selectbox(
        "Current Codebase Stability",
        ["Rock Solid", "A Few Bugs", "Held by Duct Tape", "Dumpster Fire", "What Codebase?"]
    )
    
    mood_word = st.text_input("Describe your mood in one word", value="Chaotic")

    st.header("2. Scientific Dials")
    time_dial = st.slider("Years Back (Max)", min_value=1, max_value=20, value=5)
    
    complexity = st.select_slider(
        "Complexity (Abstract Length Proxy)",
        options=["Light Read", "Moderate", "Dense", "Brain Melter"]
    )
    
    domains = st.multiselect(
        "Domain Toggles",
        options=list(DOMAIN_MAPPINGS.keys()),
        default=["AI for Science (AI4Science)", "Computer Science"]
    )

with col2:
    st.header("3. The Roulette")
    
    if st.button("🎲 Spin the Roulette!", use_container_width=True):
        if not domains:
            st.warning("Please select at least one Domain Toggle.")
        else:
            with st.spinner("Channeling your vibes to the arXiv gods..."):
                # 1. Generate Seed
                seed_val = generate_seed([caffeine, social_battery, codebase_stability, mood_word])
                random.seed(seed_val + random.randint(0,100))
                
                # 2. Fetch Papers
                papers = fetch_papers(domains, time_dial)
                
                if not papers:
                    st.error("No papers found matching your criteria. Try expanding your search!")
                else:
                    # 3. Apply Complexity Filter
                    # Sort by abstract length to divide into quartiles
                    papers.sort(key=lambda x: x['abstract_length'])
                    n = len(papers)
                    
                    if complexity == "Light Read":
                        filtered_papers = papers[:max(1, n//4)]
                    elif complexity == "Moderate":
                        filtered_papers = papers[n//4 : 2*n//4]
                    elif complexity == "Dense":
                        filtered_papers = papers[2*n//4 : 3*n//4]
                    else: # Brain Melter
                        filtered_papers = papers[3*n//4:]
                        
                    # If the selected quartile is empty, fallback to all papers
                    if not filtered_papers:
                        filtered_papers = papers
                        
                    # 4. Select ONE paper randomly using the seeded RNG
                    selected_paper = random.choice(filtered_papers)
                    
                    # 5. Display
                    st.balloons()
                    
                    st.success("✨ Paper Selected! ✨")
                    
                    st.subheader(selected_paper["title"])
                    st.caption(f"**Published:** {selected_paper['published'][:10]} | **Authors:** {', '.join(selected_paper['authors'])}")
                    
                    st.markdown("### Abstract")
                    st.write(selected_paper["summary"])
                    
                    st.markdown(f"[🔗 Read the PDF]({selected_paper['pdf_link']})")
                    
                    with st.expander("Nerd Stats (Seed Details)"):
                        st.write(f"- **Inputs Hash:** {hex(seed_val)}")
                        st.write(f"- **Papers Fetched:** {len(papers)}")
                        st.write(f"- **Papers after Complexity Filter:** {len(filtered_papers)}")
                        st.write(f"- **Selected Abstract Length:** {selected_paper['abstract_length']} chars")
