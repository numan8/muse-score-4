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

        # --- Smart financial insight ---
        city = row['city']
        state = row['state_name']

        messages = {
            "🔴 Financial Stress": (
                f"According to your AGI, you are in **financial stress** compared to others in {city}, {state}. "
                f"Your income is significantly below the local average, and the cost of living in this area may be putting additional pressure on your finances. "
                "Consider exploring income growth opportunities and tightening control over essential expenses."
            ),

            "🟠 At Risk": (
                f"Based on your AGI, you are considered **financially at risk** within {city}, {state}. "
                f"While your income is only slightly below the local average, the cost of living could make it difficult to maintain financial resilience over time. "
                "Strengthen your savings and reassess non-essential spending to build more flexibility."
            ),

            "🟡 Good": (
                f"Your AGI places you in a **financially stable** position relative to others in {city}, {state}. "
                f"Your income is well-aligned with the local economy, and you appear to manage the area's living costs effectively. "
                "Now is a good time to focus on long-term planning through investments and structured savings."
            ),

            "🟢 Excellent": (
                f"You are in an **excellent financial position** compared to residents of {city}, {state}. "
                f"Your income is well above the local average, giving you strong purchasing power and insulation from the area's cost of living pressures. "
                "This is a great opportunity to optimize your wealth through strategic planning, investing, or giving back."
            )
        }

        st.markdown(f"💬 **Financial Insight:** {messages[tier]}")

        # --- Summary Output ---
        st.write({
            'Your AGI': f"${agi:,.0f}",
            'City': city,
            'State': state,
        })
