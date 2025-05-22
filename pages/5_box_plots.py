"""
Vizualizare interactivă a unui boxplot pentru o variabilă numerică.

Utilizatorul selectează o coloană, iar aplicația afișează distribuția și detectează outlieri.

Include interpretare bazată pe skewness, medie, mediană și IQR.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Box plots", page_icon="📦", layout="wide")
nav_bar()

st.title("Box plots pentru variabilele numerice")
df: pd.DataFrame = st.session_state.get("df", default=None)

def boxplot_si_intepretare(df: pd.DataFrame, coloana: str):
	"""
	Generează un boxplot interactiv și oferă interpretări statistice pentru o variabilă numerică.

	Parametri:
	----------
	df : pd.DataFrame
	    DataFrame-ul ce conține coloana analizată.
	coloana : str
	    Numele coloanei numerice pentru care se generează boxplot-ul și interpretarea.

	Ce face funcția:
	----------------
	- Creează un boxplot interactiv folosind Plotly, care afișează și media.
	- Calculează și afișează statisticile esențiale:
	    • Mediana, media, quartilele Q1 și Q3
	    • IQR (Interquartile Range)
	    • Numărul de outlieri (valori în afara intervalului [Q1 - 1.5*IQR, Q3 + 1.5*IQR])
	    • Forma distribuției estimată din skewness (simetrică, skewed stânga/dreapta)
	- Afișează toate informațiile în interfața Streamlit cu marcaje vizuale colorate.
	"""
	serie = df[coloana].dropna()
	mediana = serie.median()
	media = serie.mean()
	q1 = serie.quantile(0.25)
	q3 = serie.quantile(0.75)
	iqr = q3 - q1
	minim = serie.min()
	maxim = serie.max()
	skew = serie.skew()

	fig = go.Figure()
	fig.add_trace(
		go.Box(
			y=df[coloana],
			name=coloana,
			boxmean=True,
			marker=dict(color="royalblue"),
		)
	)
	fig.update_layout(
		title=f"📦 Box Plot pentru `{coloana}`",
		yaxis_title=coloana,
	)
	st.plotly_chart(fig, use_container_width=True)

	# Outlieri: sub Q1 - 1.5*IQR sau peste Q3 + 1.5*IQR
	lower_bound = q1 - 1.5 * iqr
	upper_bound = q3 + 1.5 * iqr
	outlieri = serie[(serie < lower_bound) | (serie > upper_bound)]

	# Forma distribuției
	if -0.5 < skew < 0.5:
		forma = "aproximativ simetrică"
		culoare = "green"
	elif skew <= -0.5:
		forma = "asimetrică spre stânga (negativ skewed)"
		culoare = "red"
	else:
		forma = "asimetrică spre dreapta (pozitiv skewed)"
		culoare = "orange"

	st.header("Interpretare")

	st.markdown(f":blue-background[**Mediana:**] {mediana:.2f}")
	st.markdown(f":violet-background[**Media:**] {media:.2f}")
	st.markdown(f":blue-background[**Quartile:**] Q1 = {q1:.2f}, Q3 = {q3:.2f}")
	st.markdown(f":orange-background[**IQR (Interquartile Range):**] {iqr:.2f}")
	st.markdown(f":red-background[**Outlieri detectați:**] {len(outlieri)} observații")
	st.markdown(f":{culoare}-background[**Forma distribuției:**] {forma}")


if df is not None:
	coloane_numerice = df.select_dtypes(include=['int64', 'float64']).columns
	coloana = st.selectbox("Alege o coloana", coloane_numerice)
	boxplot_si_intepretare(df, coloana)
else:
	st.warning("Încarcă mai întâi un fișier CSV.")
