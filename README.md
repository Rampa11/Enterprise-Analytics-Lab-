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

- 🤖 **AI Business Agent**  
  Generate real-world business questions from datasets.

- 🧠 **AI Business Manager**  
  Simulate consulting-style analytics projects.

- 📊 **AI Dataset Generator**  
  Create realistic datasets across multiple industries.

- 🧪 **Practice Lab**  
  Solve analytics challenges and get AI-powered feedback.

- 🏆 **Leaderboard System**  
  Track performance and compete with other users.

- 🔥 **Streaks & Badges**  
  Build consistency and earn achievements.

- 💳 **Monetization System**  
  - Pay-per-answer credits  
  - Premium subscription  
  - Stripe-powered checkout

---

## 🏗️ Tech Stack

### Frontend
- Streamlit

### Backend / AI
- Python
- OpenAI API

### Database
- Supabase (PostgreSQL)

### Payments
- Stripe Checkout
- Webhook (FastAPI on Render)

### Deployment
- Streamlit Cloud (App)
- Render (Webhook Server)

---

## 🔐 Authentication

- Email/password authentication via Supabase
- Session-based access control
- Secure logout and session handling

---

## 💰 Payment Architecture

```text
User → Stripe Checkout → Webhook (Render) → Supabase → App updates
