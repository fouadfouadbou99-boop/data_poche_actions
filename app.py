import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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

if uploaded_file is not None:

    try:

        df = pd.read_excel(uploaded_file)

        # Nettoyage des noms des colonnes
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

        st.subheader("Aperçu des données")
        st.dataframe(df.head())

        with st.expander("Colonnes détectées"):
            st.write(df.columns.tolist())

        # ======================================================
        # Détection automatique des colonnes
        # ======================================================

        col_perf_port = None
        col_perf_indice = None
        col_vl_port = None
        col_indice = None

        for col in df.columns:

            if "Perf Hebdo Portefeuille" in col:
                col_perf_port = col

            elif "Perf Hebdo MASI" in col:
                col_perf_indice = col

            elif "VL_" in col and "portefeuille" in col.lower():
                col_vl_port = col

            elif col == "MAISI_RB":
                col_indice = col

        # Vérifications

        colonnes_manquantes = []

        if col_perf_port is None:
            colonnes_manquantes.append("Perf Hebdo Portefeuille")

        if col_perf_indice is None:
            colonnes_manquantes.append("Perf Hebdo MASIRB")

        if col_vl_port is None:
            colonnes_manquantes.append("VL_portefeuille_actions")

        if col_indice is None:
            colonnes_manquantes.append("MAISI_RB")

        if colonnes_manquantes:
            st.error(
                "Colonnes manquantes : "
                + ", ".join(colonnes_manquantes)
            )
            st.stop()

        # ======================================================
        # Séries de rendements
        # ======================================================

        portefeuille = (
            pd.to_numeric(
                df[col_perf_port],
                errors="coerce"
            )
            .dropna()
        )

        indice = (
            pd.to_numeric(
                df[col_perf_indice],
                errors="coerce"
            )
            .dropna()
        )

        n = min(len(portefeuille), len(indice))

        portefeuille = portefeuille.iloc[:n]
        indice = indice.iloc[:n]

        # ======================================================
        # Valeurs liquidatives
        # ======================================================

        vl_port = (
            pd.to_numeric(
                df[col_vl_port],
                errors="coerce"
            )
            .dropna()
        )

        vl_indice = (
            pd.to_numeric(
                df[col_indice],
                errors="coerce"
            )
            .dropna()
        )

        if len(vl_port) < 2:
            st.error("Pas assez de données VL portefeuille.")
            st.stop()

        if len(vl_indice) < 2:
            st.error("Pas assez de données indice.")
            st.stop()

        # ======================================================
        # Performances
        # ======================================================

        perf_portefeuille = (
            vl_port.iloc[-1] / vl_port.iloc[0] - 1
        )

        perf_indice = (
            vl_indice.iloc[-1] / vl_indice.iloc[0] - 1
        )

        alpha = (
            perf_portefeuille - perf_indice
        )

        # ======================================================
        # Volatilité
        # ======================================================

        vol_port = portefeuille.std()

        vol_indice = indice.std()

        vol_port_ann = vol_port * np.sqrt(52)

        vol_indice_ann = vol_indice * np.sqrt(52)

        # ======================================================
        # Beta
        # ======================================================

        variance_indice = np.var(indice)

        if variance_indice == 0:
            beta = np.nan
        else:
            beta = (
                np.cov(
                    portefeuille,
                    indice
                )[0, 1]
                / variance_indice
            )

        # ======================================================
        # Corrélation
        # ======================================================

        corr = portefeuille.corr(indice)

        # ======================================================
        # Tracking Error
        # ======================================================

        active_return = portefeuille - indice

        te_hebdo = active_return.std()

        te_ann = te_hebdo * np.sqrt(52)

        # ======================================================
        # Information Ratio
        # ======================================================

        if te_hebdo == 0:
            info_ratio = np.nan
        else:
            info_ratio = (
                active_return.mean()
                / te_hebdo
                * np.sqrt(52)
            )

        # ======================================================
        # Sharpe
        # ======================================================

        sharpe_port = (
            portefeuille.mean()
            / vol_port
            if vol_port != 0
            else np.nan
        )

        sharpe_indice = (
            indice.mean()
            / vol_indice
            if vol_indice != 0
            else np.nan
        )

        # ======================================================
        # Tableau résultats
        # ======================================================

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
            "Valeur": [
                perf_portefeuille,
                perf_indice,
                alpha,
                vol_port,
                vol_indice,
                vol_port_ann,
                vol_indice_ann,
                beta,
                corr,
                te_hebdo,
                te_ann,
                info_ratio,
                sharpe_port,
                sharpe_indice
            ]
        })

        # ======================================================
        # Affichage KPI
        # ======================================================

        st.subheader("📈 Indicateurs clés")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Performance Portefeuille",
            f"{perf_portefeuille:.2%}"
        )

        c2.metric(
            "Performance Indice",
            f"{perf_indice:.2%}"
        )

        c3.metric(
            "Alpha",
            f"{alpha:.2%}"
        )

        st.dataframe(
            resultats.style.format(
                {"Valeur": "{:.4f}"}
            ),
            use_container_width=True
        )

        # ======================================================
        # Graphique VL
        # ======================================================

        st.subheader("📊 Evolution des VL")

        if "Date" in df.columns:

            graph_df = df.copy()

            graph_df["Date"] = pd.to_datetime(
                graph_df["Date"],
                errors="coerce"
            )

            fig = px.line(
                graph_df,
                x="Date",
                y=[col_vl_port, col_indice],
                title="Evolution Portefeuille vs Indice"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    except Exception as e:
        st.error(
            f"Erreur : {str(e)}"
        )

else:
    st.info(
        "Veuillez sélectionner un fichier Excel."
    )
