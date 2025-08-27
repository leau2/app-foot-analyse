import requests
import pandas as pd
import streamlit as st
from datetime import datetime
import os
import json

st.set_page_config(page_title="ISOCSS PRONOSTIC", layout="wide")

pays_options = ['Argentina', 'Brazil', 'Belgium', 'England', 'Europe', 'France', 'Germany', 'Italy', 'Spain', 'Portugal', 'Turkey', 'Netherlands', 'USA']
ligues_options = {
    'Argentina': ['Liga Profesional'],
    'Brazil': ['Serie A'],
    'Belgium': ['Jupiter Pro League'],
    'England': ['Premier League'],
    'Europe': ['Champions League'],
    'France': ['Ligue 1', 'Ligue 2'],
    'Germany': ['Bundesliga'],
    'Italy': ['Serie A'],
    'Spain': ['LaLiga'],
    'Portugal': ['Liga Portugal'],
    'Turkey': ['Super Lig'],
    'Netherlands': ['Eredivisie'],
    'USA': ['MLS']
}


if "show_interface_1" not in st.session_state:
    st.session_state["show_interface_1"] = False
if "show_interface_2" not in st.session_state:
    st.session_state["show_interface_2"] = False
if "resultats_interface_1" not in st.session_state:
    st.session_state["resultats_interface_1"] = pd.DataFrame()
if "resultats_interface_2" not in st.session_state:
    st.session_state["resultats_interface_2"] = pd.DataFrame()

@st.cache_data
def charger_fichier():
    df = pd.read_excel("https://www.dropbox.com/scl/fi/hmuzsmfh0zrqhsjkx3u9v/FTPINNACLEBET365.xlsx?rlkey=2xpjhij52j6qlt9vf5j1bzohx&st=30bzfp5q&raw=1", skiprows=2, header=None)
    df.columns = [
        *[f"col_{i}" for i in range(0, 5)],
        "Pays", "Championnat",
        *[f"col_{i}" for i in range(7, 10)],
        "Score_Dom", "Score_Ext", "Resultat",
        *[f"col_{i}" for i in range(13, 24)],
        "Pinnacle_1", "Pinnacle_N", "Pinnacle_2",
        *[f"col_{i}" for i in range(27, 30)],
        "Bet365_1", "Bet365_N", "Bet365_2",
        *[f"col_{i}" for i in range(33, 36)]
    ]
    return df

df = charger_fichier()

def color_result(val):
    if val == 'H': return f"<span style='color:green'><b>{val}</b></span>"
    if val == 'D': return f"<span style='color:red'><b>{val}</b></span>"
    if val == 'A': return f"<span style='color:blue'><b>{val}</b></span>"
    return val

def afficher_tableau(resultats):
    df_display = resultats.copy()
    df_display["Score"] = df_display["Score_Dom"].astype(str) + " - " + df_display["Score_Ext"].astype(str)
    df_display["Résultat"] = df_display["Resultat"].apply(color_result)
    st.write(df_display[[ 
        'Pinnacle_1', 'Pinnacle_N', 'Pinnacle_2',
        'Bet365_1', 'Bet365_N', 'Bet365_2',
        'Score', 'Résultat'
    ]].to_html(escape=False, index=False), unsafe_allow_html=True)

def afficher_pronostics(resultats):
    counts = resultats['Resultat'].value_counts()
    total = counts.sum()
    if total > 0:
        for res, nb in counts.items():
            percent = round((nb / total) * 100)
            label = {"H": "🏠 Domicile", "A": "✈️ Extérieur", "D": "⚖️ Nul"}.get(res, res)
            st.success(f"{label} : {percent}%")

    total_buts = resultats["Score_Dom"] + resultats["Score_Ext"]
    total_buts = pd.to_numeric(total_buts, errors='coerce')
    dom = pd.to_numeric(resultats["Score_Dom"], errors='coerce')
    ext = pd.to_numeric(resultats["Score_Ext"], errors='coerce')
    total = len(resultats)

    if total > 0:
        over_pct = round((total_buts > 2.5).sum() / total * 100)
        under_pct = round((total_buts <= 2.5).sum() / total * 100)
        if over_pct > 0: st.info(f"⚽ Over 2.5 : {over_pct}%")
        if under_pct > 0: st.info(f"⚽ Under 2.5 : {under_pct}%")

        btts_yes = ((dom > 0) & (ext > 0)).sum()
        btts_no = total - btts_yes
        yes_pct = round(btts_yes / total * 100)
        no_pct = round(btts_no / total * 100)
        if yes_pct > 0: st.info(f"🔁 BTTS Oui : {yes_pct}%")
        if no_pct > 0: st.info(f"🔁 BTTS Non : {no_pct}%")

def analyse_croisee(r1, r2):
    bloc = ""
    if r1.empty or r2.empty:
        return "Aucune donnée pour analyser."

    def get_top(df, col, seuil):
        count = df[col].value_counts()
        if count.empty: return None, 0
        val = count.idxmax()
        pct = round(count[val] / count.sum() * 100)
        return (val, pct) if pct >= seuil else (None, 0)

    res1, p1 = get_top(r1, "Resultat", 50)
    res2, p2 = get_top(r2, "Resultat", 55)
    if res1 and res2 and res1 == res2:
        q = round((1 - p1/100) * (1 - p2/100), 2)
        bloc += f"📊 **Résultat du match : {res1}** ({p1}% + {p2}%) | Quotient : {q}<br>"

    buts1 = pd.to_numeric(r1["Score_Dom"], errors='coerce') + pd.to_numeric(r1["Score_Ext"], errors='coerce')
    buts2 = pd.to_numeric(r2["Score_Dom"], errors='coerce') + pd.to_numeric(r2["Score_Ext"], errors='coerce')
    over1 = round((buts1 > 2.5).sum() / len(r1) * 100) if len(r1) else 0
    over2 = round((buts2 > 2.5).sum() / len(r2) * 100) if len(r2) else 0
    under1 = 100 - over1
    under2 = 100 - over2

    if over1 >= 50 and over2 >= 55:
        q = round((1 - over1/100) * (1 - over2/100), 2)
        bloc += f"⚽ **Over 2.5 buts** ({over1}% + {over2}%) | Quotient : {q}<br>"
    elif under1 >= 50 and under2 >= 55:
        q = round((1 - under1/100) * (1 - under2/100), 2)
        bloc += f"⚽ **Under 2.5 buts** ({under1}% + {under2}%) | Quotient : {q}<br>"

    dom1 = pd.to_numeric(r1["Score_Dom"], errors='coerce')
    ext1 = pd.to_numeric(r1["Score_Ext"], errors='coerce')
    dom2 = pd.to_numeric(r2["Score_Dom"], errors='coerce')
    ext2 = pd.to_numeric(r2["Score_Ext"], errors='coerce')

    btts1 = ((dom1 > 0) & (ext1 > 0)).sum()
    btts2 = ((dom2 > 0) & (ext2 > 0)).sum()
    b1 = round(btts1 / len(r1) * 100) if len(r1) else 0
    b2 = round(btts2 / len(r2) * 100) if len(r2) else 0
    non_b1 = 100 - b1
    non_b2 = 100 - b2

    if b1 >= 50 and b2 >= 55:
        q = round((1 - b1/100) * (1 - b2/100), 2)
        bloc += f"🔁 **BTTS Oui** ({b1}% + {b2}%) | Quotient : {q}<br>"
    elif non_b1 >= 50 and non_b2 >= 55:
        q = round((1 - non_b1/100) * (1 - non_b2/100), 2)
        bloc += f"🔁 **BTTS Non** ({non_b1}% + {non_b2}%) | Quotient : {q}<br>"

    return bloc or "Pas de pronostic croisé valide."
    
# Interface
with st.sidebar:
    st.title("ISOCSS PRONOSTIC")
    choix = st.radio("Navigation", ["Analyser un match", "POURCENTAGE BOOK", "ANALYSE IA"])

if choix == "Analyser un match":
    st.subheader("Analyse d'un match")

    # Menus déroulants pour Pays et Championnat
    pays = st.selectbox("Pays", options=pays_options)
    championnat = st.selectbox("Championnat", options=ligues_options[pays])

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])  # 8 colonnes égales plus petites
    with col1: pin_1 = st.number_input("Pinnacle 1", step=0.01, format="%.2f")
    with col2: pin_n = st.number_input("Pinnacle N", step=0.01, format="%.2f")
    with col3: pin_2 = st.number_input("Pinnacle 2", step=0.01, format="%.2f")
    with col4: bet_1 = st.number_input("Bet365 1", step=0.01, format="%.2f")
    with col5: bet_n = st.number_input("Bet365 N", step=0.01, format="%.2f")
    with col6: bet_2 = st.number_input("Bet365 2", step=0.01, format="%.2f")

    # Résultats d'analyse dans un panneau pliable
    with st.expander("Résultats d'analyse"):
        if st.session_state["resultats_interface_1"].empty or st.session_state["resultats_interface_2"].empty:
            st.warning("Aucun résultat trouvé. Assurez-vous d'avoir lancé une analyse avant.")
        else:
            st.markdown(analyse_croisee(st.session_state["resultats_interface_1"], st.session_state["resultats_interface_2"]), unsafe_allow_html=True)

    colG, colD = st.columns(2)

    with colG:
        st.markdown("### Interface 1")
        if st.button("Lancer Interface 1"):
            st.session_state["show_interface_1"] = True
            r = pd.DataFrame()
            if pin_1 and pin_2:
                if pin_n:
                    r = df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_N"] == pin_n) & (df["Pinnacle_2"] == pin_2)]
                if r.empty and bet_1 and bet_2:
                    r = df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_2"] == pin_2) & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2)]
                if r.empty:
                    r = pd.concat([df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_2"] == pin_2) & (df["Bet365_1"] == bet_1)],
                        df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_2"] == pin_2) & (df["Bet365_2"] == bet_2)]
                    ])
                if r.empty:
                    r = df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_2"] == pin_2)]
            st.session_state["resultats_interface_1"] = r

        if st.session_state["show_interface_1"] and not st.session_state["resultats_interface_1"].empty:
            afficher_tableau(st.session_state["resultats_interface_1"])
            afficher_pronostics(st.session_state["resultats_interface_1"])

    with colD:
        st.markdown("### Interface 2")
        if st.button("Lancer Interface 2"):
            st.session_state["show_interface_2"] = True
            r = pd.DataFrame()
            if championnat:
                base = df["Championnat"].str.lower() == championnat.lower()
                if pays:
                    base &= df["Pays"].str.lower() == pays.lower()
                r1 = df[base & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2) & (df["Pinnacle_1"] == pin_1)]
                r2 = df[base & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2) & (df["Pinnacle_2"] == pin_2)]
                r = pd.concat([r1, r2]).drop_duplicates()
                if r.empty:
                    r = df[base & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2) & (df["Bet365_N"] == bet_n)]
                if r.empty:
                    r = df[base & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2)]
            st.session_state["resultats_interface_2"] = r

        if st.session_state["show_interface_2"] and not st.session_state["resultats_interface_2"].empty:
            afficher_tableau(st.session_state["resultats_interface_2"])
            afficher_pronostics(st.session_state["resultats_interface_2"])

    # Bouton "Enregistrer"
    with st.expander("Enregistrer les résultats"):
        nom_fichier = st.text_input("Entrez un nom pour enregistrer les résultats :")
        if st.button("Enregistrer"):
            if nom_fichier:
                analyse_text = analyse_croisee(st.session_state["resultats_interface_1"], st.session_state["resultats_interface_2"])  # Extraire l'analyse croisée
                enregistrer_resultats(nom_fichier, analyse_text)
            else:
                st.warning("Veuillez entrer un nom de fichier.")

elif choix == "ANALYSE IA":
    st.subheader("ANALYSE IA")

    # Menus déroulants pour Pays et Championnat (identiques à "Analyser un match")
    pays = st.selectbox("Pays", options=pays_options, key="ia_pays")
    championnat = st.selectbox("Championnat", options=ligues_options[pays], key="ia_champ")

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1: pin_1 = st.number_input("Pinnacle 1", step=0.01, format="%.2f", key="ia_pin1")
    with col2: pin_n = st.number_input("Pinnacle N", step=0.01, format="%.2f", key="ia_pinn")
    with col3: pin_2 = st.number_input("Pinnacle 2", step=0.01, format="%.2f", key="ia_pin2")
    with col4: bet_1 = st.number_input("Bet365 1", step=0.01, format="%.2f", key="ia_bet1")
    with col5: bet_n = st.number_input("Bet365 N", step=0.01, format="%.2f", key="ia_betn")
    with col6: bet_2 = st.number_input("Bet365 2", step=0.01, format="%.2f", key="ia_bet2")

    # Résultats d'analyse (même logique d'analyse croisée, on réutilise les mêmes session_state)
    with st.expander("Résultats d'analyse"):
        if st.session_state["resultats_interface_1"].empty or st.session_state["resultats_interface_2"].empty:
            st.warning("Aucun résultat trouvé. Lance une analyse d'abord.")
        else:
            st.markdown(analyse_croisee(st.session_state["resultats_interface_1"],
                                        st.session_state["resultats_interface_2"]),
                        unsafe_allow_html=True)

    colG, colD = st.columns(2)

    # Interface 1 : marche EXACTEMENT comme dans "Analyser un match"
    with colG:
        st.markdown("### PINNACLE")
        if st.button("LANCER L'IA 1"):
            st.session_state["show_interface_1"] = True
            r = pd.DataFrame()
            if pin_1 and pin_2:
                if pin_n:
                    r = df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_N"] == pin_n) & (df["Pinnacle_2"] == pin_2)]
                if r.empty and bet_1 and bet_2:
                    r = df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_2"] == pin_2) &
                           (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2)]
                if r.empty:
                    r = pd.concat([
                        df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_2"] == pin_2) & (df["Bet365_1"] == bet_1)],
                        df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_2"] == pin_2) & (df["Bet365_2"] == bet_2)]
                    ])
                if r.empty:
                    r = df[(df["Pinnacle_1"] == pin_1) & (df["Pinnacle_2"] == pin_2)]
            st.session_state["resultats_interface_1"] = r

        if st.session_state["show_interface_1"] and not st.session_state["resultats_interface_1"].empty:
            afficher_tableau(st.session_state["resultats_interface_1"])
            afficher_pronostics(st.session_state["resultats_interface_1"])

    # Interface 2 : UNIQUEMENT Cas 3 et Cas 4 (dans le championnat/pays)
    with colD:
        st.markdown("### BET365")
        if st.button("LANCER L'IA 2"):
            st.session_state["show_interface_2"] = True
            r = pd.DataFrame()
            if championnat:
                base = df["Championnat"].str.lower() == championnat.lower()
                if pays:
                    base &= df["Pays"].str.lower() == pays.lower()

                # Cas 3 : bet_1 & bet_2 & bet_n
                r = df[base & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2) & (df["Bet365_N"] == bet_n)]

                # Cas 4 : si vide, bet_1 & bet_2
                if r.empty:
                    r = df[base & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2)]

            st.session_state["resultats_interface_2"] = r

        if st.session_state["show_interface_2"] and not st.session_state["resultats_interface_2"].empty:
            afficher_tableau(st.session_state["resultats_interface_2"])
            afficher_pronostics(st.session_state["resultats_interface_2"])

elif choix == "POURCENTAGE BOOK":
    st.subheader("POURCENTAGE BOOK")

    # Menus
    pays = st.selectbox("Pays", options=pays_options, key="pb_pays")
    championnat = st.selectbox("Championnat", options=ligues_options[pays], key="pb_champ")

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1: pin_1 = st.number_input("Pinnacle 1", step=0.01, format="%.2f", key="pb_pin1")
    with col2: pin_n = st.number_input("Pinnacle N", step=0.01, format="%.2f", key="pb_pinn")
    with col3: pin_2 = st.number_input("Pinnacle 2", step=0.01, format="%.2f", key="pb_pin2")
    with col4: bet_1 = st.number_input("Bet365 1", step=0.01, format="%.2f", key="pb_bet1")
    with col5: bet_n = st.number_input("Bet365 N", step=0.01, format="%.2f", key="pb_betn")
    with col6: bet_2 = st.number_input("Bet365 2", step=0.01, format="%.2f", key="pb_bet2")

    with st.expander("Résultats d'analyse"):
        if st.session_state["resultats_interface_1"].empty or st.session_state["resultats_interface_2"].empty:
            st.warning("Aucun résultat trouvé. Lance une analyse d'abord.")
        else:
            st.markdown(
                analyse_croisee(st.session_state["resultats_interface_1"], st.session_state["resultats_interface_2"]),
                unsafe_allow_html=True
            )

    colG, colD = st.columns(2)

    # --- Interface PINNACLE ---
    with colG:
        st.markdown("### PINNACLE")
        if st.button("LANCER PB 1", key="pb_btn_if1"):
            st.session_state["show_interface_1"] = True
            r = pd.DataFrame()
            if pin_1 and pin_2:
                # Cas 1 : Pinnacle_1 + Pinnacle_N + Pinnacle_2
                if pin_n:
                    r = df[
                        (df["Pinnacle_1"] == pin_1) &
                        (df["Pinnacle_N"] == pin_n) &
                        (df["Pinnacle_2"] == pin_2)
                    ]
                # Cas 2 : fallback -> Pinnacle_1 + Pinnacle_2
                if r.empty:
                    r = df[
                        (df["Pinnacle_1"] == pin_1) &
                        (df["Pinnacle_2"] == pin_2)
                    ]
            st.session_state["resultats_interface_1"] = r

        if st.session_state["show_interface_1"] and not st.session_state["resultats_interface_1"].empty:
            afficher_tableau(st.session_state["resultats_interface_1"])
            afficher_pronostics(st.session_state["resultats_interface_1"])

    # --- Interface BET365 ---
    with colD:
        st.markdown("### BET365")
        if st.button("LANCER PB 2", key="pb_btn_if2"):
            st.session_state["show_interface_2"] = True
            r = pd.DataFrame()
            if championnat:
                base = df["Championnat"].str.lower() == championnat.lower()
                if pays:
                    base &= df["Pays"].str.lower() == pays.lower()

                # Cas 3 : bet_1 & bet_2 & bet_n
                r = df[base & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2) & (df["Bet365_N"] == bet_n)]

                # Cas 4 : fallback -> bet_1 & bet_2
                if r.empty:
                    r = df[base & (df["Bet365_1"] == bet_1) & (df["Bet365_2"] == bet_2)]

            st.session_state["resultats_interface_2"] = r

        if st.session_state["show_interface_2"] and not st.session_state["resultats_interface_2"].empty:
            afficher_tableau(st.session_state["resultats_interface_2"])
            afficher_pronostics(st.session_state["resultats_interface_2"])









