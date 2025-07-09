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

# --- Page Config ---
st.set_page_config(page_title="Muse Score™", layout="centered", page_icon="💸")
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>Muse Score™ Calculator 💸</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Estimate your financial strength based on AGI and ZIP Code location</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Input Section ---
st.subheader("📥 Input Details")
col1, col2 = st.columns(2)
with col1:
    agi = st.number_input("Your Adjusted Gross Income (AGI)", min_value=0, step=500, format="%d")
with col2:
    zip_input = st.text_input("5-digit ZIP Code", placeholder="e.g. 10001")

st.markdown("---")

# --- Calculate Score ---
if st.button("🎯 Calculate Muse Score") and zip_input:
    zip_input = zip_input.zfill(5)

    if zip_input not in df['zip'].values:
        st.error("❌ ZIP Code not found in dataset.")
    else:
        row = df[df['zip'] == zip_input].iloc[0]
        zip_agi = row['adjusted_gross_income']

        if pd.isna(zip_agi) or zip_agi == 0:
            st.error("⚠️ Missing or invalid AGI data for this ZIP code.")
            st.stop()

        # --- Scoring Logic ---
        ratio = agi / zip_agi
        muse_score = min(850, max(450, round(500 + (ratio - 1) * 300)))

        # --- Tier Assignment ---
        if muse_score >= 750:
            tier, color = "🟢 Excellent", "#4caf50"
        elif muse_score >= 650:
            tier, color = "🟡 Good", "#ffeb3b"
        elif muse_score >= 550:
            tier, color = "🟠 At Risk", "#ff9800"
        else:
            tier, color = "🔴 Financial Stress", "#f44336"

        # --- Gauge Visualization ---
        option = {
            "series": [{
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
                "detail": {
                    "formatter": f"{muse_score}",
                    "fontSize": 24,
                    "color": "auto"
                },
                "data": [{"value": muse_score, "name": "Muse Score"}]
            }]
        }

        # --- Display Score ---
        st.markdown("### 📈 Your Muse Score")
        st_echarts(options=option, height="300px")
        st.success(f"**{muse_score} — {tier}**", icon="💡")

        # --- Personalized insight ---
        messages = {
            "🔴 Financial Stress": "Your income is significantly below the average for your area. This may limit your ability to manage unexpected expenses or maintain standard living costs. Consider reviewing budgeting and income-boosting strategies.",
            "🟠 At Risk": "You're slightly below the typical AGI for your ZIP code. While you may be managing, there's vulnerability to rising costs. Focus on building savings and reducing unnecessary spending.",
            "🟡 Good": "You're financially aligned with or slightly above your local average. You’re on stable ground — now is a good time to optimize tax planning, investments, or savings.",
            "🟢 Excellent": "You're well above the average income level for your area. This suggests strong financial resilience and the potential to build long-term wealth. Consider strategies for scaling savings, investing, or philanthropy."
        }

        st.markdown("---")
        st.subheader("💬 Personalized Financial Insight")
        st.markdown(f"<div style='color: {color}; font-size: 16px'>{messages[tier]}</div>", unsafe_allow_html=True)

        # --- Clean summary (without local avg AGI) ---
        st.markdown("---")
        st.subheader("🗂️ Summary")
        st.markdown(
            f"""
            <div style='background-color:#f0f2f6; padding:15px; border-radius:10px; font-size:15px;'>
                <b>Your AGI:</b> ${agi:,.0f}<br>
                <b>ZIP Code:</b> {zip_input}<br>
                <b>City:</b> {row['city']}<br>
                <b>State:</b> {row['state_name']}<br>
            </div>
            """,
            unsafe_allow_html=True
        )
