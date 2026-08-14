import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# ======================================================
# CONFIGURATION
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
# TRAITEMENT DU FICHIER
# ======================================================

if uploaded_file is not None:

    try:

        df = pd.read_excel(uploaded_file)

        # Nettoyage des noms de colonnes
        df.columns = df.columns.str.strip()

        st.subheader("Aperçu des données")
        st.dataframe(df.head())

        with st.expander("Colonnes détectées"):
            st.write(df.columns.tolist())

        # ==================================================
        # VERIFICATION DES COLONNES
        # ==================================================

        colonnes_requises = [
            "Perf Hebdo Portefeuille_actions",
            "Perf Hebdo MASIRB",
            "VL_ portefeuille_actions",
            "MAISI_RB"
        ]

        colonnes_absentes = [
            col for col in colonnes_requises
            if col not in df.columns
        ]

        if colonnes_absentes:
            st.error(
                "Colonnes manquantes : "
                + ", ".join(colonnes_absentes)
            )
            st.stop()

        # ==================================================
        # DONNEES
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

        vl_port = df[
            "VL_ portefeuille_actions"
        ].dropna()

        vl_indice = df[
            "MAISI_RB"
        ].dropna()

        # ==================================================
        # INDICATEURS
        # ==================================================

        perf_portefeuille = (
            vl_port.iloc[-1] / vl_port.iloc[0]
        ) - 1

        perf_indice = (
            vl_indice.iloc[-1] / vl_indice.iloc[0]
        ) - 1

        alpha = perf_portefeuille - perf_indice

        vol_port = portefeuille.std()
        vol_indice = indice.std()

        vol_port_ann = vol_port * np.sqrt(52)
        vol_indice_ann = vol_indice * np.sqrt(52)

        variance_indice = np.var(indice)

        if variance_indice != 0:
            beta = (
                np.cov(portefeuille, indice)[0, 1]
                / variance_indice
            )
        else:
            beta = np.nan

        corr = portefeuille.corr(indice)

        active_return = portefeuille - indice

        te_hebdo = active_return.std()
        te_ann = te_hebdo * np.sqrt(52)

        if te_hebdo != 0:
            info_ratio = (
                active_return.mean()
                / te_hebdo
            ) * np.sqrt(52)
        else:
            info_ratio = np.nan

        sharpe_port = (
            portefeuille.mean() / vol_port
            if vol_port != 0 else np.nan
        )

        sharpe_indice = (
            indice.mean() / vol_indice
            if vol_indice != 0 else np.nan
        )

        # ==================================================
        # TABLEAU DE RESULTATS
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
                "Bêta",
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

        st.subheader("Indicateurs")

        st.dataframe(
            resultats.style.format({
                "Valeur": "{:.4f}"
            })
        )

        # ==================================================
        # GRAPHIQUE RENDEMENTS
        # ==================================================

        st.subheader("Evolution des rendements")

        graph_df = pd.DataFrame({
            "Portefeuille": portefeuille.reset_index(drop=True),
            "Indice": indice.reset_index(drop=True)
        })

        fig = px.line(
            graph_df,
            title="Rendements hebdomadaires"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ==================================================
        # GRAPHIQUE BETA
        # ==================================================

        st.subheader("Sensibilité (Bêta)")

        reg_df = pd.DataFrame({
            "Indice": indice.reset_index(drop=True),
            "Portefeuille": portefeuille.reset_index(drop=True)
        })

        fig2 = px.scatter(
            reg_df,
            x="Indice",
            y="Portefeuille",
            trendline="ols",
            title="Régression Portefeuille / Indice"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.metric(
            "Bêta",
            f"{beta:.4f}"
            if pd.notna(beta)
            else "N/A"
        )

        # ==================================================
        # EXPORT EXCEL PROFESSIONNEL
        # ==================================================

        st.subheader("📥 Export du rapport")

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            resultats.to_excel(
                writer,
                sheet_name="Indicateurs",
                index=False
            )

            df.to_excel(
                writer,
                sheet_name="Donnees",
                index=False
            )

            ws = writer.book["Indicateurs"]

            for col in ws.columns:

                longueur = max(
                    len(str(cell.value))
                    if cell.value is not None else 0
                    for cell in col
                )

                ws.column_dimensions[
                    col[0].column_letter
                ].width = longueur + 5

        output.seek(0)

        st.download_button(
            label="📥 Télécharger le rapport Excel",
            data=output.getvalue(),
            file_name="Rapport_Analyse_Portefeuille.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Erreur : {e}")
