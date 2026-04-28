**🧠 FinMind — AI-Powered Financial Advisor for Developing Countries**

 *1.4 billion people deserve financial guidance. FinMind makes that possible.*

<img width="1582" height="710" alt="demo1" src="https://github.com/user-attachments/assets/d36567a0-3a96-4a60-9c10-5fd02c26e442" />

<img width="1584" height="719" alt="demo2" src="https://github.com/user-attachments/assets/c29b8c5e-6bb3-489b-ad88-3aa15591a2dc" />

<img width="1580" height="709" alt="demo3" src="https://github.com/user-attachments/assets/8f71ef3b-c4da-438f-873e-610e8ffd96c2" />

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

### 1. Clone the repo

```bash
git clone https://github.com/maheenfatim/finm-agent.git
cd finm-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```
### 3. Set up environment variables

MODEL=gemini-2.5-flash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_LOCATION=us-central1

### 4. Authenticate with Google Cloud

```bash
gcloud auth application-default login
gcloud config set project your-project-id
```

### 5. Run locally

```bash
adk web
```

## ☁️ Cloud Deployment

```bash
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=europe-west1 \
  --service_name=finm-guide \
  --with_ui \
  . \
  -- \
  --service-account=$SERVICE_ACCOUNT
```

**💬 Example Conversations**

**Budget with Categories**
User: My income is PKR 80,000. Expenses PKR 55,000.
Food: 15,000 Rent: 20,000 Transport: 8,000
FinMind: Savings rate 31% — GOOD 🟢
Health Score: 93/100
23% above Pakistan average!
Emergency fund needed: PKR 165,000

**Goal with Milestones**
User: I want to buy a laptop for PKR 120,000 in 6 months
FinMind: Monthly needed: PKR 20,000
25% → PKR 30,000 (month 2)
50% → PKR 60,000 (month 3)
100% → PKR 120,000 (month 6) ✓

**Debt Management**
User: I have a loan of PKR 50,000 at 12% interest
FinMind: Debt-free in 11 months
Total interest: PKR 2,936

**Multi-language**
User: مجھے بچت کے بارے میں بتاؤ
FinMind: آپ کی بچت کی شرح 31% ہے — بہترین! 🟢

## 🗺️ Roadmap

- Email-based user authentication for completely isolated user profiles
- WhatsApp and SMS integration via Twilio
- Voice support for non-literate users

**📁 Project Structure**

<img width="462" height="127" alt="structure" src="https://github.com/user-attachments/assets/28841c2f-5645-44c3-b030-5f27b58f364d" />

**🌍 Impact**

FinMind targets 24+ countries with multi-currency support, built for populations that have historically had no access to financial guidance. By combining multi-agent AI with persistent memory, real-time data, and local financial context, FinMind delivers expert-quality advice to anyone with a smartphone.

**Developer**: Bisma Asif
📧 bismaasifbcs90@gmail.com
🔗 GitHub
