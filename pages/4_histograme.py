import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nav_bar import nav_bar


nav_bar()

st.title("Histograme pentru variabilele numerice")
df: pd.DataFrame = st.session_state.get("df", default=None)


def histograma_si_interpretare(df: pd.DataFrame, coloana: str, num_bins: int):
	serie = df[coloana].dropna()

	# 1. Histograma (NumPy)
	counts, bin_edges = np.histogram(serie, bins=num_bins)
	bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

	# 2. Plot (Plotly)
	fig = go.Figure()
	fig.add_trace(
		go.Bar(
			x=bin_centers,
			y=counts,
			name=coloana
		)
	)
	fig.update_layout(
		title=f"Histograma pentru `{coloana}`",
		xaxis_title=coloana,
		yaxis_title="Frecvență"
	)
	st.plotly_chart(fig, use_container_width=True)

	# 3. Interpretare
	skewness = serie.skew()
	media = serie.mean()
	mediana = serie.median()
	std = serie.std()
	minim = serie.min()
	maxim = serie.max()
	mod_bin = bin_centers[np.argmax(counts)]
	max_count = counts.max()

	if -0.5 < skewness < 0.5:
		forma = "aproximativ simetrică (posibil normală)"
	elif skewness <= -0.5:
		forma = "asimetrică spre stânga (negativ skewed)"
	else:
		forma = "asimetrică spre dreapta (pozitiv skewed)"

	frecvente_egale = np.allclose(counts, counts[0], rtol=0.2)
	uniform = "Distribuția pare relativ uniformă." if frecvente_egale else ""

	dispersie = "mică" if std < (maxim - minim) / 6 else "ridicată"

	total_obs = counts.sum()
	outlieri = ""

	stanga = counts[0] / total_obs
	dreapta = counts[-1] / total_obs

	if stanga < 0.05 and dreapta < 0.05:
		outlieri = "Există câțiva :rainbow-background[**outlieri**] în ambele capete ale distribuției."
	elif stanga < 0.05:
		outlieri = "Există :rainbow-background[**outlieri**] în partea stângă a distribuției (valori mici)."
	elif dreapta < 0.05:
		outlieri = "Există :rainbow-background[**outlieri**] în partea dreaptă a distribuției (valori mari)."

	frecvente = np.sum(counts >= 0.9 * max_count)
	moduri = ""
	if frecvente >= 3:
		moduri = "Distribuția pare a fi multimodală – adică are mai multe valori frecvente."

	st.markdown("### Interpretare")
	st.markdown(f":red-background[**Distribuția variabilei**] -> {forma}.")
	st.markdown(
		f":blue-background[**Binul cu frecvență maximă**] -> centrat pe **{mod_bin:.2f}**, cu **{max_count}** observații.")
	st.markdown(f":violet-background[**Media**] -> {media:.2f}")
	st.markdown(f":violet-background[**Mediana**] -> {mediana:.2f}")
	st.markdown(f":violet-background[**Interval**] -> {minim:.2f} – {maxim:.2f}")
	st.markdown(f":green-background[**Deviația standard**] -> {std:.2f} -> dispersie **{dispersie}**")

	if uniform:
		st.markdown(f"{uniform}")
	if moduri:
		st.markdown(f"{moduri}")
	if outlieri:
		st.markdown(f"{outlieri}")


if df is not None:
	coloane_numerice = df.select_dtypes(include=['int64', 'float64']).columns
	coloana = st.selectbox("Alege o coloana numerica", coloane_numerice)
	num_bins = st.slider(f"Alege numărul de binuri", min_value=5, max_value=30, value=15)
	histograma_si_interpretare(df, coloana, num_bins)
else:
	st.warning("Încarcă mai întâi un fișier CSV.")
