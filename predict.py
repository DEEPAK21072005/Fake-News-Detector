import pickle
from preprocessing import clean_text

# Load saved model & vectorizer
model = pickle.load(open("fake_news_model.pkl", "rb"))
vectorizer = pickle.load(open("tfidf_vectorizer.pkl", "rb"))

def predict_news(news_text):
    processed_text = clean_text(news_text)
    transformed_text = vectorizer.transform([processed_text])
    prediction = model.predict(transformed_text)
    return "Fake News" if prediction[0] == 0 else "Real News"

# Example Test
news_sample = "Government announces new policies for economic growth."
print("Prediction:", predict_news(news_sample))
