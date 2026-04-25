import streamlit as st
import pandas as pd
import os

# ---------------- FILES ---------------- #
USER_FILE = "users.csv"
DATA_FILE = "data.csv"

# ---------------- SAFE LOAD ---------------- #
def load_users():
    if not os.path.exists(USER_FILE):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USER_FILE, index=False)
        return df

    df = pd.read_csv(USER_FILE)
    df.columns = [col.strip().lower() for col in df.columns]

    if "username" not in df.columns or "password" not in df.columns:
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USER_FILE, index=False)

    return df


def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["username","sleep","study","screen","caffeine","exercise","score"])
        df.to_csv(DATA_FILE, index=False)
        return df

    df = pd.read_csv(DATA_FILE)
    df.columns = [col.strip().lower() for col in df.columns]
    return df

# ---------------- SESSION ---------------- #
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = ""

# ---------------- FUNCTIONS ---------------- #
def register_user(username, password):
    df = load_users()
    username = username.strip()
    password = password.strip()

    df["username"] = df["username"].astype(str).str.strip()

    if username in df["username"].values:
        return False

    new = pd.DataFrame([[username, password]], columns=["username","password"])
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(USER_FILE, index=False)
    return True


def login_user(username, password):
    df = load_users()

    df["username"] = df["username"].astype(str).str.strip()
    df["password"] = df["password"].astype(str).str.strip()

    return ((df["username"] == username.strip()) &
            (df["password"] == password.strip())).any()


def save_data(user, sleep, study, screen, caffeine, exercise, score):
    df = load_data()
    new = pd.DataFrame([[user,sleep,study,screen,caffeine,exercise,score]],
                       columns=df.columns)
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ---------------- UI STYLE ---------------- #
st.set_page_config(page_title="Stress Analyzer", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f172a,#020617);
    color:white;
}
.card {
    background:#1e293b;
    padding:20px;
    border-radius:15px;
    text-align:center;
}
div.stButton > button {
    background:linear-gradient(45deg,#9333ea,#6366f1);
    color:white;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ---------------- #
if st.session_state.page == "login":
    st.title("Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(u,p):
            st.session_state.user = u
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

    u = st.text_input("New Username")
    p = st.text_input("New Password", type="password")

    if st.button("Register"):
        if register_user(u,p):
            st.success("Registered! Go to login.")
        else:
            st.error("User exists")

    if st.button("Back"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- DASHBOARD ---------------- #
elif st.session_state.page == "dashboard":

    st.title("Welcome " + st.session_state.user)

    # -------- CARDS -------- #
    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'>📊 Track Habits<br>Monitor routine</div>",unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'>💜 AI Analysis<br>Predict stress</div>",unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'>✨ Improve Lifestyle<br>Get advice</div>",unsafe_allow_html=True)

    st.markdown("---")

    # -------- INPUT -------- #
    sleep = st.slider("Sleep Hours",0,10,6)
    study = st.slider("Study Hours",0,10,5)
    screen = st.slider("Screen Time",0,10,5)
    caffeine = st.slider("Caffeine",0,5,2)
    exercise = st.slider("Exercise (0/1)",0,1,1)

    # -------- ANALYSIS -------- #
    if st.button("Analyze"):

        score = ((10-sleep)*6)+(study*4)+(screen*4)+(caffeine*5)+((1-exercise)*10)
        score = max(0,min(score,100))

        if score < 30:
            level="Low 😊"
        elif score < 70:
            level="Moderate 😐"
        else:
            level="High 🚨"

        st.success(f"Score: {score}")
        st.subheader(f"Stress Level: {level}")
        st.progress(score/100)

        save_data(st.session_state.user,sleep,study,screen,caffeine,exercise,score)

        # -------- STRONG RECOMMENDATIONS -------- #
        st.subheader("💡 Recommendations")

        if score > 70:
            st.error("⚠ High stress detected! Take immediate rest & reduce workload.")
        if sleep < 6:
            st.warning("😴 Sleep more (7-8 hrs needed)")
        if screen > 6:
            st.warning("📱 Reduce screen exposure")
        if exercise == 0:
            st.warning("🏃 Start physical activity")
        if caffeine > 3:
            st.warning("☕ Reduce caffeine intake")

        if score < 30:
            st.success("🎉 Excellent lifestyle! Keep going!")

    st.markdown("---")

    # -------- HISTORY -------- #
    st.subheader("📈 Stress History")

    df = load_data()
    user_df = df[df["username"] == st.session_state.user]

    if not user_df.empty:
        st.line_chart(user_df["score"])
        st.dataframe(user_df.tail(5))  # last 5 records

    if st.button("Logout"):
        st.session_state.page="login"
        st.session_state.user=""
        st.rerun()