import streamlit as st
import pandas as pd
from jobspy import scrape_jobs

# Page setup
st.set_page_config(page_title="Direct Job Aggregator", page_icon="💼", layout="wide")

# Custom styling for cleaner job cards
st.markdown("""
    <style>
    .job-card {
        padding: 18px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Direct Source Job Portal")
st.caption("Search live jobs across Indeed, LinkedIn, Naukri, and Glassdoor — and go straight to the source to apply.")

# Top Search Bar
with st.form("search_form"):
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    
    with col1:
        keyword = st.text_input("Job Title / Field / Keyword", placeholder="e.g., Data Analyst, React Developer, HR")
    with col2:
        location = st.text_input("City or Location", value="Delhi, India")
    with col3:
        hours_old = st.selectbox(
            "Date Posted",
            options=[24, 72, 168, 720],
            index=1,
            format_func=lambda x: {24: "Last 24 Hours", 72: "Last 3 Days", 168: "Last 7 Days", 720: "Last 30 Days"}[x]
        )
    with col4:
        country = st.selectbox("Country Server", ["india", "usa", "uk", "canada", "australia"], index=0)

    f_col1, f_col2, f_col3 = st.columns([4, 2, 2])
    with f_col1:
        sites = st.multiselect(
            "Job Boards to Search",
            options=["indeed", "naukri", "linkedin", "glassdoor"],
            default=["indeed", "naukri", "linkedin"]
        )
    with f_col2:
        results_wanted = st.slider("Results per board", min_value=5, max_value=30, value=15)
    with f_col3:
        remote_only = st.checkbox("Remote roles only")

    submitted = st.form_submit_button("🔍 Search Live Jobs", type="primary", use_container_width=True)

# Run Scraper When User Clicks Search
if submitted:
    if not keyword.strip():
        st.warning("Please enter a job keyword first.")
    elif not sites:
        st.warning("Please select at least one job board.")
    else:
        with st.spinner(f"Fetching live '{keyword}' jobs from {', '.join(sites)}... (Takes ~10 seconds)"):
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
                    st.info("No matching jobs found right now. Try broadening your keyword or timeframe.")
                else:
                    # Top bar with total count and CSV export
                    top_c1, top_c2 = st.columns([4, 1])
                    with top_c1:
                        st.success(f"✅ Found **{len(jobs)}** live jobs matching **'{keyword}'**")
                    with top_c2:
                        csv = jobs.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "📥 Export CSV",
                            data=csv,
                            file_name=f"{keyword.replace(' ', '_')}_jobs.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    st.divider()

                    # Display each job with direct apply button
                    for _, row in jobs.iterrows():
                        title = row.get("title") or "Untitled Role"
                        company = row.get("company") or "Company Not Listed"
                        loc = row.get("location") or location
                        site = str(row.get("site", "")).capitalize()
                        date_posted = row.get("date_posted") or "Recently"

                        # Prioritize direct company ATS application link if available
                        direct_url = row.get("job_url_direct")
                        board_url = row.get("job_url")
                        has_direct = pd.notna(direct_url) and str(direct_url).strip() != ""
                        
                        target_url = str(direct_url).strip() if has_direct else str(board_url).strip()
                        btn_label = "🚀 Apply on Company Site" if has_direct else f"🔗 Apply on {site}"

                        with st.container(border=True):
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                st.subheader(f"{title}")
                                st.markdown(f"🏢 **{company}** &nbsp;•&nbsp; 📍 {loc} &nbsp;•&nbsp; 🗓️ Posted: `{date_posted}` &nbsp;•&nbsp; 🌐 Source: `{site}`")
                                
                                # Show salary if available
                                if pd.notna(row.get("min_amount")) and pd.notna(row.get("max_amount")):
                                    currency = row.get("currency") or ""
                                    interval = row.get("interval") or "yearly"
                                    st.caption(f"💰 Salary: {currency} {row['min_amount']:,.0f} – {row['max_amount']:,.0f} ({interval})")
                            with c2:
                                st.write("") # Vertical alignment spacing
                                if target_url and target_url != "nan":
                                    st.link_button(btn_label, target_url, use_container_width=True, type="primary" if has_direct else "secondary")

            except Exception as e:
                st.error(f"Could not complete search: {e}")
