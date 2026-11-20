import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
import joblib

# Load dataset
data = pd.read_csv("dataset.csv")

# Separate messages and labels
X = data["message"]
y = data["label"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# Create model
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB())
])

# Train model
model.fit(X_train, y_train)

# Test model
predictions = model.predict(X_test)

# Accuracy
print("Model Accuracy:", accuracy_score(y_test, predictions) * 100, "%")

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Confusion Matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions, labels=["ham", "spam"]))

# Save model
joblib.dump(model, "spam_model.pkl")

print("\nModel trained successfully!")