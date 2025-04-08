from PIL import Image
import streamlit as st

from nav_bar import nav_bar


st.set_page_config(page_title="Proiect PSW", layout="wide")

nav_bar()

st.title("🎓 Analiza succesului academic al studenților")

image_path = "graduation.png"
image = Image.open(image_path)
st.image(image, width=500)
