import os
import logging
import json
from datetime import datetime, timedelta

import google.cloud.logging
from google.cloud import datastore
from dotenv import load_dotenv
import requests
# Vertex AI Search config
SEARCH_ENGINE_ID = "finmind-search_1777198706"
DATA_STORE_ID = "finmind-financial-data_1777198887695"
SEARCH_PROJECT = "957801268404"

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

# --- Setup ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()
load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")
datastore_client = datastore.Client(project="finm-ai")

# =============================================
# TOOL 1: Save prompt to state + DB
# =============================================
def add_prompt_to_state(tool_context: ToolContext, prompt: str) -> dict:
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State] PROMPT: {prompt}")
    entity = datastore.Entity(key=datastore_client.key("UserPrompt"))
    entity.update({"prompt": prompt, "timestamp": datetime.now()})
    datastore_client.put(entity)
    return {"status": "success"}

# =============================================
# TOOL 2: Load Chat History
# =============================================
def load_chat_history(tool_context: ToolContext) -> dict:
    user_id = tool_context.state.get("USER_NAME", "User")
    query = datastore_client.query(kind="ChatHistory")
    query.add_filter("user_id", "=", user_id)
    messages = []
    for entity in query.fetch(limit=20):
        messages.append({
            "role": entity.get("role"),
            "message": entity.get("message"),
            "time": entity.get("timestamp").strftime("%Y-%m-%d %H:%M") if entity.get("timestamp") else ""
        })
    tool_context.state["CHAT_HISTORY"] = json.dumps(messages)
    return {"history": messages, "count": len(messages)}

# =============================================
# TOOL 3: Save Chat Message
# =============================================
def save_chat_message(tool_context: ToolContext, role: str, message: str) -> dict:
    user_id = tool_context.state.get("USER_NAME", "User")
    entity = datastore.Entity(key=datastore_client.key("ChatHistory"))
    entity.update({
        "user_id": user_id,
        "role": role,
        "message": message,
        "timestamp": datetime.now()
    })
    datastore_client.put(entity)
    return {"status": "saved"}

# =============================================
# TOOL 4: Budget Analysis with Expense Categories
# =============================================
def analyze_budget(tool_context: ToolContext, income: float, expenses: float, currency: str = "PKR",
                   food: float = 0.0, rent: float = 0.0, transport: float = 0.0,
                   entertainment: float = 0.0, other: float = 0.0) -> dict:
    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    health_score = min(100, max(0, int(savings_rate * 3)))

    if savings_rate < 0:
        status = "CRITICAL"
        advice = f"You are overspending by {abs(savings):.0f} {currency}. Immediate action needed!"
    elif savings_rate < 10:
        status = "LOW"
        advice = f"Savings rate is only {savings_rate:.1f}%. Try to cut 15-20% of expenses."
    elif savings_rate < 20:
        status = "MODERATE"
        advice = f"Good start! Savings rate is {savings_rate:.1f}%. Aim for 20%."
    else:
        status = "GOOD"
        advice = f"Excellent! Savings rate is {savings_rate:.1f}%. Keep it up!"

    categories = {}
    if food > 0: categories["Food"] = food
    if rent > 0: categories["Rent"] = rent
    if transport > 0: categories["Transport"] = transport
    if entertainment > 0: categories["Entertainment"] = entertainment
    if other > 0: categories["Other"] = other

    category_tips = []
    if income > 0:
        if food > income * 0.3:
            category_tips.append(f"Food spending is high ({food/income*100:.0f}% of income). Try meal planning.")
        if entertainment > income * 0.1:
            category_tips.append(f"Entertainment is {entertainment/income*100:.0f}% of income. Consider reducing.")
        if rent > income * 0.4:
            category_tips.append(f"Rent is {rent/income*100:.0f}% of income — above recommended 40%.")

    avg_savings_pk = 8.0
    if savings_rate > avg_savings_pk:
        comparison = f"You save {savings_rate - avg_savings_pk:.1f}% above Pakistan average ({avg_savings_pk}%). Top performer!"
    else:
        comparison = f"Pakistan average savings rate is {avg_savings_pk}%. You can improve!"

    emergency_fund_needed = expenses * 3
    emergency_fund_status = f"You need {currency} {emergency_fund_needed:,.0f} as emergency fund (3 months expenses)."

    result = {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "savings_rate": round(savings_rate, 2),
        "status": status,
        "advice": advice,
        "health_score": health_score,
        "currency": currency,
        "categories": categories,
        "category_tips": category_tips,
        "comparison": comparison,
        "emergency_fund_needed": emergency_fund_needed,
        "emergency_fund_status": emergency_fund_status
    }

    tool_context.state["BUDGET_DATA"] = json.dumps(result)
    entity = datastore.Entity(key=datastore_client.key("Budget"))
    entity.update({
        "income": income, "expenses": expenses, "savings": savings,
        "savings_rate": round(savings_rate, 2), "status": status,
        "health_score": health_score, "currency": currency
    })
    entity["timestamp"] = datetime.now()
    datastore_client.put(entity)
    return result

# =============================================
# TOOL 5: Goal Planning with Milestones
# =============================================
def create_goal_plan(tool_context: ToolContext, goal_title: str, target_amount: float,
                     months: int, monthly_savings_available: float, currency: str = "PKR") -> dict:
    monthly_needed = target_amount / months
    feasible = monthly_needed <= monthly_savings_available

    saved_so_far = tool_context.state.get("SAVED_SO_FAR", 0)
    if isinstance(saved_so_far, str):
        saved_so_far = float(saved_so_far)
    progress_pct = min(100, round((saved_so_far / target_amount) * 100, 1)) if target_amount > 0 else 0

    milestones = [
        {"milestone": "25%", "amount": target_amount * 0.25, "months": round(months * 0.25)},
        {"milestone": "50%", "amount": target_amount * 0.50, "months": round(months * 0.50)},
        {"milestone": "75%", "amount": target_amount * 0.75, "months": round(months * 0.75)},
        {"milestone": "100%", "amount": target_amount, "months": months},
    ]

    result = {
        "goal": goal_title,
        "target_amount": target_amount,
        "monthly_saving_needed": round(monthly_needed, 2),
        "months": months,
        "feasible": feasible,
        "currency": currency,
        "progress_percent": progress_pct,
        "saved_so_far": saved_so_far,
        "milestones": milestones
    }

    tool_context.state["GOAL_DATA"] = json.dumps(result)
    entity = datastore.Entity(key=datastore_client.key("Goal"))
    entity.update({
        "goal": goal_title, "target_amount": target_amount,
        "monthly_saving_needed": round(monthly_needed, 2),
        "months": months, "feasible": feasible, "currency": currency
    })
    entity["timestamp"] = datetime.now()
    datastore_client.put(entity)
    return result

# =============================================
# TOOL 6: Investment Advice
# =============================================
def get_investment_advice(tool_context: ToolContext, savings_amount: float,
                           country_code: str = "PK", currency: str = "PKR") -> dict:
    try:
        gold_response = requests.get("https://api.metals.live/v1/spot/gold", timeout=5)
        gold_price_usd = gold_response.json()[0]["gold"]
    except:
        gold_price_usd = 92

   # Fetch live USD/PKR rate
    try:
        fx_response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=5
        )
        fx_data = fx_response.json()
        live_pkr = fx_data["rates"].get("PKR", 280)
        live_inr = fx_data["rates"].get("INR", 83)
        live_ngn = fx_data["rates"].get("NGN", 1580)
        rates = {"PKR": live_pkr, "INR": live_inr, "USD": 1, "NGN": live_ngn}
    except:
        rates = {"PKR": 280, "INR": 83, "USD": 1, "NGN": 1580}
    rate = rates.get(currency, 278)
    gold_price_local = round(gold_price_usd * rate, 2)
    monthly_savings = round(savings_amount * 0.2, 2)

    if country_code == "PK":
        recommendations = [
            f"Gold: Current rate {currency} {gold_price_local}/gram — safe long-term investment",
            "National Savings: Behbood or Special Savings Certificate",
            f"Monthly saving target: {currency} {monthly_savings} (20% of savings)",
            "Meezan Bank profit account — halal banking option"
        ]
    elif country_code == "IN":
        recommendations = [
            f"Gold: Current rate {currency} {gold_price_local}/gram",
            f"Monthly SIP target: {currency} {monthly_savings}",
            "PPF or NSC — safe government schemes",
            "Index funds for long-term growth"
        ]
    else:
        recommendations = [
            f"Gold: Current rate USD {gold_price_usd}/gram",
            f"Monthly saving target: {currency} {monthly_savings}",
            "Diversify across bonds, stocks and gold",
            "Emergency fund first — 3-6 months expenses"
        ]

    result = {
        "savings_amount": savings_amount,
        "country": country_code,
        "currency": currency,
        "gold_price_local": gold_price_local,
        "gold_price_usd": gold_price_usd,
        "recommendations": recommendations,
        "tip": "Diversify: 40% gold, 40% national savings, 20% liquid cash"
    }

    tool_context.state["INVESTMENT_DATA"] = json.dumps(result)
    entity = datastore.Entity(key=datastore_client.key("Investment"))
    entity.update(result)
    entity["timestamp"] = datetime.now()
    datastore_client.put(entity)
    return result

# =============================================
# TOOL 7: Financial Alerts
# =============================================
def check_financial_alerts(tool_context: ToolContext, income: float,
                             expenses: float, currency: str = "PKR") -> dict:
    savings = income - expenses
    alerts = []

    if expenses > income:
        alerts.append(f"CRITICAL: Expenses exceed income by {abs(savings):.0f} {currency}!")
    if income > 0 and (savings / income) < 0.1:
        alerts.append("WARNING: Savings below 10% — financial risk!")
    if income > 0 and (savings / income) >= 0.3:
        alerts.append("GREAT: You are saving 30%+ — excellent financial discipline!")

    result = {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "alerts": alerts,
        "timestamp": datetime.now().isoformat()
    }

    tool_context.state["ALERT_DATA"] = json.dumps(result)
    entity = datastore.Entity(key=datastore_client.key("Alerts"))
    entity.update({"income": income, "expenses": expenses, "savings": savings})
    datastore_client.put(entity)
    return result

# =============================================
# TOOL 8: Debt Management
# =============================================
def calculate_debt_plan(tool_context: ToolContext, total_debt: float,
                         monthly_payment: float, interest_rate: float = 12.0,
                         currency: str = "PKR") -> dict:
    import math
    monthly_rate = interest_rate / 100 / 12
    if monthly_rate > 0 and monthly_payment > total_debt * monthly_rate:
        months_to_payoff = round(-1 * (
            math.log(1 - (total_debt * monthly_rate / monthly_payment))
        ) / math.log(1 + monthly_rate))
        total_paid = monthly_payment * months_to_payoff
        total_interest = total_paid - total_debt
    else:
        months_to_payoff = 0
        total_interest = 0
        total_paid = total_debt

    result = {
        "total_debt": total_debt,
        "monthly_payment": monthly_payment,
        "interest_rate": interest_rate,
        "months_to_payoff": months_to_payoff,
        "total_interest_paid": round(total_interest, 2),
        "total_amount_paid": round(total_paid, 2),
        "currency": currency,
        "advice": f"Pay off highest interest debt first. You will be debt-free in {months_to_payoff} months!"
    }

    tool_context.state["DEBT_DATA"] = json.dumps(result)
    entity = datastore.Entity(key=datastore_client.key("Debt"))
    entity.update(result)
    entity["timestamp"] = datetime.now()
    datastore_client.put(entity)
    return result

# =============================================
# TOOL 9: Financial History Comparison
# =============================================
def get_financial_history(tool_context: ToolContext) -> dict:
    query = datastore_client.query(kind="Budget")
    query.order = ["-timestamp"]
    history = []
    for entity in query.fetch(limit=3):
        history.append({
            "date": entity.get("timestamp").strftime("%Y-%m-%d") if entity.get("timestamp") else "",
            "income": entity.get("income", 0),
            "expenses": entity.get("expenses", 0),
            "savings_rate": entity.get("savings_rate", 0),
            "health_score": entity.get("health_score", 0),
            "currency": entity.get("currency", "PKR")
        })

    comparison = ""
    if len(history) >= 2:
        diff = history[0]["savings_rate"] - history[1]["savings_rate"]
        if diff > 0:
            comparison = f"Your savings rate improved by {diff:.1f}% since last session!"
        elif diff < 0:
            comparison = f"Your savings rate decreased by {abs(diff):.1f}% since last session."
        else:
            comparison = "Your savings rate is consistent with last session."

    result = {"history": history, "comparison": comparison, "sessions": len(history)}
    tool_context.state["HISTORY_DATA"] = json.dumps(result)
    return result

    # =============================================
# TOOL 10: Vertex AI Search — Real-time Financial Data
# =============================================
def search_financial_news(tool_context: ToolContext, query: str) -> dict:
    """Search real-time Pakistan financial news and rates using Vertex AI Search."""
    import subprocess
    import json as json_lib

    try:
        # Get access token
        token_result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True
        )
        token = token_result.stdout.strip()

        # Vertex AI Search API call
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{SEARCH_PROJECT}/locations/global/collections/default_collection/engines/{SEARCH_ENGINE_ID}/servingConfigs/default_search:search"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "pageSize": 5,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"}
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()

        results = []
        for result in data.get("results", []):
            doc = result.get("document", {})
            derived = doc.get("derivedStructData", {})
            title = derived.get("title", "")
            snippet = derived.get("snippets", [{}])[0].get("snippet", "") if derived.get("snippets") else ""
            link = derived.get("link", "")
            if title or snippet:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link
                })

        tool_context.state["SEARCH_RESULTS"] = json.dumps(results)
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "status": "success"
        }

    except Exception as e:
        logging.error(f"Search error: {e}")
        # Fallback data jab tak Vertex AI Search index ho
        fallback_data = {
            "Pakistan gold price": [{"title": "Gold Price Pakistan Today", "snippet": "24K gold price in Pakistan is approximately PKR 42,439 to PKR 42,525 per gram as of April 2026."}],
            "State Bank": [{"title": "SBP Policy Rate", "snippet": "State Bank of Pakistan policy rate is 12% as of April 2026. Home remittances increased 29% year-on-year."}],
            "inflation": [{"title": "Pakistan Inflation 2026", "snippet": "Pakistan inflation rate has decreased to 0.7% in March 2026, lowest in years."}],
            "NSS rates": [{"title": "National Savings Pakistan", "snippet": "Behbood Savings Certificate profit rate is 15.12% per annum. Special Savings Certificates offer 12.96% annually."}],
        }
        
        results = []
        for key, data in fallback_data.items():
            if key.lower() in query.lower():
                results = data
                break
        
        if not results:
            results = [{"title": "Pakistan Financial Update", "snippet": "Pakistan economy showing stability. SBP rate at 12%, inflation at 0.7%, gold at PKR 42,000+/gram."}]
        
        return {
            "query": query,
            "results": results,
            "status": "fallback"
        }
        

# =============================================
# AGENTS
# =============================================

financial_researcher = Agent(
    name="financial_researcher",
    model=model_name,
    description="Analyzes user budget, categories, history and alerts.",
    instruction="""
    You are FinMind's financial analyst.

    When user provides financial data:
    1. Extract income, expenses, currency from message
    2. If user mentions expense categories (food, rent, transport etc), extract those too
    3. Call analyze_budget with all available values
    4. Call check_financial_alerts
    5. Call get_financial_history to show progress vs last session

    Detect user language (Urdu/Hindi/English) and respond in same language.
    If user mentions debt or loan, note it for goal_investment_planner.
    """,
    tools=[analyze_budget, check_financial_alerts, get_financial_history, search_financial_news],
    output_key="research_data"
)

goal_investment_planner = Agent(
    name="goal_investment_planner",
    model=model_name,
    description="Creates savings goals, milestones, debt plans and investment advice.",
    instruction="""
    You are FinMind's financial planner.

    1. Always call get_investment_advice with savings amount from research_data
    2. If user mentioned a goal or purchase, call create_goal_plan with milestones
    3. If user mentioned debt or loan, call calculate_debt_plan
    4. Detect country (PK, IN, NG, US) and use correct currency
    5. Match user language (Urdu/Hindi/English)

    research_data: { research_data }
    """,
    tools=[create_goal_plan, get_investment_advice, calculate_debt_plan],
    output_key="plan_data"
)

response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Formats all financial data into clean readable response.",
    instruction="""
    You are FinMind's friendly presenter.

    Format all data clearly and warmly using this structure:

    👋 FinMind Financial Summary for [name]
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    💰 Budget Analysis
    • Income: [value]
    • Expenses: [value]
    • Savings: [value]
    • Savings Rate: [%] — [status]
    • Health Score: [score]/100
    • vs Average: [comparison]
    • [advice]

    📊 Expense Breakdown (if provided)
    • Food: [value]
    • Rent: [value]
    • Transport: [value]
    • Tips: [category tips]

    🎯 Goal Plan (if exists)
    • Goal: [value]
    • Target: [value]
    • Monthly Needed: [value]
    • Timeline: [months]
    • Progress: [%]
    • Milestones: 25% → 50% → 75% → 100%
    • Feasible: [Yes/Needs Adjustment]

    💳 Debt Plan (if exists)
    • Total Debt: [value]
    • Monthly Payment: [value]
    • Debt-free in: [months]
    • Total Interest: [value]

    📈 Investment Advice
    • Gold Today: [price]/gram
    • [recommendations]

    🚨 Emergency Fund
    • You need: [value] (3 months expenses)

    📅 Progress vs Last Session
    • [comparison from history]

    📰 Latest Financial News (if available)
    • [news title and snippet]
    • [news title and snippet]

    ⚠️ Alerts (if any)
    • [alerts]

    🏆 Financial Health Score: [score]/100
    💡 Tip: [relevant tip]
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Rules:
    - Use ONLY real data — never placeholders
    - Skip sections with no data
    - Match user language (Urdu/Hindi/English)
    - Be warm, encouraging and professional
    - Address user by name always

    research_data: { research_data }
    plan_data: { plan_data }
    """
)

finmind_workflow = SequentialAgent(
    name="finmind_workflow",
    sub_agents=[
        financial_researcher,
        goal_investment_planner,
        response_formatter,
    ]
)

root_agent = Agent(
    name="finmind_greeter",
    model=model_name,
    description="Main entry point — smart conversational financial advisor.",
    instruction="""
    You are FinMind, a warm and intelligent AI financial advisor — like a trusted friend who knows finance.

    SMART CONVERSATION RULES:

    1. START: Greet warmly in English, ask name and country.

    2. AFTER NAME:
       - Use add_prompt_to_state to save
       - Use load_chat_history to check history
       - If returning: "Welcome back [name]! Last session your savings rate was X%. Shall we continue?"
       - If new: "Great to meet you [name]! Let's get started."

    3. LANGUAGE DETECTION — VERY IMPORTANT:
       - Detect the language from user's VERY FIRST message
       - If user writes in Urdu → reply in Urdu for entire conversation
       - If user writes in Hindi → reply in Hindi for entire conversation
       - If user writes in English → reply in English for entire conversation
       - NEVER ask the user which language they prefer — detect automatically
       - If user writes in any other language you don't know → say:
         "I am currently in learning phase for this language. I will support it soon! 
          For now, can we chat in English or Urdu?"
       - Once language detected, NEVER switch languages mid conversation

    4. SMART DATA COLLECTION:
       - If user gives ALL info at once → accept everything, say thank you naturally → transfer to finmind_workflow
       - If user gives PARTIAL info → ask only for MISSING pieces one at a time
       - If user gives NO info → ask ONE question at a time:
         * "What is your monthly income [name]?"
         * After answer: "And your monthly expenses?"
         * After answer: "Any specific savings goal?"
         * After answer: "Any loans or debts?"
         * Then transfer to finmind_workflow

    5. NATURAL REACTIONS:
       - After good savings: "That's impressive [name]! Keep it up!"
       - After overspending: "Don't worry [name], we will fix this together."
       - After goal: "Great goal! Let's see how we can get you there."
       - Always encouraging, never judgmental

    6. TRANSFER:
       - Once enough data collected → transfer to finmind_workflow
       - Never ask for same info twice

    Always address user by name. Be like a smart friend, not a robot.
    """,
    tools=[add_prompt_to_state, load_chat_history],
    sub_agents=[finmind_workflow]
)