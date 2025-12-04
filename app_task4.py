import streamlit as st
import altair as alt
import pandas as pd

# --- 1. CONFIGURATION & FILE PATHS ---
# 映射下拉菜单选项到对应的 CSV 文件名
# 注意：文件名基于你之前上传的文件
DATA_FILES = {
    "Global": {
        "incidence": "GTB_report_2025_incidence.csv",
        "rr": "GTB_report_2025_RR_prevalence.csv"
    },
    "WHO African Region": {
        "incidence": "African_region_report_2025_incidence.csv",
        "rr": "African_region_report_2025_RR_prevalence.csv"
    },
    "WHO/PAHO Region of the Americas": {
        "incidence": "Region_of_the_Americas_report_2025_incidence.csv",
        "rr": "Region_of_the_Americas_report_2025_RR_prevalence.csv"
    },
    "WHO Eastern Mediterranean Region": {
        "incidence": "Eastern_Mediterranean_region_report_2025_incidence.csv",
        "rr": "Eastern_Mediterranean_region_report_2025_RR_prevalence.csv"
    },
    "WHO European Region": {
        "incidence": "European_region_report_2025_incidence.csv",
        "rr": "European_region_report_2025_RR_prevalence.csv"
    },
    "WHO South-East Asia Region": {
        "incidence": "South_East_Asia_Region_report_2025_incidence.csv",
        "rr": "South_East_Asia_Region_report_2025_RR_prevalence.csv"
    },
    "WHO Western Pacific Region": {
        "incidence": "Western_Pacific_Region_report_2025_incidence.csv",
        "rr": "Western_Pacific_Region_report_2025_RR_prevalence.csv"
    }
}

# --- 2. DATA LOADING FUNCTION ---
@st.cache_data
def load_data(region_key):
    """Loads and cleans data for the selected region."""
    files = DATA_FILES.get(region_key)
    if not files:
        return pd.DataFrame() # Return empty if not found

    try:
        # Load Raw CSVs
        inc_df = pd.read_csv(files["incidence"])
        rr_df = pd.read_csv(files["rr"])

        # 1. Clean Incidence Data
        # Rename columns to standardized internal names
        inc_clean = inc_df.rename(columns={
            'Category': 'year',
            'Estimated TB incidence per 100 000 population': 'tb_incidence',
            'Uncertainty interval (low)': 'tb_incidence_low',
            'Uncertainty interval (high)': 'tb_incidence_high'
        })
        # Keep only relevant columns
        inc_clean = inc_clean[['year', 'tb_incidence', 'tb_incidence_low', 'tb_incidence_high']]

        # 2. Clean RR Prevalence Data
        rr_clean = rr_df.rename(columns={
            'Category': 'year',
            'Previously treated pulmonary bacteriologically confirmed cases': 'rr_prev_prevtx',
            'New pulmonary bacteriologically confirmed cases': 'rr_prev_new'
        })
        rr_clean = rr_clean[['year', 'rr_prev_prevtx', 'rr_prev_new']]

        # 3. Merge Datasets
        merged = pd.merge(inc_clean, rr_clean, on='year', how='inner')

        # 4. Filter for 2015-2023 as requested
        merged = merged[(merged['year'] >= 2015) & (merged['year'] <= 2023)]
        
        return merged

    except Exception as e:
        st.error(f"Error loading data for {region_key}: {e}")
        return pd.DataFrame()

# --- 3. STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="TB Trends Visualization", layout="wide")

st.title("Trend comparison of TB incidence and RR-TB prevalence (2015–2023)")
st.markdown("This visualization explores the relationship between disease burden and drug resistance over time.")

# --- 4. INTERACTIVE CONTROLS (SELECTION BAR) ---
# Exact categories as requested
region_options = [
    "Global",
    "WHO African Region",
    "WHO/PAHO Region of the Americas",
    "WHO Eastern Mediterranean Region",
    "WHO European Region",
    "WHO South-East Asia Region",
    "WHO Western Pacific Region"
]

selected_region = st.selectbox("Select WHO Region:", region_options)

# Load Data based on selection
df = load_data(selected_region)

if df.empty:
    st.warning("Data not found for this region. Please ensure CSV files are uploaded.")
else:
    # --- 5. ALTAIR VISUALIZATION ---
    
    # We need to transform the data to Long Format to create a proper legend for the lines.
    # The CI Band will be a separate layer.
    
    # Define colors
    COLOR_INCIDENCE = "#2ca02c"      # Green
    COLOR_CI = "#98df8a"             # Light Green
    COLOR_RR_PREV = "#ffbb78"        # Light Orange
    COLOR_RR_NEW = "#ff7f0e"         # Dark Orange
    
    # Base chart
    base = alt.Chart(df).encode(
        x=alt.X('year:O', axis=alt.Axis(title='Year'))
    )

    # Layer 1: 95% Confidence Interval (Band)
    # This stands alone as an area chart
    ci_band = base.mark_area(opacity=0.3, color=COLOR_CI).encode(
        y=alt.Y('tb_incidence_low:Q'),
        y2=alt.Y2('tb_incidence_high:Q'),
        tooltip=[
            alt.Tooltip('year', title='Year'),
            alt.Tooltip('tb_incidence_low', title='Incidence CI Low'),
            alt.Tooltip('tb_incidence_high', title='Incidence CI High')
        ]
    )

    # To create a unified legend for the lines, we fold the columns.
    # We create a new dataframe for the lines part or use transform_fold
    lines_base = base.transform_fold(
        ['tb_incidence', 'rr_prev_prevtx', 'rr_prev_new'],
        as_=['Indicator', 'Value']
    )

    # Layer 2: Lines
    # We manually map the fold names to colors to match requirements
    lines = lines_base.mark_line(point=True, strokeWidth=3).encode(
        y=alt.Y('Value:Q', axis=alt.Axis(title='Indicator value')),
        color=alt.Color('Indicator:N', 
                        scale=alt.Scale(
                            domain=['tb_incidence', 'rr_prev_prevtx', 'rr_prev_new'],
                            range=[COLOR_INCIDENCE, COLOR_RR_PREV, COLOR_RR_NEW]
                        ),
                        legend=alt.Legend(title="Legend", orient='right')
        ),
        tooltip=['year', 'Indicator', 'Value']
    )

    # Combine Layers
    # Note: We are using a single Y-axis ("Indicator value") for both rates and percentages
    # as per the "compare trend direction" instruction.
    chart = alt.layer(
        ci_band,
        lines
    ).properties(
        title=f"{selected_region}: Incidence vs. Resistance",
        height=500
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
    
    # Optional: Display raw data snippet for verification
    with st.expander("View Data Source"):
        st.dataframe(df)