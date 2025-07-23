import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
from typing import Dict, List, Any
import uuid

# Configurare pagină
st.set_page_config(page_title="Aplicația Dietă", layout="wide")

# Fișiere pentru persistența datelor
DATA_DIR = "../data"
RETETAR_FILE = os.path.join(DATA_DIR, "retetar.json")
CZA_FILE = os.path.join(DATA_DIR, "cza.json")

# Crearea directorului pentru date
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Funcții pentru gestionarea datelor
def load_data(filename):
    """Încarcă datele din fișierul JSON"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data, filename):
    """Salvează datele în fișierul JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def initialize_session_state():
    """Inițializează session state cu datele salvate"""
    if 'retetar' not in st.session_state:
        st.session_state.retetar = load_data(RETETAR_FILE)
    
    if 'cza_data' not in st.session_state:
        st.session_state.cza_data = load_data(CZA_FILE)
    
    if 'selected_coordinates' not in st.session_state:
        st.session_state.selected_coordinates = {
            'loc_consum': 'C1',
            'masa_zi': 'M1', 
            'regim_alimentar': 'R1',
            'data': date.today().strftime('%d.%m.%Y')
        }

def generate_cza_key(coords):
    """Generează cheia pentru coordonatele CZA"""
    return f"{coords['loc_consum']}_{coords['masa_zi']}_{coords['regim_alimentar']}_{coords['data']}"

# Inițializare
initialize_session_state()

st.title("🍽️ Aplicația Dietă")

# Taburi principale
tab1, tab2, tab3, tab4 = st.tabs(["📖 Rețetar", "📍 Coordonate CZA", "📊 CZA", "📋 Listă Alimente"])

# TAB 1: REȚETAR
with tab1:
    st.header("Rețetar")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Alimente și Ingrediente")
        
        # Afișare tabel rețetar
        if st.session_state.retetar:
            for aliment, ingrediente in st.session_state.retetar.items():
                with st.expander(f"🍳 {aliment}", expanded=False):
                    
                    # Adăugare ingredient nou
                    st.write("**Adaugă ingredient nou:**")
                    col_ing, col_um, col_cant, col_btn = st.columns([3, 1, 1, 1])
                    
                    with col_ing:
                        new_ingredient = st.text_input(f"Ingredient", key=f"new_ing_{aliment}")
                    with col_um:
                        new_um = st.selectbox("UM", ["kg", "g", "l", "ml", "buc", "linguri", "lingurite"], key=f"new_um_{aliment}")
                    with col_cant:
                        new_cantitate = st.number_input("Cantitate", min_value=0.0, step=0.1, key=f"new_cant_{aliment}")
                    with col_btn:
                        if st.button("Adaugă", key=f"add_ing_{aliment}"):
                            if new_ingredient:
                                ingredient_id = str(uuid.uuid4())
                                st.session_state.retetar[aliment][ingredient_id] = {
                                    'ingredient': new_ingredient,
                                    'um': new_um,
                                    'cantitate': new_cantitate
                                }
                                save_data(st.session_state.retetar, RETETAR_FILE)
                                st.rerun()
                    
                    # Tabel cu ingredientele existente
                    if ingrediente:
                        st.write("**Ingrediente existente:**")
                        for ing_id, ing_data in ingrediente.items():
                            col_ing_edit, col_um_edit, col_cant_edit, col_btn_edit = st.columns([3, 1, 1, 1])
                            
                            with col_ing_edit:
                                edit_ingredient = st.text_input("", value=ing_data['ingredient'], key=f"edit_ing_{aliment}_{ing_id}")
                            with col_um_edit:
                                edit_um = st.selectbox("", ["kg", "g", "l", "ml", "buc", "linguri", "lingurite"], 
                                                     index=["kg", "g", "l", "ml", "buc", "linguri", "lingurite"].index(ing_data['um']),
                                                     key=f"edit_um_{aliment}_{ing_id}")
                            with col_cant_edit:
                                edit_cantitate = st.number_input("", value=float(ing_data['cantitate']), min_value=0.0, step=0.1, key=f"edit_cant_{aliment}_{ing_id}")
                            with col_btn_edit:
                                col_save, col_del = st.columns(2)
                                with col_save:
                                    if st.button("💾", key=f"save_ing_{aliment}_{ing_id}", help="Salvează"):
                                        st.session_state.retetar[aliment][ing_id] = {
                                            'ingredient': edit_ingredient,
                                            'um': edit_um,
                                            'cantitate': edit_cantitate
                                        }
                                        save_data(st.session_state.retetar, RETETAR_FILE)
                                        st.success("Salvat!")
                                        st.rerun()
                                with col_del:
                                    if st.button("🗑️", key=f"del_ing_{aliment}_{ing_id}", help="Șterge"):
                                        del st.session_state.retetar[aliment][ing_id]
                                        save_data(st.session_state.retetar, RETETAR_FILE)
                                        st.rerun()
                    
                    # Buton pentru ștergerea alimentului
                    if st.button(f"🗑️ Șterge alimentul '{aliment}'", key=f"del_aliment_{aliment}", type="secondary"):
                        del st.session_state.retetar[aliment]
                        save_data(st.session_state.retetar, RETETAR_FILE)
                        st.rerun()
    
    with col2:
        st.subheader("Adaugă Aliment Nou")
        
        new_aliment = st.text_input("Nume aliment")
        if st.button("Creează Aliment", type="primary"):
            if new_aliment and new_aliment not in st.session_state.retetar:
                st.session_state.retetar[new_aliment] = {}
                save_data(st.session_state.retetar, RETETAR_FILE)
                st.success(f"Alimentul '{new_aliment}' a fost creat!")
                st.rerun()
            elif new_aliment in st.session_state.retetar:
                st.error("Alimentul există deja!")

# TAB 2: COORDONATE CZA
with tab2:
    st.header("Coordonate CZA")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        loc_consum = st.selectbox("Loc consum", ["C1", "C2", "C3"], 
                                index=["C1", "C2", "C3"].index(st.session_state.selected_coordinates['loc_consum']))
    
    with col2:
        masa_zi = st.selectbox("Masa din zi", ["M1", "M2", "M3", "M4", "M5"],
                             index=["M1", "M2", "M3", "M4", "M5"].index(st.session_state.selected_coordinates['masa_zi']))
    
    with col3:
        regim_alimentar = st.selectbox("Regim alimentar", ["R1", "R2", "R3", "R4", "R5", "R6"],
                                     index=["R1", "R2", "R3", "R4", "R5", "R6"].index(st.session_state.selected_coordinates['regim_alimentar']))
    
    with col4:
        try:
            data_obj = datetime.strptime(st.session_state.selected_coordinates['data'], '%d.%m.%Y').date()
        except:
            data_obj = date.today()
        
        selected_date = st.date_input("Data", value=data_obj)
        data_str = selected_date.strftime('%d.%m.%Y')
    
    # Actualizare coordonate în session state
    st.session_state.selected_coordinates = {
        'loc_consum': loc_consum,
        'masa_zi': masa_zi,
        'regim_alimentar': regim_alimentar,
        'data': data_str
    }
    
    st.info(f"Coordonate selectate: {loc_consum} - {masa_zi} - {regim_alimentar} - {data_str}")

# TAB 3: CZA (Cantitate Zilnică Alimente) - MODIFICAT
with tab3:
    st.header("CZA - Cantitate Zilnică Alimente")
    
    coords = st.session_state.selected_coordinates
    cza_key = generate_cza_key(coords)
    
    st.info(f"Coordonate curente: {coords['loc_consum']} - {coords['masa_zi']} - {coords['regim_alimentar']} - {coords['data']}")
    
    # Inițializare date CZA pentru coordonatele curente
    if cza_key not in st.session_state.cza_data:
        st.session_state.cza_data[cza_key] = {}
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Adaugă Aliment")
        
        if st.session_state.retetar:
            selected_aliment = st.selectbox("Selectează aliment", list(st.session_state.retetar.keys()))
            nr_persoane = st.number_input("Numărul de persoane", min_value=1, value=1)
            
            if st.button("Adaugă în CZA", type="primary"):
                if selected_aliment not in st.session_state.cza_data[cza_key]:
                    # Generare automată a înregistrărilor din rețetar
                    aliment_data = {
                        'nr_persoane': nr_persoane,
                        'ingrediente': []
                    }
                    
                    for ing_id, ing_info in st.session_state.retetar[selected_aliment].items():
                        cantitate_totala = ing_info['cantitate'] * nr_persoane
                        aliment_data['ingrediente'].append({
                            'id': ing_id,
                            'ingredient': ing_info['ingredient'],
                            'um': ing_info['um'],
                            'cantitate_per_persoana': ing_info['cantitate'],
                            'cantitate_totala': cantitate_totala
                        })
                    
                    st.session_state.cza_data[cza_key][selected_aliment] = aliment_data
                    save_data(st.session_state.cza_data, CZA_FILE)
                    st.success(f"Alimentul '{selected_aliment}' a fost adăugat în CZA!")
                    st.rerun()
                else:
                    st.warning("Alimentul este deja în CZA pentru aceste coordonate!")
        else:
            st.warning("Nu există alimente în rețetar!")
    
    with col2:
        st.subheader("Alimente în CZA")
        
        if st.session_state.cza_data[cza_key]:
            for aliment, aliment_data in st.session_state.cza_data[cza_key].items():
                with st.expander(f"🍳 {aliment} - {aliment_data['nr_persoane']} persoane", expanded=True):
                    
                    # Modificare numărul de persoane
                    col_pers, col_btn_update = st.columns([2, 1])
                    with col_pers:
                        new_nr_persoane = st.number_input("Numărul de persoane:", 
                                                        value=aliment_data['nr_persoane'], 
                                                        min_value=1,
                                                        key=f"nr_pers_{cza_key}_{aliment}")
                    with col_btn_update:
                        if st.button("Actualizează", key=f"update_pers_{cza_key}_{aliment}"):
                            # Actualizează numărul de persoane și recalculează cantitățile
                            st.session_state.cza_data[cza_key][aliment]['nr_persoane'] = new_nr_persoane
                            for ing in st.session_state.cza_data[cza_key][aliment]['ingrediente']:
                                ing['cantitate_totala'] = ing['cantitate_per_persoana'] * new_nr_persoane
                            save_data(st.session_state.cza_data, CZA_FILE)
                            st.success("Actualizat!")
                            st.rerun()
                    
                    # Tabel cu ingredientele
                    if aliment_data['ingrediente']:
                        # Creează dataframe pentru tabel
                        df_data = []
                        for ing in aliment_data['ingrediente']:
                            df_data.append({
                                'Ingredient': ing['ingredient'],
                                'UM': ing['um'],
                                'Cantitate/persoană': f"{ing['cantitate_per_persoana']:.2f}",
                                'Cantitate totală': f"{ing['cantitate_totala']:.2f}"
                            })
                        
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Buton pentru ștergerea alimentului din CZA
                    if st.button(f"🗑️ Șterge '{aliment}' din CZA", key=f"del_cza_{cza_key}_{aliment}", type="secondary"):
                        del st.session_state.cza_data[cza_key][aliment]
                        save_data(st.session_state.cza_data, CZA_FILE)
                        st.rerun()
        else:
            st.info("Nu există alimente adăugate în CZA pentru coordonatele selectate.")

# TAB 4: LISTĂ ALIMENTE
with tab4:
    st.header("Listă Alimente")
    
    data_selectata = st.session_state.selected_coordinates['data']
    st.subheader(f"Totaluri ingrediente pentru data: {data_selectata}")
    
    # Calculare totaluri pentru data selectată
    totaluri = {}
    
    for key, alimente in st.session_state.cza_data.items():
        # Verifică dacă data din cheie coincide cu data selectată
        key_parts = key.split('_')
        if len(key_parts) >= 4 and key_parts[3] == data_selectata:
            for aliment, aliment_data in alimente.items():
                for ing in aliment_data['ingrediente']:
                    ingredient_name = ing['ingredient']
                    um = ing['um']
                    cantitate = ing['cantitate_totala']
                    
                    key_ingredient = f"{ingredient_name}_{um}"
                    
                    if key_ingredient not in totaluri:
                        totaluri[key_ingredient] = {
                            'ingredient': ingredient_name,
                            'um': um,
                            'cantitate_totala': 0
                        }
                    
                    totaluri[key_ingredient]['cantitate_totala'] += cantitate
    
    if totaluri:
        # Afișare tabel cu totalurile
        data_for_table = []
        for key, data in totaluri.items():
            data_for_table.append({
                'Ingredient': data['ingredient'],
                'UM': data['um'],
                'Cantitate Totală': f"{data['cantitate_totala']:.2f}"
            })
        
        df = pd.DataFrame(data_for_table)
        st.dataframe(df, use_container_width=True)
        
        # Opțiune de export
        csv = df.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="📥 Descarcă ca CSV",
            data=csv,
            file_name=f"lista_alimente_{data_selectata.replace('.', '_')}.csv",
            mime="text/csv"
        )
    else:
        st.info(f"Nu există date CZA pentru data {data_selectata}")

# Footer
st.markdown("---")
st.markdown("*Aplicația Dietă - Gestionare completă a alimentelor și rețetelor*")