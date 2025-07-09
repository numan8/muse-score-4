import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

@st.cache_data
def load_data():
    df = pd.read_csv('zip_code_demographics.csv')
    df['zip'] = df['zip'].astype(str).str.zfill(5)
    return df

df = load_data()

# ---- UI ----
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
        ratio = agi / zip_agi if zip_agi > 0 else 0

        # --- Scoring with multiplier ---
        muse_score = min(850, max(450, round(500 + (ratio - 1) * 300)))

        # --- Tier ---
        if muse_score >= 750:
            tier = "🟢 Excellent"
        elif muse_score >= 650:
            tier = "🟡 Good"
        elif muse_score >= 550:
            tier = "🟠 At Risk"
        else:
            tier = "🔴 Financial Stress"

        # --- Meter Visualization ---
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

        # --- Comparison Summary ---
        st.markdown("### 📊 Comparison Summary")
        st.write({
            'Your AGI': f"${agi:,.0f}",
            'City': row['city'],
            'State': row['state_name'],
        })
