import streamlit as st
import pandas as pd
import altair as alt

try:
    incidence_df = pd.read_csv('GTB_report_2025_incidence.csv')
    rr_prevalence_df = pd.read_csv('GTB_report_2025_RR_prevalence.csv')
except FileNotFoundError:
    st.error("Data files not found. Please ensure 'GTB_report_2025_incidence.csv' and 'GTB_report_2025_RR_prevalence.csv' are in the same directory.")
    st.stop()

incidence_df = incidence_df.rename(columns={'Category': 'Year'})
rr_prevalence_df = rr_prevalence_df.rename(columns={'Category': 'Year'})

merged_df = pd.merge(incidence_df, rr_prevalence_df, on='Year', how='inner')

st.title("Task 4: Drug Resistance vs. Disease Incidence")
st.markdown("""
### Explore how the percentage of Rifampicin-Resistant TB (RR-TB) relates to overall incidence.
This visualization helps us understand if the burden of drug resistance is growing relative to the overall spread of Tuberculosis.
""")

view_selection = st.selectbox("Select View Level", ["Global", "Regional (Not available in demo data)", "Country (Not available in demo data)"])

if view_selection == "Global":
    st.subheader("Global Trends (2015 - 2024)")
    
    base = alt.Chart(merged_df).encode(
        x=alt.X('Year:O', axis=alt.Axis(title='Year'))
    )

    line_incidence = base.mark_line(point=True, strokeDash=[5,5]).encode(
        y=alt.Y('Estimated TB incidence per 100 000 population', 
                axis=alt.Axis(title='Incidence per 100k (Blue)', titleColor='#1f77b4')),
        tooltip=['Year', 'Estimated TB incidence per 100 000 population']
    ).properties(
        title='Global TB Incidence and RR-TB Prevalence'
    )
    
    line_incidence = line_incidence.mark_line(color='#1f77b4', point=True)

    line_rr_new = base.mark_line(point=True, color='#2ca02c').encode(
        y=alt.Y('New pulmonary bacteriologically confirmed cases', 
                axis=alt.Axis(title='RR-TB Prevalence % (Green/Red)', titleColor='#2ca02c')),
        tooltip=['Year', alt.Tooltip('New pulmonary bacteriologically confirmed cases', title='RR % (New Cases)')]
    )

    line_rr_prev = base.mark_line(point=True, color='#d62728').encode(
        y=alt.Y('Previously treated pulmonary bacteriologically confirmed cases', 
                axis=alt.Axis(title='RR-TB Prevalence %')), 
        tooltip=['Year', alt.Tooltip('Previously treated pulmonary bacteriologically confirmed cases', title='RR % (Prev. Treated)')]
    )

    chart = alt.layer(
        line_incidence,
        line_rr_new,
        line_rr_prev
    ).resolve_scale(
        y='independent' 
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    st.info("""
    **Legend:**
    - 🔵 **Blue (Left Axis):** Estimated TB Incidence per 100,000 population.
    - 🔴 **Red (Right Axis):** % of RR-TB in Previously Treated Cases.
    - 🟢 **Green (Right Axis):** % of RR-TB in New Cases.
    """)