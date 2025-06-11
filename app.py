from flask import Flask, request, jsonify
import gzip
import pickle
from preprocessing import clean_text

# Load compressed model & vectorizer
with gzip.open("fake_news_model.pkl.gz", "rb") as f:
    model = pickle.load(f)

with open("tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    news_text = data.get("news_text", "")

    if not news_text:
        return jsonify({"error": "No news text provided!"}), 400
    
    processed_text = clean_text(news_text)
    transformed_text = vectorizer.transform([processed_text])
    prediction = model.predict(transformed_text)

    result = "Fake News" if prediction[0] == 0 else "Real News"
    return jsonify({"prediction": result})

if __name__ == '__main__':
    app.run(debug=True)
