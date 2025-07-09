import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load ZIP-level data
@st.cache_data
def load_data():
    df = pd.read_csv('zip_code_demographics.csv')
    df['zip'] = df['zip'].astype(str).str.zfill(5)  # Ensure all ZIPs are 5-digit
    return df

df = load_data()

# ---- UI ----
st.set_page_config(page_title="Muse Score Calculator", layout="centered")
st.title("Muse Score™ Calculator 💸")
st.markdown("Estimate your financial efficiency based on **Adjusted Gross Income (AGI)** and **ZIP Code** location.")

agi = st.number_input("📥 Enter your Adjusted Gross Income (AGI)", min_value=10000, max_value=500000, step=1000)
zip_input = st.text_input("📍 Enter your 5-digit ZIP Code (e.g. 10001)")

if st.button("🎯 Calculate Muse Score") and zip_input:
    zip_input = zip_input.zfill(5)
    
    if zip_input not in df['zip'].values:
        st.error("❌ ZIP Code not found in dataset.")
    else:
        row = df[df['zip'] == zip_input].iloc[0]
        zip_agi = row['adjusted_gross_income']

        # --- Scoring Logic ---
        if agi < zip_agi * 0.8:
            muse_score = 520
            tier = "🔴 Financial Stress"
        elif agi < zip_agi:
            muse_score = 580
            tier = "🟠 At Risk"
        elif agi < zip_agi * 1.2:
            muse_score = 680
            tier = "🟡 Good"
        else:
            muse_score = 770
            tier = "🟢 Excellent"

        # --- Display Results ---
        st.success(f"🧠 Your Muse Score: **{muse_score}**")
        st.markdown(f"Tier: **{tier}**")
        
        # Show comparison chart
        fig, ax = plt.subplots()
        bars = ax.bar(["Your AGI", "ZIP Median AGI"], [agi, zip_agi], width=0.4)
        ax.set_ylabel("AGI ($)")
        ax.set_title("AGI Comparison")
        ax.bar_label(bars)
        st.pyplot(fig)

        # Show more ZIP insights
        st.markdown("### 🗺️ ZIP Insights")
        st.write({
            'City': row['city'],
            'State': row['state_name'],
            'Population': int(row['population']),
            'AGI (ZIP)': f"${int(zip_agi):,}",
            'Density': round(row['density'], 1),
            'Businesses': int(row['number_of_business']),
        })
