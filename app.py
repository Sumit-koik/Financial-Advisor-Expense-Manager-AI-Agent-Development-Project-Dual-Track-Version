import streamlit as st
import pandas as pd
import json
import pytesseract
from PIL import Image
import re
import matplotlib.pyplot as plt

def load_expenses():
    try:
        with open("expenses.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_expenses(data):
    with open("expenses.json", "w") as f:
        json.dump(data, f, indent=4)

def extract_amount(text):
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else 0

def categorize_expense(text):
    text = text.lower()
    if "zomato" in text or "dominos" in text:
        return "Food"
    elif "uber" in text:
        return "Transport"
    elif "amazon" in text:
        return "Shopping"
    else:
        return "Other"

def smart_advice(total, income):
    if total > income:
        return " You are overspending! Reduce expenses immediately."
    elif total > income * 0.7:
        return "Spending is high. Try to control unnecessary expenses."
    elif total < income * 0.3:
        return " Great! You are saving well."
    else:
        return " Your spending is balanced."


data = load_expenses()
df = pd.DataFrame(data)


st.set_page_config(page_title="Finance AI", layout="wide")

st.markdown(" Smart AI Financial Advisor")
st.caption("Track • Analyze • Save Money")

st.sidebar.title(" Menu")
option = st.sidebar.selectbox("Select", ["Chatbot", "Dashboard", "Upload"])


if option == "Chatbot":
    st.subheader(" Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    
    if st.button(" Clear Chat"):
        st.session_state.messages = []

    income = st.number_input("Enter your monthly income:", value=20000)

    user_input = st.text_input("Ask your question:")

    if user_input and user_input.strip() != "":
        total = df["amount"].sum() if not df.empty else 0
        user_input_lower = user_input.lower()

        if "total" in user_input_lower:
            response = f"Total expense is ₹{total}"

        elif "advice" in user_input_lower or "advise" in user_input_lower:
            response = smart_advice(total, income)

        elif "saving" in user_input_lower or "savings" in user_input_lower:
            savings = income - total
            response = f" Your estimated savings: ₹{savings}"

        elif "food" in user_input_lower:
            response = " Reduce outside food spending"

        elif "hello" in user_input_lower:
            response = " Hello! I am your AI Financial Assistant"

        else:
            response = "Ask about expense, savings, or advice"

        st.session_state.messages.append(("You", user_input))
        st.session_state.messages.append(("AI", response))

    for sender, msg in st.session_state.messages:
        st.write(f"**{sender}:** {msg}")

elif option == "Dashboard":
    st.subheader(" Dashboard")

    if not df.empty:

        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(df["category"].unique())
        )

        if category_filter != "All":
            df = df[df["category"] == category_filter]

        category_summary = df.groupby("category")["amount"].sum()

        st.bar_chart(category_summary)

        total = df["amount"].sum()
        st.metric("Total Spending", f"₹{total}")

        prediction = int(total * 1.1)
        st.info(f"Next month prediction: ₹{prediction}")

        if total > 20000:
            st.error("You are overspending!")
        elif total > 15000:
            st.warning(" Near budget limit!")
        else:
            st.success("Spending is healthy")

        fig, ax = plt.subplots()
        category_summary.plot.pie(autopct='%1.1f%%', ax=ax)
        ax.set_ylabel("")
        st.pyplot(fig)

        st.subheader("📋 Recent Expenses")
        st.dataframe(df.tail(5))

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Report",
            data=csv,
            file_name="expenses.csv",
            mime="text/csv"
        )

    else:
        st.warning("No data available. Upload expenses first.")

elif option == "Upload":
    st.subheader("📤 Upload Receipt")

    file = st.file_uploader("Upload receipt", type=["png", "jpg", "jpeg"])

    if file:
        image = Image.open(file)
        st.image(image)

        text = pytesseract.image_to_string(image)
        st.write(" Extracted Text:", text)

        category = categorize_expense(text)
        amount = extract_amount(text)

        st.write(" Category:", category)
        st.write("Amount:", amount)

        expense = {
            "amount": amount,
            "category": category,
            "description": text
        }

        data = load_expenses()
        data.append(expense)
        save_expenses(data)

        st.success(" Expense saved!")
