import pandas as pd
import streamlit as st
from streamlit_theme import st_theme

from nav_bar import nav_bar


nav_bar()

st.title("Vizualizare date")
df: pd.DataFrame = st.session_state.get("df", default=None)

def colorare_randuri(rand):
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
