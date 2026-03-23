import streamlit as st
import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Citi Cards · NBA Engine",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .hero-card {
    background: linear-gradient(135deg, #003b70 0%, #0071bc 100%);
    border-radius: 16px; padding: 28px 32px; color: white; margin-bottom: 24px;
  }
  .hero-card h1 { font-size: 1.8rem; font-weight: 700; margin: 0; }
  .hero-card p  { font-size: 0.95rem; opacity: 0.85; margin: 6px 0 0; }
  .kpi-box {
    background: white; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 18px 20px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.06);
  }
  .kpi-val  { font-size: 1.9rem; font-weight: 700; color: #003b70; }
  .kpi-lbl  { font-size: 0.78rem; color: #6b7280; margin-top: 2px; }
  .offer-card {
    border-left: 5px solid #0071bc; background: #f0f7ff;
    border-radius: 10px; padding: 16px 20px; margin-bottom: 14px;
  }
  .offer-card.gold { border-left-color: #d4a017; background: #fffbeb; }
  .offer-card.green{ border-left-color: #16a34a; background: #f0fdf4; }
  .offer-title { font-size: 1rem; font-weight: 600; color: #1f2937; }
  .offer-meta  { font-size: 0.8rem; color: #6b7280; margin-top: 4px; }
  .score-bar-bg { background: #e5e7eb; border-radius: 8px; height: 8px; margin-top: 6px; }
  .score-bar    { background: linear-gradient(90deg,#0071bc,#38bdf8); height: 8px; border-radius: 8px; }
  .tag {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600; margin: 2px;
  }
  .tag-blue  { background: #dbeafe; color: #1d4ed8; }
  .tag-green { background: #dcfce7; color: #15803d; }
  .tag-amber { background: #fef9c3; color: #a16207; }
  .tag-red   { background: #fee2e2; color: #b91c1c; }
  .section-hd{ font-size: 1.1rem; font-weight: 700; color: #003b70; margin-bottom: 12px; }
  .explainer { background: #f8fafc; border-radius: 10px; padding: 14px 18px; font-size: 0.85rem; color: #374151; }
  div[data-testid="stSidebar"] { background: #f1f5f9; }
</style>
""", unsafe_allow_html=True)

# ─── Synthetic Data ──────────────────────────────────────────────────────────
CUSTOMERS = {
    "C-10042 · Priya Sharma":   {"age":34,"income":1_40_000,"card":"Citi Prestige","tenure":5,"spend_monthly":28_500,"top_cats":["Dining","Travel","Groceries"],"lifecycle":"Active","churn_risk":0.11,"ltv":9_20_000,"clv_segment":"High","engagement":"High","transactions":38,"last_offer_accepted":"Dining 5x Points"},
    "C-20817 · Rahul Mehta":    {"age":42,"income":2_10_000,"card":"Citi Premier","tenure":9,"spend_monthly":52_000,"top_cats":["Travel","Hotels","Electronics"],"lifecycle":"Loyal","churn_risk":0.07,"ltv":24_00_000,"clv_segment":"Premium","engagement":"Medium","transactions":55,"last_offer_accepted":"Travel Insurance"},
    "C-33409 · Ananya Reddy":   {"age":27,"income":72_000,"card":"Citi Cashback","tenure":1,"spend_monthly":9_800,"top_cats":["Groceries","OTT","Food Delivery"],"lifecycle":"New","churn_risk":0.31,"ltv":1_80_000,"clv_segment":"Medium","engagement":"Low","transactions":14,"last_offer_accepted":"None"},
    "C-47115 · Vikram Singh":   {"age":51,"income":5_50_000,"card":"Citi Prestige","tenure":14,"spend_monthly":1_18_000,"top_cats":["Business Travel","Luxury Dining","Insurance"],"lifecycle":"Champion","churn_risk":0.04,"ltv":78_00_000,"clv_segment":"Ultra-Premium","engagement":"High","transactions":91,"last_offer_accepted":"Airport Lounge Upgrade"},
    "C-58831 · Sneha Iyer":     {"age":31,"income":95_000,"card":"Citi Rewards","tenure":3,"spend_monthly":15_200,"top_cats":["Shopping","Beauty","Dining"],"lifecycle":"At-Risk","churn_risk":0.58,"ltv":4_20_000,"clv_segment":"Medium","engagement":"Low","transactions":9,"last_offer_accepted":"Cashback on Shopping"},
}

OFFERS_DB = {
    "High":        [("5x Points on Dining for 90 days","Dining","ML Collaborative Filtering","blue",88),("Complimentary Airport Lounge (4 visits)","Travel","Lifecycle Model","green",82),("Zero-fee Balance Transfer for 6 months","Retention","Churn Predictor","amber",76)],
    "Premium":     [("10x Points on International Spends","Travel","Gradient Boost Propensity","blue",93),("Citi Prestige Upgrade Offer","Upsell","CLV Segmentation","amber",87),("Complimentary Travel Insurance","Travel","Rules Engine","green",80)],
    "Medium":      [("Flat 10% Cashback on Groceries","Groceries","NLP Intent + CF","green",72),("OTT Bundle (Netflix+Hotstar) 3 months free","Digital","Retention Model","blue",68),("Spend ₹10k get ₹500 reward points","Activation","Rules Engine","amber",61)],
    "Ultra-Premium":[("Bespoke Concierge Service Trial","Luxury","Banker-level CLV Model","gold",96),("Business Travel Corporate Card Offer","Business","Segment + Propensity","blue",91),("Priority Pass Membership 1 Year","Lounge","Lifecycle Model","green",88)],
}
CHURN_OFFERS = [("Spend ₹5,000 get ₹750 instant cashback","Win-back","Churn Predictor (p=0.58)","red",91),("3 months fee waiver on renewal","Retention","Survival Analysis","amber",87),("Personal call from Relationship Manager","Retention","Rule: Churn>0.5","green",82)]

ARCH_STEPS = [
    ("1. Data Ingestion","Transaction streams, CRM, bureau signals, mobile events ingested via Kafka → Feature Store","Streaming ML"),
    ("2. Feature Engineering","RFM scores, spend velocity, category affinity, seasonality flags computed in Feast","Feature Platform"),
    ("3. Churn Prediction","XGBoost survival model on 180-day rolling window; outputs churn probability P(churn)","Gradient Boosting"),
    ("4. CLV Segmentation","K-Means + HDBSCAN on spend × tenure × category diversity → 5 tiers","Clustering ML"),
    ("5. Propensity Scoring","Multi-label GBM outputs P(accept|offer_type) for each customer × offer matrix","Propensity Model"),
    ("6. Offer Retrieval","RAG pipeline: offer embeddings indexed in FAISS; context = customer profile summary","RAG + Embeddings"),
    ("7. Offer Ranking","Learning-to-Rank (LambdaMART) re-ranks top-K offers using business constraints","LTR / Rules"),
    ("8. Explanation","LLM (Claude) generates natural-language rationale for top offer for RM/customer channel","LLM / NLG"),
    ("9. Delivery & A/B","Optimizely A/B splits, Contextual Bandits adjust offer mix in real-time","Bandit / Experimentation"),
]

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Citibank.svg/320px-Citibank.svg.png", width=120)
    st.markdown("### 🧠 NBA Engine Console")
    selected_cust = st.selectbox("Select Cardholder", list(CUSTOMERS.keys()))
    st.divider()
    view = st.radio("View", ["Customer 360 & Offers","Architecture Walkthrough","Simulation Lab","AI Explainer Chat"])
    st.divider()
    st.caption("Demo | Citi × TCS AI Immersion · 2025")

cust = CUSTOMERS[selected_cust]
cust_name = selected_cust.split("·")[1].strip()

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-card">
  <h1>💳 Citi Cards · Next-Best-Action Engine</h1>
  <p>Hyper-Personalization Platform &nbsp;|&nbsp; Consumer Cards &nbsp;|&nbsp; Viewing: <b>{cust_name}</b> &nbsp;·&nbsp; {cust['card']}</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW 1 – Customer 360 & Offers
# ═══════════════════════════════════════════════════════════════════════════════
if view == "Customer 360 & Offers":

    # KPIs
    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.markdown(f'<div class="kpi-box"><div class="kpi-val">₹{cust["spend_monthly"]:,.0f}</div><div class="kpi-lbl">Monthly Spend</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box"><div class="kpi-val">{cust["tenure"]}y</div><div class="kpi-lbl">Card Tenure</div></div>', unsafe_allow_html=True)
    with k3:
        cr = cust["churn_risk"]
        color = "#dc2626" if cr>0.4 else ("#d97706" if cr>0.2 else "#16a34a")
        st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:{color}">{cr*100:.0f}%</div><div class="kpi-lbl">Churn Risk</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box"><div class="kpi-val">₹{cust["ltv"]/1_00_000:.1f}L</div><div class="kpi-lbl">Lifetime Value</div></div>', unsafe_allow_html=True)
    with k5: st.markdown(f'<div class="kpi-box"><div class="kpi-val">{cust["transactions"]}</div><div class="kpi-lbl">Txns (90d)</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.2,1])

    with left:
        st.markdown('<div class="section-hd">📋 Customer 360 Profile</div>', unsafe_allow_html=True)
        profile_df = pd.DataFrame({
            "Attribute": ["Segment","Lifecycle Stage","CLV Tier","Engagement","Income Band","Top Spend Categories","Last Accepted Offer"],
            "Value": [cust["clv_segment"], cust["lifecycle"], cust["clv_segment"],
                      cust["engagement"], f"₹{cust['income']:,.0f}/yr",
                      " · ".join(cust["top_cats"]), cust["last_offer_accepted"]]
        })
        st.dataframe(profile_df, hide_index=True, use_container_width=True)

        # Spend category bar
        st.markdown('<div class="section-hd" style="margin-top:18px">📊 Spend Category Mix (simulated)</div>', unsafe_allow_html=True)
        cats = cust["top_cats"]
        vals = sorted([random.randint(20,60) for _ in cats], reverse=True)
        bar_df = pd.DataFrame({"Category": cats, "Share (%)": vals})
        st.bar_chart(bar_df.set_index("Category"), color="#0071bc", height=160)

    with right:
        st.markdown('<div class="section-hd">🎯 Top Next-Best-Action Offers</div>', unsafe_allow_html=True)

        seg = cust["clv_segment"]
        if cust["churn_risk"] > 0.4:
            offers = CHURN_OFFERS
            st.warning(f"⚠️ High churn risk detected ({cust['churn_risk']*100:.0f}%). Retention offers prioritised.", icon="🚨")
        else:
            offers = OFFERS_DB.get(seg, OFFERS_DB["Medium"])

        for title, category, model, color, score in offers:
            pct = score
            st.markdown(f"""
            <div class="offer-card {color if color in ['gold','green'] else ''}">
              <div class="offer-title">🎁 {title}</div>
              <div class="offer-meta">Category: <b>{category}</b> &nbsp;|&nbsp; Model: <i>{model}</i></div>
              <div style="margin-top:8px; font-size:0.78rem; color:#374151">Confidence Score: <b>{score}%</b></div>
              <div class="score-bar-bg"><div class="score-bar" style="width:{pct}%"></div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="explainer">
          <b>How this was generated:</b><br>
          1. Churn model scored this customer at <b>{cust['churn_risk']*100:.0f}%</b> risk<br>
          2. CLV model placed them in <b>{cust['clv_segment']}</b> tier<br>
          3. Propensity GBM ranked offers by P(accept)<br>
          4. Business rules filtered ineligible offers<br>
          5. LLM generated the offer copy & rationale
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW 2 – Architecture Walkthrough
# ═══════════════════════════════════════════════════════════════════════════════
elif view == "Architecture Walkthrough":
    st.markdown('<div class="section-hd">🏗️ Solution Architecture — AI Technique Mapping</div>', unsafe_allow_html=True)
    st.caption("Each layer of the NBA pipeline maps to a specific AI/ML technique chosen for that sub-problem.")

    for step, desc, technique in ARCH_STEPS:
        with st.expander(f"**{step}** — `{technique}`"):
            st.markdown(f"**What it does:** {desc}")
            # Why this technique
            whys = {
                "Streaming ML": "Real-time Kafka ingestion ensures low-latency feature freshness; batch alternatives add >24h lag unacceptable for live offer serving.",
                "Feature Platform": "Feast decouples feature computation from model serving; prevents training-serving skew — the #1 cause of model degradation in production.",
                "Gradient Boosting": "XGBoost handles class imbalance (rare churn events) natively, is interpretable via SHAP, and outperforms deep models on tabular data.",
                "Clustering ML": "K-Means gives business-readable segments; HDBSCAN handles outlier ultra-premium customers without forcing them into a cluster.",
                "Propensity Model": "Multi-label GBM scores all offer types in one pass, capturing cross-offer correlations; faster inference than running N binary classifiers.",
                "RAG + Embeddings": "Offer catalogue changes frequently; RAG lets us update offer embeddings without re-training the ranking model — pure retrieval flexibility.",
                "LTR / Rules": "LambdaMART optimises NDCG (ranked relevance) not accuracy; rules layer enforces regulatory constraints (e.g. no balance transfer to new-to-credit).",
                "LLM / NLG": "Structured model outputs (scores, features) alone can't be shown to RMs or customers; LLM translates them into persuasive, human-readable rationale.",
                "Bandit / Experimentation": "Contextual bandits balance exploration (trying new offers) vs exploitation (repeating winners) — outperforms pure A/B by converging 3-5x faster.",
            }
            st.info(f"**Why this technique:** {whys.get(technique,'—')}")

    st.divider()
    st.markdown("### 🔄 Data Flow Diagram")
    st.markdown("""
```
[Transaction Stream] ──Kafka──▶ [Feature Store (Feast)]
[CRM / Bureau]       ──batch──▶        │
[Mobile Events]      ──API───▶         │
                                        ▼
                             ┌──────────────────────┐
                             │   ML Model Layer      │
                             │  ├ Churn Predictor    │
                             │  ├ CLV Segmenter      │
                             │  └ Propensity GBM     │
                             └──────────┬───────────┘
                                        │ scores
                                        ▼
                             ┌──────────────────────┐
                             │  Offer Retrieval      │
                             │  RAG + FAISS Index    │
                             │  LambdaMART Ranker    │
                             │  Business Rules       │
                             └──────────┬───────────┘
                                        │ top-K offers
                                        ▼
                             ┌──────────────────────┐
                             │  LLM Explainer (NLG)  │
                             │  A/B & Bandit Layer   │
                             └──────────┬───────────┘
                                        │
                           ┌────────────┼───────────┐
                           ▼            ▼            ▼
                     [Mobile App]  [Email/SMS]  [RM Console]
```
    """)

# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW 3 – Simulation Lab
# ═══════════════════════════════════════════════════════════════════════════════
elif view == "Simulation Lab":
    st.markdown('<div class="section-hd">🔬 Simulation Lab — What-If Scenario Explorer</div>', unsafe_allow_html=True)
    st.caption("Adjust parameters to see how the NBA engine responds in real time.")

    col1, col2 = st.columns(2)
    with col1:
        sim_spend = st.slider("Monthly Spend (₹)", 5_000, 2_00_000, cust["spend_monthly"], step=5_000)
        sim_churn = st.slider("Churn Risk (%)", 0, 100, int(cust["churn_risk"]*100))
        sim_tenure = st.slider("Card Tenure (years)", 0, 20, cust["tenure"])
    with col2:
        sim_engagement = st.selectbox("Engagement Level", ["Low","Medium","High"], index=["Low","Medium","High"].index(cust["engagement"]))
        sim_cats = st.multiselect("Top Spend Categories", ["Dining","Travel","Groceries","Shopping","Electronics","OTT","Hotels","Fuel"], default=cust["top_cats"])
        sim_income = st.slider("Annual Income (₹)", 50_000, 10_00_000, cust["income"], step=10_000)

    st.divider()
    # Logic
    churn_p = sim_churn / 100
    clv_raw = sim_spend * 12 * (sim_tenure + 1) * (1.2 if sim_engagement == "High" else (1.0 if sim_engagement == "Medium" else 0.8))

    if clv_raw > 20_00_000: sim_seg = "Ultra-Premium"
    elif clv_raw > 8_00_000: sim_seg = "Premium"
    elif clv_raw > 3_00_000: sim_seg = "High"
    else: sim_seg = "Medium"

    st.markdown("#### 📈 Simulated Model Outputs")
    m1,m2,m3,m4 = st.columns(4)
    with m1: st.metric("Simulated CLV",f"₹{clv_raw/1_00_000:.1f}L")
    with m2: st.metric("Segment",sim_seg)
    with m3:
        color = "🔴" if churn_p>0.4 else ("🟡" if churn_p>0.2 else "🟢")
        st.metric("Churn Risk",f"{color} {sim_churn}%")
    with m4: st.metric("Engagement",sim_engagement)

    st.markdown("#### 🎯 Recommended Offers (Simulated)")
    if churn_p > 0.4:
        rec_offers = CHURN_OFFERS
        st.error("Retention mode activated — churn probability exceeds threshold.")
    else:
        rec_offers = OFFERS_DB.get(sim_seg, OFFERS_DB["Medium"])

    for title, cat, model, color, score in rec_offers:
        st.markdown(f"""
        <div class="offer-card {color if color in ['gold','green'] else ''}">
          <div class="offer-title">🎁 {title}</div>
          <div class="offer-meta">Category: <b>{cat}</b> &nbsp;|&nbsp; Model Signal: <i>{model}</i> &nbsp;|&nbsp; Score: <b>{score}%</b></div>
        </div>""", unsafe_allow_html=True)

    # Spend trend simulation
    st.markdown("#### 📉 Spend Trajectory Simulation (12 months)")
    months = [datetime(2024,m,1).strftime("%b") for m in range(1,13)]
    base = sim_spend
    trend = [max(1000, int(base * (1 + 0.03*i - (0.08 if churn_p>0.4 else 0)*i + random.gauss(0,0.04)))) for i in range(12)]
    chart_df = pd.DataFrame({"Month": months, "Spend (₹)": trend})
    st.line_chart(chart_df.set_index("Month"), color="#0071bc", height=200)

# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW 4 – AI Explainer Chat
# ═══════════════════════════════════════════════════════════════════════════════
elif view == "AI Explainer Chat":
    st.markdown('<div class="section-hd">💬 AI Offer Explainer — Relationship Manager Assistant</div>', unsafe_allow_html=True)
    st.caption("Simulates how an LLM layer would explain NBA decisions to an RM or directly to the customer.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    seg = cust["clv_segment"]
    top_offer = (CHURN_OFFERS if cust["churn_risk"]>0.4 else OFFERS_DB.get(seg, OFFERS_DB["Medium"]))[0]

    # System context
    context = f"""
Customer: {cust_name} | Card: {cust['card']} | Segment: {cust['clv_segment']} | Lifecycle: {cust['lifecycle']}
Monthly Spend: ₹{cust['spend_monthly']:,.0f} | Churn Risk: {cust['churn_risk']*100:.0f}%
Top Categories: {', '.join(cust['top_cats'])} | Tenure: {cust['tenure']} years
Top Recommended Offer: {top_offer[0]} (Category: {top_offer[1]}, Model: {top_offer[2]}, Score: {top_offer[4]}%)
"""

    # Preset questions
    st.markdown("**Quick Questions:**")
    q_cols = st.columns(3)
    preset_qs = [
        "Why was this offer chosen for this customer?",
        "What is the churn risk and what triggered it?",
        "How should I pitch this offer to the customer?",
    ]
    for i, (col, q) in enumerate(zip(q_cols, preset_qs)):
        with col:
            if st.button(q, key=f"pq{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","content":q})

    user_input = st.chat_input("Ask anything about this customer's offers or risk signals...")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})

    # Display history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "user":
                # Generate canned-but-contextual AI response
                q_lower = msg["content"].lower()
                if "churn" in q_lower:
                    response = f"""**Churn Risk Analysis for {cust_name}**

The XGBoost survival model assigns this customer a churn probability of **{cust['churn_risk']*100:.0f}%**.

Key signals driving this score:
- **Engagement drop**: Transaction count is {cust['transactions']} in 90 days — {"below" if cust['transactions']<20 else "above"} segment average
- **Lifecycle stage**: {cust['lifecycle']} — {"elevated concern" if cust['lifecycle'] in ['At-Risk','New'] else "stable"}
- **Category concentration**: Spending is concentrated in {cust['top_cats'][0]}, indicating limited product stickiness

The survival model uses a 180-day rolling window and was trained on 2.4M historical churn events. SHAP feature importance places engagement score as the top contributor (weight: 0.34)."""
                elif "pitch" in q_lower or "how" in q_lower:
                    response = f"""**RM Pitch Guide for {cust_name}**

Recommended opening: *"Hi {cust_name.split()[0]}, I noticed you frequently spend on {cust['top_cats'][0]} — I have an exclusive offer that could save you significantly on those purchases."*

Key talking points:
1. Tie the offer ({top_offer[0]}) directly to their **{cust['top_cats'][0]}** spending habit
2. Quantify the benefit: "Based on your average monthly spend of ₹{cust['spend_monthly']:,.0f}, you could earn/save approximately ₹{int(cust['spend_monthly']*0.05):,.0f} this quarter"
3. Urgency frame: "This is available for your tier only and valid for the next 30 days"

**Tone**: {("Empathetic and value-focused" if cust['churn_risk']>0.3 else "Aspirational and reward-focused")}"""
                else:
                    response = f"""**NBA Offer Rationale for {cust_name}**

The recommendation engine selected **"{top_offer[0]}"** through a 5-layer decision pipeline:

1. **Churn Model** (XGBoost): Scored {cust['churn_risk']*100:.0f}% risk → {"Retention mode" if cust['churn_risk']>0.4 else "Growth mode"}
2. **CLV Segmentation** (K-Means): Classified as **{cust['clv_segment']}** based on ₹{cust['ltv']/1_00_000:.1f}L LTV
3. **Propensity Model** (GBM): P(accept | {top_offer[1]} offer) = **{top_offer[4]}%** — highest across all offer types
4. **RAG Retrieval**: Offer embedding similarity to customer context vector = 0.87 cosine
5. **Business Rules**: Verified eligibility (tenure ≥ {max(0,cust['tenure']-1)}y ✓, no active same-category offer ✓)

**Bottom line**: This customer has strong affinity for {top_offer[1]}-related rewards, high propensity to accept, and the offer aligns with Citi's Q4 spend-stimulation objective."""

                with st.chat_message("assistant"):
                    st.markdown(response)
                    st.session_state.chat_history.append({"role":"assistant","content":response})

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.caption("🔒 Demo prototype | Citi × TCS AI Immersion 2025 | Data is synthetic and for demonstration purposes only.")
