import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stress Analyzer", layout="wide")

USER_FILE = "users.csv"
DATA_FILE = "data.csv"

# ---------- FILE SETUP ----------
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["Username", "Password"]).to_csv(USER_FILE, index=False)

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Username","Sleep","Study","Screen","Exercise","Caffeine","Score"]).to_csv(DATA_FILE, index=False)

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- CSS ----------
st.markdown("""
<style>
body { background-color: #0f172a; }

.main-title {
    text-align: center;
    font-size: 45px;
    font-weight: bold;
    color: #a855f7;
}

.card {
    background-color: white;
    color: black;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
}

.stButton>button {
    background: linear-gradient(to right, #7c3aed, #a855f7);
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- REGISTER ----------
if st.session_state.page == "register":
    st.markdown('<div class="main-title">Register</div>', unsafe_allow_html=True)

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        users = pd.read_csv(USER_FILE)

        if u in users["Username"].values:
            st.error("User exists")
        else:
            users.loc[len(users)] = [u, p]
            users.to_csv(USER_FILE, index=False)
            st.success("Registered!")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------- LOGIN ----------
elif st.session_state.page == "login":
    st.markdown('<div class="main-title">Login</div>', unsafe_allow_html=True)

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        users = pd.read_csv(USER_FILE)

        if ((users["Username"] == u) & (users["Password"] == p)).any():
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Create Account"):
        st.session_state.page = "register"
        st.rerun()

# ---------- MAIN ----------
elif st.session_state.logged_in:

    # ---------- HOME ----------
    if st.session_state.page == "home":

        st.markdown(f'<div class="main-title">Welcome {st.session_state.username}</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="card"><h3>📊 Track Habits</h3><p>Monitor routine</p></div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card"><h3>💜 AI Analysis</h3><p>Predict stress</p></div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="card"><h3>✨ Improve Lifestyle</h3><p>Get advice</p></div>', unsafe_allow_html=True)

        if st.button("Go to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

        if st.button("Start Analysis"):
            st.session_state.page = "form"
            st.rerun()

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

    # ---------- DASHBOARD ----------
    elif st.session_state.page == "dashboard":

        st.markdown('<div class="main-title">Dashboard</div>', unsafe_allow_html=True)

        df = pd.read_csv(DATA_FILE)
        user_data = df[df["Username"] == st.session_state.username]

        if user_data.empty:
            st.warning("No data yet. Do analysis first.")
        else:
            avg = int(user_data["Score"].mean())
            mx = int(user_data["Score"].max())
            mn = int(user_data["Score"].min())

            c1, c2, c3 = st.columns(3)

            c1.markdown(f'<div class="card"><h3>Avg Stress</h3><p>{avg}</p></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="card"><h3>Max Stress</h3><p>{mx}</p></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="card"><h3>Min Stress</h3><p>{mn}</p></div>', unsafe_allow_html=True)

            st.subheader("📈 Stress Trend")
            fig, ax = plt.subplots()
            ax.plot(user_data["Score"], marker='o')
            ax.set_ylim(0,100)
            ax.grid()
            st.pyplot(fig)

            st.subheader("🧠 Insights")

            if user_data["Sleep"].mean() < 6:
                st.write("• Low sleep is increasing stress")
            if user_data["Screen"].mean() > 7:
                st.write("• High screen time detected")
            if user_data["Exercise"].mean() < 0.5:
                st.write("• Lack of exercise affects stress")

        if st.button("Back"):
            st.session_state.page = "home"
            st.rerun()

    # ---------- FORM ----------
    elif st.session_state.page == "form":

        st.markdown('<div class="main-title">Enter Details</div>', unsafe_allow_html=True)

        sleep = st.slider("Sleep", 0, 10, 6)
        study = st.slider("Study", 0, 10, 5)
        screen = st.slider("Screen", 0, 10, 6)
        exercise = st.slider("Exercise", 0, 1, 0)
        caffeine = st.slider("Caffeine", 0, 5, 2)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Analyze"):
                st.session_state.sleep = sleep
                st.session_state.study = study
                st.session_state.screen = screen
                st.session_state.exercise = exercise
                st.session_state.caffeine = caffeine

                score = ((10 - sleep)*6)+(study*4)+(screen*4)+(caffeine*5)+((1-exercise)*10)
                score = min(max(score,0),100)

                new = pd.DataFrame([[st.session_state.username,sleep,study,screen,exercise,caffeine,score]],
                                   columns=["Username","Sleep","Study","Screen","Exercise","Caffeine","Score"])

                new.to_csv(DATA_FILE, mode='a', header=False, index=False)

                st.session_state.score = score
                st.session_state.page = "result"
                st.rerun()

        with col2:
            if st.button("⬅ Back"):
                st.session_state.page = "home"
                st.rerun()

    # ---------- RESULT ----------
    elif st.session_state.page == "result":

        score = st.session_state.score

        st.markdown('<div class="main-title">Result</div>', unsafe_allow_html=True)

        st.metric("Stress Score", f"{score}/100")

        if score > 75:
            st.error("🚨 High Stress Alert!")

        st.progress(score/100)

        st.subheader("🎯 Recommendations")

        if st.session_state.sleep < 6:
            st.write("• Increase sleep")
        if st.session_state.screen > 7:
            st.write("• Reduce screen time")
        if st.session_state.exercise == 0:
            st.write("• Start exercising")

        if st.button("Back"):
            st.session_state.page = "home"
            st.rerun()