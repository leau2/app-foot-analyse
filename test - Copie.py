import requests
import pandas as pd
import streamlit as st
from datetime import datetime
import os
import json

# ============================================================================
# CONFIGURATION ET STYLE
# ============================================================================

st.set_page_config(
    page_title="ISOCSS PRONOSTIC", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Custom pour un look moderne
st.markdown("""
<style>
    /* Thème général */
    .main {
        background-color: #0e1117;
    }
    
    /* En-tête stylé */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 800;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    
    /* Cards modernes */
    .metric-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin: 0.5rem 0;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #c2410c 0%, #f97316 100%);
    }
    
    .metric-label {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    
    /* Section titre */
    .section-header {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366f1;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin: 1rem 0 0.8rem 0;
    }
    
    .section-title {
        color: #6366f1;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* Boutons modernisés */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Tabs stylés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255,255,255,0.05);
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: rgba(255,255,255,0.6);
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Inputs modernisés */
    .stNumberInput>div>div>input {
        border-radius: 8px;
        border: 2px solid rgba(99, 102, 241, 0.3);
        background-color: rgba(255,255,255,0.05);
        color: white;
        font-weight: 600;
    }
    
    .stNumberInput>div>div>input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Selectbox modernisé */
    .stSelectbox>div>div {
        border-radius: 8px;
        background-color: rgba(255,255,255,0.05);
    }
    
    /* Dataframe stylé */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Expander modernisé */
    .streamlit-expanderHeader {
        background-color: rgba(99, 102, 241, 0.1);
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Labels plus compacts */
    .stNumberInput > label, .stSelectbox > label, .stTextInput > label {
        font-size: 0.85rem !important;
        font-weight: 500;
        margin-bottom: 0.3rem !important;
    }
    
    /* Réduction de l'espace entre les inputs */
    .stNumberInput, .stSelectbox, .stTextInput {
        margin-bottom: 0.5rem;
    }
    
    /* Style des text inputs pour les cotes */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid rgba(99, 102, 241, 0.3);
        background-color: rgba(255,255,255,0.05);
        color: white;
        font-weight: 600;
        text-align: center;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DONNÉES ET HELPERS
# ============================================================================

pays_options = ['Australia', 'Argentina', 'Brazil', 'Belgium', 'England', 'Europe', 
                'France', 'Germany', 'Italy', 'Spain', 'Portugal', 'Turkey', 'Netherlands', 'USA']

ligues_options = {
    'Argentina': ['Liga Profesional'],
    'Australia': ['A League'],
    'Brazil': ['Serie A'],
    'Belgium': ['Jupiter Pro League'],
    'England': ['Premier League'],
    'Europe': ['Champions League', 'Europa League'],
    'France': ['Ligue 1', 'Ligue 2'],
    'Germany': ['Bundesliga'],
    'Italy': ['Serie A'],
    'Spain': ['LaLiga'],
    'Portugal': ['Liga Portugal'],
    'Turkey': ['Super Lig'],
    'Netherlands': ['Eredivisie'],
    'USA': ['MLS']
}

# Session state
if "resultats_interface_1" not in st.session_state:
    st.session_state["resultats_interface_1"] = pd.DataFrame()
if "resultats_interface_2" not in st.session_state:
    st.session_state["resultats_interface_2"] = pd.DataFrame()

# Helper pour convertir les cotes saisies
def parse_cote(raw_value):
    """Convertit une cote saisie (accepte , ou .) en float ou None"""
    if not raw_value or not raw_value.strip():
        return None
    s = raw_value.strip().replace(" ", "").replace(",", ".")
    try:
        return round(float(s), 2)
    except ValueError:
        return None

@st.cache_data
def charger_fichier():
    df = pd.read_excel(
        "https://www.dropbox.com/scl/fi/hmuzsmfh0zrqhsjkx3u9v/FTPINNACLEBET365.xlsx?rlkey=2xpjhij52j6qlt9vf5j1bzohx&st=30bzfp5q&raw=1", 
        skiprows=2, 
        header=None
    )
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

# ============================================================================
# FONCTIONS MÉTIER
# ============================================================================

def analyser_pinnacle(df_source, pin_1, pin_n, pin_2, bet_1, bet_2):
    """Logique d'analyse pour Pinnacle"""
    r = pd.DataFrame()
    if pin_1 and pin_2:
        if pin_n:
            r = df_source[(df_source["Pinnacle_1"] == pin_1) & 
                          (df_source["Pinnacle_N"] == pin_n) & 
                          (df_source["Pinnacle_2"] == pin_2)]
        if r.empty and bet_1 and bet_2:
            r = df_source[(df_source["Pinnacle_1"] == pin_1) & 
                          (df_source["Pinnacle_2"] == pin_2) &
                          (df_source["Bet365_1"] == bet_1) & 
                          (df_source["Bet365_2"] == bet_2)]
        if r.empty:
            r = pd.concat([
                df_source[(df_source["Pinnacle_1"] == pin_1) & 
                          (df_source["Pinnacle_2"] == pin_2) & 
                          (df_source["Bet365_1"] == bet_1)],
                df_source[(df_source["Pinnacle_1"] == pin_1) & 
                          (df_source["Pinnacle_2"] == pin_2) & 
                          (df_source["Bet365_2"] == bet_2)]
            ])
        if r.empty:
            r = df_source[(df_source["Pinnacle_1"] == pin_1) & 
                          (df_source["Pinnacle_2"] == pin_2)]
    return r

def analyser_bet365(df_source, pays, championnat, bet_1, bet_n, bet_2, pin_1=None, pin_2=None):
    """Logique d'analyse pour Bet365"""
    r = pd.DataFrame()
    if championnat:
        base = df_source["Championnat"].str.lower() == championnat.lower()
        if pays:
            base &= df_source["Pays"].str.lower() == pays.lower()
        
        # Tentative avec pin_1 et pin_2 si fournis
        if pin_1 and pin_2:
            r1 = df_source[base & (df_source["Bet365_1"] == bet_1) & 
                           (df_source["Bet365_2"] == bet_2) & 
                           (df_source["Pinnacle_1"] == pin_1)]
            r2 = df_source[base & (df_source["Bet365_1"] == bet_1) & 
                           (df_source["Bet365_2"] == bet_2) & 
                           (df_source["Pinnacle_2"] == pin_2)]
            r = pd.concat([r1, r2]).drop_duplicates()
        
        if r.empty and bet_n:
            r = df_source[base & (df_source["Bet365_1"] == bet_1) & 
                          (df_source["Bet365_2"] == bet_2) & 
                          (df_source["Bet365_N"] == bet_n)]
        if r.empty:
            r = df_source[base & (df_source["Bet365_1"] == bet_1) & 
                          (df_source["Bet365_2"] == bet_2)]
    return r

def color_result(val):
    if val == 'H': return f"<span style='color:#10b981; font-weight:bold; font-size:1.1rem'>🏠 {val}</span>"
    if val == 'D': return f"<span style='color:#ef4444; font-weight:bold; font-size:1.1rem'>⚖️ {val}</span>"
    if val == 'A': return f"<span style='color:#3b82f6; font-weight:bold; font-size:1.1rem'>✈️ {val}</span>"
    return val

def afficher_tableau_moderne(resultats):
    """Affiche un tableau stylé avec les résultats"""
    if resultats.empty:
        st.info("📊 Aucun résultat à afficher")
        return
    
    df_display = resultats.copy()
    df_display["Score"] = df_display["Score_Dom"].astype(str) + " - " + df_display["Score_Ext"].astype(str)
    df_display["Résultat"] = df_display["Resultat"].apply(color_result)
    
    # Affichage avec dataframe interactif
    st.markdown("### 📋 Historique des matchs")
    st.write(df_display[[ 
        'Pinnacle_1', 'Pinnacle_N', 'Pinnacle_2',
        'Bet365_1', 'Bet365_N', 'Bet365_2',
        'Score', 'Résultat'
    ]].to_html(escape=False, index=False), unsafe_allow_html=True)

def afficher_stats_modernes(resultats):
    """Affiche les stats avec des metrics cards modernes"""
    if resultats.empty:
        return
    
    counts = resultats['Resultat'].value_counts()
    total = counts.sum()
    
    st.markdown("### 📊 Statistiques du match")
    
    # Résultats du match
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dom_pct = round((counts.get('H', 0) / total) * 100) if total > 0 else 0
        st.markdown(f"""
        <div class="metric-card metric-card-green">
            <div class="metric-label">🏠 Victoire Domicile</div>
            <div class="metric-value">{dom_pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        nul_pct = round((counts.get('D', 0) / total) * 100) if total > 0 else 0
        st.markdown(f"""
        <div class="metric-card metric-card-orange">
            <div class="metric-label">⚖️ Match Nul</div>
            <div class="metric-value">{nul_pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ext_pct = round((counts.get('A', 0) / total) * 100) if total > 0 else 0
        st.markdown(f"""
        <div class="metric-card metric-card-blue">
            <div class="metric-label">✈️ Victoire Extérieur</div>
            <div class="metric-value">{ext_pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats buts
    st.markdown("### ⚽ Statistiques des buts")
    total_buts = pd.to_numeric(resultats["Score_Dom"], errors='coerce') + pd.to_numeric(resultats["Score_Ext"], errors='coerce')
    dom = pd.to_numeric(resultats["Score_Dom"], errors='coerce')
    ext = pd.to_numeric(resultats["Score_Ext"], errors='coerce')
    
    col1, col2 = st.columns(2)
    
    with col1:
        over_pct = round((total_buts > 2.5).sum() / total * 100) if total > 0 else 0
        under_pct = 100 - over_pct
        st.metric("📈 Over 2.5", f"{over_pct}%")
        st.metric("📉 Under 2.5", f"{under_pct}%")
    
    with col2:
        btts_yes = ((dom > 0) & (ext > 0)).sum()
        yes_pct = round(btts_yes / total * 100) if total > 0 else 0
        no_pct = 100 - yes_pct
        st.metric("✅ BTTS Oui", f"{yes_pct}%")
        st.metric("❌ BTTS Non", f"{no_pct}%")

def analyse_croisee(r1, r2):
    """Génère l'analyse croisée entre deux résultats"""
    if r1.empty or r2.empty:
        return "⚠️ Données insuffisantes pour l'analyse croisée"
    
    bloc = ""
    
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
    
    # Buts
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
    
    # BTTS
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
    
    return bloc or "⚠️ Pas de pronostic croisé valide (seuils non atteints)"

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

# Header moderne
st.markdown("""
<div class="header-container">
    <h1 class="header-title">⚽ ISOCSS PRONOSTIC</h1>
    <p class="header-subtitle">Analyse avancée de matchs de football basée sur les cotes</p>
</div>
""", unsafe_allow_html=True)

# Navigation par tabs (moderne)
tab1, tab2, tab3 = st.tabs(["🎯 Analyser un match", "🤖 Analyse IA", "📊 Pourcentage Book"])

# ============================================================================
# TAB 1: ANALYSER UN MATCH
# ============================================================================

with tab1:
    st.markdown('<div class="section-header"><h2 class="section-title">🎯 Analyse d\'un match</h2></div>', unsafe_allow_html=True)
    
    # Formulaire pour les paramètres
    with st.form("form_analyse_match"):
        # Pays et Championnat sur une seule ligne compacte
        col1, col2 = st.columns([1, 1])
        with col1:
            pays = st.selectbox("🌍 Pays", options=pays_options, key="am_pays")
        with col2:
            championnat = st.selectbox("🏆 Championnat", options=ligues_options[pays], key="am_champ")
        
        # Cotes en grille compacte 2x3
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("**📊 Pinnacle**")
            col1, col2, col3 = st.columns(3)
            with col1:
                pin_1 = st.text_input("1", key="am_pin1")
            with col2:
                pin_n = st.text_input("N", key="am_pinn")
            with col3:
                pin_2 = st.text_input("2", key="am_pin2")
        
        with col_right:
            st.markdown("**📊 Bet365**")
            col1, col2, col3 = st.columns(3)
            with col1:
                bet_1 = st.text_input("1", key="am_bet1")
            with col2:
                bet_n = st.text_input("N", key="am_betn")
            with col3:
                bet_2 = st.text_input("2", key="am_bet2")
        
        submitted = st.form_submit_button("🚀 Lancer l'analyse", use_container_width=True)
        
        if submitted:
            with st.spinner("🔍 Analyse en cours..."):
                # Conversion des cotes
                pin_1_val = parse_cote(pin_1)
                pin_n_val = parse_cote(pin_n)
                pin_2_val = parse_cote(pin_2)
                bet_1_val = parse_cote(bet_1)
                bet_n_val = parse_cote(bet_n)
                bet_2_val = parse_cote(bet_2)
                
                # Analyse Pinnacle
                st.session_state["resultats_interface_1"] = analyser_pinnacle(
                    df, pin_1_val, pin_n_val, pin_2_val, bet_1_val, bet_2_val
                )
                # Analyse Bet365
                st.session_state["resultats_interface_2"] = analyser_bet365(
                    df, pays, championnat, bet_1_val, bet_n_val, bet_2_val, pin_1_val, pin_2_val
                )
            st.success("✅ Analyse terminée !")
    
    # Affichage des résultats
    if not st.session_state["resultats_interface_1"].empty or not st.session_state["resultats_interface_2"].empty:
        
        # Analyse croisée
        with st.expander("🎯 Analyse Croisée", expanded=True):
            st.markdown(analyse_croisee(
                st.session_state["resultats_interface_1"], 
                st.session_state["resultats_interface_2"]
            ), unsafe_allow_html=True)
        
        # Résultats côte à côte
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header"><h3 class="section-title">📌 Résultats Pinnacle</h3></div>', unsafe_allow_html=True)
            if not st.session_state["resultats_interface_1"].empty:
                afficher_tableau_moderne(st.session_state["resultats_interface_1"])
                afficher_stats_modernes(st.session_state["resultats_interface_1"])
            else:
                st.info("Aucun résultat Pinnacle")
        
        with col2:
            st.markdown('<div class="section-header"><h3 class="section-title">📌 Résultats Bet365</h3></div>', unsafe_allow_html=True)
            if not st.session_state["resultats_interface_2"].empty:
                afficher_tableau_moderne(st.session_state["resultats_interface_2"])
                afficher_stats_modernes(st.session_state["resultats_interface_2"])
            else:
                st.info("Aucun résultat Bet365")

# ============================================================================
# TAB 2: ANALYSE IA
# ============================================================================

with tab2:
    st.markdown('<div class="section-header"><h2 class="section-title">🤖 Analyse IA</h2></div>', unsafe_allow_html=True)
    
    with st.form("form_ia"):
        col1, col2 = st.columns(2)
        with col1:
            pays_ia = st.selectbox("🌍 Pays", options=pays_options, key="ia_pays")
        with col2:
            champ_ia = st.selectbox("🏆 Championnat", options=ligues_options[pays_ia], key="ia_champ")
        
        st.markdown("#### 📊 Cotes Pinnacle")
        col1, col2, col3 = st.columns(3)
        with col1:
            pin_1_ia = st.text_input("1", key="ia_pin1")
        with col2:
            pin_n_ia = st.text_input("N", key="ia_pinn")
        with col3:
            pin_2_ia = st.text_input("2", key="ia_pin2")
        
        st.markdown("#### 📊 Cotes Bet365")
        col1, col2, col3 = st.columns(3)
        with col1:
            bet_1_ia = st.text_input("1", key="ia_bet1")
        with col2:
            bet_n_ia = st.text_input("N", key="ia_betn")
        with col3:
            bet_2_ia = st.text_input("2", key="ia_bet2")
        
        submitted_ia = st.form_submit_button("🚀 Lancer l'IA", use_container_width=True)
        
        if submitted_ia:
            with st.spinner("🤖 L'IA analyse..."):
                # Conversion des cotes
                pin_1_val = parse_cote(pin_1_ia)
                pin_n_val = parse_cote(pin_n_ia)
                pin_2_val = parse_cote(pin_2_ia)
                bet_1_val = parse_cote(bet_1_ia)
                bet_n_val = parse_cote(bet_n_ia)
                bet_2_val = parse_cote(bet_2_ia)
                
                st.session_state["resultats_interface_1"] = analyser_pinnacle(
                    df, pin_1_val, pin_n_val, pin_2_val, bet_1_val, bet_2_val
                )
                # Pour l'IA, uniquement Bet365 dans le championnat
                st.session_state["resultats_interface_2"] = analyser_bet365(
                    df, pays_ia, champ_ia, bet_1_val, bet_n_val, bet_2_val
                )
            st.success("✅ Analyse IA terminée !")
    
    # Affichage identique à Tab1
    if not st.session_state["resultats_interface_1"].empty or not st.session_state["resultats_interface_2"].empty:
        with st.expander("🎯 Analyse Croisée", expanded=True):
            st.markdown(analyse_croisee(
                st.session_state["resultats_interface_1"], 
                st.session_state["resultats_interface_2"]
            ), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header"><h3 class="section-title">📌 PINNACLE</h3></div>', unsafe_allow_html=True)
            if not st.session_state["resultats_interface_1"].empty:
                afficher_tableau_moderne(st.session_state["resultats_interface_1"])
                afficher_stats_modernes(st.session_state["resultats_interface_1"])
        
        with col2:
            st.markdown('<div class="section-header"><h3 class="section-title">📌 BET365</h3></div>', unsafe_allow_html=True)
            if not st.session_state["resultats_interface_2"].empty:
                afficher_tableau_moderne(st.session_state["resultats_interface_2"])
                afficher_stats_modernes(st.session_state["resultats_interface_2"])

# ============================================================================
# TAB 3: POURCENTAGE BOOK
# ============================================================================

with tab3:
    st.markdown('<div class="section-header"><h2 class="section-title">📊 Pourcentage Book</h2></div>', unsafe_allow_html=True)
    
    with st.form("form_book"):
        col1, col2 = st.columns(2)
        with col1:
            pays_pb = st.selectbox("🌍 Pays", options=pays_options, key="pb_pays")
        with col2:
            champ_pb = st.selectbox("🏆 Championnat", options=ligues_options[pays_pb], key="pb_champ")
        
        st.markdown("#### 📊 Cotes Pinnacle")
        col1, col2, col3 = st.columns(3)
        with col1:
            pin_1_pb = st.text_input("1", key="pb_pin1")
        with col2:
            pin_n_pb = st.text_input("N", key="pb_pinn")
        with col3:
            pin_2_pb = st.text_input("2", key="pb_pin2")
        
        st.markdown("#### 📊 Cotes Bet365")
        col1, col2, col3 = st.columns(3)
        with col1:
            bet_1_pb = st.text_input("1", key="pb_bet1")
        with col2:
            bet_n_pb = st.text_input("N", key="pb_betn")
        with col3:
            bet_2_pb = st.text_input("2", key="pb_bet2")
        
        submitted_pb = st.form_submit_button("🚀 Lancer l'analyse", use_container_width=True)
        
        if submitted_pb:
            with st.spinner("📊 Calcul des pourcentages..."):
                # Conversion des cotes
                pin_1_val = parse_cote(pin_1_pb)
                pin_n_val = parse_cote(pin_n_pb)
                pin_2_val = parse_cote(pin_2_pb)
                bet_1_val = parse_cote(bet_1_pb)
                bet_n_val = parse_cote(bet_n_pb)
                bet_2_val = parse_cote(bet_2_pb)
                
                # Pour Book: logique simplifiée (cas 1 et 2 pour Pinnacle)
                r_pin = pd.DataFrame()
                if pin_1_val and pin_2_val:
                    if pin_n_val:
                        r_pin = df[(df["Pinnacle_1"] == pin_1_val) & 
                                   (df["Pinnacle_N"] == pin_n_val) & 
                                   (df["Pinnacle_2"] == pin_2_val)]
                    if r_pin.empty:
                        r_pin = df[(df["Pinnacle_1"] == pin_1_val) & 
                                   (df["Pinnacle_2"] == pin_2_val)]
                st.session_state["resultats_interface_1"] = r_pin
                
                # Bet365: cas 3 et 4
                st.session_state["resultats_interface_2"] = analyser_bet365(
                    df, pays_pb, champ_pb, bet_1_val, bet_n_val, bet_2_val
                )
            st.success("✅ Analyse Book terminée !")
    
    # Affichage
    if not st.session_state["resultats_interface_1"].empty or not st.session_state["resultats_interface_2"].empty:
        with st.expander("🎯 Analyse Croisée", expanded=True):
            st.markdown(analyse_croisee(
                st.session_state["resultats_interface_1"], 
                st.session_state["resultats_interface_2"]
            ), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header"><h3 class="section-title">📌 PINNACLE</h3></div>', unsafe_allow_html=True)
            if not st.session_state["resultats_interface_1"].empty:
                afficher_tableau_moderne(st.session_state["resultats_interface_1"])
                afficher_stats_modernes(st.session_state["resultats_interface_1"])
        
        with col2:
            st.markdown('<div class="section-header"><h3 class="section-title">📌 BET365</h3></div>', unsafe_allow_html=True)
            if not st.session_state["resultats_interface_2"].empty:
                afficher_tableau_moderne(st.session_state["resultats_interface_2"])
                afficher_stats_modernes(st.session_state["resultats_interface_2"])

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.5);'>⚽ ISOCSS PRONOSTIC © 2025 - Analyse professionnelle de paris sportifs</p>", 
    unsafe_allow_html=True
)
