import streamlit as st
import altair as alt
import pandas as pd

# --- 1. CONFIGURATION & FILE PATHS ---
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
    files = DATA_FILES.get(region_key)
    if not files:
        return pd.DataFrame() 

    try:
        inc_df = pd.read_csv(files["incidence"])
        rr_df = pd.read_csv(files["rr"])

        # Clean Incidence Data
        if 'Category' in inc_df.columns:
            inc_df = inc_df.rename(columns={'Category': 'year'})
        
        inc_clean = inc_df.rename(columns={
            'Estimated TB incidence per 100 000 population': 'tb_incidence',
            'Uncertainty interval (low)': 'tb_incidence_low',
            'Uncertainty interval (high)': 'tb_incidence_high'
        })
        cols_to_keep = ['year', 'tb_incidence', 'tb_incidence_low', 'tb_incidence_high']
        inc_clean = inc_clean[[c for c in cols_to_keep if c in inc_clean.columns]]

        # Clean RR Prevalence Data
        if 'Category' in rr_df.columns:
            rr_df = rr_df.rename(columns={'Category': 'year'})
            
        rr_clean = rr_df.rename(columns={
            'Previously treated pulmonary bacteriologically confirmed cases': 'rr_prev_prevtx',
            'New pulmonary bacteriologically confirmed cases': 'rr_prev_new'
        })
        cols_to_keep_rr = ['year', 'rr_prev_prevtx', 'rr_prev_new']
        rr_clean = rr_clean[[c for c in cols_to_keep_rr if c in rr_clean.columns]]

        # Merge
        if not inc_clean.empty and not rr_clean.empty:
            merged = pd.merge(inc_clean, rr_clean, on='year', how='inner')
            merged = merged[(merged['year'] >= 2015) & (merged['year'] <= 2023)]
            return merged
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error loading data for {region_key}: {e}")
        return pd.DataFrame()

# --- 3. STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="TB Trends Visualization", layout="wide")

st.title("Trend comparison of TB incidence and RR-TB prevalence (2015–2023)")
st.markdown("### Disease Burden vs. Drug Resistance")

# --- 4. INTERACTIVE CONTROLS ---
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

# Load Data
df = load_data(selected_region)

if df.empty:
    st.warning(f"Data not found for **{selected_region}**.")
else:
    # --- 5. ALTAIR VISUALIZATION ---
    
    # Define Colors
    COLOR_INCIDENCE = "#2ca02c"      # Green
    COLOR_CI = "#98df8a"             # Light Green
    COLOR_RR_PREV = "#ffbb78"        # Light Orange
    COLOR_RR_NEW = "#ff7f0e"         # Dark Orange

    # Define Readable Labels (for the Legend)
    LABEL_INCIDENCE = "TB Incidence (per 100k)"
    LABEL_RR_PREV = "RR-TB: Previously Treated Cases (%)"
    LABEL_RR_NEW = "RR-TB: New Cases (%)"
    
    # Base chart
    base = alt.Chart(df).encode(
        x=alt.X('year:O', axis=alt.Axis(title='Year'))
    )

    # Layer 1: 95% Confidence Interval (Band)
    ci_band = base.mark_area(opacity=0.3, color=COLOR_CI).encode(
        y=alt.Y('tb_incidence_low:Q'),
        y2=alt.Y2('tb_incidence_high:Q'),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('tb_incidence_low:Q', title='Incidence CI Low'),
            alt.Tooltip('tb_incidence_high:Q', title='Incidence CI High')
        ]
    )

    # Layer 2: Lines (Interactive Legend Logic)
    # 1. Fold the columns (transform wide to long)
    # 2. Calculate a new column 'Legend Label' to replace cryptic codes with readable text
    lines_base = base.transform_fold(
        ['tb_incidence', 'rr_prev_prevtx', 'rr_prev_new'],
        as_=['Indicator_Code', 'Value']
    ).transform_calculate(
        # Vega Expression to map codes to readable labels
        Legend_Label="datum.Indicator_Code == 'tb_incidence' ? '" + LABEL_INCIDENCE + "' : " +
                     "datum.Indicator_Code == 'rr_prev_prevtx' ? '" + LABEL_RR_PREV + "' : '" + LABEL_RR_NEW + "'"
    )

    lines = lines_base.mark_line(point=True, strokeWidth=3).encode(
        y=alt.Y('Value:Q', axis=alt.Axis(title='Indicator Value')),
        # Use the NEW readable label column for Color
        color=alt.Color('Legend_Label:N', 
                        scale=alt.Scale(
                            # Map the readable labels to colors
                            domain=[LABEL_INCIDENCE, LABEL_RR_PREV, LABEL_RR_NEW],
                            range=[COLOR_INCIDENCE, COLOR_RR_PREV, COLOR_RR_NEW]
                        ),
                        legend=alt.Legend(title="Indicator Details", orient='right') # Legend Title
        ),
        # Tooltip now uses the readable label
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('Legend_Label:N', title='Type'),
            alt.Tooltip('Value:Q', title='Value', format='.1f')
        ]
    )

    chart = alt.layer(
        ci_band,
        lines
    ).properties(
        title=f"{selected_region}: Incidence & Resistance Trends",
        height=500
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
    
    st.caption("Note: 'Incidence' is a rate per 100,000 population. 'RR-TB' values are percentages (%). Comparison focuses on trend direction.")

    with st.expander("View Source Data"):
        st.dataframe(df)