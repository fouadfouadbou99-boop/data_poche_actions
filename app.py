import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# ======================================================
# Configuration
# ======================================================

st.set_page_config(
    page_title="Analyse Portefeuille",
    layout="wide"
)

st.title("📊 Analyse Automatique de Portefeuille")

uploaded_file = st.file_uploader(
    "Importer le fichier Excel",
    type=["xlsx"]
)

# ======================================================
# Lecture du fichier
# ======================================================

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # Nettoyage des noms de colonnes
    df.columns = df.columns.str.strip()

    st.subheader("Aperçu des données")
    st.dataframe(df.head())

    # Affichage des colonnes détectées
    st.expander("Colonnes détectées").write(df.columns.tolist())

    # ==================================================
    # Colonnes attendues
    # ==================================================

    colonnes_requises = [
        "Perf Hebdo Portefeuille_actions",
        "Perf Hebdo MASIRB",
        "VL_ portefeuille_actions",
        "MAISI_RB"
    ]

    colonnes_absentes = [
        c for c in colonnes_requises
        if c not in df.columns
    ]

    if colonnes_absentes:
        st.error(
            f"Colonnes absentes : {', '.join(colonnes_absentes)}"
        )
        st.stop()

    # ==================================================
    # Séries de rendement
    # ==================================================

    portefeuille = df[
        "Perf Hebdo Portefeuille_actions"
    ].dropna()

    indice = df[
        "Perf Hebdo MASIRB"
    ].dropna()

    n = min(len(portefeuille), len(indice))

    portefeuille = portefeuille.iloc[:n]
    indice = indice.iloc[:n]

    # ==================================================
    # Performances cumulées
    # ==================================================

    vl_port = df["VL_ portefeuille_actions"].dropna()

    vl_indice = df["MAISI_RB"].dropna()

    perf_portefeuille = (
        vl_port.iloc[-1] / vl_port.iloc[0] - 1
    )

    perf_indice = (
        vl_indice.iloc[-1] / vl_indice.iloc[0] - 1
    )

    alpha = perf_portefeuille - perf_indice

    # ==================================================
    # Volatilités
    # ==================================================

    vol_port = portefeuille.std()

    vol_indice = indice.std()

    vol_port_ann = vol_port * np.sqrt(52)

    vol_indice_ann = vol_indice * np.sqrt(52)

    # ==================================================
    # Beta
    # ==================================================

    variance_indice = np.var(indice)

    if variance_indice == 0:
        beta = np.nan
    else:
        beta = (
            np.cov(portefeuille, indice)[0, 1]
            / variance_indice
        )

    # ==================================================
    # Corrélation
    # ==================================================

    corr = portefeuille.corr(indice)

    # ==================================================
    # Tracking Error
    # ==================================================

    active_return = portefeuille - indice

    te_hebdo = active_return.std()

    te_ann = te_hebdo * np.sqrt(52)

    if te_hebdo == 0:
        info_ratio = np.nan
    else:
        info_ratio = (
            active_return.mean()
            / te_hebdo
            * np.sqrt(52)
        )

    # ==================================================
    # Sharpe
    # ==================================================

    sharpe_port = (
        portefeuille.mean() / vol_port
        if vol_port != 0
        else np.nan
    )

    sharpe_indice = (
        indice.mean() / vol_indice
        if vol_indice != 0
        else np.nan
    )

    # ==================================================
    # Résultats
    # ==================================================

    resultats = pd.DataFrame({
        "Indicateur": [
            "Performance Portefeuille",
            "Performance Indice",
            "Alpha",
            "Volatilité Portefeuille",
            "Volatilité Indice",
            "Volatilité Annualisée Portefeuille",
            "Volatilité Annualisée Indice",
            "Beta",
            "Corrélation",
            "Tracking Error",
            "Tracking Error Annualisé",
            "Information Ratio",
            "Sharpe Portefeuille",
            "Sharpe Indice"
        ],
      
