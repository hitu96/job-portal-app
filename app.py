import streamlit as st
import pandas as pd
from jobspy import scrape_jobs

st.set_page_config(page_title="Pro Job Portal", page_icon="⚡", layout="wide")

# Modern SaaS UI Custom Styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .subtitle {
        color: #9ca3af;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">⚡ Direct Source Job Portal</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Search live job postings and jump directly to company ATS application pages.</p>', unsafe_allow_html=True)

# Sleek Sidebar Controls
with st.sidebar:
    st.header("⚙️ Preferences")
    country = st.selectbox("Country Server", ["india", "usa", "uk", "canada", "australia"], index=0)
    hours_old = st.selectbox("Date Posted", [24, 72, 168, 720], index=1, format_func=lambda x: {24: "Last 24 Hours", 72: "Last 3 Days", 168: "Last 7 Days", 720: "Last 30 Days"}[x])
    results_wanted = st.slider("Results per board", 5, 30, 15)
    remote_only = st.checkbox("Remote roles only")
    sites = st.multiselect("Active Boards", ["indeed", "naukri", "linkedin", "glassdoor"], default=["indeed", "naukri", "linkedin"])

# Main Search Input Bar
with st.form("search_bar"):
    col1, col2, col3 = st.col_2 = st.columns([3, 2, 1]) if False else st.columns([3, 2, 1])
    with col1:
        keyword = st.text_input("Job Title / Keyword", placeholder="e.g. Full Stack Developer, Product Manager")
    with col2:
        location = st.text_input("Location", value="Delhi, India")
    with col3:
        st.write("") # spacing alignment
        st.write("")
        search_submitted = st.form_submit_button("Search Jobs", type="primary", use_container_width=True)

if search_submitted:
    if not keyword.strip():
        st.warning("Please type a keyword to search.")
    else:
        with st.spinner(f"Scraping live listings for '{keyword}'... Please wait (~10s)"):
            try:
                jobs = scrape_jobs(
                    site_name=sites,
                    search_term=keyword,
                    location=location,
                    results_wanted=results_wanted,
                    hours_old=hours_old,
                    country_indeed=country,
                    is_remote=remote_only
                )

                if jobs is None or jobs.empty:
                    st.info("No matching jobs found. Try loosening your location or keyword filters.")
                else:
                    st.success(f"Found {len(jobs)} live openings!")
                    st.divider()

                    for _, row in jobs.iterrows():
                        title = row.get("title") or "Untitled Role"
                        company = row.get("company") or "Confidential"
                        loc = row.get("location") or location
                        site = str(row.get("site", "")).capitalize()
                        date_posted = row.get("date_posted") or "Recently"
                        
                        direct_url = row.get("job_url_direct")
                        board_url = row.get("job_url")
                        has_direct = pd.notna(direct_url) and str(direct_url).strip() != ""
                        target_url = str(direct_url).strip() if has_direct else str(board_url).strip()
                        btn_label = "🚀 Apply on Company Site" if has_direct else f"🔗 Apply on {site}"

                        with st.container(border=True):
                            c_info, c_btn = st.columns([4, 1])
                            with c_info:
                                st.markdown(f"### {title}")
                                st.markdown(f"🏢 **{company}** &nbsp;•&nbsp; 📍 {loc} &nbsp;•&nbsp; 🗓️ `{date_posted}` &nbsp;•&nbsp; 🌐 `{site}`")
                                
                                if pd.notna(row.get("min_amount")) and pd.notna(row.get("max_amount")):
                                    st.caption(f"💰 {row.get('currency', '')} {row['min_amount']:,.0f} – {row['max_amount']:,.0f} ({row.get('interval', 'yearly')})")
                            with c_btn:
                                st.write("")
                                if target_url and target_url != "nan":
                                    st.link_button(btn_label, target_url, use_container_width=True, type="primary" if has_direct else "secondary")
            except Exception as e:
                st.error(f"Search failed: {e}")
