import pandas as pd
import streamlit as st

from nav_bar import nav_bar


nav_bar()
st.title("Configurare preprocesare și algoritmi")

df: pd.DataFrame = st.session_state.get("df", default=None)

if df is not None:
	st.header("Tratare outlieri (numerici)")
	tratare_outlieri = st.selectbox(
		"Alege strategia de tratare a outlierilor:",
		["Eliminare rânduri cu outlieri", "Înlocuire cu NaN", "Transformare logaritmică", "Capping (1%-99%)",
		 "Păstrare"]
	)

	st.header("Tratare valori lipsă")
	st.info("Doar pentru variabilele numerice. Variabilele categoriale și booleene vor fi imputate cu valoarea modală.")
	tratare_valori_lipsa = st.selectbox(
		"Alege strategia de completare a valorilor lipsă:",
		["Medie", "Mediană", "Mod", "KNN", "Interpolare"]
	)

	st.header("Scalarea datelor")
	metoda_scalare = st.selectbox(
		"Alege metoda de scalare:",
		["StandardScaler", "MinMaxScaler", "RobustScaler", "Niciuna"]
	)

	st.header("Împărțirea în seturile de antrenare și testare")
	dimensiune_test = st.slider(
		"Alege procentajul pentru setul de testare:",
		min_value=0.1,
		max_value=0.4,
		step=0.1,
		value=0.2,
	)
	stratificat = st.checkbox("Împărțire stratificată")

	st.header("Algoritmii ML")
	algoritmi = st.multiselect(
		"Alege algoritmii:",
		["CatBoost", "LightGBM", "XGBoost"]
	)

	st.session_state.config = {
		"tratare_valori_lipsa": tratare_valori_lipsa,
		"tratare_outlieri": tratare_outlieri,
		"metoda_scalare": metoda_scalare,
		"dimensiune_test": dimensiune_test,
		"stratificat": stratificat,
		"algoritmi": algoritmi
	}

else:
	st.warning("Încarcă mai întâi un fișier CSV.")
