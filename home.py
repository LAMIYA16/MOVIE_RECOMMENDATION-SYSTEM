import streamlit as st

def home_page():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: black;
            }
            h1 {
                color: red;
                text-align: center;
                font-size: 60px;
                font-weight: bold;
            }
            p {
                color: white;
                text-align: center;
                font-size: 20px;
            }
            .start-button {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: 20px;
            }
            .start-button button {
                background-color: red !important;
                color: white !important;
                font-size: 20px !important;
                padding: 10px 20px !important;
                border-radius: 10px !important;
                border: none !important;
            }
            .start-button button:hover {
                background-color: darkred !important;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .fade-in {
                animation: fadeIn 2s;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<h1 class="fade-in">MovieSearch</h1>', unsafe_allow_html=True)
    st.markdown('<p class="fade-in">Your ultimate destination for discovering movies, exploring genres, and reading reviews!</p>', unsafe_allow_html=True)

    if st.button("Get Started"):
        st.session_state["page"] = "login_signup"
