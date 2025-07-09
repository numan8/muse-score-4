import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

# Load data
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

        # ---- Muse Score Logic with Intervals ----
        ratio = agi / zip_agi if zip_agi > 0 else 0

        if ratio < 0.8:
            muse_score = 520
            tier = "🔴 Financial Stress"
        elif 0.8 <= ratio < 1.0:
            muse_score = 580
            tier = "🟠 At Risk"
        elif 1.0 <= ratio < 1.2:
            muse_score = 680
            tier = "🟡 Good"
        else:
            muse_score = 770
            tier = "🟢 Excellent"

        # ---- Meter Visualization ----
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

        # ---- Output ----
        st_echarts(options=option, height="300px")
        st.success(f"🧠 Muse Score: **{muse_score}** — {tier}")

        st.markdown("### 📊 Comparison Summary")
        st.write({
            'Your AGI': f"${agi:,.0f}",
            'ZIP AGI': f"${zip_agi:,.0f}",
            'City': row['city'],
            'State': row['state_name'],
            'Population': int(row['population']),
            'Density': round(row['density'], 1),
            'Businesses': int(row['number_of_business']),
        })
