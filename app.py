import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Goodnite Dashboard", layout="wide")
st.title("📊 Goodnite Reality - Feedback Hub")

if os.path.exists('vysledne_recenze.csv'):
    df = pd.read_csv('vysledne_recenze.csv')
    df['Datum'] = pd.to_datetime(df['Datum'])
    for col in ['Celkove', 'Uklid', 'Personal']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- FILTRY ---
    st.sidebar.header("Filtry")
    selected_apartman = st.sidebar.multiselect("Vyber apartmán", options=df['Apartman'].unique(), default=df['Apartman'].unique())
    filtered_df = df[df['Apartman'].isin(selected_apartman)]

    # --- GRAF ---
    st.subheader("Trend hodnocení")
    fig = px.line(filtered_df, x='Datum', y='Celkove', color='Apartman', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # --- TEXTOVÉ RECENZE ---
    st.divider()
    st.subheader("💬 Poslední psané recenze")
    
    for idx, row in filtered_df.sort_values('Datum', ascending=False).head(10).iterrows():
        with st.container():
            st.markdown(f"**{row['Apartman']}** ({row['Datum'].strftime('%d.%m.%Y')})")
            st.info(row['Text_Recenze'])
            st.write(f"Skóre: {row['Celkove']}")
            st.divider()
else:
    st.warning("Data se připravují. Spusťte robota v Actions.")
