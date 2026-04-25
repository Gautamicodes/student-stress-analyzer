import streamlit as st
import pandas as pd
import os

# ---------------- FILES ---------------- #
USER_FILE = "users.csv"
DATA_FILE = "data.csv"

# ---------------- INIT ---------------- #
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USER_FILE, index=False)

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["username", "sleep", "study", "screen", "caffeine", "exercise", "score"]).to_csv(DATA_FILE, index=False)

# ---------------- SESSION ---------------- #
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = ""

# ---------------- FUNCTIONS ---------------- #
def register_user(username, password):
    df = pd.read_csv(USER_FILE)

    username = username.strip()
    password = password.strip()

    df["username"] = df["username"].astype(str).str.strip()

    if username in df["username"].values:
        return False

    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)

    return True


def login_user(username, password):
    df = pd.read_csv(USER_FILE)

    df["username"] = df["username"].astype(str).str.strip()
    df["password"] = df["password"].astype(str).str.strip()

    username = username.strip()
    password = password.strip()

    return ((df["username"] == username) & (df["password"] == password)).any()


def save_data(username, sleep, study, screen, caffeine, exercise, score):
    df = pd.read_csv(DATA_FILE)

    new_data = pd.DataFrame([[username, sleep, study, screen, caffeine, exercise, score]],
                            columns=["username", "sleep", "study", "screen", "caffeine", "exercise", "score"])

    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


# ---------------- UI ---------------- #
st.set_page_config(page_title="Stress Analyzer", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}
h1, h2, h3 {
    color: #a855f7;
}
div.stButton > button {
    background: linear-gradient(45deg, #9333ea, #6366f1);
    color: white;
    border-radius: 10px;
}
.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ---------------- #
if st.session_state.page == "login":

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(username, password):
            st.session_state.user = username
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Create Account"):
        st.session_state.page = "register"
        st.rerun()

# ---------------- REGISTER ---------------- #
elif st.session_state.page == "register":

    st.title("Create Account")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("Registered Successfully! Now login.")
        else:
            st.error("Username already exists")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- DASHBOARD ---------------- #
elif st.session_state.page == "dashboard":

    st.title("Student Stress Analysis System")
    st.subheader(f"Welcome {st.session_state.user} 👋")

    st.markdown("""
    <div style="display:flex; gap:15px;">
        <div class="card"><h3>📊 Track Habits</h3><p>Monitor lifestyle</p></div>
        <div class="card"><h3>🧠 AI Analysis</h3><p>Predict stress</p></div>
        <div class="card"><h3>💡 Tips</h3><p>Improve health</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Enter Your Daily Data")

    sleep = st.slider("Sleep Hours", 0, 10, 6)
    study = st.slider("Study Hours", 0, 10, 5)
    screen = st.slider("Screen Time", 0, 10, 5)
    caffeine = st.slider("Caffeine Intake", 0, 5, 2)
    exercise = st.slider("Exercise (0/1)", 0, 1, 1)

    if st.button("Analyze Stress"):

        score = ((10 - sleep) * 6) + (study * 4) + (screen * 4) + (caffeine * 5) + ((1 - exercise) * 10)
        score = max(0, min(score, 100))

        # Stress Level
        if score < 30:
            level = "Low 😊"
        elif score < 70:
            level = "Moderate 😐"
        else:
            level = "High 🚨"

        st.success(f"Your Stress Score: {score}")
        st.subheader(f"Stress Level: {level}")

        st.progress(score / 100)

        # Save
        save_data(st.session_state.user, sleep, study, screen, caffeine, exercise, score)

        # Recommendations
        st.subheader("💡 Recommendations")

        if sleep < 6:
            st.write("• 😴 Increase sleep to 7–8 hours")

        if screen > 7:
            st.write("• 📱 Reduce screen time")

        if exercise == 0:
            st.write("• 🏃 Start daily exercise")

        if caffeine > 3:
            st.write("• ☕ Reduce caffeine")

        if study > 8:
            st.write("• 📚 Take breaks while studying")

        if score < 30:
            st.write("• 🎉 You are doing great!")

    st.markdown("---")

    st.subheader("📈 Stress Trend")

    df = pd.read_csv(DATA_FILE)
    user_data = df[df["username"] == st.session_state.user]

    if not user_data.empty:
        st.line_chart(user_data["score"])

    st.markdown("---")

    if st.button("Logout"):
        st.session_state.page = "login"
        st.session_state.user = ""
        st.rerun()