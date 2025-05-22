"""
Pagină Streamlit pentru antrenarea și evaluarea modelelor de clasificare pe un set de date preprocesat.

Permite selectarea mai multor algoritmi de machine learning (ex. CatBoost, LightGBM, XGBoost, etc.),
antrenarea acestora pe datele din `st.session_state["seturi_date"]` și afișarea rezultatelor.

Rezultatele includ scoruri de acuratețe, scor F1 și matrici de confuzie, precum și configurarea folosită pentru reproducerea rezultatelor.
"""

from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
import pandas as pd
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.tree import DecisionTreeClassifier
import streamlit as st
from xgboost import XGBClassifier

from nav_bar import nav_bar


st.set_page_config(page_title="Modele ML", page_icon="🤖", layout="wide")
nav_bar()
st.title("Modele ML")

df: pd.DataFrame = st.session_state.get("df", None)
config: dict = st.session_state.get("config", None)
seturi_date: dict = st.session_state.get("seturi_date", None)

MODELE_DISPONIBILE = {
	"CatBoost": CatBoostClassifier(verbose=0),
	"LightGBM": LGBMClassifier(),
	"XGBoost": XGBClassifier(enable_categorical=True, tree_method="hist"),
	"Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
	"Logistic Regression": LogisticRegression(max_iter=1000, solver="lbfgs"),
	"Decision Tree": DecisionTreeClassifier(random_state=42),
}


def antrenare_model(denumire_model: str, model, X_train, X_test, y_train, y_test):
	"""
	Antrenează un model de clasificare pe datele furnizate și salvează rezultatele în session state.

	Parametri:
	----------
	denumire_model : str
	    Numele modelului (util pentru afișare și tratamente speciale, ex. CatBoost).
	model : object
	    Instanța modelului ML (ex. CatBoostClassifier, XGBClassifier, etc.).
	X_train, X_test : pd.DataFrame
	    Seturile de antrenare și testare pentru caracteristici.
	y_train, y_test : pd.Series
	    Etichetele corespunzătoare seturilor de antrenare și testare.

	Ce face funcția:
	----------------
	- Antrenează modelul pe datele de antrenare.
	- Face predicții pe test set.
	- Calculează acuratețea, scorul F1 (ponderat) și matricea de confuzie.
	- Adaugă rezultatele într-o listă din `st.session_state.rezultate`.
	- Afișează un mesaj informativ dacă apare o eroare în timpul antrenării.
	"""
	try:
		if denumire_model == "CatBoost":
			cat_features = X_train.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
			model.fit(X_train, y_train, cat_features=cat_features)
		else:
			model.fit(X_train, y_train)

		y_pred = model.predict(X_test)
		acc = accuracy_score(y_test, y_pred)
		f1 = f1_score(y_test, y_pred, average="weighted")
		cm = confusion_matrix(y_test, y_pred)

		st.session_state.rezultate.append((denumire_model, acc, f1, cm))
	except Exception as e:
		st.info(f"Modelul **{denumire_model}** nu a putut fi antrenat. Eroare: {e}")


if df is not None and config is not None and seturi_date is not None:
	st.header("Alege modelele de ML")

	modele_selectate = st.multiselect(
		"Selectează modelele pe care dorești să le antrenezi:",
		list(MODELE_DISPONIBILE.keys()),
		default=["CatBoost", "LightGBM", "XGBoost"],
	)

	if st.button("🚀 Antrenează modelele"):
		st.session_state.rezultate = []

		X_train = seturi_date["X_train"]
		X_test = seturi_date["X_test"]
		y_train = seturi_date["y_train"]
		y_test = seturi_date["y_test"]

		X_train.columns = X_train.columns.str.replace("[^A-Za-z0-9_]+", "_", regex=True)
		X_test.columns = X_test.columns.str.replace("[^A-Za-z0-9_]+", "_", regex=True)

		CLASE_ORDONATE = ["Dropout", "Enrolled", "Graduate"]
		label_map = {label: idx for idx, label in enumerate(CLASE_ORDONATE)}
		inverse_label_map = {idx: label for label, idx in label_map.items()}
		y_train = y_train.map(label_map)
		y_test = y_test.map(label_map)

		for model_nume in modele_selectate:
			model = MODELE_DISPONIBILE.get(model_nume)
			if model is not None:
				with st.spinner(f"Antrenare model {model_nume}..."):
					antrenare_model(model_nume, model, X_train, X_test, y_train, y_test)

	if "rezultate" in st.session_state and st.session_state.rezultate:
		st.subheader("📊 Rezultate modele")

		leaderboard_df = pd.DataFrame(
			st.session_state.rezultate, columns=["Model", "Acuratețe", "Scor F1", "Matrice de confuzie"]
		)
		st.dataframe(leaderboard_df.iloc[:, :-1], hide_index=True, use_container_width=True)

		for denumire_model, acc, f1, cm in st.session_state.rezultate:
			st.subheader(f"{denumire_model} - Matrice de confuzie")

			clase = ["Dropout", "Enrolled", "Graduate"]
			fig = go.Figure(
				data=go.Heatmap(
					z=cm[:, ::-1],
					x=clase[::-1],
					y=clase,
					colorscale="Blues",
					text=cm[:, ::-1],
					texttemplate="%{text}",
					hovertemplate="Predicted %{x}<br>Actual %{y}<br>Count: %{z}<extra></extra>",
				)
			)

			fig.update_layout(xaxis_title="Valori prezise", yaxis_title="Valori reale", height=400, width=600)
			st.plotly_chart(fig, use_container_width=True)

		st.header("Configurație folosită")
		st.json(config)

else:
	st.warning("Te rugăm să încarci datele și să finalizezi configurarea în tab-ul anterior.")
