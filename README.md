# 🌍 TourMate AI  
### AI-Powered Tourist Destination Recommendation System

TourMate AI is an intelligent travel recommendation system that suggests personalized tourist destinations based on a user’s **personality traits (OCEAN model)**, **budget**, **group type**, and **preferences**.  
The system enhances user satisfaction with **sentiment-based learning**, allowing destination rankings to improve over time.

---

## 🚀 Features

### 🔹 **1. Personality-Based Recommendations**
Uses the OCEAN model (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) collected via a custom quiz to personalize travel suggestions.

### 🔹 **2. Preference Matching**
Considers:
- Budget range  
- Group type (Solo, Friends, Family, Couple)  
- Trip style preferences  

### 🔹 **3. Machine Learning Recommender Engine**
Uses **Cosine Similarity / KMeans Clustering** to match users with the most suitable destinations from the dataset.

### 🔹 **4. Sentiment Analysis Module**
After a trip, users can submit a review which is analyzed with **TextBlob** to:
- Understand user satisfaction  
- Improve future recommendations  

### 🔹 **5. Clean and Interactive UI**
Built using **HTML, CSS, and JavaScript** for a smooth experience.

### 🔹 **6. Flask Backend API**
Handles:
- Quiz submission  
- Preference storage  
- Recommendation fetching  
- Review sentiment analysis  

---

## 🧠 Tech Stack

### **Frontend**
- HTML  
- CSS  
- JavaScript  

### **Backend**
- Python  
- Flask  

### **Machine Learning / NLP**
- Scikit-learn  
- Pandas  
- NumPy  
- TextBlob  

### **Database**
- SQLite (persona_trip.db)

---

## 📊 Project Architecture



TourMate-AI/
│── app.py
│── templates/
│ ├── index.html
│ ├── quiz.html
│ ├── preferences.html
│ ├── results.html
│ ├── review.html
│── static/
│ ├── css/
│ ├── js/
│── models/
│ ├── recommender.py
│ ├── sentiment.py
│── data/
│ ├── destinations.csv
│── database/
│ ├── tourmate.db
│── README.md


---

## 📥 Installation & Setup

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/yashdhudat/TourMate-AI.git
cd TourMate-AI

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Flask App
python app.py


Open the browser:
👉 http://127.0.0.1:5000

📡 API Endpoints (Overview)
Endpoint	Method	Description
/quiz	POST	Submits personality test results
/preferences	POST	Saves budget and group type
/recommend	GET	Returns top recommended destinations
/review	POST	Saves review + performs sentiment analysis
📂 Dataset

destinations.csv contains fields like:

Destination Name

State / Region

Category (Beach, Hill Station, Adventure, Culture, Wildlife, etc.)

Cost Level

Ideal Group Type

Best Season

Personality Match Scores

🧪 Machine Learning Logic
✔ Personality Matching

Uses cosine similarity to compare user personality scores with destination profiles.

✔ Preference Filtering

Destinations are given weighted scores based on:

Budget

Group type

Category rating

✔ Sentiment Learning

User reviews update average sentiment for each destination, improving ranking.

🛠 Future Enhancements

Add Deep Learning–based sentiment classifier

Support multi-language recommendations

Add a user dashboard with analytics

Integrate live weather & travel cost APIs

Deploy using Render / Vercel / AWS

🤝 Contributing

Contributions are welcome!
Feel free to open issues or submit PRs.

📄 License

This project is licensed under the MIT License.

⭐ Support

If you like this project, consider giving it a star ⭐ on GitHub!

---

If you want, I can also generate a **requirements.txt**, a **project logo**, or a **demo GIF** placeholder.

Want me to generate anything else?
