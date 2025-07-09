import streamlit as st
import pandas as pd

# Load ZIP-level data
@st.cache_data
def load_data():
    return pd.read_csv('zip_code_demographics.csv')

df = load_data()

# ---- UI ----
st.title("Muse Score™ Calculator 💸")
st.markdown("Estimate your financial efficiency based on AGI and ZIP location")

agi = st.number_input("Enter your Adjusted Gross Income (AGI)", min_value=10000, max_value=500000, step=1000)
zip_input = st.text_input("Enter your 5-digit ZIP Code (e.g. 10001)")

if st.button("Calculate Muse Score") and zip_input:
    if zip_input not in df['zip'].astype(str).values:
        st.error("ZIP Code not found in dataset.")
    else:
        row = df[df['zip'].astype(str) == zip_input].iloc[0]

        # --- Deterministic scoring using proxies ---
        # Normalize fields
        max_agi = df['adjusted_gross_income'].max()
        max_density = df['density'].max()
        income_per_cap = row['adjusted_gross_income'] / row['population']
        max_income_per_cap = (df['adjusted_gross_income'] / df['population']).max()

        agi_score = agi / max_agi
        coli_score = 1 - (income_per_cap / max_income_per_cap)
        density_score = 1 - (row['density'] / max_density)
        housing_score = 1 - ((row['total_income_amount'] / row['population']) / max_income_per_cap)

        # Weighted scoring (can be tuned)
        raw_score = (
            0.4 * agi_score +
            0.2 * coli_score +
            0.2 * density_score +
            0.2 * housing_score
        )

        muse_score = round(350 + (raw_score * 500))

        # Tier
        if muse_score >= 750:
            tier = "🟢 Excellent"
        elif muse_score >= 650:
            tier = "🟡 Good"
        elif muse_score >= 550:
            tier = "🟠 At Risk"
        else:
            tier = "🔴 Financial Stress"

        # Output
        st.success(f"🧠 Your Muse Score: **{muse_score}**")
        st.markdown(f"Tier: **{tier}**")
        st.write("**Component Scores:**")
        st.write({
            'AGI Score': round(agi_score, 2),
            'COLI Score': round(coli_score, 2),
            'Density Score': round(density_score, 2),
            'Housing Score': round(housing_score, 2)
        })
