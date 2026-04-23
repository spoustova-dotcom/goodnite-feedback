import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Goodnite Management Console", layout="wide")
st.title("🌙 Goodnite Quality & Feedback Report")

if os.path.exists('vysledne_recenze.csv'):
    df = pd.read_csv('vysledne_recenze.csv')
    df['Datum'] = pd.to_datetime(df['Datum'])
    for col in ['Celkove', 'Cistota']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sidebar
    st.sidebar.header("Nastavení")
    apartman = st.sidebar.selectbox("Detailní pohled", options=["Všechny"] + list(df['Apartman'].unique()))
    view_df = df if apartman == "Všechny" else df[df['Apartman'] == apartman]

    # Metriky
    c1, c2, c3 = st.columns(3)
    c1.metric("⭐ Průměrné skóre", f"{view_df['Celkove'].mean():.2f}")
    c2.metric("✨ Průměrná čistota", f"{view_df['Cistota'].mean():.2f}")
    c3.metric("📅 Poslední měření", view_df['Datum'].max().strftime('%d.%m.%Y'))

    # Grafy s pevnou osou 0-10
    st.subheader("📈 Vývoj kvality (škála 0-10)")
    tab1, tab2 = st.tabs(["Celkové hodnocení", "Čistota"])
    
    with tab1:
        fig1 = px.line(view_df, x='Datum', y='Celkove', color='Apartman', markers=True, range_y=[0,10.1])
        st.plotly_chart(fig1, use_container_width=True)
    with tab2:
        fig2 = px.line(view_df, x='Datum', y='Cistota', color='Apartman', markers=True, range_y=[0,10.1])
        st.plotly_chart(fig2, use_container_width=True)

    # Analýza problémů
    st.divider()
    st.subheader("⚠️ Nejčastější témata v recenzích")
    issues = view_df['Kategorie_Problemu'].str.split(', ').explode()
    issues = issues[issues != "Bez specifických problémů"]
    if not issues.empty:
        fig_issues = px.bar(issues.value_counts().reset_index(), x='index', y='Kategorie_Problemu', color='index', labels={'index':'Téma', 'Kategorie_Problemu':'Četnost'})
        st.plotly_chart(fig_issues, use_container_width=True)

    # Tabulka
    st.subheader("💬 Poslední záznamy")
    st.dataframe(view_df.sort_values('Datum', ascending=False).head(10)[['Datum', 'Apartman', 'Celkove', 'Cistota', 'Kategorie_Problemu']], use_container_width=True)

else:
    st.info("Databáze je prázdná. Spusťte Robota v Actions.")
