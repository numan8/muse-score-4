import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_csv('zip_code_demographics.csv')
    df['zip'] = df['zip'].astype(str).str.zfill(5)
    df['adjusted_gross_income'] = pd.to_numeric(df['adjusted_gross_income'], errors='coerce')
    return df

df = load_data()

# --- UI ---
st.set_page_config(page_title="Muse Score™", layout="centered")
st.title("Muse Score™ Calculator 💸")
st.markdown("Estimate your financial strength based on AGI and ZIP Code location.")

agi = st.number_input("📥 Enter your Adjusted Gross Income (AGI)", min_value=0, step=500)
zip_input = st.text_input("📍 Enter your 5-digit ZIP Code (e.g. 10001)")

if st.button("🎯 Calculate Muse Score") and zip_input:
    zip_input = zip_input.zfill(5)

    if zip_input not in df['zip'].values:
        st.error("❌ ZIP Code not found in dataset.")
    else:
        row = df[df['zip'] == zip_input].iloc[0]
        zip_agi = row['adjusted_gross_income']

        # --- Validate ZIP AGI ---
        if pd.isna(zip_agi) or zip_agi == 0:
            st.error("⚠️ Missing or invalid AGI data for this ZIP code.")
            st.stop()

        # --- Scoring with multiplier ---
        ratio = agi / zip_agi
        muse_score = min(850, max(450, round(500 + (ratio - 1) * 300)))

        # --- Tier assignment ---
        if muse_score >= 750:
            tier = "🟢 Excellent"
        elif muse_score >= 650:
            tier = "🟡 Good"
        elif muse_score >= 550:
            tier = "🟠 At Risk"
        else:
            tier = "🔴 Financial Stress"

        # --- Gauge visualization ---
        option = {
            "series": [
                {
                    "type": "gauge",
                    "startAngle": 180,
                    "endAngle": 0,
                    "min": 400,
                    "max": 850,
                    "splitNumber": 4,
                    "axisLine": {
                        "lineStyle": {
                            "width": 12,
                            "color": [
                                [0.25, '#f44336'],
                                [0.5, '#ff9800'],
                                [0.75, '#ffeb3b'],
                                [1, '#4caf50']
                            ]
                        }
                    },
                    "pointer": {"itemStyle": {"color": "auto"}},
                    "title": {"fontSize": 14},
                    "detail": {
                        "formatter": f"{muse_score}",
                        "fontSize": 24,
                        "color": "auto"
                    },
                    "data": [{"value": muse_score, "name": "Muse Score"}]
                }
            ]
        }

        st_echarts(options=option, height="300px")
        st.success(f"🧠 Muse Score: **{muse_score}** — {tier}")

        # --- Personalized insight ---
        messages = {
            "🔴 Financial Stress": "Your income is significantly below the average for your area. This may limit your ability to manage unexpected expenses or maintain standard living costs. Consider reviewing budgeting and income-boosting strategies.",
            "🟠 At Risk": "You're slightly below the typical AGI for your ZIP code. While you may be managing, there's vulnerability to rising costs. Focus on building savings and reducing unnecessary spending.",
            "🟡 Good": "You're financially aligned with or slightly above your local average. You’re on stable ground — now is a good time to optimize tax planning, investments, or savings.",
            "🟢 Excellent": "You're well above the average income level for your area. This suggests strong financial resilience and the potential to build long-term wealth. Consider strategies for scaling savings, investing, or philanthropy."
        }

        st.markdown(f"💬 **Financial Insight:** {messages[tier]}")

        # --- Clean summary ---
        st.write({
            'Your AGI': f"${agi:,.0f}",
            'City': row['city'],
            'State': row['state_name'],
        })
