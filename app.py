import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Goodnite Management Console", layout="wide")

st.title("🌙 Goodnite Reality - Feedback Dashboard")
st.markdown("---")

if os.path.exists('vysledne_recenze.csv'):
    df = pd.read_csv('vysledne_recenze.csv')
    df['Datum'] = pd.to_datetime(df['Datum'])
    for col in ['Celkove', 'Cistota', 'Personal', 'Cena_Kvalita']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sidebar
    st.sidebar.header("Filtry")
    ap_filter = st.sidebar.multiselect("Apartmán", options=df['Apartman'].unique(), default=df['Apartman'].unique())
    filtered = df[df['Apartman'].isin(ap_filter)]

    # Horní karty (KPIs)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⭐ Celkový Průměr", f"{filtered['Celkove'].mean():.2f}")
    c2.metric("✨ Čistota", f"{filtered['Cistota'].mean():.2f}")
    c3.metric("🤝 Personál", f"{filtered['Personal'].mean():.2f}")
    c4.metric("💰 Cena/Kvalita", f"{filtered['Cena_Kvalita'].mean():.2f}")

    # Grafy
    st.markdown("### 📈 Vývoj hodnocení v čase")
    fig = px.line(filtered, x='Datum', y='Celkove', color='Apartman', markers=True, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Psané recenze jako v Excelu
    st.markdown("### 💬 Poslední textové recenze")
    for _, row in filtered.sort_values('Datum', ascending=False).head(15).iterrows():
        with st.expander(f"{row['Apartman']} - {row['Datum'].strftime('%d.%m.%Y')} (Skóre: {row['Celkove']})"):
            st.write(f"**Detailní hodnocení:** Čistota: {row['Cistota']} | Personál: {row['Personal']} | Cena: {row['Cena_Kvalita']}")
            st.info(row['Text_Recenze'])
else:
    st.info("Čekáme na první data z ranního sběru robota...")
