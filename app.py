import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Goodnite Dashboard", layout="wide")

st.title("📊 Goodnite Reality - Management Dashboard")

if os.path.exists('vysledne_recenze.csv'):
    df = pd.read_csv('vysledne_recenze.csv')
    df['Datum'] = pd.to_datetime(df['Datum'])
    df = df.sort_values('Datum')

    # --- SIDEBAR FILTRY ---
    st.sidebar.header("Filtry")
    selected_apartman = st.sidebar.multiselect("Vyber apartmán", options=df['Apartman'].unique(), default=df['Apartman'].unique())
    selected_platforma = st.sidebar.multiselect("Platforma", options=df['Platforma'].unique(), default=df['Platforma'].unique())

    filtered_df = df[(df['Apartman'].isin(selected_apartman)) & (df['Platforma'].isin(selected_platforma))]

    # --- HLAVNÍ METRIKY ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Průměrné hodnocení", round(filtered_df['Celkove'].mean(), 2))
    with col2:
        st.metric("Průměrný úklid", round(filtered_df['Uklid'].mean(), 2))
    with col3:
        st.metric("Průměrný personál", round(filtered_df['Personal'].mean(), 2))
    with col4:
        st.metric("Počet měření", len(filtered_df))

    # --- GRAFY ---
    st.divider()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Vývoj hodnocení v čase")
        fig_time = px.line(filtered_df, x='Datum', y='Celkove', color='Apartman', 
                           markers=True, title="Trend celkového skóre")
        st.plotly_chart(fig_time, use_container_width=True)

    with col_right:
        st.subheader("Srovnání úklidu")
        avg_uklid = filtered_df.groupby('Apartman')['Uklid'].mean().reset_index()
        fig_bar = px.bar(avg_uklid, x='Apartman', y='Uklid', color='Apartman', title="Průměrný úklid podle objektu")
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABULKA ---
    st.subheader("Detailní data")
    st.dataframe(filtered_df.sort_values('Datum', ascending=False), use_container_width=True)

else:
    st.warning("Zatím nebyla nasbírána žádná data. Spusťte robota v sekci Actions.")
