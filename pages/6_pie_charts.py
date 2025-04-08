import pandas as pd
import plotly.express as px
import streamlit as st

from nav_bar import nav_bar


nav_bar()

st.title("Pie charts pentru variabilele categoriale")
df: pd.DataFrame = st.session_state.get("df", default=None)


def plot_pie_si_interpretare(df: pd.DataFrame, coloana: str):
	serie = df[coloana].dropna()

	fig = px.pie(
		df,
		names=coloana,
		title=f"Distribuția valorilor pentru variabila `{coloana}`",
		hole=0.3
	)
	st.plotly_chart(fig, use_container_width=True)

	frecvente = serie.value_counts(normalize=True)
	top_cat = frecvente.index[0]
	top_pct = frecvente.iloc[0] * 100
	total_cat = len(frecvente)
	rare = (frecvente < 0.05).sum()

	st.header("Interpretare")

	st.markdown(f":violet-background[**Categorie dominantă**] -> `{top_cat}` cu **{top_pct:.2f}%** din total")
	st.markdown(f":blue-background[**Număr de categorii**] -> {total_cat}")

	if top_pct > 50:
		st.markdown(":orange-background[**Distribuția este dezechilibrată**] -> O categorie domină clar.")
	elif top_pct < 30:
		st.markdown(":green-background[**Distribuția este relativ echilibrată între categorii.**]")

	if rare > 0:
		st.markdown(f":red-background[**Categorii rare**] -> Sunt {rare} categorii care au sub 5% din total.")


if df is not None:
	coloane_categoriale = df.select_dtypes(include=['object', 'category']).columns
	coloana = st.selectbox("Alege o coloană categorială", coloane_categoriale)
	plot_pie_si_interpretare(df, coloana)
else:
	st.warning("Încarcă mai întâi un fișier CSV.")
