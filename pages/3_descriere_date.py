"""
Descriere detaliată a coloanelor din setul de date.

- Permite selecția unei coloane pentru analiză.
- Afișează o descriere predefinită pentru fiecare coloană (dacă există).
- Detectează automat tipul variabilei: numerică, booleană sau categorială.
- Afișează statistici specifice în funcție de tipul detectat:
    - Booleane: număr și procent de valori `True`
    - Numerice: min, max, medie, mediană, deviație standard, quartile
    - Categoriale: număr de valori unice, cele mai frecvente valori
- Suportă afișare stilizată pentru o experiență intuitivă în Streamlit.
"""

import pandas as pd
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Descriere date", page_icon="🍎", layout="wide")
nav_bar()
st.title("Descriere date")
df: pd.DataFrame = st.session_state.get("df", default=None)


def get_tip_variabila(col):
	"""
	Determină tipul unei variabile (coloană) dintr-un DataFrame Pandas.

	Parametri:
	----------
	col : pd.Series
	    Coloana a cărei tip logic se dorește determinat.

	Returnează:
	-----------
	str
	    Tipul variabilei, ca șir de caractere:
	    - "booleană" pentru coloane de tip bool
	    - "numerică" pentru coloane numerice (int, float)
	    - "categorială" pentru tipuri obiect sau categorice
	    - "-" dacă tipul nu se încadrează în cele de mai sus
	"""
	match True:
		case _ if pd.api.types.is_bool_dtype(col):
			return "booleană"
		case _ if pd.api.types.is_numeric_dtype(col):
			return "numerică"
		case _ if isinstance(col.dtype, pd.CategoricalDtype) or pd.api.types.is_object_dtype(col):
			return "categorială"
		case _:
			return "-"


descrieri_coloane = {
	"Marital status": "Starea civilă a studentului la momentul înscrierii.",
	"Application mode": "Modalitatea prin care studentul a aplicat la universitate.",
	"Application order": "Ordinea în care programul de studii a fost selectat în lista de opțiuni.",
	"Course": "Programul de studiu la care studentul este înscris.",
	"Daytime/evening attendance": "Indică dacă studentul urmează cursuri de zi sau de seară.",
	"Previous qualification": "Tipul diplomei sau calificării deținute înainte de admitere.",
	"Previous qualification (grade)": "Nota (0-200) obținută la calificarea anterioară.",
	"Country of origin": "Țara natală a studentului.",
	"Mother's qualification": "Nivelul educațional al mamei.",
	"Father's qualification": "Nivelul educațional al tatălui.",
	"Mother's occupation": "Ocupația principală a mamei.",
	"Father's occupation": "Ocupația principală a tatălui.",
	"Admission grade": "Nota de admitere a studentului în program.",
	"Displaced": "Indică dacă studentul studiază departe de domiciliul său.",
	"Educational special needs": "Indică dacă studentul are nevoi educaționale speciale.",
	"Debtor": "Indică dacă studentul are datorii financiare față de instituție.",
	"Tuition fees up to date": "Stare actuală a plății taxelor de școlarizare.",
	"Gender": "Genul studentului (masculin/feminin).",
	"Scholarship holder": "Indică dacă studentul beneficiază de bursă.",
	"Age at enrollment": "Vârsta studentului la momentul înscrierii.",
	"International": "Indică dacă studentul este internațional.",
	"Curricular units 1st sem (credited)": "Număr de credite obținute prin echivalare în primul semestru.",
	"Curricular units 1st sem (enrolled)": "Număr total de materii înscrise în primul semestru.",
	"Curricular units 1st sem (evaluations)": "Număr de evaluări efectuate în primul semestru.",
	"Curricular units 1st sem (approved)": "Număr de materii promovate în primul semestru.",
	"Curricular units 1st sem (grade)": "Media din primul semestru.",
	"Curricular units 1st sem (without evaluations)": "Număr de materii neevaluate în primul semestru.",
	"Curricular units 2nd sem (credited)": "Număr de credite obținute prin echivalare în al doilea semestru.",
	"Curricular units 2nd sem (enrolled)": "Număr total de materii înscrise în al doilea semestru.",
	"Curricular units 2nd sem (evaluations)": "Număr de evaluări efectuate în al doilea semestru.",
	"Curricular units 2nd sem (approved)": "Număr de materii promovate în al doilea semestru.",
	"Curricular units 2nd sem (grade)": "Media din al doilea semestru.",
	"Curricular units 2nd sem (without evaluations)": "Număr de materii neevaluate în al doilea semestru.",
	"Unemployment rate": "Rata șomajului la momentul înscrierii studentului.",
	"Inflation rate": "Rata inflației la momentul înscrierii.",
	"GDP": "Produsul Intern Brut în perioada înscrierii.",
	"Target": "Variabila țintă, ce indică dacă studentul a abandonat (`Dropout`), încă mai este înscris (`Enrolled`) sau a absolvit (`Graduate`).",
}

if df is not None:
	coloana_selectata = st.selectbox("Alege o coloană", df.columns)
	col_data = df[coloana_selectata]
	st.subheader(f"{coloana_selectata}")
	st.markdown("🍎 :red-background[**Descriere**] -> " + descrieri_coloane[coloana_selectata])
	tip = get_tip_variabila(col_data)
	st.markdown(f"🔮 :violet-background[**Tip**] -> Variabilă {tip}")

	if tip == "booleană":
		st.write("✅ :green-background[**Număr valori True**] -> ", col_data.sum())
		st.write("⭐ :orange-background[**Procent valori True**] -> ", round(100 * col_data.mean(), 2), "`%`")
	elif tip == "numerică":
		st.write("⬇️ :blue-background[**Valoarea minimă**] -> ", round(col_data.min(), 2))
		st.write("⬆️ :blue-background[**Valoarea maximă**] -> ", round(col_data.max(), 2))
		st.write("🌻 :orange-background[**Media**] -> ", round(col_data.mean(), 2))
		st.write("📏 :orange-background[**Deviația standard**] -> ", round(col_data.std(), 2))
		st.write("📐 :orange-background[**Mediana**] -> ", round(col_data.median(), 2))
		st.write("📊 :rainbow-background[**Quartile**]")
		st.dataframe(col_data.quantile([0.25, 0.5, 0.75]), use_container_width=False)
	elif tip == "categorială":
		st.write("🌺 :rainbow-background[**Număr de valori unice**] -> ", col_data.nunique())
		st.write("🏆 :orange-background[**Cele mai frecvente valori**]")
		st.dataframe(col_data.value_counts().head(5), use_container_width=False)
else:
	st.warning("Încarcă mai întâi un fișier CSV.")
