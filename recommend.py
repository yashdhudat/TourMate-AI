import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ── Load dataset ──
df = pd.read_csv("data/destination_vectors.csv")

FEATURE_COLS = [
    "Climate_Warm","Climate_Cold","Climate_Moderate",
    "Budget_Low","Budget_Medium","Budget_High",
    "Solo","Couple","Family","Group",
    "Beaches","Culture","Food","Nature","Nightlife",
    "Relaxation","Shopping","Spiritual","Adventure",
    "Sightseeing","Trekking","History","Photography",
    "Safari","O","C","E","A","N"
]

def normalize_vector(v):
    arr = np.array(v, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
        norm = np.linalg.norm(arr)
        return arr if norm == 0 else arr / norm
    if arr.ndim == 2:
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return arr / norms
    arr = arr.reshape(1, -1)
    norm = np.linalg.norm(arr)
    return arr if norm == 0 else arr / norm


def get_recommendations(user_input, user_personality=None, show_more=False, use_ai=True):
    df_unique = df.drop_duplicates(subset=["Destination"]).copy()

    trait_map = {"O":"openness","C":"conscientiousness","E":"extraversion","A":"agreeableness","N":"neuroticism"}

    # Build user vector
    user_vector = []
    for col in FEATURE_COLS:
        if col in trait_map:
            user_vector.append(float(user_personality.get(trait_map[col], 0)) if user_personality else 0.0)
        else:
            user_vector.append(float(user_input.get(col, 0)))

    user_vector = normalize_vector(np.array(user_vector).reshape(1, -1))
    dest_matrix = normalize_vector(df_unique[FEATURE_COLS].values)

    print(f"[debug] user_vector.shape={user_vector.shape}, dest_matrix.shape={dest_matrix.shape}")

    final_scores = cosine_similarity(user_vector, dest_matrix)[0]
    df_unique["final_score"] = final_scores
    sorted_df = df_unique.sort_values(by="final_score", ascending=False)

    results = sorted_df.iloc[3:13] if show_more else sorted_df.iloc[:3]

    # Try to import AI utils (graceful fallback if Groq not configured)
    ai_available = False
    if use_ai:
        try:
            from ai_utils import generate_smart_explanation
            ai_available = True
        except Exception as e:
            print(f"[ai_utils] not available: {e}")

    recommendations = []
    for _, row in results.iterrows():
        score = round(float(row["final_score"]), 3)
        destination = row["Destination"]
        state = row.get("State", row.get("Country", ""))

        # Generate explanation
        if ai_available:
            explanation = generate_smart_explanation(
                destination=destination,
                state=state,
                personality=user_personality,
                user_input=user_input,
                match_score=score
            )
        else:
            explanation = _rule_explanation(row, user_input, user_personality)

        recommendations.append({
            "destination": destination,
            "state": state,
            "final_score": score,
            "explanation": explanation,
            "image_name": destination.replace(" ", "_").lower() + ".jpg",
        })

    return recommendations


def _rule_explanation(place, user_input, personality):
    """Fallback rule-based explanation if AI is unavailable."""
    reasons = []
    for col in FEATURE_COLS:
        if col not in ["O","C","E","A","N"]:
            if user_input.get(col, 0) == 1 and place[col] == 1:
                reasons.append(col.replace("_", " "))
    if personality:
        reasons.append("your personality traits")
    if not reasons:
        return "This destination matches your overall travel preferences."
    return "Perfect for you because of: " + ", ".join(reasons[:5]) + "."