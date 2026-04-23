import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Goodnite Dashboard", layout="wide")

st.title("📊 Goodnite Reality - Management Dashboard")

if os.path.exists('vysledne_recenze.csv'):
    df = pd.read_csv('vysledne_recenze.csv')
    
    # --- KLÍČOVÁ OPRAVA: Převedení na čísla a ošetření chyb ---
    # Pokud tam robot zapsal něco divného, udělá z toho NaN (nečíslo) a dashboard nespadne
    for col in ['Celkove', 'Uklid', 'Personal', 'Lokalita']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['Datum'] = pd.to_datetime(df['Datum'])
    df = df.sort_values('Datum')

    # --- SIDEBAR FILTRY ---
    st.sidebar.header("Filtry")
    # Ošetření pro případ, že by ve sloupci byly prázdné hodnoty
    apartman_list = df['Apartman'].dropna().unique()
    platform_list = df['Platforma'].dropna().unique()
    
    selected_apartman = st.sidebar.multiselect("Vyber apartmán", options=apartman_list, default=apartman_list)
    selected_platforma = st.sidebar.multiselect("Platforma", options=platform_list, default=platform_list)

    filtered_df = df[(df['Apartman'].isin(selected_apartman)) & (df['Platforma'].isin(selected_platforma))]

    # --- HLAVNÍ METRIKY ---
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            val = filtered_df['Celkove'].mean()
            st.metric("Průměrné hodnocení", f"{val:.2f}" if pd.notnull(val) else "N/A")
        with col2:
            val = filtered_df['Uklid'].mean()
            st.metric("Průměrný úklid", f"{val:.2f}" if pd.notnull(val) else "N/A")
        with col3:
            val = filtered_df['Personal'].mean()
            st.metric("Průměrný personál", f"{val:.2f}" if pd.notnull(val) else "N/A")
        with col4:
            st.metric("Počet měření", len(filtered_df))

        # --- GRAFY ---
        st.divider()
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Vývoj hodnocení v čase")
            fig_time = px.line(filtered_df, x='Datum', y='Celkove', color='Apartman', symbol='Platforma',
                               markers=True, title="Trend celkového skóre")
            st.plotly_chart(fig_time, use_container_width=True)

        with col_right:
            st.subheader("Srovnání čistoty")
            # Filtrace jen těch, co mají úklid > 0 (Booking)
            uklid_df = filtered_df[filtered_df['Uklid'] > 0]
            if not uklid_df.empty:
                avg_uklid = uklid_df.groupby('Apartman')['Uklid'].mean().reset_index()
                fig_bar = px.bar(avg_uklid, x='Apartman', y='Uklid', color='Apartman', title="Průměrný úklid")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Data pro úklid jsou dostupná pouze u Bookingu.")

        # --- TABULKA ---
        st.subheader("Detailní data")
        st.dataframe(filtered_df.sort_values('Datum', ascending=False), use_container_width=True)
    else:
        st.info("Vyberte v levém panelu apartmány a platformy pro zobrazení dat.")

else:
    st.warning("Zatím nebyla nasbírána žádná data. Spusťte robota v sekci Actions.")
