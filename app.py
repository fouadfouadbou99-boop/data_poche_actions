# Nettoyage des noms de colonnes
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

# Recherche automatique des colonnes
col_vl_port = None

for c in df.columns:
    if "VL" in c and "portefeuille" in c.lower():
        col_vl_port = c
        break

if col_vl_port is None:
    st.error(
        "Impossible de trouver la colonne VL du portefeuille."
    )
    st.stop()

colonnes_requises = [
    "Perf Hebdo Portefeuille_actions",
    "Perf Hebdo MASIRB",
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

# Rendements
portefeuille = (
    df["Perf Hebdo Portefeuille_actions"]
    .dropna()
    .astype(float)
)

indice = (
    df["Perf Hebdo MASIRB"]
    .dropna()
    .astype(float)
)

n = min(len(portefeuille), len(indice))

portefeuille = portefeuille.iloc[:n]
indice = indice.iloc[:n]

# VL
vl_port = (
    df[col_vl_port]
    .dropna()
    .astype(float)
)

vl_indice = (
    df["MAISI_RB"]
    .dropna()
    .astype(float)
)

if len(vl_port) < 2:
    st.error("Pas assez de données dans la VL portefeuille.")
    st.stop()

if len(vl_indice) < 2:
    st.error("Pas assez de données dans MAISI_RB.")
    st.stop()

perf_portefeuille = (
    vl_port.iloc[-1] / vl_port.iloc[0] - 1
)

perf_indice = (
    vl_indice.iloc[-1] / vl_indice.iloc[0] - 1
)

alpha = (
    perf_portefeuille - perf_indice
)
