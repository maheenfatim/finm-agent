**🧠 FinMind — AI-Powered Financial Advisor for Developing Countries**

"1.4 billion people deserve financial guidance. FinMind makes that possible."

<img width="1600" height="677" alt="Screenshot 2026-04-07 173119" src="https://github.com/user-attachments/assets/c7319893-61fb-4e92-82b2-143f2c9d5713" />
<img width="1569" height="661" alt="5" src="https://github.com/user-attachments/assets/ab557fda-16ce-48a3-8776-8c46a5428744" />



📌 Overview
FinMind is a cloud-deployed multi-agent AI system that acts as a personal financial advisor — built specifically for unbanked and underserved populations in developing countries like Pakistan, India, Bangladesh, Nigeria, and Egypt.
Most people in these regions have no access to banks, financial advisors, or budgeting tools. FinMind bridges that gap through natural language conversation. Users simply type their situation — and FinMind analyzes their finances, sets savings goals, recommends investments, and remembers everything for next time.
Built for the Google Gen AI Academy APAC — Multi-Agent Productivity Assistant Challenge.

🎯 Problem Statement
Over 1.4 billion adults worldwide remain unbanked. In developing countries:

People earn in cash with no digital tracking
Professional financial advice is unaffordable or inaccessible
Existing AI tools are generic and English-only
No tool exists that specializes purely in personal financial guidance for low-income users

FinMind solves all of this through a coordinated multi-agent AI pipeline.

✨ Features

💬 Natural language chat — No forms, just talk to the agent like a human
📊 Budget analysis — Calculates savings rate, flags CRITICAL / LOW / MODERATE / GOOD status
🎯 Goal planning — Sets savings targets and checks feasibility month by month
📈 Investment advice — Real-time gold prices + halal banking + national savings recommendations
🔔 Financial alerts — Detects overspending and triggers warnings automatically
🧠 Session memory — All user data persisted in Google Cloud Datastore across sessions
🔄 Multi-agent routing — Intelligent transfer between specialized sub-agents
☁️ Cloud deployed — Fully live on Google Cloud Run


🏗️ Architecture
User (Chat Interface)
        │
        ▼
Root Agent: finmind_greeter  ←  Google ADK
  • Receives user message
  • Saves prompt to Datastore
        │
        ▼
SequentialAgent: finmind_workflow
        │
        ├── Step 1: financial_researcher
        │     • analyze_budget (income / expenses / savings rate)
        │     • check_financial_alerts (overspending detection)
        │     → Saves to: Budget & Alerts collections
        │
        ├── Step 2: goal_investment_planner
        │     • create_goal_plan (target / months / feasibility)
        │     • get_investment_advice (real-time gold API + local tips)
        │     → Saves to: Goal & Investment collections
        │
        └── Step 3: response_formatter
              • Synthesizes all agent outputs
              • Delivers clean structured reply to user
        │
        ▼
Google Cloud Datastore
(UserPrompt | Budget | Alerts | Goal | Investment)

🛠️ Tech Stack
LayerTechnologyAgent FrameworkGoogle ADKAI ModelGemini 2.5 FlashBackendFastAPI (Python)DeploymentGoogle Cloud RunDatabaseGoogle Cloud DatastoreExternal APImetals.live — real-time gold pricesLoggingGoogle Cloud LoggingDev UIADK Dev UI

🚀 Getting Started
Prerequisites

Python 3.11+
Google Cloud account with billing enabled
gcloud CLI installed and authenticated

1. Clone the repo
bashgit clone https://github.com/maheenfatim/finm-agent.git
cd finm-agent
2. Install dependencies
bashpip install -r requirements.txt
3. Set up environment variables
Create a .env file in the root directory:
MODEL=gemini-2.5-flash
GOOGLE_CLOUD_PROJECT=your-project-id
4. Authenticate with Google Cloud
bashgcloud auth application-default login
gcloud config set project your-project-id
5. Run locally with ADK Dev UI
bashadk web
Then open http://localhost:8000 and select finmind_greeter from the agent dropdown.

☁️ Cloud Deployment
bashgcloud run deploy finm-agent \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated

💬 Example Conversations
Budget Analysis

User: "I earn PKR 50,000 and spend PKR 42,000 per month"
FinMind: Analyzes savings rate (16%), flags MODERATE status, suggests next steps

Goal Planning

User: "If I save PKR 5,000/month, how long to buy a laptop worth PKR 80,000?"
FinMind: "It will take you 16 months to save PKR 80,000"

Investment Advice

User: "I have PKR 50,000 and want to invest"
FinMind: Routes to investment agent → provides real-time gold price + halal banking options + diversification strategy

Session Memory

User: "What did I tell you about my income last time?"
FinMind: Retrieves stored data from Cloud Datastore and recalls previous session


📁 Project Structure
finm-agent/
├── agent.py           # All agents, tools, and workflow definition
├── requirements.txt   # Python dependencies
├── .env               # Environment variables (not committed)
├── .gitignore
└── README.md

🌍 Impact
FinMind targets 24+ countries with multi-currency support, built for populations that have historically had no access to financial guidance. By combining multi-agent AI with persistent memory and local financial context, FinMind delivers expert-quality advice to anyone with a smartphone.

👩‍💻 Developer: Bisma Asif
Bisma Asif
📧 bismaasifbcs90@gmail.com
🔗 GitHub
