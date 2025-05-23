"""
Încărcare fișier CSV în aplicația Streamlit.

- Permite utilizatorului să încarce un fișier `.csv`.
- Salvează datele în `st.session_state.df` pentru utilizare ulterioară.
- Afișează confirmare de succes sau avertisment dacă nu s-a încărcat nimic.
"""

import pandas as pd
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Încărcare fișier", page_icon="📂", layout="wide")
nav_bar()

st.title("Încărcare fișier")


def incarcare_fisier():
	"""
	Încarcă un fișier CSV în aplicația Streamlit și îl salvează în session_state.

	Ce face funcția:
	----------------
	- Deschide un selector de fișiere pentru utilizator, acceptând doar fișiere `.csv`.
	- Dacă fișierul este selectat, acesta este citit cu Pandas și salvat în `st.session_state.df`.
	- Afișează un mesaj de succes dacă fișierul a fost încărcat cu succes.
	- În caz contrar, avertizează utilizatorul să încarce un fișier.
	"""
	uploaded_file = st.file_uploader("Încarcă un fișier CSV", type=["csv"])

	if uploaded_file is not None:
		df = pd.read_csv(uploaded_file)
		st.session_state.df = df
		st.success("Datele au fost citite cu succes!")
	else:
		st.warning("Încarcă un fișier CSV.")


incarcare_fisier()
