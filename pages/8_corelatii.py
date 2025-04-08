import altair as alt
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import streamlit as st

from nav_bar import nav_bar


nav_bar()
st.title("Corelații dintre variabile")
df: pd.DataFrame = st.session_state.get("df", default=None)


def encode_categorical_columns(df, coloane_selectate):
	df_encoded = df[coloane_selectate].copy()

	for col in coloane_selectate:
		if df[col].dtype == 'object' or df[col].dtype.name == 'category':
			le = LabelEncoder()
			df_encoded[col] = le.fit_transform(df_encoded[col])
	return df_encoded


def matrice_corelatie(df, coloane_selectate):
	df_encoded = encode_categorical_columns(df, coloane_selectate)
	df_corr = df_encoded.corr()
	corr_df = df_corr.stack().reset_index()
	corr_df.columns = ['x', 'y', 'corr']

	color_scale = alt.Scale(
		domain=[-1, 0, 1],
		range=["red", "yellow", "green"]
	)

	heatmap = alt.Chart(corr_df).mark_rect().encode(
		x='x:O',
		y='y:O',
		color=alt.Color('corr:Q', scale=color_scale),
		tooltip=['x', 'y', 'corr']
	).properties(title="Matricea de corelație")

	if df_encoded.shape[1] < 10:
		text = alt.Chart(corr_df).mark_text(size=12, color='black').encode(
			x='x:O',
			y='y:O',
			text=alt.Text('corr:Q', format='.2f')
		)
		chart = heatmap + text
	else:
		chart = heatmap

	st.altair_chart(chart, use_container_width=True)


if df is not None:
	coloane_selectate = st.multiselect("Alegeți coloanele pentru matricea de corelație", df.columns)
	if st.button("Afișare matrice de corelație"):
		matrice_corelatie(df, coloane_selectate)

	st.header("Interpretare")

	st.markdown("""
			Această matrice evidențiază relațiile liniare dintre variabilele din setul de date, prin intermediul coeficientului Pearson (variază între -1 și 1):

			- :green-background[**Verde**] -> corelație pozitivă — când o variabilă crește, și cealaltă tinde să crească.
			- :orange-background[**Galben**] -> corelație slabă sau inexistentă — nu există o relație liniară clară între variabile.
			- :red-background[**Roșu**] -> corelație negativă — când o variabilă crește, cealaltă tinde să scadă.

			Pe **diagonala principală** avem întotdeauna valoarea `1`, deoarece fiecare variabilă este perfect corelată cu ea însăși.
			""")
else:
	st.warning("Încarcă mai întâi un fișier CSV.")
