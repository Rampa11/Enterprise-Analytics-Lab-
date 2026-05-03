# 🚀 Enterprise Analytics Lab

**Enterprise Analytics Lab** is an AI-powered platform designed to help users learn data analytics by solving real-world business problems.

Instead of watching tutorials, users gain hands-on experience through simulated business scenarios, AI-generated datasets, and instant feedback systems.

---

## 🌍 Vision

To build a global platform where anyone can learn data analytics by solving real business problems.

---

## 🎯 Mission

To bridge the gap between theory and real-world analytics through AI-powered simulations.

---

## 📈 Features

* 🤖 **AI Business Agent**
  Generate real-world business questions from datasets.

* 🧠 **AI Business Manager**
  Simulate consulting-style analytics projects.

* 📊 **AI Dataset Generator**
  Create realistic datasets across multiple industries.

* 🧪 **Practice Lab**
  Solve analytics challenges and get AI-powered feedback.

* 🏆 **Leaderboard System**
  Track performance and compete with other users.

* 🔥 **Streaks & Badges**
  Build consistency and earn achievements.

* 💳 **Monetization System**

  * Pay-per-answer credits
  * Premium subscription
  * Stripe-powered checkout

---

## 🏗️ Tech Stack

### Frontend

* Streamlit

### Backend / AI

* Python
* OpenAI API

### Database

* Supabase (PostgreSQL)

### Payments

* Stripe Checkout
* Webhook (FastAPI on Render)

### Deployment

* Streamlit Cloud (App)
* Render (Webhook Server)

---

## 🔐 Authentication

* Email/password authentication via Supabase
* Session-based access control
* Secure logout and session handling

---

## 💰 Payment Architecture

User → Stripe Checkout → Webhook (Render) → Supabase → App updates

* Payments are verified via webhook
* Credits and subscriptions are updated securely on the backend

---

## ⚙️ Installation (Local Setup)

### 1. Clone repository

git clone https://github.com/your-username/enterprise-analytics-lab.git
cd enterprise-analytics-lab

### 2. Create virtual environment

python -m venv venv
venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Set environment variables

Create a `.env` file:

OPENAI_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
STRIPE_SECRET_KEY=your_key
APP_URL=http://localhost:8501

### 5. Run the app

streamlit run dashboard.py

---

## 🔗 Webhook Setup (Payments)

A separate FastAPI webhook server handles Stripe events.

Webhook Flow:
Stripe → Webhook Server → Supabase → App

Webhook Environment Variables:

STRIPE_SECRET_KEY=your_key
STRIPE_WEBHOOK_SECRET=your_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key

---

## 📦 Project Structure

enterprise-analytics-lab/
│
├── dashboard.py
├── pages/
├── ai_engine/
├── assets/
├── data/
├── db.py
├── payments.py
├── requirements.txt
│
├── webhook/
│   ├── webhook_server.py
│   └── requirements.txt

---

## 🚀 Deployment

* App: Streamlit Cloud
* Webhook: Render
* Database: Supabase
* Payments: Stripe

---

## 🧠 Learning Philosophy

“The best way to learn data analytics is not by watching tutorials, but by solving real business problems.”
— The Cardinal Way

---

## 📌 Future Improvements

* Real-time credit updates after payment
* Admin dashboard & analytics
* Multi-user leaderboard scaling
* React frontend upgrade
* Advanced AI feedback engine

---

## 👤 Author

Akpor Unukogbon
Data Analyst & Software Engineer

---

## ⭐ Contributing

Contributions, ideas, and feedback are welcome!

---

## 📄 License

This project is licensed under the MIT License.
