import streamlit as st
import joblib
import pandas as pd
import os
import re

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Spam Message Detection System",
    page_icon="🛡️",
    layout="wide"
)

# DARK CYBERSECURITY THEME
st.markdown("""
<style>
.stApp {
    background-color: #080f1c;
    color: white;
}
h1, h2, h3, p, label {
    color: #e5f3ff !important;
}
.stTextArea textarea {
    background-color: #142235;
    color: white;
    border: 1px solid #00d9a6;
}
.stTextInput input {
    background-color: #142235;
    color: white;
    border: 1px solid #00d9a6;
}
.stButton button {
    background-color: #00d9a6;
    color: #07111e;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# LOAD MODEL
@st.cache_resource
def load_model():
    return joblib.load("spam_model.pkl")

# SESSION HISTORY
if "history" not in st.session_state:
    st.session_state.history = []

# SUSPICIOUS KEYWORDS
suspicious_words = [
    "free", "win", "winner", "prize",
    "claim", "urgent", "cash", "reward",
    "lottery", "click", "offer", "voucher",
    "gift", "verify", "password", "bank"
]

# MESSAGE ANALYSIS FUNCTION
def analyze_message(message, model):

    prediction = model.predict([message])[0]

    probabilities = model.predict_proba([message])[0]
    confidence = float(max(probabilities)) * 100

    if str(prediction).lower() == "spam":
        result = "SPAM"
    else:
        result = "SAFE"

    words = re.findall(r"\b[a-zA-Z]+\b", message.lower())

    found_words = sorted(
        set(words) & set(suspicious_words)
    )

    links = re.findall(
        r"https?://\S+|www\.\S+",
        message,
        re.IGNORECASE
    )

    return {
        "Message": message,
        "Result": result,
        "Confidence": round(confidence, 2),
        "Suspicious Keywords": ", ".join(found_words) or "None",
        "Links Found": ", ".join(links) or "None"
    }

# HEADER
st.title("🛡️ Spam Message Detection System")
st.subheader("AI-Powered Cybersecurity Application")
st.caption("Python | Machine Learning | Streamlit")

# NAVIGATION
st.sidebar.title("🛡️ Navigation")

page = st.sidebar.radio(
    "Select Section",
    ["Dashboard", "About Project"]
)

# DASHBOARD
if page == "Dashboard":

    st.markdown("## 🔍 Message Scanner")

    if not os.path.exists("spam_model.pkl"):
        st.error("Model file not found. Run train_model.py first.")
        st.stop()

    model = load_model()

    # EMAIL CHECKER
    st.markdown("### 📧 Email Spam Checker")

    email_subject = st.text_input(
        "Email Subject",
        placeholder="Paste email subject here...",
        key="email_subject"
    )

    email_body = st.text_area(
        "Email Body",
        placeholder="Paste complete email content here...",
        height=220,
        key="email_body"
    )

    if st.button("📧 CHECK EMAIL"):

        email_text = (
            "Subject: " + email_subject + "\n\n" + email_body
        )

        if not email_subject.strip() and not email_body.strip():
            st.warning("Please enter the email subject or body.")

        else:
            try:
                email_result = analyze_message(email_text, model)

                if email_result["Result"] == "SPAM":
                    st.error("🚨 THIS EMAIL MAY BE SPAM!")
                else:
                    st.success("✅ THIS EMAIL IS LIKELY SAFE")

                st.metric(
                    "Model Confidence",
                    f'{email_result["Confidence"]:.2f}%'
                )

                st.write(
                    "Suspicious Keywords:",
                    email_result["Suspicious Keywords"]
                )

                if email_result["Links Found"] != "None":
                    st.warning(
                        "⚠️ Links found in this email. "
                        "Check them carefully before opening."
                    )
                    st.write("Detected Links:", email_result["Links Found"])
                else:
                    st.info("No URL detected.")

                # SAVE EMAIL SCAN IN HISTORY
                if not any(
                    item["Message"] == email_text
                    for item in st.session_state.history
                ):
                    st.session_state.history.append(email_result)

            except Exception as e:
                st.error(f"Email analysis error: {e}")

    st.divider()

    # SINGLE MESSAGE SCANNER
    st.markdown("### 📩 Single Message Scanner")

    message = st.text_area(
        "Enter one message:",
        placeholder="Type your message here...",
        key="single_message"
    )

    if st.button("SCAN SINGLE MESSAGE"):

        if not message.strip():
            st.warning("Please enter a message.")

        else:
            try:
                result = analyze_message(message, model)

                if not any(
                    item["Message"] == message
                    for item in st.session_state.history
                ):
                    st.session_state.history.append(result)

                if result["Result"] == "SPAM":
                    st.error("🚨 SPAM MESSAGE DETECTED!")
                else:
                    st.success("✅ MESSAGE IS SAFE / NOT SPAM")

                st.metric(
                    "Model Confidence",
                    f'{result["Confidence"]:.2f}%'
                )

                st.write(
                    "Suspicious Keywords:",
                    result["Suspicious Keywords"]
                )

                if result["Links Found"] != "None":
                    st.warning(
                        "⚠️ Message contains a URL. "
                        "Check it carefully before opening."
                    )
                    st.write("Detected Links:", result["Links Found"])
                else:
                    st.info("No URL detected.")

            except Exception as e:
                st.error(f"Prediction error: {e}")

    st.divider()

    # BULK MESSAGE SCANNER
    st.markdown("### 📬 Bulk Message Scanner")

    bulk_messages = st.text_area(
        "Enter multiple messages (one per line):",
        placeholder="Hello, how are you?\nCongratulations! You won a prize!",
        key="bulk_messages"
    )

    if st.button("SCAN ALL MESSAGES"):

        messages = [
            msg.strip()
            for msg in bulk_messages.splitlines()
            if msg.strip()
        ]

        if not messages:
            st.warning("Please enter at least one message.")

        else:
            try:
                bulk_results = []

                for msg in messages:
                    result = analyze_message(msg, model)
                    bulk_results.append(result)
                    st.session_state.history.append(result)

                st.markdown("### 📊 Individual Scan Results")

                results_df = pd.DataFrame(bulk_results)

                st.dataframe(
                    results_df,
                    use_container_width=True
                )

                st.success(
                    f"Successfully scanned {len(messages)} messages."
                )

            except Exception as e:
                st.error(f"Bulk scanning error: {e}")

    st.divider()

    # STATISTICS
    st.markdown("## 📊 Detection Statistics")

    history = st.session_state.history

    total = len(history)

    spam = sum(
        item["Result"] == "SPAM"
        for item in history
    )

    safe = total - spam

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Scanned", total)
    col2.metric("Spam Detected", spam)
    col3.metric("Safe Messages", safe)

    # PIE CHART
    if total > 0:

        st.markdown("### 📈 Spam vs Safe Analysis")

        chart_data = pd.DataFrame({
            "Type": ["Spam", "Safe"],
            "Count": [spam, safe]
        })

        st.vega_lite_chart(
            chart_data,
            {
                "mark": {
                    "type": "arc",
                    "innerRadius": 50
                },
                "encoding": {
                    "theta": {
                        "field": "Count",
                        "type": "quantitative"
                    },
                    "color": {
                        "field": "Type",
                        "type": "nominal"
                    },
                    "tooltip": [
                        {"field": "Type"},
                        {"field": "Count"}
                    ]
                }
            },
            use_container_width=True
        )

    st.divider()

    # MESSAGE HISTORY
    st.markdown("## 📜 Message History")

    if history:

        history_df = pd.DataFrame(history)

        st.dataframe(
            history_df,
            use_container_width=True
        )

        # DOWNLOAD REPORT
        csv_data = history_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Scan Report (CSV)",
            data=csv_data,
            file_name="spam_detection_report.csv",
            mime="text/csv"
        )

        # CLEAR HISTORY
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

    else:
        st.info("No messages scanned yet.")

# ABOUT PROJECT
else:

    st.markdown("## 📖 About This Project")

    st.write("""
    Spam Message Detection System is a
    machine learning based cybersecurity project.

    It classifies messages into Spam and Safe categories.

    ### Technologies Used

    - Python
    - Streamlit
    - Pandas
    - Scikit-learn
    - TF-IDF Vectorizer
    - Multinomial Naive Bayes
    - Joblib

    ### Main Features

    - Email Spam Checker
    - Email Subject and Body Analysis
    - Single Message Scanning
    - Bulk Message Scanning
    - Confidence Score
    - Suspicious Keyword Analysis
    - URL Detection
    - Detection Statistics
    - CSV Report Download
    - Message History
    """)

    st.info(
        "This application helps identify potentially "
        "unwanted and suspicious messages. Its predictions "
        "are not a guarantee that an email is safe."
    )  