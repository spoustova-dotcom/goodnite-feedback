import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Goodnite Quality Manager", layout="wide")

st.title("🌙 Goodnite Quality Management System")
st.markdown("---")

if os.path.exists('vysledne_recenze.csv'):
    df = pd.read_csv('vysledne_recenze.csv')
    df['Datum'] = pd.to_datetime(df['Datum'])
    for col in ['Celkove', 'Cistota', 'Personal']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 1. ALERT PANEL (Varování) ---
    st.subheader("⚠️ Pozornost vyžadují (Hodnocení pod 8.5)")
    last_data = df.sort_values('Datum').groupby('Apartman').last().reset_index()
    alerts = last_data[(last_data['Celkove'] < 8.5) | (last_data['Cistota'] < 8.5)]
    
    if not alerts.empty:
        for _, alert in alerts.iterrows():
            st.warning(f"**{alert['Apartman']}**: Celkové: {alert['Celkove']} | Čistota: {alert['Cistota']} (Poslední měření: {alert['Datum'].strftime('%d.%m.')})")
    else:
        st.success("Všechny apartmány mají aktuálně skvělá čísla!")

    st.divider()

    # --- 2. HEATMAPA (Barevný přehled) ---
    st.subheader("🗺️ Přehled portfolia (Heatmapa)")
    heatmap_df = last_data[['Apartman', 'Celkove', 'Cistota', 'Personal']].set_index('Apartman')
    
    # Stylizovaná tabulka s barvami
    def color_scale(val):
        color = 'red' if val < 8.5 else 'orange' if val < 9.0 else 'green'
        return f'color: {color}; font-weight: bold'

    st.dataframe(heatmap_df.style.applymap(color_scale), use_container_width=True)

    # --- 3. TRENDY ---
    st.subheader("📈 Vývoj v čase (Osa 0-10)")
    metric_to_plot = st.radio("Zobrazit graf pro:", ["Celkove", "Cistota", "Personal"], horizontal=True)
    
    fig = px.line(df, x='Datum', y=metric_to_plot, color='Apartman', markers=True, range_y=[0, 10.5], height=500)
    st.plotly_chart(fig, use_container_width=True)

    # --- 4. ANALÝZA TEXTŮ ---
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🔍 Nejčastější problémy")
        issues = df['Kategorie_Problemu'].str.split(', ').explode()
        issues = issues[issues != "Bez specifických problémů"]
        if not issues.empty:
            fig_issues = px.pie(issues.value_counts().reset_index(), names='index', values='Kategorie_Problemu', hole=0.4)
            st.plotly_chart(fig_issues, use_container_width=True)
    
    with col_b:
        st.subheader("💬 Poslední psané recenze")
        for _, row in df.sort_values('Datum', ascending=False).head(5).iterrows():
            st.markdown(f"**{row['Apartman']}** ({row['Celkove']}⭐)")
            st.caption(row['Text_Recenze'][:250] + "...")
            st.divider()

else:
    st.info("Databáze se vytváří. Spusťte Robota v Actions.")
