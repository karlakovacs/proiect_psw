"""
Vizualizează distribuția valorilor unei variabile categoriale în funcție de clasele din `Target`.

Folosește un stacked bar chart pentru cele mai frecvente 5 valori din coloana selectată.

Include și explicații pas cu pas pentru procesul de agregare și afișare.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Stacked bar charts", page_icon="📚", layout="wide")
nav_bar()
st.title("Stacked bar charts - agregări în Pandas")
df: pd.DataFrame = st.session_state.get("df", default=None)


def stacked_bar_chart(df: pd.DataFrame, coloana: str):
	"""
	Creează un stacked bar chart pentru variabila selectată și distribuția claselor din coloana 'Target'.

	Parametri:
	----------
	df : pd.DataFrame
		Setul de date ce conține coloana analizată și coloana țintă 'Target'.
	coloana : str
		Numele coloanei categoriale pentru care se analizează distribuția claselor.

	Ce face funcția:
	----------------
	- Selectează cele mai frecvente 5 valori din coloana dată.
	- Calculează distribuția clasei 'Target' pentru fiecare dintre aceste valori.
	- Afișează o diagramă bară stivuită (stacked bar chart) interactivă cu Plotly.
	"""

	top_values = df[coloana].value_counts().head(5).index

	df_top = df[df[coloana].isin(top_values)]

	grouped = df_top.groupby([coloana, "Target"]).size().reset_index(name="count")

	totals = grouped.groupby(coloana)["count"].sum().reset_index(name="total_count")
	grouped = grouped.merge(totals, on=coloana)

	grouped = grouped.sort_values(by="total_count", ascending=False)

	grouped[coloana] = pd.Categorical(grouped[coloana], categories=grouped[coloana].unique(), ordered=True)

	fig = px.bar(
		grouped,
		x=coloana,
		y="count",
		color="Target",
		barmode="stack",
		title=f"Distribuția claselor din `Target` pentru cele mai frecvente valori din `{coloana}`"
	)

	st.plotly_chart(fig, use_container_width=True)


if df is not None:
	coloane_categoriale = df.select_dtypes(include=['object', 'category']).columns
	coloana = st.selectbox("Alege o coloană categorială", coloane_categoriale)
	stacked_bar_chart(df, coloana)

	st.header("Explicații")

	st.markdown("""
	1. **Selecția valorilor cele mai frecvente din variabila categorică**  
	   Am păstrat doar **primele 5 valori cele mai frecvente** din coloana aleasă (indiferent de clasa `Target`), astfel încât graficul să fie clar și concentrat pe cele mai reprezentative cazuri.
		""")

	st.code("top_values = df[coloana].value_counts().head(5).index", language="python")

	st.markdown("""
	2. **Filtrarea datasetului**  
	   Am păstrat doar rândurile din DataFrame unde valoarea din coloană este una dintre cele 5 selectate anterior.
		""")

	st.code("df_top = df[df[coloana].isin(top_values)]", language="python")

	st.markdown("""
	3. **Gruparea și agregarea**  
	   Am grupat datele după combinația `valoare_coloana + Target` și am numărat câte apariții are fiecare combinație (folosind `groupby().size()`).
		""")

	st.code("""grouped = df_top.groupby([coloana, "Target"]).size().reset_index(name="count"))""",
			language="python")

	st.markdown("""
	4. **Calcularea totalului per categorie**  
	   Pentru a putea sorta barele în funcție de câte valori are fiecare categorie în total (pe toate clasele de `Target`), am agregat suma per categorie.
		""")

	st.code("""
	totals = grouped.groupby(coloana)["count"].sum().reset_index(name="total_count")
	grouped = grouped.merge(totals, on=coloana)
	""", language="python")

	st.markdown("""
	5. **Sortarea**  
	   Am sortat datele în funcție de numărul total de observații per categorie și am forțat ordinea pe axa X să reflecte această sortare.
		""")

	st.code("""
	grouped = grouped.sort_values(by="total_count", ascending=False)
	grouped[coloana] = pd.Categorical(grouped[coloana],
									  categories=grouped[coloana].unique(),
									  ordered=True)
	""", language="python")

	st.markdown("""
	6. **Plotarea**  
	   În final, am folosit `plotly.express.bar` cu `barmode="stack"` pentru a vedea distribuția pe clase.
		""")

else:
	st.warning("Încarcă mai întâi un fișier CSV.")
