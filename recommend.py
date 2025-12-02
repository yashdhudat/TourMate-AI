import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
#  LOAD FINAL DATASET
# -------------------------------
df = pd.read_csv("data/destination_vectors.csv")

# -------------------------------
#  FINAL FEATURE LIST (Matches CSV EXACTLY)
# -------------------------------
FEATURE_COLS = [
    "Climate_Warm","Climate_Cold","Climate_Moderate",
    "Budget_Low","Budget_Medium","Budget_High",
    "Solo","Couple","Family","Group",
    "Beaches","Culture","Food","Nature","Nightlife",
    "Relaxation","Shopping","Spiritual","Adventure",
    "Sightseeing","Trekking","History","Photography",
    "Safari","O","C","E","A","N"
]

# -------------------------------
# SAFETY NORMALIZATION (shape-aware)
# -------------------------------
def normalize_vector(v):
    """
    Accepts either:
      - 1D array-like => returns shape (1, n_features) normalized
      - 2D array-like (n_rows, n_features) => returns same shape with each row L2-normalized
    """
    arr = np.array(v, dtype=float)

    # 1D -> treat as single vector
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return arr
        return arr / norm

    # 2D -> normalize each row independently
    if arr.ndim == 2:
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        # avoid divide-by-zero: set zero norms to 1 (so zero rows remain zero)
        norms[norms == 0] = 1.0
        return arr / norms

    # fallback: flatten and normalize
    arr = arr.reshape(1, -1)
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr
    return arr / norm


# -------------------------------
#  MAIN RECOMMENDATION FUNCTION
# -------------------------------
def get_recommendations(user_input, user_personality=None, show_more=False):

    df_unique = df.drop_duplicates(subset=["Destination"]).copy()

    # Map letters to full personality trait names (as used in app.py)
    trait_map = {
        "O": "openness",
        "C": "conscientiousness",
        "E": "extraversion",
        "A": "agreeableness",
        "N": "neuroticism"
    }

    # ---------------------------
    # BUILD USER VECTOR (len(FEATURE_COLS) features)
    # ---------------------------
    user_vector = []
    for col in FEATURE_COLS:
        if col in trait_map:
            trait_name = trait_map[col]
            user_vector.append(float(user_personality.get(trait_name, 0)) if user_personality else 0.0)
        else:
            user_vector.append(float(user_input.get(col, 0)))

    user_vector = np.array(user_vector).reshape(1, -1)
    user_vector = normalize_vector(user_vector)   # shape (1, n_features)

    # ---------------------------
    # DESTINATION MATRIX
    # ---------------------------
    dest_matrix = df_unique[FEATURE_COLS].values    # shape (n_dest, n_features)
    dest_matrix = normalize_vector(dest_matrix)     # shape (n_dest, n_features)

    # Debug: print shapes so you can verify in Flask console
    print(f"[debug] user_vector.shape={user_vector.shape}, dest_matrix.shape={dest_matrix.shape}")

    # ---------------------------
    # COSINE SIMILARITY
    # ---------------------------
    final_scores = cosine_similarity(user_vector, dest_matrix)[0]
    df_unique["final_score"] = final_scores

    # ---------------------------
    # SORT & SELECT RESULTS
    # ---------------------------
    sorted_df = df_unique.sort_values(by="final_score", ascending=False)

    if show_more:
        results = sorted_df.iloc[3:13]  # Next 10
    else:
        results = sorted_df.iloc[:3]    # Top 3

    # ---------------------------
    # FORMAT OUTPUT
    # ---------------------------
    recommendations = []
    for _, row in results.iterrows():
        recommendations.append({
            "destination": row["Destination"],
            "state": row.get("State", row.get("Country", "")),
            "final_score": round(float(row["final_score"]), 3),
            "explanation": generate_explanation(row, user_input, user_personality),
            "image_name": row["Destination"].replace(" ", "_").lower() + ".jpg",
        })
    return recommendations


# -------------------------------
#  EXPLANATION GENERATOR
# -------------------------------
def generate_explanation(place, user_input, personality):

    reasons = []

    # Match-selected activities/preferences
    for col in FEATURE_COLS:
        if col not in ["O","C","E","A","N"]:
            if user_input.get(col, 0) == 1 and place[col] == 1:
                reasons.append(col)

    # Personality
    if personality:
        reasons.append("Matches your personality traits")

    if not reasons:
        return "This destination matches your overall preferences."

    return "This place suits you because: " + ", ".join(reasons[:5])
