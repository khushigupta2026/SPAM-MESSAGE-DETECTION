import joblib

# Load trained model
model = joblib.load("spam_model.pkl")

print("==============================")
print("   SPAM MESSAGE DETECTOR")
print("==============================")

while True:

    message = input("\nEnter your message: ")

    if message.lower() == "exit":
        print("Thank you for using our system!")
        break

    prediction = model.predict([message])

    if prediction[0] == "spam":
        print("Result: SPAM MESSAGE")

    else:
        print("Result: NOT SPAM")