"""
Vizualizează corelațiile dintre variabilele selectate dintr-un DataFrame.

Aplică codificare label pentru coloanele categoriale și afișează un heatmap interactiv.

Util pentru identificarea relațiilor liniare între variabile.
"""

import altair as alt
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Corelații", page_icon="🧬", layout="wide")
nav_bar()
st.title("Corelații dintre variabile")
df: pd.DataFrame = st.session_state.get("df", default=None)


def codificare_coloane_categoriale(df, coloane_selectate):
	"""
	Aplică Label Encoding pentru coloanele categoriale selectate dintr-un DataFrame.

	Parametri:
	----------
	df : pd.DataFrame
		Setul de date original.
	coloane_selectate : list of str
		Lista cu numele coloanelor ce urmează a fi codificate.

	Returnează:
	-----------
	pd.DataFrame
		Un DataFrame nou care conține doar coloanele selectate, codificate numeric.
	"""
	df_encoded = df[coloane_selectate].copy()

	for col in coloane_selectate:
		if df[col].dtype == "object" or df[col].dtype.name == "category":
			le = LabelEncoder()
			df_encoded[col] = le.fit_transform(df_encoded[col])
	return df_encoded


def matrice_corelatie(df, coloane_selectate):
	"""
	Calculează și afișează o matrice de corelație pentru coloanele categoriale selectate, codificate numeric.

	Parametri:
	----------
	df : pd.DataFrame
		Setul de date original.
	coloane_selectate : list of str
		Lista coloanelor categoriale pentru care se va calcula corelația.

	Ce face funcția:
	----------------
	- Aplică Label Encoding pe coloanele selectate.
	- Calculează coeficienții de corelație Pearson între coloanele codificate.
	- Afișează o matrice de corelație sub formă de heatmap interactiv cu Altair.
	- Dacă sunt mai puțin de 10 coloane, afișează și valorile numerice direct pe hartă.
	"""
	df_encoded = codificare_coloane_categoriale(df, coloane_selectate)
	df_corr = df_encoded.corr()
	corr_df = df_corr.stack().reset_index()
	corr_df.columns = ["x", "y", "corr"]

	color_scale = alt.Scale(domain=[-1, 0, 1], range=["red", "yellow", "green"])

	heatmap = (
		alt.Chart(corr_df)
		.mark_rect()
		.encode(x="x:O", y="y:O", color=alt.Color("corr:Q", scale=color_scale), tooltip=["x", "y", "corr"])
		.properties(title="Matricea de corelație")
	)

	if df_encoded.shape[1] < 10:
		text = (
			alt.Chart(corr_df)
			.mark_text(size=12, color="black")
			.encode(x="x:O", y="y:O", text=alt.Text("corr:Q", format=".2f"))
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
