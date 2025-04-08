import pandas as pd
import streamlit as st

from nav_bar import nav_bar


nav_bar()

st.title("Încărcare fișier")

uploaded_file = st.file_uploader("Încarcă un fișier CSV", type=["csv"])

if uploaded_file is not None:
	df = pd.read_csv(uploaded_file)
	st.session_state.df = df
	st.success("Datele au fost citite cu succes!")
else:
	st.warning("Încarcă un fișier CSV.")
