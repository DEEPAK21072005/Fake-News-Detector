import pandas as pd
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
nltk.download('stopwords')

def clean_text(text):
    if isinstance(text, str):  # Ensure text is not NaN
        text = re.sub(r'\W', ' ', text)  # Remove special characters
        text = text.lower()  # Convert to lowercase
        return text
    return ""

# Load datasets
try:
    fake_df = pd.read_csv("Fake.csv")
    true_df = pd.read_csv("True.csv")

    # Add labels
    fake_df["label"] = 0  # Fake News
    true_df["label"] = 1  # Real News

    # Merge & shuffle dataset
    df = pd.concat([fake_df, true_df], axis=0).sample(frac=1).reset_index(drop=True)

    # Apply text cleaning
    df["text"] = df["text"].apply(clean_text)

    # Save combined dataset
    df.to_csv("fake_news_data.csv", index=False)
    print("✅ Dataset successfully created!")
except Exception as e:
    print(f"⚠️ Error processing dataset: {e}")

