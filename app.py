import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
from io import BytesIO

st.set_page_config(
    page_title="Analyse Portefeuille",
    layout="wide"
)

st.title("📊 Analyse Automatique de Portefeuille")

uploaded_file = st.file_uploader(
    "Importer le fichier Excel",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.subheader("Données")

    st.dataframe(df.head())

    portefeuille = df["Perf Hebdo Portefeuille_actions"].dropna()
    indice = df["Perf Hebdo MASIRB"].dropna()

    n = min(len(portefeuille), len(indice))

    portefeuille = portefeuille.iloc[:n]
    indice = indice.iloc[:n]

    perf_portefeuille = (
        df["VL_portefeuille_actions"].dropna().iloc[-1]
        /
        df["VL_portefeuille_actions"].dropna().iloc[0]
        - 1
    )

    perf_indice = (
        df["MAISI_RB"].dropna().iloc[-1]
        /
        df["MAISI_RB"].dropna().iloc[0]
        - 1
    )

    alpha = perf_portefeuille - perf_indice

    vol_port = portefeuille.std()

    vol_indice = indice.std()

    vol_port_ann = vol_port * np.sqrt(52)

    vol_indice_ann = vol_indice * np.sqrt(52)

    beta = np.cov(
        portefeuille,
        indice
    )[0,1] / np.var(indice)

    corr = portefeuille.corr(indice)

    active_return = portefeuille - indice

    te_hebdo = active_return.std()

    te_ann = te_hebdo * np.sqrt(52)

    info_ratio = (
        active_return.mean()
        /
        te_hebdo
        * np.sqrt(52)
    )

    sharpe_port = (
        portefeuille.mean()
        /
        vol_port
    )

    sharpe_indice = (
        indice.mean()
        /
        vol_indice
    )

    resultats = pd.DataFrame({

        "Indicateur":[
            "Performance Portefeuille",
            "Performance Indice",
            "Alpha",
            "Volatilité Portefeuille",
            "Volatilité Indice",
            "Volatilité Annuelle Portefeuille",
            "Volatilité Annuelle Indice",
            "Beta",
            "Corrélation",
            "Tracking Error",
            "Tracking Error Annualisé",
            "Information Ratio",
            "Sharpe Portefeuille",
            "Sharpe Indice"
        ],

        "Valeur":[
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

    st.dataframe(resultats)

    st.subheader("Evolution des rendements")

    graph_df = pd.DataFrame({
        "Portefeuille": portefeuille,
        "Indice": indice
    })

    fig = px.line(
        graph_df,
        title="Rendements hebdomadaires"
    )

    st.plotly_chart(fig,
                     use_container_width=True)

    st.subheader("Sensibilité (Bêta)")

    reg_df = pd.DataFrame({
        "Indice": indice,
        "Portefeuille": portefeuille
    })

    fig2 = px.scatter(
        reg_df,
        x="Indice",
        y="Portefeuille",
        trendline="ols"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.metric(
        "Bêta",
        round(beta,4)
    )

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        resultats.to_excel(
            writer,
            sheet_name="Analyse",
            index=False
        )

        graph_df.to_excel(
            writer,
            sheet_name="Rendements",
            index=False
        )

    st.download_button(
        label="Télécharger le rapport Excel",
        data=output.getvalue(),
        file_name="rapport_portefeuille.xlsx",
        mime="application/vnd.ms-excel"
    )
