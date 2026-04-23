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

    # --- 1. ALERT PANEL ---
    st.subheader("⚠️ Pozornost vyžadují (Hodnocení pod 8.5)")
    last_date = df['Datum'].max()
    last_data = df[df['Datum'] == last_date]
    
    alerts = last_data[(last_data['Celkove'] < 8.5) | (last_data['Cistota'] < 8.5)]
    if not alerts.empty:
        for _, alert in alerts.iterrows():
            st.warning(f"**{alert['Apartman']}**: Celkové: {alert['Celkove']} | Čistota: {alert['Cistota']}")
    else:
        st.success("Všechny apartmány mají dnes skvělá čísla!")

    st.divider()

    # --- 2. SROVNÁVACÍ GRAF (DNES) ---
    st.subheader("📊 Dnešní srovnání apartmánů")
    metric = st.selectbox("Vyber metriku pro srovnání:", ["Celkove", "Cistota", "Personal"])
    
    # Tento graf uvidíš i s daty z jednoho dne!
    fig_bar = px.bar(last_data.sort_values(metric, ascending=False), 
                     x='Apartman', y=metric, color=metric,
                     color_continuous_scale='RdYlGn', range_y=[0,10.5])
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- 3. TRENDY (HISTORIE) ---
    st.subheader("📈 Vývoj v čase (Trend)")
    if df['Datum'].nunique() > 1:
        fig_line = px.line(df, x='Datum', y=metric, color='Apartman', markers=True, range_y=[0, 10.5])
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Trendový graf se vykreslí zítra, jakmile budeme mít data z druhého dne.")

    # --- 4. HEATMAPA ---
    st.subheader("🗺️ Detailní přehled portfolia")
    heatmap_df = last_data[['Apartman', 'Celkove', 'Cistota', 'Personal']].set_index('Apartman')
    st.dataframe(heatmap_df.style.background_gradient(cmap='RdYlGn', low=0.5, high=0.5), use_container_width=True)

    # --- 5. ANALÝZA TEXTŮ ---
    st.divider()
    st.subheader("💬 Poslední psané recenze")
    for _, row in df.sort_values('Datum', ascending=False).head(5).iterrows():
        with st.expander(f"{row['Apartman']} ({row['Celkove']}⭐) - {row['Datum'].strftime('%d.%m.')}"):
            st.write(f"**Kategorie:** {row['Kategorie_Problemu']}")
            st.info(row['Text_Recenze'])

else:
    st.info("Databáze se vytváří. Spusťte Robota v Actions.")
