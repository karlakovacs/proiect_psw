"""
Gestionează valori lipsă și duplicate într-un set de date încărcat.

Permite introducerea artificială a valorilor NaN și afișează un grafic cu cele mai afectate coloane.

Verifică și raportează rândurile duplicate, oferind opțiunea de afișare.
"""

import random

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Duplicate și valori lipsă", page_icon="🚨", layout="wide")
nav_bar()
st.title("Duplicate și valori lipsă")
df: pd.DataFrame = st.session_state.get("df", default=None)


def introducere_valori_lipsa(df: pd.DataFrame, procent_min=0.01, procent_max=0.1):
	"""
	Introduce artificial valori lipsă (NaN) într-un DataFrame într-un interval procentual specificat.

	Parametri:
	----------
	df : pd.DataFrame
	    DataFrame-ul original.
	procent_min : float, implicit 0.01
	    Procentul minim de valori lipsă ce vor fi introduse per coloană.
	procent_max : float, implicit 0.1
	    Procentul maxim de valori lipsă ce pot fi introduse per coloană.

	Returnează:
	-----------
	pd.DataFrame
	    O copie a DataFrame-ului original cu valori lipsă introduse aleatoriu (exceptând coloana 'Target').
	"""
	df_copy = df.copy()
	for col in df_copy.columns:
		if col != "Target":
			procent = random.uniform(procent_min, procent_max)
			n = int(len(df_copy) * procent)
			index_to_nan = df_copy.sample(n=n).index
			df_copy.loc[index_to_nan, col] = np.nan
	return df_copy


def plot_valori_lipsa(df: pd.DataFrame):
	"""
	Afișează un grafic cu cele mai afectate coloane de valori lipsă într-un DataFrame.

	Parametri:
	----------
	df : pd.DataFrame
	    DataFrame-ul analizat pentru identificarea valorilor lipsă.

	Ce face funcția:
	----------------
	- Calculează numărul și procentul valorilor lipsă pentru fiecare coloană.
	- Afișează un bar chart interactiv cu primele 5 coloane cu cele mai multe valori lipsă.
	- Ignoră coloanele fără valori lipsă și nu afișează nimic dacă nu există lipsuri.
	"""
	missing_vals = df.isnull().sum()
	missing_percent = (missing_vals / len(df)) * 100

	missing_df = pd.DataFrame({
		'Coloană': missing_vals.index,
		'Valori lipsă': missing_vals.values,
		'Procent': np.round(missing_percent.values, 3)
	})

	missing_df = missing_df[missing_df['Valori lipsă'] > 0]
	missing_df = missing_df.sort_values(by='Procent', ascending=False).head(5)

	if missing_df.empty:
		return

	fig = px.bar(
		missing_df,
		x='Procent',
		y='Coloană',
		color='Procent',
		color_continuous_scale='Oranges',
		title='Procentul valorilor lipsă per coloană',
		labels={'Procent': 'Procent (%)', 'Coloană': 'Coloană'},
		category_orders={'Coloană': missing_df['Coloană'].tolist()}
	)

	fig.update_layout(
		xaxis_title='Procent (%)',
		yaxis_title='Coloană',
		height=400
	)

	st.plotly_chart(fig, use_container_width=True)


if "has_nan_values" not in st.session_state:
	st.session_state.has_nan_values = False

if df is not None:
	if not st.session_state.has_nan_values:
		if st.button("Introducere valori NaN"):
			st.session_state.df = introducere_valori_lipsa(df)
			st.session_state.has_nan_values = True
			st.warning("Am introdus artificial valori lipsă în setul de date.")
	elif st.session_state.has_nan_values:
		st.warning("Am introdus artificial valori lipsă în setul de date.")

	st.subheader("📦 Cod folosit pentru a verifica valorile lipsă")
	st.code("df.isnull().sum()", language="python")

	missing = st.session_state.df.isnull().sum()
	total_missing = missing.sum()

	if total_missing == 0:
		st.success("Nu există valori lipsă.")
	else:
		st.warning(f"Există {total_missing} valori lipsă în total.")
		# st.dataframe(missing[missing > 0])
		plot_valori_lipsa(st.session_state.df)

	st.subheader("📦 Cod folosit pentru a verifica duplicatele")
	st.code("df.duplicated().sum()", language="python")

	duplicates = st.session_state.df.duplicated().sum()
	if duplicates == 0:
		st.success("Nu există rânduri duplicate.")
	else:
		st.warning(f"Există {duplicates} rânduri duplicate.")
		if st.checkbox("Afișează duplicatele"):
			st.dataframe(st.session_state.df[st.session_state.df.duplicated()])
else:
	st.warning("Încarcă mai întâi un fișier CSV.")
