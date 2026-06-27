import streamlit as st
import pandas as pd
import time
import requests
import json
import os
from streamlit_autorefresh import st_autorefresh


# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(layout="wide")
st.set_page_config(page_title="Dashboard GRT", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=1000, key="datarefresh")

st.markdown("""
    <style>
    .stApp { background-color: #0b0c10; color: #ffffff; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    <style>
        [data-testid="stSidebar"] {display: none;}
    
    /* Box Container */
    .racing-box, .kart-box { 
        background-color: #12171e; padding: 20px; border-radius: 12px; 
        border-left: 6px solid #ffcc00; text-align: center; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .kart-warning { border-left-color: #e65100 !important; } 
    .kart-critical { border-left-color: #ff1744 !important; }
    .label-box { color: #888; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
    .timer-big { font-size: 40px; font-weight: 900; color: #ffffff; font-family: 'Courier New', monospace; }
    
    /* Pulsanti */
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: 800; height: 50px; border: none; transition: transform 0.1s ease; }
    div.stButton > button:hover { transform: scale(1.02); }
    div.stButton > button { background-color: #1a521c; color: white; }
    
    /* Animazioni */
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .blink-active { animation: blink 0.8s linear infinite; color: #ff1744 !important; }
    .radar-header { color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 15px; border-bottom: 2px solid #333; padding-bottom: 5px; }
    
    /* Navbar Tabs potenziate */
    div[data-baseweb="tab-list"] { background-color: #1a1f26; padding: 10px; border-radius: 12px; }
    button[data-baseweb="tab"] { font-size: 18px !important; font-weight: 800 !important; color: white !important; }
    button[aria-selected="true"] { background-color: #ffcc00 !important; color: #000 !important; border-radius: 8px !important; }
    </style>
""", unsafe_allow_html=True)
# --- 2. FUNZIONI (Logica e Dati) ---
MIO_TEAM = "GOATS RT RED"
API_URL = "https://youcrono.com/Pagina/6449/LiveTbkart"
BACKUP_FILE = "gara_backup.json"

def salva_dati(dati):
    with open(BACKUP_FILE, "w") as f:
        json.dump(dati, f)

def carica_dati():
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r") as f:
            return json.load(f)
    return []

def ottieni_dati_aggiornati():
    # Aggiungiamo un header per far credere al server di essere un browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # Usiamo l'header nella chiamata
        response = requests.get(API_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                dati_puliti = [{"pos": r.get("Position", "-"), "team": r.get("TeamName", "N/D"), "ultimo_giro": r.get("LastLapTime", "00:00.000"), "kart": r.get("KartNumber", "0")} for r in data]
                salva_dati(dati_puliti)
                return dati_puliti
        else:
            # Se ricevi un errore (es. 403), lo vediamo subito in dashboard
            st.error(f"Errore connessione YouCrono: Codice {response.status_code}")
            return carica_dati()
            
    except Exception as e:
        # Se c'è un errore di rete (timeout o DNS), lo vediamo qui
        st.error(f"Errore di connessione: {e}")
        return carica_dati()
# --- 3. INIZIALIZZAZIONE STATI ---
def inizializza_stato():
    defaults = {
        "autenticato": False,
        "database_rivali_v2": carica_dati(),
        "archivio_performance": {"22": {"qualita": "Top"}, "14": {"qualita": "Medio"}},
        "piloti_v2": {"Kevin Liguori": {"in_pista": True, "tempo_totale_sec": 0}, "Bruno Colombo": {"in_pista": False, "tempo_totale_sec": 0}, "Daniele Rossi": {"in_pista": False, "tempo_totale_sec": 0}},
        "conferma_cambio_kart": False,
        "timestamp_start_gara": time.time(),
        "timestamp_start_kart": time.time(),
        "radar_is_pit_lane": False,
        "storico_tempi": {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_dati_mio_team(dati_live):
    # Cerca il tuo team nel JSON di YouCrono
    for record in dati_live:
        if record['team'] == MIO_TEAM:
            return record
    return None

def tempo_in_secondi(tempo_str):
    try:
        # Se il tempo è "01:05.123", lo split(':') funziona
        minuti, secondi = tempo_str.split(':')
        return float(minuti) * 60 + float(secondi)
    except:
        return 0
    
    # --- LOGICA DI POPOLAMENTO AUTOMATICO DATI ---
def aggiorna_storico_tempi():
    dati_live = st.session_state.database_rivali_v2
    for record in dati_live:
        kart = record.get('kart')
        tempo_str = record.get('ultimo_giro', "00:00.000")
        tempo_sec = tempo_in_secondi(tempo_str)
        
        # Ignora dati non validi
        if tempo_sec == 0: continue
        
        # Inizializza la lista per il kart se non esiste
        if kart not in st.session_state.storico_tempi:
            st.session_state.storico_tempi[kart] = []
            
        # Aggiungi solo se il tempo è nuovo (evita duplicati continui)
        if not st.session_state.storico_tempi[kart] or st.session_state.storico_tempi[kart][-1] != tempo_sec:
            st.session_state.storico_tempi[kart].append(tempo_sec)

# Chiamiamo la funzione subito dopo aver ottenuto i dati dallo scraper
# Dentro la funzione 'aggiorna_dati_scraper' (che hai già definito):
@st.fragment(run_every=5.0)
def aggiorna_dati_scraper():
    dati_live = ottieni_dati_aggiornati()
    if dati_live:
        st.session_state.database_rivali_v2 = dati_live
        aggiorna_storico_tempi() # <--- AGGIUNGI QUESTA RIGA

# ... (dopo tutte le tue funzioni: salva_dati, ottieni_dati, aggiorna_storico_tempi, ecc.)

# --- 5. SIDEBAR E NAVIGAZIONE ---
# ... (il tuo codice della sidebar)

# --- INSERISCI QUI IL BLOCCO DEL LIVE TIMING ---
def visualizza_live_timing_integrato():
    st.subheader("⏱️ Live Timing Ufficiale")
    if st.session_state.database_rivali_v2:
        df = pd.DataFrame(st.session_state.database_rivali_v2)
        # Rinominiamo per chiarezza
        df = df.rename(columns={"pos": "Pos", "team": "Team", "ultimo_giro": "Ultimo Lap", "kart": "Kart"})
        st.table(df[['Pos', 'Team', 'Ultimo Lap', 'Kart']])
        st.link_button("Vai al Live Timing Esterno", "https://youcrono.com/api/LiveTiming/GetLiveTiming?idPagina=6449")
    else:
        st.warning("Nessun dato live disponibile.")

# --- DEFINIZIONE PAGINE ---
# ... (il resto del tuo codice con st.tabs e il ciclo for)
inizializza_stato()

# --- 4. LOGIN ---
if not st.session_state.autenticato:
    st.title("ACCESSO CENTRALINA BOX")
    if st.text_input("PASSWORD:", type="password") == "1234":
        if st.button("SBLOCCA 🔒"):
            st.session_state.autenticato = True
            st.rerun()
    st.stop()

# --- 5. SIDEBAR E NAVIGAZIONE ---
st.sidebar.image("https://img.icons8.com/nolan/64/filled-treadmill.png", width=50)
st.sidebar.title("GRT Control Panel")

# --- DEFINIZIONE PAGINE ---
# --- 1. DEFINIZIONE FUNZIONI (FUORI DAI CICLI) ---
@st.fragment(run_every=5.0)
def aggiorna_dati_scraper():
    dati_live = ottieni_dati_aggiornati()
    if dati_live:
        st.session_state.database_rivali_v2 = dati_live

def render_active_dashboard():
    aggiorna_dati_scraper()
    st.write("--- Dati grezzi ricevuti ---")
    st.write(st.session_state.database_rivali_v2)

# --- 2. DEFINIZIONE PAGINE ---
nomi_pagine = [
    "🏎️ Dashboard Gara", "📊 Valutazione Kart Live", "📊 Strategia", 
    "📡 Live Timing", "🛠️ Kart's Performance", "📜 Regolamento", 
    "📻 Radio", "📊 Archivio Gare", "🛠️ Configurazione GRB"
]
tab_list = st.tabs(nomi_pagine)

# --- 3. CICLO DI NAVIGAZIONE UNICO ---
for i, nome in enumerate(nomi_pagine):
    with tab_list[i]:
        if nome == "🏎️ Dashboard Gara":
            st.subheader("🏎️ Stato GOATS RT RED")
            # ... (il tuo codice esistente per i dati del tuo team)
            
            # AGGIUNGI QUESTA RIGA QUI SOTTO:
            visualizza_live_timing_integrato()
            dati_miei = get_dati_mio_team(st.session_state.database_rivali_v2)
            if dati_miei:
                col1, col2 = st.columns(2)
                col1.metric("Posizione", dati_miei['pos'])
                col2.metric("Ultimo Tempo", dati_miei['ultimo_giro'])
            else:
                st.warning("GOATS RT RED non trovato nel Live Timing.")
            
            # Costanti
            LIMITE_GARA_SEC = 8 * 3600
            LIMITE_KART_SEC = 4 * 3600

            # 1. Inizializzazione Session State
            if 'timestamp_start_gara' not in st.session_state:
                st.session_state.timestamp_start_gara = time.time()
            if 'timestamp_start_kart' not in st.session_state:
                st.session_state.timestamp_start_kart = time.time()
            if 'piloti_v2' not in st.session_state:
                st.session_state.piloti_v2 = {
                    "Pilota 1": {"tempo_totale_sec": 0, "in_pista": True}, 
                    "Pilota 2": {"tempo_totale_sec": 0, "in_pista": False}
                }

            # 2. Calcoli
            tempo_trascorso_gara = time.time() - st.session_state.timestamp_start_gara
            tempo_trascorso_kart = time.time() - st.session_state.timestamp_start_kart
            
            gara_rimanente_sec = max(0, LIMITE_GARA_SEC - tempo_trascorso_gara)
            kart_rimanente_sec = max(0, LIMITE_KART_SEC - tempo_trascorso_kart)

            # 3. Layout Visuale
            st.progress(max(0.0, min(1.0, (tempo_trascorso_gara / LIMITE_GARA_SEC))))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="racing-box"><div class="label-box">GARA</div><div class="timer-big">{int(gara_rimanente_sec // 3600):02d}:{int((gara_rimanente_sec % 3600) // 60):02d}:{int(gara_rimanente_sec % 60):02d}</div></div>', unsafe_allow_html=True)
            with col2:
                colore_box = "kart-box kart-critical" if kart_rimanente_sec < 300 else ("kart-box kart-warning" if kart_rimanente_sec < 600 else "kart-box")
                st.markdown(f'<div class="{colore_box}"><div class="label-box">KART</div><div class="timer-big">{int(kart_rimanente_sec // 3600):02d}:{int((kart_rimanente_sec % 3600) // 60):02d}:{int(kart_rimanente_sec % 60):02d}</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="radar-header">🔮 Radar Automazioni</div>', unsafe_allow_html=True)
                if st.button("🟩 CAMBIO KART", key=f"btn_swap_{i}"):
                    st.session_state.conferma_cambio_kart = True
                    st.rerun()


            # --- GESTIONE PILOTI E RADAR ---
            col_sx, col_dx = st.columns([2, 1])
            with col_sx:
                st.markdown("#### 👤 Gestione Piloti")
                cols = st.columns(len(st.session_state.piloti_v2))
                for idx, (nome_p, dati_p) in enumerate(st.session_state.piloti_v2.items()):
                    with cols[idx]:
                        st.markdown(f"**{nome_p}**<br>{int(dati_p['tempo_totale_sec']//60)}m", unsafe_allow_html=True)
                
                p_sel = st.selectbox("Nuovo pilota:", list(st.session_state.piloti_v2.keys()), key=f"sel_{i}")
                if st.button("🔄 Swap", key=f"swap_{i}"):
                    st.session_state.piloti_v2[p_sel]["in_pista"] = True
                    st.rerun()

            with col_dx:
                st.markdown("#### 🚨 Radar")
                if st.button("🚨 PIT", key=f"pit_{i}"): 
                    st.session_state.radar_is_pit_lane = True
                if st.session_state.get("radar_is_pit_lane"):
                    st.warning("PIT LANE ATTIVA")


        elif nome == "📊 Valutazione Kart Live":
            st.subheader("📊 Valutazione Performance Kart")
            
            if 'storico_tempi' in st.session_state and st.session_state.storico_tempi:
                dati_valutazione = []
                
                for kart, tempi in st.session_state.storico_tempi.items():
                    if len(tempi) >= 3: 
                        ultimi_20 = tempi[-20:]
                        media_mobile = sum(ultimi_20) / len(ultimi_20)
                        best_lap_mobile = min(ultimi_20)
                        
                        dati_valutazione.append({
                            "Kart": kart, 
                            "Media (20g)": round(media_mobile, 3),
                            "Best Lap (20g)": round(best_lap_mobile, 3)
                        })
                
                if dati_valutazione:
                    df_val = pd.DataFrame(dati_valutazione)
                    media_globale = df_val["Media (20g)"].mean()
                    
                    # Logica valutativa migliorata
                    def get_emoji(tempo):
                        if tempo < (media_globale - 0.4): return "🚀 Top"
                        elif tempo > (media_globale + 0.3): return "💩 Lento"
                        else: return "🏎️ Standard"
                    
                    df_val["Valutazione"] = df_val["Media (20g)"].apply(get_emoji)
                    
                    # Ordinamento e visualizzazione
                    st.dataframe(
                        df_val.sort_values("Media (20g)"), 
                        use_container_width=True, 
                        hide_index=True
                    )
                else:
                    st.info("Raccolta dati in corso... (attendo almeno 3 giri per kart)")
            else:
                st.info("Nessun dato ancora ricevuto da YouCrono.")

        elif nome == "📊 Strategia":
            st.title("📊 Strategia Endurance - GRT")

            # --- 1. TABELLA CENTRALE DI RIEPILOGO ---
            st.subheader("🏁 Riassunto Strategico")
            dati_riepilogo = {
                "Parametro": ["Giri Totali Stimati", "Tempo Medio Stint", "Gap Teorico (s)", "Stato Box"],
                "Valore": ["450", "45 min", "0", "Aperto"]
            }
            st.table(pd.DataFrame(dati_riepilogo))

            # --- 2. CALCOLO GAP AVVERSARIO ---
            st.subheader("⚔️ Analisi Gap Avversario")
            col_gap1, col_gap2 = st.columns(2)
            with col_gap1:
                distacco_pista = st.number_input("Distacco in Pista (s):", value=0.0)
            with col_gap2:
                diff_pit = st.number_input("Differenza Totale Pit (s):", value=0.0)
            
            gap_reale = distacco_pista - diff_pit
            st.metric("Gap Reale (s)", f"{gap_reale:.2f}", delta=f"{-diff_pit}")

            # --- 3. CALCOLO TEMPO MEDIO STINT ---
            st.subheader("⏱️ Monitoraggio Stint")
            if "stint_tempi" in st.session_state and st.session_state.stint_tempi:
                media = sum(st.session_state.stint_tempi) / len(st.session_state.stint_tempi)
                st.write(f"Tempo medio stint: **{media:.2f} minuti**")
            else:
                st.write("Nessun dato di stint disponibile.")

            # --- 4. GESTIONE PILOTI ---
            st.divider()
            st.subheader("👤 Swap Piloti")
            if "piloti_v2" in st.session_state:
                for nome_p, dati in st.session_state.piloti_v2.items():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"🏎️ {nome_p}")
                    c2.write("In Pista" if dati["in_pista"] else "Box")
                    if c3.button("🔄 Swap", key=f"swap_{nome_p}"):
                        st.session_state.piloti_v2[nome_p]["in_pista"] = not st.session_state.piloti_v2[nome_p]["in_pista"]
                        st.rerun()
            else:
                st.warning("Configura i piloti nel pannello 'Configurazione GRB'.")
        elif nome == "🛠️ Kart's Performance":
            st.title("🛠️ Gestione e Performance Kart")
            st.write("Area tecnica per il tracciamento dei telai e la sincronizzazione dell'estrazione del sabato.")
            st.write("---")

            tab_estrazione, tab_archivio = st.tabs(["🏁 Sincronizzazione Sabato Mattina", "📂 Archivio Continuo Telai"])

            if "lista_team_dinamica" not in st.session_state:
                st.session_state.lista_team_dinamica = [
                    "KARTEL", "GOATS RT RED", "PF RACING", "BREMO 58", "KRT", 
                    "TEAM LIECHTENSTEIN", "GAS RT", "KMRS PERFORMANCE", "SKART WORKING BETTER", 
                    "SKART WORKING FASTER", "NEXUS RACING", "GOATS RT BLACK", "BREMO 69", 
                    "HUULIA PINK", "LIONS FURY RT", "DMS RACING", "ROMA KARTING SEVEN", 
                    "SPARKART RACING", "SKART WORKING HARDER", "FINBUS RACING", "KMRS RACING", 
                    "NEXUS SPORT", "SLIPSTREAM RACING", "BREMO 77", "GOATS RT ORANGE", 
                    "GOATS RT WHITE", "KARTEL ACADEMY", "RED RACING", "ASV RACING", 
                    "KARTEL SPORT", "GAS MASTER", "AEM TWICE RACING", "GO RACING", 
                    "CANNES RACING THALES PRO TEAM", "KARTEL PRODIGY", "PIENO MOTORSPORT", 
                    "AEM RACING ASD", "TRX THE RACE ACADEMY", "MRC RACING TEAM", 
                    "RED RACING SPIRIT", "CRAZY HORSES RACING"
                ]

            with tab_estrazione:
                st.subheader("🎯 Accoppiamento Rapido Team ➔ Kart")
                
                if "griglia_estrazione_sabato" not in st.session_state:
                    st.session_state.griglia_estrazione_sabato = [
                        {"Seleziona": False, "Team": "GOATS RT RED", "N° Kart Estratto": "Kart 14"},
                        {"Seleziona": False, "Team": "KARTEL", "N° Kart Estratto": "Kart 22"},
                        {"Seleziona": False, "Team": "PF RACING", "N° Kart Estratto": "Kart 05"}
                    ]

                opzioni_tendina = st.session_state.lista_team_dinamica + ["➕ AGGIUNGI NUOVO TEAM..."]
                
                col_add1, col_add2, col_add3, col_add4 = st.columns([2, 1, 1, 1])
                with col_add1:
                    team_scelto = st.selectbox("Seleziona il Team:", options=opzioni_tendina, key="sb_team_select")
                with col_add2:
                    kart_scelto = st.text_input("N° Kart Estratto:", value="", placeholder="Es. Kart 45", key="txt_kart_input")
                
                team_finale = team_scelto
                if team_scelto == "➕ AGGIUNGI NUOVO TEAM...":
                    nuovo_team_nome = st.text_input("✍️ Scrivi il nome del Nuovo Team:", placeholder="Es. Winner Team 1").upper()
                    team_finale = nuovo_team_nome

                with col_add3:
                    st.write(" ")
                    st.write(" ")
                    if st.button("⚡ Inserisci", use_container_width=True):
                        if team_finale and kart_scelto:
                            if team_scelto == "➕ AGGIUNGI NUOVO TEAM..." and team_finale not in st.session_state.lista_team_dinamica:
                                st.session_state.lista_team_dinamica.append(team_finale)
                            
                            st.session_state.griglia_estrazione_sabato.append({
                                "Seleziona": False,
                                "Team": team_finale,
                                "N° Kart Estratto": kart_scelto
                            })
                            st.rerun()
                        else:
                            st.error("Compila i campi!")

                with col_add4:
                    st.write(" ")
                    st.write(" ")
                    if st.button("🗑️ Elimina", use_container_width=True, type="secondary"):
                        griglia_pulita = [riga for riga in st.session_state.griglia_estrazione_sabato if not riga.get("Seleziona", False)]
                        if len(griglia_pulita) < len(st.session_state.griglia_estrazione_sabato):
                            st.session_state.griglia_estrazione_sabato = griglia_pulita
                            st.rerun()
                        else:
                            st.warning("Spunta prima la casella nella riga del Team da eliminare!")

                st.markdown("---")
                st.write("**📋 Riepilogo Griglia di Partenza:**")

                def salva_griglia_sabato_def():
                    if "key_tabella_sabato_goats" in st.session_state:
                        edizioni = st.session_state["key_tabella_sabato_goats"]
                        if "edited_rows" in edizioni:
                            for riga_idx, variazioni in edizioni["edited_rows"].items():
                                for colonna, nuovo_valore in variazioni.items():
                                    st.session_state.griglia_estrazione_sabato[riga_idx][colonna] = nuovo_valore

                df_sabato = pd.DataFrame(st.session_state.griglia_estrazione_sabato)
                
                tabella_sabato = st.data_editor(
                    df_sabato,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "Seleziona": st.column_config.CheckboxColumn("🗑️", help="Spunta per eliminare questa riga", default=False),
                        "Team": st.column_config.SelectboxColumn("Team", options=st.session_state.lista_team_dinamica, required=True),
                        "N° Kart Estratto": st.column_config.TextColumn("N° Kart Abbinato", required=True)
                    },
                    hide_index=True,
                    key="key_tabella_sabato_goats",
                    on_change=salva_griglia_sabato_def
                )
                st.session_state.griglia_estrazione_sabato = tabella_sabato.to_dict(orient="records")

            with tab_archivio:
                st.subheader("📂 Registro Storico Permanente dei Telai")
                st.write("Il tuo database continuo. Inserisci qui i giudizi sui kart riscontrati nei test o nelle gare passate.")

                if "database_continuo_telai" not in st.session_state:
                    st.session_state.database_continuo_telai = [
                        {"N° Kart": "Kart 14", "Giudizio": "🚀 Razzo", "Commento Tecnico Libero": "Motore devastante sul dritto, telaio perfetto."},
                        {"N° Kart": "Kart 05", "Giudizio": "✅ Ottimo", "Commento Tecnico Libero": "Molto costante, soffre leggermente a caldo."},
                        {"N° Kart": "Kart 22", "Giudizio": "❌ Pessimo", "Commento Tecnico Libero": "Chiodo totale, perde un secondo al giro sul dritto."}
                    ]

                def salva_database_continuo_def():
                    if "key_tabella_continuo_goats" in st.session_state:
                        edizioni = st.session_state["key_tabella_continuo_goats"]
                        if "edited_rows" in edizioni:
                            for riga_idx, variazioni in edizioni["edited_rows"].items():
                                for colonna, nuovo_valore in variazioni.items():
                                    st.session_state.database_continuo_telai[riga_idx][colonna] = nuovo_valore
                        if "added_rows" in edizioni:
                            for nuova_riga in edizioni["added_rows"]:
                                st.session_state.database_continuo_telai.append({
                                    "N° Kart": nuova_riga.get("N° Kart", "Kart 00"),
                                    "Giudizio": nuova_riga.get("Giudizio", "✅ Ottimo"),
                                    "Commento Tecnico Libero": nuova_riga.get("Commento Tecnico Libero", "")
                                })
                        if "deleted_rows" in edizioni:
                            for riga_idx in sorted(edizioni["deleted_rows"], reverse=True):
                                st.session_state.database_continuo_telai.pop(riga_idx)

                df_continuo = pd.DataFrame(st.session_state.database_continuo_telai)
                
                tabella_continuo = st.data_editor(
                    df_continuo,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "N° Kart": st.column_config.TextColumn("Numero Telaio / Kart", required=True),
                        "Giudizio": st.column_config.SelectboxColumn("Giudizio Tecnico", options=["🚀 Razzo", "✅ Ottimo", "❌ Pessimo"], required=True),
                        "Commento Tecnico Libero": st.column_config.TextColumn("Note Meccaniche (Libere / Aperte)")
                    },
                    hide_index=True,
                    key="key_tabella_continuo_goats",
                    on_change=salva_database_continuo_def
                )
                st.session_state.database_continuo_telai = tabella_continuo.to_dict(orient="records")



        elif nome == "📻 Radio":
            st.subheader("📻 Radio")
            st.write("Consultazione rapida delle regole di ingaggio.")
            # In futuro qui caricheremo il PDF delle regole di ingaggio

        elif "Regolamento" in nome:
            st.title("📋 Regolamento IRK Championship")
            st.write("Consultazione rapida delle regole di ingaggio e delle penalità ufficiali.")
            st.write("---")
            link_regolamento_default = "https://irkpromotion.com/wp-content/uploads/ITA-RD1-_-R-ONE-Championship-2026-v1.0-1.pdf"
            url_regolamento = st.text_input("🔗 Link al PDF Regolamento Ufficiale:", value=link_regolamento_default)
            st.link_button("📥 Apri PDF Regolamento Completo", url=url_regolamento)
            tab_regole, tab_penalita = st.tabs(["🏁 Info Voci Regolamento", "⚠️ Tabella Penalità Rapida"])
            
            with tab_regole:
                st.subheader("📊 Regolamento Sintetizzato")
                st.caption("Nota: La procedura di partenza è LANCIATA ed il rifornimento è LIBERO.")
                
            with tab_penalita:
                st.subheader("🛑 Prontuario Sanzioni e Violazioni")
                st.error("⚠️ Attenzione al muretto: Cambi corsia e pesature errate possono compromettere la strategia!")

        elif nome == "📚 Archivio Storico":
            st.title("📚 Archivio Storico Gare")
            if "archivio_gare" not in st.session_state:
                st.session_state.archivio_gare = []
            
            elenco_gare = [g["Gara"] for g in st.session_state.archivio_gare]
            gara_selezionata = st.selectbox("Seleziona una gara:", elenco_gare if elenco_gare else ["Nessuna gara"])
            
            st.write("Gestione database storico attiva.")

        elif nome == "🛠️ Configurazione GRB":
            st.subheader("⚙️ Configurazione GRB")
            st.title("🛠️ Pannello di Controllo Master GRB")
            # --- Autenticazione Master ---
            if not st.session_state.get("master_autenticato", False):
                master_pssw = st.text_input("Inserisci Chiave Master:", type="password")
                if st.button("Sblocca Parametri"):
                    if master_pssw == "12345":
                        st.session_state.master_autenticato = True
                        st.rerun()
            else:
                st.success("🔓 Modalità Amministratore Attiva.")
