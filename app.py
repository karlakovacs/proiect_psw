"""
Pagină de întâmpinare pentru aplicația Streamlit dedicată analizei succesului academic al studenților.

Afișează un titlu descriptiv și o imagine reprezentativă (ex. absolvire) pentru introducerea în contextul proiectului.

Această pagină funcționează ca punct de pornire vizual și informativ pentru utilizator.
"""

from PIL import Image
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Proiect PSW", page_icon="🎓", layout="wide")

nav_bar()

st.title("🎓 Analiza succesului academic al studenților")

image_path = "graduation.png"
image = Image.open(image_path)
st.image(image, width=500)
