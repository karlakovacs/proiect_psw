"""
Vizualizare date în aplicația Streamlit.

- Afișează un număr selectabil de rânduri din datele încărcate.
- Aplică stilizare condiționată pe baza valorilor din coloana "Target":
	- Graduate → verde
	- Enrolled → albastru
	- Dropout → roșu
- Culorile sunt ajustate în funcție de tema activă (light/dark) detectată automat.
- Utilizează librăria `streamlit_theme` pentru a identifica tema curentă.
"""

import pandas as pd
import streamlit as st
from streamlit_theme import st_theme

from nav_bar import nav_bar


st.set_page_config(page_title="Vizualizare date", page_icon="🔍", layout="wide")
nav_bar()

st.title("Vizualizare date")
df: pd.DataFrame = st.session_state.get("df", default=None)

def colorare_randuri(rand):
	"""
	Aplică stilizare condiționată pentru un rând dintr-un DataFrame, în funcție de valoarea din coloana 'Target'.

	Parametri:
	----------
	rand : pd.Series
	    Rândul din DataFrame care va fi stilizat.

	Returnează:
	-----------
	list of str
	    O listă de stiluri CSS aplicabile fiecărei celule din rând, colorate în funcție de valoarea 'Target' și de tema activă (light/dark):
	    - Graduate → verde
	    - Enrolled → albastru
	    - Dropout → roșu
	"""
	if theme == "light":
		culori = {
			"Graduate": "#ccffcc",
			"Enrolled": "#cce5ff",
			"Dropout": "#ffcccc"
		}
	else:
		culori = {
			"Graduate": "#2e7d32",
			"Enrolled": "#1565c0",
			"Dropout": "#b71c1c"
		}
	color = culori.get(rand["Target"], "white")
	return [f"background-color: {color}; color: white"
			if theme == "Dark"
			else f"background-color: {color}"] * len(rand)


if df is not None:
	nr_randuri = st.slider("Alegeți câte rânduri doriți să vedeți", 1, df.shape[0], 5)

	theme = None
	st_theme_object = st_theme()
	if st_theme_object is not None:
		theme = st_theme_object["base"]

	if theme is not None:
		df_styled = df.head(nr_randuri).style.apply(colorare_randuri, axis=1)
		st.write(df_styled)
else:
	st.warning("Încarcă mai întâi un fișier CSV.")
