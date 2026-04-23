import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Goodnite Feedback Hub", layout="wide")

st.title("🌙 Goodnite Feedback Hub")

# 1. Načtení výsledků od robota
if os.path.exists('vysledne_recenze.csv'):
    try:
        df_vysledky = pd.read_csv('vysledne_recenze.csv')
        st.subheader("Aktuální hodnocení z Booking.com")
        st.dataframe(df_vysledky, use_container_width=True)
    except Exception as e:
        st.error(f"Chyba při načítání výsledků: {e}")
else:
    st.info("Robot už pracuje, ale první výsledky budou vidět za malou chvíli.")

st.divider()

# 2. Načtení seznamu tvých apartmánů (pro kontrolu)
try:
    links = pd.read_csv('apartments_links_clean.csv')
    with st.expander("Zobrazit seznam sledovaných apartmánů"):
        st.table(links)
except Exception as e:
    st.warning(f"Seznam apartmánů se nepodařilo načíst: {e}")

st.info("Data se automaticky aktualizují každé ráno v 8:00.")
