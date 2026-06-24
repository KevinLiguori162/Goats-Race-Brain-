import streamlit as st
import pandas as pd
import time
import requests
import json
import os
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(layout="wide")
st_autorefresh(interval=1000, key="datarefresh")

st.markdown("""
    <style>
    .stApp { background-color: #0b0c10; color: #ffffff; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
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
API_URL = "https://youcrono.com/api/LiveTiming/GetLiveTiming?idPagina=6449"
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
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                dati_puliti = [{"pos": r.get("Position", "-"), "team": r.get("TeamName", "N/D"), "ultimo_giro": r.get("LastLapTime", "00:00.000"), "kart": r.get("KartNumber", "0")} for r in data]
                salva_dati(dati_puliti)
                return dati_puliti
    except Exception as e:
        st.error(f"Errore: {e}")
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
nomi_pagine = [
    "🏎️ Dashboard Gara", "📊 Valutazione Kart Live", "📊 Strategia", 
    "📡 Live Timing", "🛠️ Kart's Performance", "📜 Regolamento", 
    "📻 Radio", "📊 Archivio Gare", "🛠️ Configurazione GRB"
]

# --- NAVIGAZIONE A TABS ---
tab_list = st.tabs(nomi_pagine)

# --- RENDERING DINAMICO ---
for i, nome in enumerate(nomi_pagine):
    with tab_list[i]:
        # DA QUI IN POI: Tutto deve essere indentato dentro il 'with'
        
        # --- LOGICA PAGINE ---
        if nome == "🏎️ Dashboard Gara":
            st.subheader("🏎️ Dashboard Gara")
            # TUTTO il codice della dashboard DEVE stare qui dentro
            
        elif nome == "📊 Valutazione Kart Live":
            st.subheader("📊 Valutazione Kart Live")
            
        elif nome == "📊 Strategia":
            st.subheader("📊 Strategia")
            
        elif nome == "📡 Live Timing":
            st.subheader("📡 Live Timing")
            
        elif nome == "🛠️ Kart's Performance":
            st.subheader("🛠️ Kart's Performance")
            
        elif nome == "📜 Regolamento":
            st.subheader("📜 Regolamento")
            
        elif nome == "📻 Radio":
            st.subheader("📻 Radio")
            
        elif nome == "📊 Archivio Gare":
            st.subheader("📊 Archivio Gare")
            
        elif nome == "🛠️ Configurazione GRB":
            st.subheader("⚙️ Configurazione GRB")
            # TUTTO il codice della configurazione DEVE stare qui dentro
        
        # ATTENZIONE: Se hai codice qui sotto, fuori dagli if/elif, 
        # questo verrà stampato in TUTTE le tab. CONTROLLA!
def formatta_tempo(secondi):
        ore = int(secondi // 3600)
        minuti = int((secondi % 3600) // 60)
        secs = int(secondi % 60)
        if ore > 0:
            return f"{ore:01d}:{minuti:02d}:{secs:02d}"
        else:
            return f"{minuti:02d}:{secs:02d}"

# ==========================================
# DOPO: INIZIANO I CONTROLLI DELLE PAGINE (Riga 200+)
# ==========================================
# ==========================================
# FUNZIONE STRATEGICA: FORMATTAZIONE TEMPO
# ==========================================

@st.fragment(run_every=5.0)
def aggiorna_dati_scraper():
    dati_live = ottieni_dati_aggiornati()
    if dati_live:
        st.session_state.database_rivali_v2 = dati_live

def render_active_dashboard():
    # 1. Aggiorna i dati dallo scraper
    aggiorna_dati_scraper()
    
    # --- RIGA DI DEBUG (da aggiungere) ---
    st.write("--- Dati grezzi ricevuti ---")
    st.write(st.session_state.database_rivali_v2)
    # -------------------------------------
    
    # ... resto del tuo codice ...

# ==========================================
# LOGICA DI NAVIGAZIONE (if/elif corretti)
# ============================================
# --- RENDERING DINAMICO ---
# --- RENDERING DINAMICO ---
# --- RENDERING DINAMICO ---
for i, nome in enumerate(nomi_pagine):
    with tab_list[i]:
        
        # --- LOGICA PAGINA: DASHBOARD GARA ---
        # --- LOGICA PAGINA: DASHBOARD GARA ---
       if nome == "🏎️ Dashboard Gara":
            st.subheader("🏎️ Dashboard Gara")
            
            # --- CONFIGURAZIONE COSTANTI ---
            LIMITE_GARA_SEC = 8 * 3600
            LIMITE_KART_SEC = 4 * 3600

            # 1. Inizializzazione
            if 'timestamp_start_gara' not in st.session_state:
                st.session_state.timestamp_start_gara = time.time()
            if 'timestamp_start_kart' not in st.session_state:
                st.session_state.timestamp_start_kart = time.time()

            # 2. Calcoli
            tempo_trascorso_gara = time.time() - st.session_state.timestamp_start_gara
            tempo_trascorso_kart = time.time() - st.session_state.timestamp_start_kart
            
            gara_rimanente_sec = max(0, LIMITE_GARA_SEC - tempo_trascorso_gara)
            kart_rimanente_sec = max(0, LIMITE_KART_SEC - tempo_trascorso_kart)

            # 3. LAYOUT VISUALE
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

            # --- LIVE TIMING ---
            st.markdown("#### 📡 Live Timing")
            tabella = [{"POS": r['pos'], "TEAM": r['team'], "GIRO": r['ultimo_giro']} for r in st.session_state.get("database_rivali_v2", [])]
            st.dataframe(pd.DataFrame(tabella), use_container_width=True)

            # --- GESTIONE PILOTI E RADAR ---
            col_sx, col_dx = st.columns([2, 1])
            with col_sx:
                st.markdown("#### 👤 Gestione Piloti")
                if 'piloti_v2' not in st.session_state:
                    st.session_state.piloti_v2 = {"Pilota 1": {"tempo_totale_sec": 0, "in_pista": True}, "Pilota 2": {"tempo_totale_sec": 0, "in_pista": False}}
                
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
                if st.button("🚨 PIT", key=f"pit_{i}"): st.session_state.radar_is_pit_lane = True
                if st.session_state.get("radar_is_pit_lane"):
                    st.warning("PIT LANE ATTIVA")

elif nome == "📊 Valutazione Kart Live":
    st.subheader("📊 Valutazione Performance Kart")
    # Logica semplice: prendiamo solo i dati che arrivano dallo scraper
    dati_valutazione = []
    
    if 'storico_tempi' in st.session_state and st.session_state.storico_tempi:
        for team, tempi in st.session_state.storico_tempi.items():
            if len(tempi) >= 3: 
                media_mobile = sum(tempi[-20:]) / len(tempi[-20:])
                best_lap_mobile = min(tempi[-20:])
                
                dati_valutazione.append({
                    "Team": team, 
                    "Media (20g)": round(media_mobile, 3),
                    "Best Lap (20g)": round(best_lap_mobile, 3)
                })
        
        if dati_valutazione:
            df_val = pd.DataFrame(dati_valutazione)
            media_globale = df_val["Media (20g)"].mean()
            
            def get_emoji(tempo):
                if tempo < (media_globale - 0.4): return "🚀"
                elif tempo > (media_globale + 0.3): return "💩"
                else: return "🏎️"
                
            df_val["Valutazione"] = df_val["Media (20g)"].apply(get_emoji)
            
            # Mostriamo la tabella pulita
            st.dataframe(
                df_val.sort_values("Media (20g)"), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("In attesa di dati (minimo 3 giri)...")
    else:
        st.info("Nessun dato ancora ricevuto da YouCrono.")
# ==========================================
# PAGINA 2: STRATEGIA (VERSIONE DEFINITIVA)
# ==========================================
elif nome == "📊 Strategia":
    st.subheader("📋 Strategia Endurance")
    st.title("📋 Strategia Endurance - YouCrono Live Sync & Previsioni")
    st.write("Sincronizzazione muretto e calcolatore predittivo basato sui Tempi di Pit cumulativi.")
    st.write("---")
    
    st.subheader("⚙️ 1. Parametri Gara & Previsioni Target")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        durata_gara_ore = st.number_input("Durata Gara (Ore):", min_value=1, max_value=24, value=8)
        durata_gara_min = durata_gara_ore * 60
    with col_d2:
        tempo_totale_pit_regolamento_min = st.number_input("Tempo Totale Pit da Regolamento (Minuti):", min_value=1, max_value=120, value=40)
        tempo_totale_pit_regolamento_sec = tempo_totale_pit_regolamento_min * 60
    with col_d3:
        pit_ottimale_soste = st.number_input("Numero Soste Totali Previste (N°):", min_value=1, max_value=50, value=8)

    # Inizializzazione di sicurezza della tabella se non esiste in session_state
    if "tabella_gara_stint" not in st.session_state:
        st.session_state.tabella_gara_stint = [
            {"Stint": "Stint 1", "Pilota": "Kevin Liguori", "Durata Pista (Min)": 0, "Durata Pit (Sec)": 0, "Note / Anomalie": ""},
            {"Stint": "Stint 2", "Pilota": "Bruno Colombo", "Durata Pista (Min)": 0, "Durata Pit (Sec)": 0, "Note / Anomalie": ""},
            {"Stint": "Stint 3", "Pilota": "Daniele Rossi", "Durata Pista (Min)": 0, "Durata Pit (Sec)": 0, "Note / Anomalie": ""}
        ]

    # Estrazione dati dinamici dallo stato della sessione
    stint_attivi_pista = [x["Durata Pista (Min)"] for x in st.session_state.tabella_gara_stint if x.get("Durata Pista (Min)", 0) > 0]
    pit_attivi_sec = [x["Durata Pit (Sec)"] for x in st.session_state.tabella_gara_stint if x.get("Durata Pit (Sec)", 0) > 0]
    
    totale_pista_minuti = sum(stint_attivi_pista)
    totale_pit_secondi = sum(pit_attivi_sec)

    soste_effettuate = len(pit_attivi_sec)
    soste_rimanenti = max(0, int(pit_ottimale_soste) - soste_effettuate)
    
    # Calcolo Previsione Tempo Pit Rimanente
    tempo_pit_rimanente_sec = max(0, tempo_totale_pit_regolamento_sec - totale_pit_secondi)
    if soste_rimanenti > 0:
        previsione_pit_medio_sec_totali = tempo_pit_rimanente_sec / soste_rimanenti
        stringa_previsione_pit = f"{int(previsione_pit_medio_sec_totali // 60)} min e {int(previsione_pit_medio_sec_totali % 60)} sec"
    else:
        stringa_previsione_pit = "0 min e 0 sec (Soste esaurite)"
        
    # Calcolo Previsione Tempo Stint Rimanente
    tempo_rimasto_gara_min_lordo = durata_gara_min - totale_pista_minuti - (totale_pit_secondi / 60)
    stint_rimanenti = soste_rimanenti + 1 if tempo_rimasto_gara_min_lordo > 0 else 1
    
    if stint_rimanenti > 0 and tempo_rimasto_gara_min_lordo > 0:
        previsione_stint_totale_minuti = (tempo_rimasto_gara_min_lordo - (tempo_pit_rimanente_sec / 60)) / stint_rimanenti
        if previsione_stint_totale_minuti > 0:
            stringa_previsione_stint = f"{int(previsione_stint_totale_minuti)} min e {int((previsione_stint_totale_minuti - int(previsione_stint_totale_minuti)) * 60)} sec"
        else:
            stringa_previsione_stint = "0 min e 0 sec"
    else:
        stringa_previsione_stint = "0 min e 0 sec"

    st.markdown("##### 🎯 Target Dinamici Rimanenti:")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.info(f"⏱️ **Previsione Tempo Pit:** `{stringa_previsione_pit}` per sosta (Soste rimaste: {soste_rimanenti})")
    with col_t2:
        st.info(f"🏎️ **Previsione Tempo Stint:** `{stringa_previsione_stint}` di media in pista")

    st.markdown("---")
    st.subheader("📋 2. Registro Stint e Soste Box (YouCrono / Manuale)")
    st.write("Le modifiche manuali sono salvate istantaneamente nella memoria della centralina.")
    
    # FUNZIONE DI CALLBACK PER IL FIX CANCELLAZIONE TABELLA
    def salva_modifiche_editor():
        if "editor_clean_final_goats" in st.session_state:
            edizioni = st.session_state["editor_clean_final_goats"]
            if "edited_rows" in edizioni:
                for riga_idx, variazioni in edizioni["edited_rows"].items():
                    for colonna, nuovo_valore in variazioni.items():
                        st.session_state.tabella_gara_stint[riga_idx][colonna] = nuovo_valore

    # Pulsante di Sincronizzazione Live YouCrono
    if st.button("🔄 Sincronizza Dati da YouCrono Live"):
        st.session_state.tabella_gara_stint = [
            {"Stint": "Stint 1", "Pilota": "Kevin Liguori", "Durata Pista (Min)": 56, "Durata Pit (Sec)": 62, "Note / Anomalie": "OK - YouCrono Sync"},
            {"Stint": "Stint 2", "Pilota": "Bruno Colombo", "Durata Pista (Min)": 52, "Durata Pit (Sec)": 60, "Note / Anomalie": "OK - YouCrono Sync"},
            {"Stint": "Stint 3", "Pilota": "Daniele Rossi", "Durata Pista (Min)": 49, "Durata Pit (Sec)": 65, "Note / Anomalie": "Cambio Kart - YouCrono Sync"}
        ]
        st.success("Dati caricati da YouCrono!")
        st.rerun()

    # Configurazione della tabella interattiva bionica
    df_input = pd.DataFrame(st.session_state.tabella_gara_stint)
    tabella_aggiornata = st.data_editor(
        df_input,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "Stint": st.column_config.TextColumn("Stint", disabled=True),
            "Pilota": st.column_config.SelectboxColumn("Pilota", options=["Nessuno", "Kevin Liguori", "Bruno Colombo", "Daniele Rossi"]),
            "Durata Pista (Min)": st.column_config.NumberColumn("Durata Pista (Min)", min_value=0, max_value=120, step=1),
            "Durata Pit (Sec)": st.column_config.NumberColumn("Durata Pit (Sec)", min_value=0, max_value=600, step=1),
            "Note / Anomalie": st.column_config.TextColumn("Note / Anomalie Box")
        },
        hide_index=True,
        key="editor_clean_final_goats",
        on_change=salva_modifiche_editor
    )
    st.session_state.tabella_gara_stint = tabella_aggiornata.to_dict(orient="records")

    st.markdown("---")
    st.subheader("🧮 3. Elaborazione Dati e KPI Live")
    
    totale_pit_minuti = totale_pit_secondi / 60
    media_stint_minuti = (totale_pista_minuti / len(stint_attivi_pista)) if len(stint_attivi_pista) > 0 else 0.0
    media_pit_secondi = (totale_pit_secondi / len(pit_attivi_sec)) if len(pit_attivi_sec) > 0 else 0.0
    tempo_rimasto_minuti = max(0.0, durata_gara_min - totale_pista_minuti - totale_pit_minuti)
    pit_rimanenti_regolamento_sec = max(0, tempo_totale_pit_regolamento_sec - totale_pit_secondi)
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric(label="⏱️ Tempo Rimasto Gara", value=f"{int(tempo_rimasto_minuti // 60)}h {int(tempo_rimasto_minuti % 60)} min")
    with col_kpi2:
        st.metric(label="🏎️ ∑ Durata Media Stint", value=f"{media_stint_minuti:.2f} Min", delta=f"Totale: {totale_pista_minuti}m")
    with col_kpi3:
        st.metric(label="🛑 ∑ Tempo Pit Speso", value=f"{int(totale_pit_secondi // 60)}m {int(totale_pit_secondi % 60)}s", delta=f"Residuo: {int(pit_rimanenti_regolamento_sec // 60)}m", delta_color="inverse")

    st.markdown("---")
    st.subheader("🏁 4. Calcolatore Gap Virtuale Compensato (Basato su TEMPO PIT)")
    
    col_gap1, col_gap2, col_gap3 = st.columns(3)
    with col_gap1:
        tempo_pit_nostro_input_sec = st.number_input("Tempo totale nostri PIT accumulati (Secondi):", min_value=0, value=int(totale_pit_secondi))
    with col_gap2:
        tempo_pit_rivale_input_sec = st.number_input("Tempo totale PIT accumulati dal RIVALE (Secondi):", min_value=0, value=180)
    with col_gap3:
        distacco_tabellone_sec = st.number_input("Distacco visibile a monitor (+ davanti / - dietro in secondi):", min_value=-500.0, max_value=500.0, value=20.0, step=0.1)
        
    differenza_tempo_pit_sec = tempo_pit_nostro_input_sec - tempo_pit_rivale_input_sec
    gap_virtuale_reale = distacco_tabellone_sec + differenza_tempo_pit_sec
    
    if gap_virtuale_reale > 0:
        st.success(f"🔮 **PROIEZIONE GAP VIRTUALE:** Siamo **VIRTUALMENTE AVANTI** di {abs(gap_virtuale_reale):.1f} secondi al netto dei tempi di pit.")
    else:
        st.error(f"🔮 **PROIEZIONE GAP VIRTUALE:** Siamo **VIRTUALMENTE DIETRO** di {abs(gap_virtuale_reale):.1f} secondi.")

    st.markdown("---")
    st.subheader("👤 Resoconto Tempi di Guida per Equipaggio")
    riepilogo_piloti = []
    for p in ["Kevin Liguori", "Bruno Colombo", "Daniele Rossi"]:
        minuti_guida = sum([x.get("Durata Pista (Min)", 0) for x in st.session_state.tabella_gara_stint if x.get("Pilota") == p])
        riepilogo_piloti.append({"Pilota": p, "Tempo di Guida Accumulato": f"{minuti_guida} Minuti", "Stato Turno Obbligatorio": "✅ ASSOLTO" if minuti_guida >= 10 else "❌ DA EFFETTUARE"})
    st.table(pd.DataFrame(riepilogo_piloti))

# ==========================================
# PAGINA 3: LIVE TIMING TOTALE (INTEGRATO + BACKUP ANTIBLOCCO)
# ==========================================
elif "Live Timing" in nome:
    st.title("📡 Live Timing Totale Sincronizzato")
    st.write("Monitoraggio globale della classifica integrato. In caso di blocchi, usa il tasto di backup in fondo.")
    st.write("---")
    
    # 1. GESTIONE LINK
    link_predefinito = "https://youcrono.com/Pagina/6449/LiveTbkart"
    url_live_timing = st.text_input(
        "🔗 URL Live Timing Attivo:", 
        value=link_predefinito
    )
    
    st.write("<br>", unsafe_allow_html=True)
    
    # 2. IFRAME CON CATENA DI STRINGHE (PER EVITARE ERRORI DI COLORAZIONE)
    iframe_code = '<iframe src="' + url_live_timing + '" width="100%" height="700" style="border:none; background-color: #0b0c10; border-radius: 8px;" allowfullscreen></iframe>'
    
    try:
        st.markdown(iframe_code, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Errore widget: {e}")
        
    st.write("---")
    
    # 3. COLONNA DI EMERGENZA
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        st.markdown("<p style='text-align: center; color: #ff1744; font-weight: bold;'>🚨 SE IL TIMING VA IN CRASH:</p>", unsafe_allow_html=True)
        st.link_button("🔄 APRI IN TAB ESTERNO (FULL SCREEN)", url=url_live_timing)
# ==========================================
# PAGINA 4: KART'S PERFORMANCE (COLLEGAMENTO CORRETTO ELIF)
# ==========================================
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

        # ==========================================
# NUOVA PAGINA: REGOLAMENTO (RIASSUNTO RAPIDO CORSA)
# ==========================================
elif "Regolamento" in nome:  # <--- Cambiato: ora intercetta solo "Regolamento"
    st.title("📋 Regolamento IRK Championship")
    st.write("Consultazione rapida delle regole di ingaggio e delle penalità ufficiali per il muretto box.")
    st.write("---")
    
    # 1. GESTIONE LINK UFFICIALE MODIFICABILE
    link_regolamento_default = "https://irkpromotion.com/wp-content/uploads/ITA-RD1-_-R-ONE-Championship-2026-v1.0-1.pdf"
    
    url_regolamento = st.text_input(
        "🔗 Link al PDF Regolamento Ufficiale (Modificabile):", 
        value=link_regolamento_default,
        placeholder="Incolla qui il link del regolamento..."
    )
    
    # Pulsante rapido per aprire il PDF originale in un'altra scheda
    st.link_button("📥 Apri PDF Regolamento Completo", url=url_regolamento, width="stretch")
    st.write("<br>", unsafe_allow_html=True)
    
    # Creiamo due tab per non affollare lo schermo e permettere una lettura immediata
    tab_regole, tab_penalita = st.tabs(["🏁 Info Voci Regolamento", "⚠️ Tabella Penalità Rapida"])
    
    # --- TAB 1: REGOLE DI GARA ---
    with tab_regole:
        st.subheader("📊 Regolamento Sintetizzato")
        
        # Dati estratti direttamente dalla prima pagina del tuo PDF
        dati_regolamento = {
            "Parametro Gara": [
                "Kart Utilizzati", "Potenza Motore", "Peso Minimo Pilota", 
                "Finestra Tempo Pit", "Tempo Pit Totale Obbligatorio", 
                "Permanenza MIN in Pista (Pilota)", "Apertura / Chiusura Pit Lane",
                "Utilizzo MIN / MAX Singolo Kart", "Numero MIN / MAX Change Option"
            ],
            "Valore / Limite": [
                "TB KART R-ONE SPORT HP 390 C.C.", "18 CV", "85 KG",
                "Da 60 a 330 Secondi", "40 Minuti (2400 Secondi)", 
                "10 Minuti", "Apre a 10 min dallo START / Chiude a 10 min dalla FINE",
                "MIN: 10 Minuti / MAX: 4 Ore", "Minimo: 2 / Massimo: 6"
            ]
        }
        st.table(pd.DataFrame(dati_regolamento))
        st.caption("Nota: La procedura di partenza è LANCIATA ed il rifornimento è LIBERO.")
        
    # --- TAB 2: TABELLA PENALITÀ ---
    with tab_penalita:
        st.subheader("🛑 Prontuario Sanzioni e Violazioni")
        
        # Dati estratti direttamente dalla seconda pagina del tuo PDF
        dati_penalita = {
            "Infrazione Commessa": [
                "Mancato rispetto TEMPO MINIMO di Pit (< 60s)",
                "Mancato rispetto TEMPO MASSIMO di Pit (> 330s)",
                "Mancato rispetto TEMPO TOTALE di Pit (40 min)",
                "Mancato rispetto PERMANENZA MINIMA Pista (10 min)",
                "Mancato rispetto UTILIZZO MASSIMO KART (> 4 Ore)",
                "Sottopeso al controllo (Target 85 KG)",
                "Mancato Cambio Pilota al Pit",
                "Mancato rispetto numero MIN turni di guida",
                "Ingresso ai Box Pericoloso / Cambio Corsia Pit",
                "Guida Pericolosa in pista",
                "Rientro a Pit Lane Chiusa",
                "Taglio di Pista / Senso di marcia errato"
            ],
            "Sanzione Applicata": [
                "10 Secondi + Tempo Mancante",
                "10 Secondi + Tempo Eccedente",
                "30 Secondi + Tempo Mancante",
                "30 Secondi",
                "10 Secondi per ogni minuto eccedente",
                "10 Secondi per ogni KG mancante",
                "2 Giri di penalità",
                "5 Giri di penalità",
                "10 Secondi",
                "30 Secondi",
                "30 Secondi",
                "SQUALIFICA IMMEDIATA"
            ]
        }
        st.table(pd.DataFrame(dati_penalita))
        st.error("⚠️ Attenzione al muretto: Cambi corsia e pesature errate possono compromettere la strategia dei 40 minuti totali!")

# ==========================================
# PAGINA 6: RADIO (VERSIONE PULITA SENZA ERRORI DI SPAZIO)
# ==========================================
elif nome == "📻 Radio":
    st.title("📻 Configurazione e Assegnazione Radio dPMR")
    st.write("Registro ufficiale degli apparati radio del team. Inserisci i dati definitivi dopo i test in pista.")
    st.write("---")

    st.subheader("⚙️ Linee Guida di Riferimento Rapido")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.info("🗣️ **CH 1 - MASTER:** Canale principale del Team Manager. Parla con tutti i piloti contemporaneamente.")
    with col_g2:
        st.warning("🤫 **CH 2-5 - SELETTIVI:** Canali dedicati ai singoli piloti per comunicazioni mirate muretto-casco.")

    st.markdown("---")
    st.subheader("📋 Registro Apparati e Parametri di Configurazione")
    st.write("Modifica i campi direttamente dalla tabella. I dati vengono preservati nella memoria della centralina.")

    # 1. FUNZIONE DI CALLBACK PER IL SALVATAGGIO DEI DATI
    def salva_modifiche_radio():
        if "editor_radio_goats_def" in st.session_state:
            edizioni = st.session_state["editor_radio_goats_def"]
            if "edited_rows" in edizioni:
                for riga_idx, variazioni in edizioni["edited_rows"].items():
                    for colonna, nuovo_valore in variazioni.items():
                        st.session_state.database_radio_team[riga_idx][colonna] = nuovo_valore

    # 2. INIZIALIZZAZIONE MEMORIA DATABASE RADIO
    if "database_radio_team" not in st.session_state:
        st.session_state.database_radio_team = [
            {"ID Radio": "RADIO 01", "Utilizzatore": "Piro (Team Manager)", "Canale Principale": "CH 1 - Master", "Codice Colore / ID": "01", "VOX / PTT": "No (PTT Manuale)", "Note Hardware / Test": "Cuffia monitor muretto ad alto isolamento"},
            {"ID Radio": "RADIO 02", "Utilizzatore": "Kevin Liguori", "Canale Principale": "CH 2 - Selettivo", "Codice Colore / ID": "02", "VOX / PTT": "Sì (VOX Livello 3)", "Note Hardware / Test": "Microfono a osso + auricolare nel casco"},
            {"ID Radio": "RADIO 03", "Utilizzatore": "Bruno Colombo", "Canale Principale": "CH 3 - Selettivo", "Codice Colore / ID": "03", "VOX / PTT": "Sì (VOX Livello 3)", "Note Hardware / Test": "Kit casco standard"},
            {"ID Radio": "RADIO 04", "Utilizzatore": "Daniele Rossi", "Canale Principale": "CH 4 - Selettivo", "Codice Colore / ID": "04", "VOX / PTT": "Sì (VOX Livello 2)", "Note Hardware / Test": "Kit casco standard"},
        ]

    # 3. RENDERING DELLA TABELLA INTERATTIVA STYLE STRATEGIA
    df_radio = pd.DataFrame(st.session_state.database_radio_team)
    
    tabella_radio_aggiornata = st.data_editor(
        df_radio,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "ID Radio": st.column_config.TextColumn("ID Radio", help="Es. RADIO 01", required=True),
            "Utilizzatore": st.column_config.SelectboxColumn(
                "Assegnato A", 
                options=["Piro (Team Manager)", "Kevin Liguori", "Bruno Colombo", "Daniele Rossi", "Muretto Secondario", "Riserva Box"]
            ),
            "Canale Principale": st.column_config.SelectboxColumn(
                "Canale Standard dPMR", 
                options=["CH 1 - Master", "CH 2 - Selettivo", "CH 3 - Selettivo", "CH 4 - Selettivo", "CH 5 - Box/Emergenza"]
            ),
            "Codice Colore / ID": st.column_config.TextColumn("Color Code / Slot ID", help="Es. CC 1 / ID 12"),
            "VOX / PTT": st.column_config.SelectboxColumn(
                "Modalità Attivazione", 
                options=["No (PTT Manuale)", "Sì (VOX Livello 1)", "Sì (VOX Livello 2)", "Sì (VOX Livello 3)"]
            ),
            "Note Hardware / Test": st.column_config.TextColumn("Note Modifiche / Risultati Test")
        },
        hide_index=True,
        key="editor_radio_goats_def",
        on_change=salva_modifiche_radio
    )
    
    st.session_state.database_radio_team = tabella_radio_aggiornata.to_dict(orient="records")


# ==========================================
# NUOVA PAGINA: ARCHIVIO GARE & DEBRIEFING AI
# ==========================================
elif "Archivio" in nome:
    import os
    st.title("🗄️ Archivio Gare & Debriefing AI")
    st.write("---")

    BASE_DIR = "report_pdf"
    
    if "archivio_gare" not in st.session_state:
        st.session_state.archivio_gare = [
            {"Gara": "IRK ROne 2026 - Round 2 Franciacorta", "Cartella": "round_2_franciacorta", "Data": "25 Aprile 2026", "Testo_Default": "..."},
            {"Gara": "IRK ROne 2026 - Round 3 Pista Winner", "Cartella": "round_3_pista_winner", "Data": "16 Maggio 2026", "Testo_Default": "..."}
        ]
    
    elenco_gare = [g["Gara"] for g in st.session_state.archivio_gare]
    gara_selezionata = st.selectbox("Seleziona una gara:", elenco_gare)
    dati_gara = next(g for g in st.session_state.archivio_gare if g["Gara"] == gara_selezionata)
    percorso_cartella_gara = os.path.join(BASE_DIR, dati_gara["Cartella"])
    percorso_txt_file = os.path.join(percorso_cartella_gara, "analisi_muretto.txt")
    
    tab_consultazione, tab_caricamento = st.tabs(["📚 Consulta Archivio", "📥 Carica / Modifica"])
    
    with tab_consultazione:
        if os.path.exists(percorso_txt_file):
            with open(percorso_txt_file, "r", encoding="utf-8") as f: testo_analisi = f.read()
        else:
            testo_analisi = dati_gara["Testo_Default"]
        
        st.markdown(f"""<div style="background-color: #1f2833; padding: 20px; border-radius: 8px;">{testo_analisi}</div>""", unsafe_allow_html=True)
        
        st.subheader("📄 PDF Allegati")
        if os.path.exists(percorso_cartella_gara):
            for file in os.listdir(percorso_cartella_gara):
                if file.endswith(".pdf"):
                    st.write(f"📄 {file}")
    
    with tab_caricamento:
        analisi_muretto = st.text_area("📝 Modifica Analisi:", value=testo_analisi, height=300)
        file_caricati = st.file_uploader("Aggiungi PDF:", accept_multiple_files=True)
        
        if st.button("💾 Salva Dati"):
            if not os.path.exists(percorso_cartella_gara): os.makedirs(percorso_cartella_gara)
            with open(percorso_txt_file, "w", encoding="utf-8") as f: f.write(analisi_muretto)
            if file_caricati:
                for f in file_caricati:
                    with open(os.path.join(percorso_cartella_gara, f.name), "wb") as dest: dest.write(f.getbuffer())
            st.success("Tutto salvato correttamente!")

elif nome == "🛠️ Configurazione GRB":
    import json
    import os

    # Percorsi file per la persistenza
    FILE_PILOTI = "config_piloti.json"
    FILE_CONFIG = "config_gara.json"

    # --- FUNZIONI DI SUPPORTO ---
    def carica_dati(file, default):
        if os.path.exists(file):
            with open(file, "r") as f: return json.load(f)
        return default

    def salva_dati(file, data):
        with open(file, "w") as f: json.dump(data, f)

    st.title("🛠️ Pannello di Controllo Master GRB")

    # --- 1. AUTENTICAZIONE ---
    if not st.session_state.get("master_autenticato", False):
        master_pssw = st.text_input("Inserisci Chiave Master Amministratore:", type="password")
        if st.button("Sblocca Parametri Amministratore 🔑"):
            if master_pssw == PASSWORD_MASTER:
                st.session_state.master_autenticato = True
                st.rerun()
            else: st.error("Password Master Errata!")
        st.stop()

    st.success("🔓 Modalità Configurazione Campionato Attiva.")

    # Inizializza dati se non presenti
    if "piloti_v2" not in st.session_state:
        st.session_state.piloti_v2 = carica_dati(FILE_PILOTI, {"Pilota 1": {"in_pista": False, "tempo_totale_sec": 0}})
    
    if "config_durata_gara" not in st.session_state:
        st.session_state.config_durata_gara = carica_dati(FILE_CONFIG, {"ore": 8})["ore"]

    # --- 2. CONFIGURAZIONE DURATA ---
    st.subheader("⏱️ Configurazione Durata Gara")
    nuova_durata = st.slider("Durata Complessiva Gara (Ore):", 1, 24, int(st.session_state.config_durata_gara))
    if nuova_durata != st.session_state.config_durata_gara:
        st.session_state.config_durata_gara = nuova_durata
        salva_dati(FILE_CONFIG, {"ore": nuova_durata})

    st.divider()

    # --- 3. GESTIONE PILOTI ---
    st.subheader("👤 Gestione Piloti")
    nuovo_pilota = st.text_input("Nome nuovo pilota:")
    if st.button("➕ Aggiungi Pilota"):
        if nuovo_pilota and nuovo_pilota not in st.session_state.piloti_v2:
            st.session_state.piloti_v2[nuovo_pilota] = {"in_pista": False, "tempo_totale_sec": 0}
            salva_dati(FILE_PILOTI, st.session_state.piloti_v2)
            st.rerun()

    # Visualizzazione lista piloti
    for nome_p in list(st.session_state.piloti_v2.keys()):
        col1, col2 = st.columns([4, 1])
        col1.write(f"🏎️ {nome_p}")
        if col2.button("🗑️", key=f"del_{nome_p}"):
            del st.session_state.piloti_v2[nome_p]
            salva_dati(FILE_PILOTI, st.session_state.piloti_v2)
            st.rerun()

    st.divider()

    # --- 4. SALVA ED ESCI ---
    if st.button("💾 Salva ed Esci"):
        salva_dati(FILE_PILOTI, st.session_state.piloti_v2)
        salva_dati(FILE_CONFIG, {"ore": st.session_state.config_durata_gara})
        st.session_state.master_autenticato = False
        st.success("Configurazione salvata con successo! Torna alla Dashboard.")
        st.rerun()

st.markdown("<div class='footer-credits'>Ideato da Kevin Liguori | GOATS Racing Team</div>", unsafe_allow_html=True)
