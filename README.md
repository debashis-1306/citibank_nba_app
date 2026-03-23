# Citi Cards · Next-Best-Action (NBA) Engine — Prototype


The prototype is built for the **Citibank and TCS AI Immersion** programme and is designed so that a business stakeholder can click through and understand the concept end-to-end.

---

## What the App Does

The app simulates a production NBA platform across **four interactive views**:

### 1. Customer 360 & Offers
- Loads a synthetic cardholder profile (5 demo customers)
- Displays KPIs: Monthly Spend, Tenure, Churn Risk, Lifetime Value, Transactions
- Shows the customer's spend category mix as a bar chart
- Generates **Top 3 Next-Best-Action Offers** ranked by propensity score
- If churn risk > 40%, the engine automatically switches to **Retention Mode** and surfaces win-back offers
- Each offer card shows the AI model that generated it and its confidence score

### 2. Architecture Walkthrough
- Walks through all 9 layers of the NBA pipeline (from data ingestion to delivery)
- Each step is expandable to reveal: what it does, which AI technique it uses, and **why that technique is the right fit**
- Includes a full ASCII data flow diagram showing how data moves from source to channel

### 3. Simulation Lab
- Interactive "what-if" sliders for spend, churn risk, tenure, engagement, income
- Real-time recalculation of CLV segment, churn flag, and recommended offers
- Shows how the engine transitions between Growth Mode and Retention Mode
- Simulates a 12-month spend trajectory chart

### 4. AI Explainer Chat (RM Assistant)
- Simulates an LLM layer that explains NBA decisions in natural language
- Preset questions: "Why this offer?", "What triggered the churn risk?", "How do I pitch this?"
- Generates contextual, customer-specific answers combining ML model outputs with narrative
- Represents how a Relationship Manager console would use LLM-generated rationale

---

## How to Run Locally

### Prerequisites
- Python 3.9 or higher
- pip

### Installation

```bash
# 1. Clone or download the project folder
cd to the folder that has the app.py

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### No API key required
This prototype uses synthetic data and simulated model outputs — no external API calls are made. It runs fully offline.

---

## Deploying to Streamlit Cloud

1. Push the `citibank_nba_app/` folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set the main file as `app.py`
5. Click **Deploy**

The app will be live at `https://<your-app>.streamlit.app`

---

## Folder Structure

```
nba_app/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```
