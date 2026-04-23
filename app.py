import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Goodnite Quality Manager", layout="wide")
st.title("🌙 Goodnite Quality & Feedback Report")

if os.path.exists('vysledne_recenze.csv'):
    df = pd.read_csv('vysledne_recenze.csv')
    df['Datum'] = pd.to_datetime(df['Datum'])
    for col in ['Celkove', 'Cistota']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- FILTRY ---
    st.sidebar.header("Nastavení reportu")
    apartman = st.sidebar.selectbox("Vyber apartmán pro detail", options=["Všechny"] + list(df['Apartman'].unique()))
    
    view_df = df if apartman == "Všechny" else df[df['Apartman'] == apartman]

    # --- KPI KARTY ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Průměrné skóre", f"{view_df['Celkove'].mean():.2f}")
    c2.metric("Průměrná čistota", f"{view_df['Cistota'].mean():.2f}")
    c3.metric("Počet recenzí v systému", len(view_df))

    # --- GRAF TRENDU ---
    st.subheader("📈 Vývoj kvality v čase")
    tab1, tab2 = st.tabs(["Celkové hodnocení", "Čistota"])
    with tab1:
        fig1 = px.line(view_df, x='Datum', y='Celkove', color='Apartman', markers=True)
        st.plotly_chart(fig1, use_container_width=True)
    with tab2:
        fig2 = px.line(view_df, x='Datum', y='Cistota', color='Apartman', markers=True)
        st.plotly_chart(fig2, use_container_width=True)

    # --- ANALÝZA PROBLÉMŮ ---
    st.divider()
    st.subheader("⚠️ Na co si hosté stěžují? (Analýza textů)")
    
    # Spočítáme výskyt kategorií
    issues = view_df['Kategorie_Problemu'].str.split(', ').explode()
    issues = issues[issues != "Bez specifických problémů"]
    if not issues.empty:
        issue_counts = issues.value_counts().reset_index()
        fig_issues = px.bar(issue_counts, x='index', y='Kategorie_Problemu', 
                           labels={'index': 'Kategorie', 'Kategorie_Problemu': 'Počet zmínek'},
                           color='index')
        st.plotly_chart(fig_issues, use_container_width=True)
    else:
        st.success("Zatím nebyly detekovány žádné opakující se problémy v textech.")

    # --- POSLEDNÍ RECENZE ---
    st.subheader("💬 Poslední záznamy")
    st.table(view_df.sort_values('Datum', ascending=False).head(10)[['Datum', 'Apartman', 'Celkove', 'Kategorie_Problemu']])

else:
    st.info("Databáze je zatím prázdná. Počkejte na první ranní běh robota.")
