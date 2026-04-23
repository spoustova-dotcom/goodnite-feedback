import streamlit as st
import pandas as pd

st.set_page_config(page_title="Goodnite Feedback", layout="wide")

st.title("🌙 Goodnite Feedback Hub")

try:
    links = pd.read_csv('apartments_links_clean.csv')
    st.success("Seznam apartmánů byl úspěšně načten.")
    st.dataframe(links)
except Exception as e:
    st.error(f"Nepodařilo se načíst seznam apartmánů. Chyba: {e}")

st.info("Web je připraven. Nyní čekáme na spuštění robota pro sběr recenzí.")
