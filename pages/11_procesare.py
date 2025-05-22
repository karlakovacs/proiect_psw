"""
Interfață Streamlit pentru configurarea completă a procesului de preprocesare a datelor.

Permite alegerea strategiilor pentru tratarea outlierilor, completarea valorilor lipsă, codificarea variabilelor categoriale
(Label Encoding și One Hot Encoding), scalarea numerică și împărțirea în seturi de antrenare/testare.

Rezultatul final este salvat în `st.session_state` sub forma unui set de date pregătit pentru antrenarea modelelor ML.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, RobustScaler, StandardScaler
import streamlit as st
from streamlit_sortables import sort_items

from nav_bar import nav_bar


st.set_page_config(page_title="Procesarea datelor", page_icon="⚙️", layout="wide")
nav_bar()
st.title("Procesarea datelor")

df: pd.DataFrame = st.session_state.get("df", default=None)
if "label_sort_orders" not in st.session_state:
	st.session_state["label_sort_orders"] = {}


def tratare_outlieri_df(df: pd.DataFrame, strategie: str) -> pd.DataFrame:
	"""
	Aplică o strategie de tratare a outlierilor pe coloanele numerice dintr-un DataFrame.

	Parametri:
	----------
	df : pd.DataFrame
		Setul de date original.
	strategie : str
		Strategia aleasă pentru tratarea outlierilor. Opțiuni posibile:
		- "Eliminare rânduri cu outlieri"
		- "Înlocuire cu NaN"
		- "Transformare logaritmică"
		- "Capping (1%-99%)"
		- "Păstrare" (nu aplică nicio modificare)

	Returnează:
	-----------
	pd.DataFrame
		DataFrame-ul modificat conform strategiei selectate, fără a altera coloana 'Target'.
	"""
	df = df.copy()
	for col in df.select_dtypes(include=["float64", "int64"]).columns:
		if col == "Target":
			continue
		q1 = df[col].quantile(0.25)
		q3 = df[col].quantile(0.75)
		iqr = q3 - q1
		lower = q1 - 1.5 * iqr
		upper = q3 + 1.5 * iqr

		if strategie == "Eliminare rânduri cu outlieri":
			df = df[(df[col] >= lower) & (df[col] <= upper)]
		elif strategie == "Înlocuire cu NaN":
			df[col] = df[col].mask((df[col] < lower) | (df[col] > upper))
		elif strategie == "Transformare logaritmică":
			df[col] = np.log1p(df[col])
		elif strategie == "Capping (1%-99%)":
			lower_cap = df[col].quantile(0.01)
			upper_cap = df[col].quantile(0.99)
			df[col] = np.clip(df[col], lower_cap, upper_cap)
		elif strategie == "Păstrare":
			pass
	return df


def tratare_valori_lipsa_df(df: pd.DataFrame, strategie: str) -> pd.DataFrame:
	"""
	Tratează valorile lipsă dintr-un DataFrame conform unei strategii specificate.

	Parametri:
	----------
	df : pd.DataFrame
		DataFrame-ul original cu posibile valori lipsă.
	strategie : str
		Metoda de completare pentru coloanele numerice:
		- "Medie": înlocuiește valorile lipsă cu media coloanei.
		- "Mediană": înlocuiește valorile lipsă cu mediana coloanei.
		- "Mod": înlocuiește valorile lipsă cu valoarea modală (cea mai frecventă).

	Ce face în plus:
	----------------
	- Pentru coloanele de tip object, category sau bool, înlocuiește valorile lipsă cu moda,
	  indiferent de strategia selectată (dacă nu e coloana 'Target').

	Returnează:
	-----------
	pd.DataFrame
		O copie a DataFrame-ului original, cu valorile lipsă completate.
	"""
	df = df.copy()
	for col in df.select_dtypes(include=np.number).columns:
		if col != "Target" and df[col].isnull().any():
			if strategie == "Medie":
				df[col] = df[col].fillna(df[col].mean())
			elif strategie == "Mediană":
				df[col] = df[col].fillna(df[col].median())
			elif strategie == "Mod":
				df[col] = df[col].fillna(df[col].mode()[0])
	for col in df.select_dtypes(include=["object", "category", "bool"]).columns:
		if col != "Target" and df[col].isnull().any():
			df[col] = df[col].fillna(df[col].mode()[0])
	return df


def tratare_codificari_df(
	df: pd.DataFrame, use_one_hot: bool, label_encoding: dict, max_categorii: int = None
) -> pd.DataFrame:
	"""
	Codifică variabilele categoriale dintr-un DataFrame folosind Label Encoding și/sau One Hot Encoding.

	Parametri:
	----------
	df : pd.DataFrame
		Setul de date original.
	use_one_hot : bool
		Dacă este True, se aplică One Hot Encoding pentru variabilele categoriale care nu au fost deja codificate cu Label Encoding.
	label_encoding : dict
		Dicționar cu perechi {coloană: ordine_valori} ce specifică ordinea dorită pentru codificarea label.
	max_categorii : int, optional
		Număr maxim de categorii permis pentru aplicarea One Hot Encoding. Coloanele cu un număr mai mare de categorii vor fi ignorate.

	Returnează:
	-----------
	pd.DataFrame
		DataFrame-ul rezultat după aplicarea codificărilor. Coloana 'Target' este exclusă din orice codificare.
	"""
	df_transformed = df.copy()

	cols_to_encode = [col for col in label_encoding if col != "Target"]

	for col in cols_to_encode:
		if col in df_transformed.columns:
			encoder = LabelEncoder()
			encoder.classes_ = np.array(label_encoding[col])
			df_transformed[col] = encoder.transform(df_transformed[col])

	if use_one_hot:
		remaining_categoricals = df_transformed.select_dtypes(include="object").columns.difference(
			list(label_encoding.keys()) + ["Target"]
		)
		cols_one_hot = []
		for col in remaining_categoricals:
			if max_categorii is None or df_transformed[col].nunique() <= max_categorii:
				cols_one_hot.append(col)

		if cols_one_hot:
			df_transformed = pd.get_dummies(df_transformed, columns=cols_one_hot, drop_first=True)

	return df_transformed


def scalare_date(X: pd.DataFrame, metoda_scalare: str) -> pd.DataFrame:
	"""
	Aplică o metodă de scalare numerică asupra coloanelor numerice dintr-un DataFrame.

	Parametri:
	----------
	X : pd.DataFrame
		DataFrame-ul de intrare, conținând caracteristicile de scalat.
	metoda_scalare : str
		Metoda de scalare aleasă. Opțiuni posibile:
		- "StandardScaler": scalare standard (medie 0, deviație standard 1)
		- "MinMaxScaler": scalare între 0 și 1
		- "RobustScaler": scalare robustă față de outlieri (mediana și IQR)
		- "Niciuna": nu se aplică nicio scalare

	Returnează:
	-----------
	pd.DataFrame
		DataFrame-ul cu coloanele numerice scalate, restul coloanelor rămân neschimbate.
	"""
	if metoda_scalare == "Niciuna":
		return X
	if metoda_scalare == "StandardScaler":
		scaler = StandardScaler()
	elif metoda_scalare == "MinMaxScaler":
		scaler = MinMaxScaler()
	elif metoda_scalare == "RobustScaler":
		scaler = RobustScaler()

	X = X.copy()
	coloane_numerice = X.select_dtypes(include=["float64", "int64"]).columns
	X_scaled = scaler.fit_transform(X[coloane_numerice])
	X[coloane_numerice] = pd.DataFrame(X_scaled, columns=coloane_numerice, index=X.index)
	return X


def pregatire_date(df: pd.DataFrame, config: dict):
	"""
	Preprocesează un DataFrame pentru antrenarea modelelor de machine learning, conform configurației oferite.

	Pași realizați:
	---------------
	- Aplică o strategie de tratare a outlierilor.
	- Completează valorile lipsă pe baza unei metode specificate.
	- Codifică variabilele categoriale (Label Encoding / One Hot Encoding).
	- Scalează datele numerice (Standard, MinMax, Robust, sau niciuna).
	- Împarte datele în seturi de antrenare și testare, cu posibilitate de stratificare.
	- Conversie la tip `category` pentru coloanele obiect.
	- Resetarea indexului pentru toate seturile.

	Parametri:
	----------
	df : pd.DataFrame
		DataFrame-ul original ce conține și coloana 'Target'.
	config : dict
		Dicționar cu setările de preprocesare (strategii, codificare, scalare, split etc.).

	Returnează:
	-----------
	tuple:
		- df_final: pd.DataFrame — datele de antrenare cu 'Target' inclus.
		- X_train, X_test: pd.DataFrame — caracteristicile separate pentru antrenare și testare.
		- y_train, y_test: pd.Series — valorile țintă corespunzătoare.
	"""
	df = tratare_outlieri_df(df, config["tratare_outlieri"])
	df = tratare_valori_lipsa_df(df, config["tratare_valori_lipsa"])
	df = tratare_codificari_df(df, config["codificare_one_hot"], config["codificare_label"])

	X = df.drop("Target", axis=1)
	y = df["Target"]

	X = scalare_date(X, config["metoda_scalare"])

	stratify = y if config["stratificat"] else None
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=config["dimensiune_test"], stratify=stratify)

	for col in X_train.select_dtypes(include="object").columns:
		X_train[col] = X_train[col].astype("category")
		X_test[col] = X_test[col].astype("category")

	X_train = X_train.reset_index(drop=True)
	X_test = X_test.reset_index(drop=True)
	y_train = y_train.reset_index(drop=True)
	y_test = y_test.reset_index(drop=True)

	df_final = X_train.copy()
	df_final["Target"] = y_train

	return df_final, X_train, X_test, y_train, y_test


if df is not None:
	st.header("Tratare outlieri (numerici)")
	tratare_outlieri = st.selectbox(
		"Alege strategia de tratare a outlierilor:",
		[
			"Eliminare rânduri cu outlieri",
			"Înlocuire cu NaN",
			"Transformare logaritmică",
			"Capping (1%-99%)",
			"Păstrare",
		],
	)

	st.header("Tratare valori lipsă")
	st.info(
		"Doar pentru variabilele numerice. Variabilele categoriale și booleene vor fi completate cu valoarea modală."
	)
	tratare_valori_lipsa = st.selectbox(
		"Alege strategia de completare a valorilor lipsă:",
		["Medie", "Mediană", "Mod"],
	)

	st.header("Codificarea datelor")
	use_one_hot = st.checkbox("Folosire One Hot Encoding pentru variabilele categoriale")
	max_categorii = None
	if use_one_hot:
		max_categorii = st.slider(
			"Număr maxim de categorii pentru One Hot Encoding (coloanele cu mai multe vor fi ignorate):",
			min_value=2,
			max_value=50,
			value=10,
			step=1
		)

	use_label_encoding = st.checkbox("Folosire Label Encoding pentru variabilele categoriale ordonate")

	if use_label_encoding:
		cat_cols = df.select_dtypes(include="object").columns.tolist()
		selected_cols = st.multiselect("Selectează coloanele pentru Label Encoding", options=cat_cols)

		for col in selected_cols:
			st.markdown(f"Sortează valorile din coloana **{col}** în ordinea dorită:")
			unique_values = df[col].unique().tolist()
			sorted_values = sort_items(unique_values, direction="horizontal", key=f"sort_{col}")
			st.markdown(f"Ordine aleasă: `{sorted_values}`")
			st.session_state["label_sort_orders"][col] = sorted_values

	st.header("Scalarea datelor")
	metoda_scalare = st.selectbox(
		"Alege metoda de scalare:",
		["StandardScaler", "MinMaxScaler", "RobustScaler", "Niciuna"],
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

	if st.button("Aplicare setări", type="primary"):
		config = {
			"tratare_outlieri": tratare_outlieri,
			"tratare_valori_lipsa": tratare_valori_lipsa,
			"codificare_one_hot": use_one_hot,
			"codificare_label": st.session_state.label_sort_orders,
			"metoda_scalare": metoda_scalare,
			"dimensiune_test": dimensiune_test,
			"stratificat": stratificat,
		}

		df_final, X_train, X_test, y_train, y_test = pregatire_date(df, config)
		st.session_state.seturi_date = {"X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test}

		st.header("Date finale preprocesate")
		st.dataframe(df_final.head(20))

		st.session_state.config = config

else:
	st.warning("Încarcă mai întâi un fișier CSV.")
