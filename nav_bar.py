"""
Modul ce definește bara laterală de navigare pentru aplicația Streamlit.

Include link-uri către toate paginile aplicației, facilitând accesul rapid și intuitiv
la funcționalitățile proiectului de analiză a datelor studenților.
"""

import streamlit as st


def nav_bar():
	"""
	Creează un meniu de navigare lateral (sidebar) pentru aplicația Streamlit.

	Fiecare link duce către o pagină a aplicației, reprezentată printr-un fișier `.py`,
	și este însoțit de o pictogramă sugestivă pentru îmbunătățirea experienței utilizatorului.
	"""
	with st.sidebar:
		st.page_link("app.py", label="Acasă", icon="🏠")
		st.page_link("pages/1_incarcare_fisier.py", label="Încărcare fișier", icon="📂")
		st.page_link("pages/2_vizualizare_date.py", label="Vizualizare date", icon="🔍")
		st.page_link("pages/3_descriere_date.py", label="Descriere date", icon="🍎")
		st.page_link("pages/4_histograme.py", label="Histograme", icon="📊")
		st.page_link("pages/5_box_plots.py", label="Box plots", icon="📦")
		st.page_link("pages/6_pie_charts.py", label="Pie charts", icon="🥧")
		st.page_link("pages/7_bar_charts.py", label="Stacked bar charts", icon="📚")
		st.page_link("pages/8_corelatii.py", label="Corelații", icon="🧬")
		st.page_link("pages/9_harta.py", label="Hartă", icon="🗺️")
		st.page_link("pages/10_duplicate_nan.py", label="Duplicate și valori lipsă", icon="🚨")
		st.page_link("pages/11_procesare.py", label="Procesarea datelor", icon="⚙️")
		st.page_link("pages/12_modele_ml.py", label="Modele ML", icon="🤖")
