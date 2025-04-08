from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
import streamlit as st
from xgboost import XGBClassifier

from nav_bar import nav_bar


nav_bar()
st.title("Modele ML")

df: pd.DataFrame = st.session_state.get("df", default=None)
config: dict = st.session_state.get("config", default=None)


def tratare_outlieri(df: pd.DataFrame, strategie: str) -> pd.DataFrame:
	df = df.copy()

	for col in df.select_dtypes(include=['float64', 'int64']).columns:
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
			df[col] = np.where(df[col] < lower_cap, lower_cap,
							   np.where(df[col] > upper_cap, upper_cap, df[col]))

		elif strategie == "Păstrare":
			pass

	return df


def tratare_valori_lipsa(df: pd.DataFrame, strategie: str) -> pd.DataFrame:
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


def pregatire_date(df: pd.DataFrame, strategie_scalare: str, dimensiune_test: float, stratificat: bool):
	X = df.drop("Target", axis=1)
	y = df["Target"]

	clase = {
		"Dropout": 0,
		"Enrolled": 1,
		"Graduate": 2
	}

	y = y.map(clase)

	scaler = None

	if strategie_scalare == "StandardScaler":
		scaler = StandardScaler()

	elif strategie_scalare == "MinMaxScaler":
		scaler = MinMaxScaler()

	elif strategie_scalare == "RobustScaler":
		scaler = RobustScaler()

	if scaler is not None:
		coloane_numerice = X.select_dtypes(include=['float64', 'int64']).columns
		X_scaled = scaler.fit_transform(X[coloane_numerice])
		X_scaled_df = pd.DataFrame(X_scaled, columns=coloane_numerice, index=X.index)
		X[coloane_numerice] = X_scaled_df

	X_train, X_test, y_train, y_test = train_test_split(
		X, y, test_size=dimensiune_test, stratify=y if stratificat else None, random_state=42)
	return X_train, X_test, y_train, y_test


def antrenare_model(denumire_model: str, model, X_train, X_test, y_train, y_test):
	if denumire_model == "CatBoost":
		cat_features = X_train.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
		model.fit(X_train, y_train, cat_features=cat_features)
	elif denumire_model == "XGBoost":
		model.fit(X_train, y_train)
	else:
		model.fit(X_train, y_train)
	y_pred = model.predict(X_test)
	acc = accuracy_score(y_test, y_pred)
	f1 = f1_score(y_test, y_pred, average="weighted")
	cm = confusion_matrix(y_test, y_pred)
	st.session_state.rezultate.append((denumire_model, acc, f1, cm))


if df is not None and config is not None:

	st.subheader("Leaderboard")

	if not "training_done" in st.session_state:
		df = tratare_outlieri(df, config["tratare_outlieri"])
		df = tratare_valori_lipsa(df, config["tratare_valori_lipsa"])
		X_train, X_test, y_train, y_test = pregatire_date(
			df, config["metoda_scalare"], config["dimensiune_test"], config["stratificat"])
		for col in X_train.select_dtypes(include="object").columns:
			X_train[col] = X_train[col].astype("category")
			X_test[col] = X_test[col].astype("category")
		st.session_state.rezultate = []

		modele: dict = {
			"CatBoost": CatBoostClassifier(verbose=0),
			"LightGBM": LGBMClassifier(),
			"XGBoost": XGBClassifier(enable_categorical=True, tree_method="hist")
		}

		for (denumire_model, model) in modele.items():
			if denumire_model in config["algoritmi"]:
				antrenare_model(denumire_model, model, X_train, X_test, y_train, y_test)

		st.session_state.training_done = True

	leaderboard_df = pd.DataFrame(st.session_state.rezultate,
								  columns=["Model", "Acuratețe", "Scor F1", "Matrice de confuzie"])
	st.dataframe(leaderboard_df.iloc[:, :-1], hide_index=True, use_container_width=False)

	st.header("Rezultate")

	for rezultat in st.session_state.rezultate:
		denumire_model, acc, f1, cm = rezultat

		st.subheader(denumire_model)
		clase = ["Dropout", "Enrolled", "Graduate"]

		fig = go.Figure(data=go.Heatmap(
			z=cm[:, ::-1],
			x=clase[::-1],
			y=clase,
			colorscale="Blues",
			text=cm[:, ::-1],
			texttemplate="%{text}",
			hovertemplate="Predicted %{x}<br>Actual %{y}<br>Count: %{z}<extra></extra>"
		))

		fig.update_layout(
			title="Matrice de confuzie",
			xaxis_title="Valori prezise",
			yaxis_title="Valori reale",
			height=500,
			width=700
		)

		st.plotly_chart(fig, use_container_width=False)


else:
	st.warning("Configurează rularea în tab-ul anterior.")
