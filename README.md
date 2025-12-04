# Streamlit App: Drug Resistance and Disease Control (Task 4)

## Project Overview
This Streamlit application visualizes the relationship between global Tuberculosis (TB) incidence and the prevalence of Rifampicin-resistant TB (RR-TB). It aims to answer the critical question: **Does antibiotic resistance decline in parallel with overall disease incidence?**

This project is part of the "Visualization Task 4" assignment.

## Key Features
- **Dual-Axis Visualization:** Simultaneously displays TB incidence rates (left axis) and RR-TB percentages (right axis) over time (2015-2024).
- **Comparative Analysis:** Distinguishes between resistance trends in "New Cases" vs. "Previously Treated Cases".
- **Interactive Tooltips:** Allows users to inspect precise data points for each year.

## Data Sources
The application uses data from the Global Tuberculosis Report 2025:
1. `GTB_report_2025_incidence.csv`: Estimated TB incidence per 100,000 population.
2. `GTB_report_2025_RR_prevalence.csv`: Prevalence of rifampicin-resistant TB.

## How to Run Locally
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt