"""
Generează o hartă choropleth care arată distribuția studenților după țara de origine.

Folosește o transformare logaritmică pentru a echilibra reprezentarea vizuală a frecvențelor.

Afișează detalii interactive și oferă contextul interpretării în interfața Streamlit.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Hartă", page_icon="🗺️", layout="wide")
nav_bar()
st.title("Hartă")
df: pd.DataFrame = st.session_state.get("df", default=None)

if df is not None:
	if "Country of origin" in df.columns:
		country_counts = df["Country of origin"].value_counts().reset_index()
		country_counts.columns = ["Țară", "Număr de studenți"]
		# st.dataframe(country_counts, use_container_width=False)
		country_counts["Număr de studenți_log"] = np.log1p(country_counts["Număr de studenți"])

		fig = px.choropleth(
			country_counts,
			locations="Țară",
			locationmode="country names",
			color="Număr de studenți_log",
			color_continuous_scale="magenta",
			title="Distribuția studenților pe țări",
			hover_data={"Țară": True, "Număr de studenți": True, "Număr de studenți_log": False}
		)

		fig.update_layout(height=700)

		st.plotly_chart(fig, use_container_width=True)

		st.header("Modul de realizare a hărții")
		st.markdown("""
			Pentru a evidenția distribuția studenților în funcție de țara de origine, am folosit o hartă tip choropleth.

			Deoarece `Portugalia` (țara din care provin datele) are un număr de studenți mult mai mare decât celelalte, am aplicat o **transformare logaritmică** asupra frecvenței studenților.

			Această abordare evită dominanța vizuală a țării cu număr extrem de mare de studenți și permite o comparație mai echilibrată între toate țările, inclusiv cele cu valori mici.

			Valoarea reală (ne-logaritmată) este afișată la hover pentru transparență.
			""")

	else:
		st.warning("Setul de date nu conține coloana 'Country of origin'.")
else:
	st.warning("Încarcă mai întâi un fișier CSV.")
