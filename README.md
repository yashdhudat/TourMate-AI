# 🌍 PersonaTrip AI — Personality-Based Travel Recommender

> An AI-powered travel recommendation system that matches destinations to your unique personality using the **OCEAN / Big Five psychological model** and **machine learning**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1.2-black?style=flat-square&logo=flask)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-orange?style=flat-square)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6.1-F7931E?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📌 What is PersonaTrip AI?

Most travel apps recommend destinations based on **what everyone else likes**. PersonaTrip AI is different — it recommends destinations based on **who you are**.

Using the scientifically validated **OCEAN personality model** (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism), the system builds a unique personality vector for each user and matches it against a curated destination dataset using **cosine similarity**.

The result? Travel recommendations that feel personally crafted — not generic.

---

## ✨ Key Features

### 🧠 OCEAN Personality Auto-Detector
- 10 real psychometric questions (not manual sliders)
- Auto-calculates all 5 OCEAN trait scores
- Live progress bar as you answer
- Scores saved to your profile for future use

### 🤖 AI-Powered Recommendation Engine
- Cosine similarity matching across 29-dimensional feature vectors
- Combines personality traits + travel preferences (climate, budget, activities)
- Returns Top 3 personalised destinations with match percentage

### 💬 Destination AI Chatbot (Groq LLaMA)
- Ask anything about a recommended destination
- Personality-aware responses tailored to your travel style
- Quick-question buttons for instant insights
- Powered by Groq's ultra-fast LLaMA 3.3 inference

### 🗓️ AI Trip Itinerary Generator
- Day-by-day personalised travel plan
- Morning / Afternoon / Evening activity breakdown
- Insider tips based on your personality and budget
- Switchable between 2, 3, and 5-day views

### 📜 Recommendation History
- All past recommendations saved per user
- Grouped by date with accordion view
- Delete individual entries

### 🔐 Secure Authentication
- User registration & login
- Password hashing with Werkzeug
- Session-based auth with SQLite storage

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| AI / ML | scikit-learn (Cosine Similarity) |
| LLM | Groq API — LLaMA 3.3 70B |
| Database | SQLite |
| Frontend | HTML5, CSS3, Jinja2 |
| Data | Pandas, NumPy |

---

## 📁 Project Structure

```
tourism_recommender/
│
├── app.py                  # Flask routes & session handling
├── recommend.py            # ML recommendation engine
├── ai_utils.py             # Groq AI — chatbot, itinerary, explanations
├── preprocess.py           # Data preprocessing pipeline
├── db_schema.sql           # SQLite database schema
├── requirements.txt        # Python dependencies
│
├── data/
│   └── destination_vectors.csv   # Preprocessed destination feature vectors
│
├── database/
│   └── persona_trip.db           # SQLite database (auto-created)
│
├── static/
│   ├── style.css                 # Premium dark UI design system
│   └── destinations/             # Destination images
│
└── templates/
    ├── index.html                # Home — travel preferences form
    ├── quiz.html                 # OCEAN personality quiz
    ├── results.html              # Recommendations + chatbot + itinerary
    ├── itinerary.html            # AI day-by-day trip planner
    ├── history.html              # User recommendation history
    ├── login.html                # Login page
    └── register.html             # Registration page
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yashdhudat/TourMate-AI.git
cd TourMate-AI
```

**2. Create and activate a virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Set your Groq API key:**

Create a `.env` file in the project root:
```
GROQ_API_KEY=gsk_your_api_key_here
```

Or set it as an environment variable:
```bash
# Windows
set GROQ_API_KEY=gsk_your_api_key_here

# Mac / Linux
export GROQ_API_KEY=gsk_your_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com) — no credit card required.

**5. Run the application:**
```bash
python app.py
```

**6. Open in browser:**
```
http://127.0.0.1:5000
```

---

## 🔄 How It Works

```
User Registers / Logs In
        ↓
Completes 10-Question OCEAN Quiz
        ↓
OCEAN Scores Auto-Calculated (0.0 – 1.0 scale)
        ↓
User Sets Travel Preferences (Climate, Budget, Activities)
        ↓
29-Dimensional Feature Vector Built
        ↓
Cosine Similarity vs Destination Matrix
        ↓
Top 3 Destinations Returned
        ↓
Groq AI Generates Personalised Explanation
        ↓
User Can: Ask Chatbot | Generate Itinerary | View History
```

---

## 🧪 The OCEAN Model

| Trait | What it measures | Travel implication |
|-------|-----------------|-------------------|
| **O**penness | Creativity, curiosity | Prefers unique, cultural destinations |
| **C**onscientiousness | Organisation, planning | Prefers structured itineraries |
| **E**xtraversion | Sociability, energy | Prefers lively, social destinations |
| **A**greeableness | Cooperation, trust | Prefers group-friendly destinations |
| **N**euroticism | Stress sensitivity | Prefers safe, comfortable destinations |

---

## 🔮 Future Scope

- [ ] Live budget estimation (flights + hotel + food)
- [ ] Hotel & activity recommendations
- [ ] Feedback-based adaptive ML (ratings improve future results)
- [ ] Google Maps integration
- [ ] Group compatibility analysis
- [ ] Eco-friendly destination tagging
- [ ] Mobile app (React Native)

---

## 👨‍💻 Author

**Yash Dhudat**
- GitHub: [@yashdhudat](https://github.com/yashdhudat)

---

## 📄 License

This project is licensed under the MIT License.

---

> *"Travel is the only thing you buy that makes you richer — PersonaTrip makes sure you buy the right one."*
