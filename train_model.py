import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils import resample
from preprocessing import clean_text  # Import the cleaning function

# Load dataset
df = pd.read_csv("fake_news_data.csv")

# Separate fake and real news
fake_df = df[df["label"] == 0]
true_df = df[df["label"] == 1]

# Balance both datasets by resampling the smaller one
fake_df_balanced = resample(fake_df, replace=True, n_samples=len(true_df), random_state=42)
df_balanced = pd.concat([fake_df_balanced, true_df])

# Shuffle dataset
df_balanced = df_balanced.sample(frac=1).reset_index(drop=True)

# Clean text to improve training quality
df_balanced["text"] = df_balanced["text"].apply(clean_text)

# Convert text to TF-IDF vectors
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(df_balanced["text"])
y = df_balanced["label"]

# Split dataset into training & testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = PassiveAggressiveClassifier(max_iter=50)
model.fit(X_train, y_train)

# Evaluate accuracy
y_pred = model.predict(X_test)
print("Model Accuracy:", accuracy_score(y_test, y_pred))

# Save the trained model & vectorizer for future use
pickle.dump(model, open("fake_news_model.pkl", "wb"))
pickle.dump(vectorizer, open("tfidf_vectorizer.pkl", "wb"))

print("✅ Model training completed and saved!")
