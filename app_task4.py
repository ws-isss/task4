import streamlit as st
import pandas as pd
import altair as alt

DATA_FILES = {
    "Global": {
        "incidence": "GTB_report_2025_incidence.csv",
        "rr": "GTB_report_2025_RR_prevalence.csv",
        "description": "Worldwide average trends showing the overall global picture."
    },
    "African Region": {
        "incidence": "African_region_report_2025_incidence.csv",
        "rr": "African_region_report_2025_RR_prevalence.csv",
        "description": "High burden region showing significant progress in reducing incidence."
    },
    "Region of the Americas": {
        "incidence": "Region_of_the_Americas_report_2025_incidence.csv",
        "rr": "Region_of_the_Americas_report_2025_RR_prevalence.csv",
        "description": "Region with relatively low TB incidence compared to global averages."
    },
    "Eastern Mediterranean Region": {
        "incidence": "Eastern_Mediterranean_region_report_2025_incidence.csv",
        "rr": "Eastern_Mediterranean_region_report_2025_RR_prevalence.csv",
        "description": "Shows distinct trends in resistance reduction among treated cases."
    },
    "European Region": {
        "incidence": "European_region_report_2025_incidence.csv",
        "rr": "European_region_report_2025_RR_prevalence.csv",
        "description": "Characterized by lower incidence but exceptionally high rates of drug resistance."
    },
    "South-East Asia Region": {
        "incidence": "South_East_Asia_Region_report_2025_incidence.csv",
        "rr": "South_East_Asia_Region_report_2025_RR_prevalence.csv",
        "description": "Region with a very high incidence burden."
    },
    "Western Pacific Region": {
        "incidence": "Western_Pacific_Region_report_2025_incidence.csv",
        "rr": "Western_Pacific_Region_report_2025_RR_prevalence.csv",
        "description": "Diverse region showing steady declines in incidence."
    }
}

@st.cache_data
def load_and_process_data(region_name):
    files = DATA_FILES.get(region_name)
    if not files:
        return None

    try:
        inc_df = pd.read_csv(files["incidence"])
        rr_df = pd.read_csv(files["rr"])

        if 'Category' in inc_df.columns:
            inc_df = inc_df.rename(columns={'Category': 'Year'})
        if 'Category' in rr_df.columns:
            rr_df = rr_df.rename(columns={'Category': 'Year'})

        # Merge on Year (Inner join to keep matching years)
        merged = pd.merge(inc_df, rr_df, on='Year', how='inner')
        return merged
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error processing {region_name}: {e}")
        return None

st.set_page_config(page_title="TB Task 4", layout="wide")
st.title("Task 4: Drug Resistance vs. Disease Incidence")
st.markdown("""
### Explore Global and Regional Trends
Compare how the percentage of Rifampicin-Resistant TB (RR-TB) relates to overall TB incidence across different WHO regions.
""")

st.sidebar.header("Filter Settings")

available_regions = list(DATA_FILES.keys())
selected_region = st.sidebar.selectbox("Select Region / View:", available_regions)

current_df = load_and_process_data(selected_region)

if selected_region in DATA_FILES:
    st.sidebar.info(f"**{selected_region}:** {DATA_FILES[selected_region]['description']}")

if current_df is not None:
    st.subheader(f"Trends in {selected_region}")
    
    base = alt.Chart(current_df).encode(
        x=alt.X('Year:O', axis=alt.Axis(title='Year'))
    )

    line_incidence = base.mark_line(point=True, strokeDash=[5,5]).encode(
        y=alt.Y('Estimated TB incidence per 100 000 population', 
                axis=alt.Axis(title='Incidence per 100k (Blue)', titleColor='#1f77b4')),
        tooltip=['Year', alt.Tooltip('Estimated TB incidence per 100 000 population', title='Incidence')]
    ).mark_line(color='#1f77b4')

    line_rr_new = base.mark_line(point=True).encode(
        y=alt.Y('New pulmonary bacteriologically confirmed cases', 
                axis=alt.Axis(title='RR-TB Prevalence % (Green/Red)', titleColor='#d62728')), 
        tooltip=['Year', alt.Tooltip('New pulmonary bacteriologically confirmed cases', title='RR % (New)')]
    ).mark_line(color='#2ca02c')

    line_rr_prev = base.mark_line(point=True).encode(
        y=alt.Y('Previously treated pulmonary bacteriologically confirmed cases', 
                axis=alt.Axis(title='RR-TB Prevalence %')), 
        tooltip=['Year', alt.Tooltip('Previously treated pulmonary bacteriologically confirmed cases', title='RR % (Prev. Treated)')]
    ).mark_line(color='#d62728')

    chart = alt.layer(
        line_incidence, 
        line_rr_new, 
        line_rr_prev
    ).resolve_scale(
        y='independent' 
    ).properties(
        height=450
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    st.divider()
    st.markdown("### 📊 Key Observations")
    
    latest_year = current_df['Year'].max()
    latest_inc = current_df.loc[current_df['Year'] == latest_year, 'Estimated TB incidence per 100 000 population'].values[0]
    
    st.write(f"In **{latest_year}**, the estimated TB incidence in **{selected_region}** was **{latest_inc:.1f}** per 100,000 population.")

    if selected_region == "European Region":
        st.warning("⚠️ **Critical Insight:** Europe has a unique pattern. While incidence is low, the drug resistance in *previously treated cases* is alarmingly high (over 50%), highlighting a crisis in antibiotic effectiveness for relapsed patients.")
    elif selected_region == "African Region":
        st.success("✅ **Progress:** The African region started with a very high burden but shows a steep downward trend in incidence, indicating successful disease control interventions.")
    elif selected_region == "Region of the Americas":
        st.info("ℹ️ **Low Burden:** The Americas maintain one of the lowest incidence rates globally, though surveillance for resistance remains important.")
    elif selected_region == "Global":
        st.write("🌍 **Global Trend:** Overall, we see a positive correlation where resistance rates are slowly declining alongside incidence, suggesting that global control strategies are working, though gaps remain.")
    
else:
    st.error(f"⚠️ Data files for **{selected_region}** not found.")
    st.code(f"Please ensure these files are in your directory:\n- {DATA_FILES[selected_region]['incidence']}\n- {DATA_FILES[selected_region]['rr']}")

st.caption("""
**Legend:** - 🔵 **Blue (Left Axis):** Estimated TB Incidence per 100k.
- 🟢 **Green (Right Axis):** % of RR-TB in New Cases.
- 🔴 **Red (Right Axis):** % of RR-TB in Previously Treated Cases.
""")