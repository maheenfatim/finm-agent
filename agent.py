import os
import logging
import json
from datetime import datetime

import google.cloud.logging
from google.cloud import datastore   
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

# --- Setup Logging and Environment ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")

# ✅ Datastore Client (YOUR DATABASE = project id)
datastore_client = datastore.Client(project="finm-ai")

# =============================================
# TOOL 1: Save user prompt to state + DB
# =============================================

def add_prompt_to_state(tool_context: ToolContext, prompt: str) -> dict[str, str]:
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] PROMPT: {prompt}")

    # ✅ Save to Datastore
    entity = datastore.Entity(key=datastore_client.key("UserPrompt"))
    entity.update({
        "prompt": prompt,
        "timestamp": datetime.now()
    })
    datastore_client.put(entity)

    return {"status": "success"}


# =============================================
# TOOL 2: Budget Analysis Tool
# =============================================

def analyze_budget(tool_context: ToolContext, income: float, expenses: float, currency: str = "PKR") -> dict:

    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0

    if savings_rate < 0:
        status = "CRITICAL"
        advice = f"Aap {abs(savings):.0f} {currency} zyada kharch kar rahe hain."
    elif savings_rate < 10:
        status = "LOW"
        advice = f"Savings sirf {savings_rate:.1f}% hai."
    elif savings_rate < 20:
        status = "MODERATE"
        advice = f"Savings {savings_rate:.1f}% hai."
    else:
        status = "GOOD"
        advice = f"Zabardast! {savings_rate:.1f}% savings!"

    result = {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "savings_rate": round(savings_rate, 2),
        "status": status,
        "advice": advice,
        "currency": currency
    }

    tool_context.state["BUDGET_DATA"] = json.dumps(result)

    # ✅ Save to Datastore
    entity = datastore.Entity(key=datastore_client.key("Budget"))
    entity.update(result)
    entity["timestamp"] = datetime.now()
    datastore_client.put(entity)

    return result


# =============================================
# TOOL 3: Goal Planning Tool
# =============================================

def create_goal_plan(tool_context: ToolContext, goal_title: str, target_amount: float, months: int, monthly_savings_available: float, currency: str = "PKR") -> dict:

    monthly_needed = target_amount / months

    feasible = monthly_needed <= monthly_savings_available

    result = {
        "goal": goal_title,
        "target_amount": target_amount,
        "monthly_saving_needed": monthly_needed,
        "months": months,
        "feasible": feasible,
        "currency": currency
    }

    tool_context.state["GOAL_DATA"] = json.dumps(result)

    # ✅ Save to Datastore
    entity = datastore.Entity(key=datastore_client.key("Goal"))
    entity.update(result)
    entity["timestamp"] = datetime.now()
    datastore_client.put(entity)

    return result


# =============================================
# TOOL 4: Investment Advice Tool
# =============================================

import requests

def get_investment_advice(tool_context: ToolContext, savings_amount: float, country_code: str = "PK", currency: str = "PKR") -> dict:
    
    # Real gold price fetch
    try:
        gold_response = requests.get(
            "https://api.metals.live/v1/spot/gold",
            timeout=5
        )
        gold_price_usd = gold_response.json()[0]["gold"]
    except:
        gold_price_usd = 92  # fallback per gram

    # PKR conversion (approximate)
    usd_to_pkr = 278
    gold_price_pkr = round(gold_price_usd * usd_to_pkr, 2)

    monthly_savings = round(savings_amount * 0.2, 2)

    result = {
        "savings_amount": savings_amount,
        "country": country_code,
        "currency": currency,
        "gold_price_per_gram_pkr": gold_price_pkr,
        "recommendations": [
            f"Gold: Current rate PKR {gold_price_pkr}/gram — safe long-term investment",
            f"National Savings: Invest in Behbood or Special Savings Certificate",
            f"Monthly saving target: PKR {monthly_savings} (20% of your amount)",
            "Meezan Bank profit account — halal banking option for PK"
        ],
        "tip": "Diversify: 40% gold, 40% national savings, 20% liquid cash"
    }

    tool_context.state["INVESTMENT_DATA"] = json.dumps(result)
    return result
    # ✅ Save to Datastore
    entity = datastore.Entity(key=datastore_client.key("Investment"))
    entity.update(result)
    entity["timestamp"] = datetime.now()
    datastore_client.put(entity)

    return result


# =============================================
# TOOL 5: Alert Check Tool
# =============================================

def check_financial_alerts(tool_context: ToolContext, income: float, expenses: float, currency: str = "PKR") -> dict:

    savings = income - expenses

    result = {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "timestamp": datetime.now().isoformat()
    }

    tool_context.state["ALERT_DATA"] = json.dumps(result)

    # ✅ Save to Datastore
    entity = datastore.Entity(key=datastore_client.key("Alerts"))
    entity.update(result)
    datastore_client.put(entity)

    return result


# =============================================
# AGENTS (UNCHANGED)
# =============================================

financial_researcher = Agent(
    name="financial_researcher",
    model=model_name,
    tools=[analyze_budget, check_financial_alerts],
    output_key="research_data"
)

goal_investment_planner = Agent(
    name="goal_investment_planner",
    model=model_name,
    tools=[create_goal_plan, get_investment_advice],
    output_key="plan_data"
)

response_formatter = Agent(
    name="response_formatter",
    model=model_name
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
    tools=[add_prompt_to_state],
    sub_agents=[finmind_workflow]
)