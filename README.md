**🧠 FinMind — AI-Powered Financial Advisor for Developing Countries**

 *1.4 billion people deserve financial guidance. FinMind makes that possible.*

<img width="1600" height="677" alt="Screenshot 2026-04-07 173119" src="https://github.com/user-attachments/assets/c7319893-61fb-4e92-82b2-143f2c9d5713" />
<img width="1569" height="661" alt="5" src="https://github.com/user-attachments/assets/ab557fda-16ce-48a3-8776-8c46a5428744" />



**📌 Overview**

FinMind is a cloud-deployed multi-agent AI system that acts as a personal financial advisor — built specifically for unbanked and underserved populations in developing countries like Pakistan, India, Bangladesh, Nigeria, and Egypt.

Users simply chat in their own language — FinMind analyzes their budget, plans savings goals, manages debt, recommends investments, and remembers everything across sessions.

Built for the **Google Gen AI Academy APAC — Multi-Agent Productivity Assistant Challenge.**

**🎯 Problem Statement**

Over 1.4 billion adults worldwide remain unbanked. In developing countries:

- People earn in cash with no digital tracking
- Professional financial advice is unaffordable or inaccessible
- Existing AI tools are generic and English-only
- No tool exists that specializes purely in personal financial guidance for low-income users

FinMind solves all of this through a coordinated multi-agent AI pipeline.

<img width="521" height="609" alt="3" src="https://github.com/user-attachments/assets/d65b7c6c-de87-447c-a1f7-19b2a4b9a4c9" />


| # | Feature | Tool/Service |
|---|---------|-------------|
| 1 | Expense Categories — food, rent, transport, entertainment | ADK Tools |
| 2 | Financial History Comparison — current vs last session | Cloud Datastore |
| 3 | Savings Milestones — 25% → 50% → 75% → 100% | ADK Tools |
| 4 | Multi-language Support — English, Urdu, Hindi | Gemini on Vertex AI |
| 5 | Emergency Fund Calculator — 3 months expenses | ADK Tools |
| 6 | Debt Management — payoff plan with interest | ADK Tools |
| 7 | Average Comparison — vs Pakistan national average 8% | ADK Tools |
| 8 | Financial Health Score — 0 to 100 | ADK Tools |
| 9 | Session Memory — persistent across sessions | Cloud Datastore |
| 10 | Multi-currency — PKR, INR, USD, NGN live rates | External API |
| 11 | Personalized User Name — addressed by name | ADK Root Agent |
| 12 | Returning User Recognition — loads previous history | Cloud Datastore |
| 13 | Vertex AI Integration — Gemini 2.5 Flash, no rate limits | Vertex AI |
| 14 | Language Auto-detect — no selection needed | Gemini on Vertex AI |
| 15 | Structured Output Format — clean emoji-based sections | ADK Response Formatter |
| 16 | Vertex AI Search — real-time SBP, NSS, financial news | Vertex AI Search |
| 17 | Conversational Flow — one question at a time | ADK Root Agent |


**🏗️ Architecture**

<img width="540" height="544" alt="architechture" src="https://github.com/user-attachments/assets/f74e7fbf-2965-4c7d-b8a2-5422d3da3ee7" />

## 🛠️ Tech Stack

| Layer            | Technology                         | Why Chosen                                      |
|------------------|------------------------------------|-------------------------------------------------|
| Agent Framework  | Google ADK                         | Multi-agent orchestration, SequentialAgent      |
| AI Model         | Gemini 2.5 Flash via Vertex AI     | No rate limits, enterprise scale                |
| Deployment       | Google Cloud Run                   | Serverless, auto-scaling                        |
| Database         | Google Cloud Datastore             | Persistent user memory across sessions          |
| Search           | Vertex AI Search                   | Real-time SBP, NSS, financial news              |
| Gold Price API   | metals.live                        | Real-time gold prices                           |
| Currency API     | exchangerate-api                   | Live USD/PKR/INR/NGN conversion                 |
| Logging          | Google Cloud Logging               | Centralized monitoring                          |

**🚀 Getting Started**

Prerequisites

Python 3.11+
Google Cloud account with billing enabled
gcloud CLI installed and authenticated

**1. Clone the repo**

bashgit clone https://github.com/maheenfatim/finm-agent.git
cd finm-agent

**2. Install dependencies**

bashpip install -r requirements.txt

**3. Set up environment variables**

Create a .env file in the root directory:
MODEL=gemini-2.5-flash
GOOGLE_CLOUD_PROJECT=your-project-id

**4. Authenticate with Google Cloud**

bashgcloud auth application-default login
gcloud config set project your-project-id

**5. Run locally with ADK Dev UI**

bashadk web
Then open http://localhost:8000 and select finmind_greeter from the agent dropdown.

**☁️ Cloud Deploymen**t

bashgcloud run deploy finm-agent \

  --source . \
  
  --region europe-west1 \
  
  --allow-unauthenticated

**💬 Example Conversations**

**Budget Analysis**

User: "I earn PKR 50,000 and spend PKR 42,000 per month"

FinMind: Analyzes savings rate (16%), flags MODERATE status, suggests next steps

**Goal Planning**

User: "If I save PKR 5,000/month, how long to buy a laptop worth PKR 80,000?"

FinMind: "It will take you 16 months to save PKR 80,000"

**Investment Advice**

User: "I have PKR 50,000 and want to invest"

FinMind: Routes to investment agent → provides real-time gold price + halal banking options + diversification strategy

**Session Memory**

User: "What did I tell you about my income last time?"

FinMind: Retrieves stored data from Cloud Datastore and recalls previous session


**📁 Project Structure**

<img width="462" height="127" alt="structure" src="https://github.com/user-attachments/assets/28841c2f-5645-44c3-b030-5f27b58f364d" />

**🌍 Impact**

FinMind targets 24+ countries with multi-currency support, built for populations that have historically had no access to financial guidance. By combining multi-agent AI with persistent memory and local financial context, FinMind delivers expert-quality advice to anyone with a smartphone.

**Developer**: Bisma Asif
📧 bismaasifbcs90@gmail.com
🔗 GitHub
