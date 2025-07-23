import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path

# Configurare pagină
st.set_page_config(
    page_title="Aplicația Dieta",
    page_icon="🍽️",
    layout="wide"
)

# Configurare directorul de date
DATA_DIR = Path.home() / "data"
DATA_DIR.mkdir(exist_ok=True)

RECETAR_FILE = DATA_DIR / "recetar.json"
CZA_FILE = DATA_DIR / "cza.json"

# Funcții pentru gestionarea datelor
def load_data(file_path):
    """Încarcă datele din fișier JSON"""
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data, file_path):
    """Salvează datele în fișier JSON"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_unique_alimente():
    """Obține lista unică de alimente din rețetar"""
    recetar_data = load_data(RECETAR_FILE)
    alimente = set()
    for reteta in recetar_data:
        for ingredient in reteta.get('ingrediente', []):
            alimente.add(ingredient['ingredient'])
    return sorted(list(alimente))

# Inițializare session state
if 'selected_coords' not in st.session_state:
    st.session_state.selected_coords = {
        'loc_consum': 'C1',
        'masa_zi': 'M1', 
        'regim_alimentar': 'R1',
        'data': datetime.now().strftime('%d.%m.%Y')
    }

if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = {'recetar': None, 'cza': None}

# Titlu aplicație
st.title("🍽️ Aplicația Dieta")

# Crearea taburilor
tab1, tab2, tab3, tab4 = st.tabs(["📖 Rețetar", "📍 Coordonate CZA", "📊 CZA", "📋 Listă Alimente"])

# TAB 1: REȚETAR
with tab1:
    st.header("Rețetar")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Afișare tabel rețetar
        recetar_data = load_data(RECETAR_FILE)
        
        if recetar_data:
            # Creează un DataFrame pentru afișare
            display_data = []
            for i, reteta in enumerate(recetar_data):
                for j, ingredient in enumerate(reteta.get('ingrediente', [])):
                    display_data.append({
                        'ID': f"{i}-{j}",
                        'Aliment': reteta['nume'],
                        'Ingredient': ingredient['ingredient'],
                        'UM': ingredient['um'],
                        'Cantitate/Porție': ingredient['cantitate']
                    })
            
            if display_data:
                df = pd.DataFrame(display_data)
                
                # Afișare tabel cu opțiuni de editare/ștergere
                for idx, row in df.iterrows():
                    col_data, col_edit, col_delete = st.columns([4, 1, 1])
                    
                    with col_data:
                        st.write(f"**{row['Aliment']}**: {row['Ingredient']} - {row['Cantitate/Porție']} {row['UM']}")
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_recetar_{row['ID']}", help="Editează"):
                            st.session_state.edit_mode['recetar'] = row['ID']
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️", key=f"delete_recetar_{row['ID']}", help="Șterge"):
                            # Șterge ingredientul
                            reteta_idx, ingredient_idx = map(int, row['ID'].split('-'))
                            if 0 <= reteta_idx < len(recetar_data):
                                if 0 <= ingredient_idx < len(recetar_data[reteta_idx]['ingrediente']):
                                    del recetar_data[reteta_idx]['ingrediente'][ingredient_idx]
                                    # Șterge rețeta dacă nu mai are ingrediente
                                    if not recetar_data[reteta_idx]['ingrediente']:
                                        del recetar_data[reteta_idx]
                                    save_data(recetar_data, RECETAR_FILE)
                                    st.rerun()
        else:
            st.info("Nu există rețete în baza de date.")
    
    with col2:
        # Formular pentru adăugare/editare
        if st.session_state.edit_mode['recetar']:
            st.subheader("Editează Ingredient")
            # Logica de editare
            reteta_idx, ingredient_idx = map(int, st.session_state.edit_mode['recetar'].split('-'))
            if 0 <= reteta_idx < len(recetar_data) and 0 <= ingredient_idx < len(recetar_data[reteta_idx]['ingrediente']):
                current_ingredient = recetar_data[reteta_idx]['ingrediente'][ingredient_idx]
                current_aliment = recetar_data[reteta_idx]['nume']
                
                with st.form("edit_recetar_form"):
                    edit_aliment = st.text_input("Aliment", value=current_aliment)
                    edit_ingredient = st.text_input("Ingredient", value=current_ingredient['ingredient'])
                    edit_um = st.selectbox("UM", ['g', 'kg', 'ml', 'l', 'buc', 'lingură', 'linguriță', 'cană'], 
                                         index=['g', 'kg', 'ml', 'l', 'buc', 'lingură', 'linguriță', 'cană'].index(current_ingredient['um']) if current_ingredient['um'] in ['g', 'kg', 'ml', 'l', 'buc', 'lingură', 'linguriță', 'cană'] else 0)
                    edit_cantitate = st.number_input("Cantitate/Porție", value=current_ingredient['cantitate'], min_value=0.0, step=0.1)
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Salvează", use_container_width=True):
                            # Actualizează ingredientul
                            recetar_data[reteta_idx]['nume'] = edit_aliment
                            recetar_data[reteta_idx]['ingrediente'][ingredient_idx] = {
                                'ingredient': edit_ingredient,
                                'um': edit_um,
                                'cantitate': edit_cantitate
                            }
                            save_data(recetar_data, RECETAR_FILE)
                            st.session_state.edit_mode['recetar'] = None
                            st.success("Ingredient actualizat!")
                            st.rerun()
                    
                    with col_cancel:
                        if st.form_submit_button("❌ Anulează", use_container_width=True):
                            st.session_state.edit_mode['recetar'] = None
                            st.rerun()
        else:
            st.subheader("Adaugă Ingredient Nou")
            
            with st.form("add_recetar_form"):
                new_aliment = st.text_input("Aliment")
                new_ingredient = st.text_input("Ingredient")
                new_um = st.selectbox("UM", ['g', 'kg', 'ml', 'l', 'buc', 'lingură', 'linguriță', 'cană'])
                new_cantitate = st.number_input("Cantitate/Porție", min_value=0.0, step=0.1)
                
                if st.form_submit_button("➕ Adaugă Ingredient", use_container_width=True):
                    if new_aliment and new_ingredient and new_cantitate > 0:
                        # Caută dacă alimentul există deja
                        found = False
                        for reteta in recetar_data:
                            if reteta['nume'].lower() == new_aliment.lower():
                                reteta['ingrediente'].append({
                                    'ingredient': new_ingredient,
                                    'um': new_um,
                                    'cantitate': new_cantitate
                                })
                                found = True
                                break
                        
                        if not found:
                            # Creează o rețetă nouă
                            recetar_data.append({
                                'nume': new_aliment,
                                'ingrediente': [{
                                    'ingredient': new_ingredient,
                                    'um': new_um,
                                    'cantitate': new_cantitate
                                }]
                            })
                        
                        save_data(recetar_data, RECETAR_FILE)
                        st.success("Ingredient adăugat!")
                        st.rerun()
                    else:
                        st.error("Completează toate câmpurile!")

# TAB 2: COORDONATE CZA
with tab2:
    st.header("Coordonate CZA")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        loc_consum = st.selectbox("Loc Consum", ['C1', 'C2', 'C3'], 
                                 index=['C1', 'C2', 'C3'].index(st.session_state.selected_coords['loc_consum']))
    
    with col2:
        masa_zi = st.selectbox("Masa din zi", ['M1', 'M2', 'M3', 'M4', 'M5'],
                              index=['M1', 'M2', 'M3', 'M4', 'M5'].index(st.session_state.selected_coords['masa_zi']))
    
    with col3:
        regim_alimentar = st.selectbox("Regim Alimentar", ['R1', 'R2', 'R3', 'R4', 'R5', 'R6'],
                                      index=['R1', 'R2', 'R3', 'R4', 'R5', 'R6'].index(st.session_state.selected_coords['regim_alimentar']))
    
    with col4:
        data_selectata = st.date_input("Data", value=datetime.strptime(st.session_state.selected_coords['data'], '%d.%m.%Y'))
        data_str = data_selectata.strftime('%d.%m.%Y')
    
    # Actualizează coordonatele în session state
    st.session_state.selected_coords = {
        'loc_consum': loc_consum,
        'masa_zi': masa_zi,
        'regim_alimentar': regim_alimentar,
        'data': data_str
    }
    
    st.info(f"**Coordonate selectate:** {loc_consum} | {masa_zi} | {regim_alimentar} | {data_str}")

# TAB 3: CZA
with tab3:
    st.header("CZA (Cantitate Zilnică Alimente)")
    
    # Generează cheia pentru coordonatele curente
    coords_key = f"{st.session_state.selected_coords['loc_consum']}_{st.session_state.selected_coords['masa_zi']}_{st.session_state.selected_coords['regim_alimentar']}_{st.session_state.selected_coords['data']}"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Afișare date CZA pentru coordonatele selectate
        cza_data = load_data(CZA_FILE)
        current_cza = cza_data.get(coords_key, [])
        
        if current_cza:
            st.subheader(f"CZA pentru {coords_key.replace('_', ' | ')}")
            
            for i, record in enumerate(current_cza):
                col_data, col_edit, col_delete = st.columns([4, 1, 1])
                
                with col_data:
                    st.write(f"**{record['ingredient']}**: {record['nr_persoane']} pers. × {record['cantitate_per_persoana']} {record['um']} = {record['cantitate_totala']} {record['um']}")
                
                with col_edit:
                    if st.button("✏️", key=f"edit_cza_{i}", help="Editează"):
                        st.session_state.edit_mode['cza'] = i
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_cza_{i}", help="Șterge"):
                        del current_cza[i]
                        cza_data[coords_key] = current_cza
                        if not current_cza:
                            del cza_data[coords_key]
                        save_data(cza_data, CZA_FILE)
                        st.rerun()
        else:
            st.info("Nu există înregistrări CZA pentru coordonatele selectate.")
    
    with col2:
        # Formular pentru adăugare/editare CZA
        alimente_disponibile = get_unique_alimente()
        
        if alimente_disponibile:
            if st.session_state.edit_mode['cza'] is not None:
                st.subheader("Editează CZA")
                
                if st.session_state.edit_mode['cza'] < len(current_cza):
                    current_record = current_cza[st.session_state.edit_mode['cza']]
                    
                    with st.form("edit_cza_form"):
                        edit_ingredient = st.selectbox("Ingredient", alimente_disponibile,
                                                     index=alimente_disponibile.index(current_record['ingredient']) if current_record['ingredient'] in alimente_disponibile else 0)
                        edit_nr_persoane = st.number_input("Nr. Persoane", value=current_record['nr_persoane'], min_value=1, step=1)
                        edit_um = st.selectbox("UM", ['g', 'kg', 'ml', 'l', 'buc', 'lingură', 'linguriță', 'cană'],
                                             index=['g', 'kg', 'ml', 'l', 'buc', 'lingură', 'linguriță', 'cană'].index(current_record['um']) if current_record['um'] in ['g', 'kg', 'ml', 'l', 'buc', 'lingură', 'linguriță', 'cană'] else 0)
                        edit_cantitate_per_persoana = st.number_input("Cantitate per persoană", value=current_record['cantitate_per_persoana'], min_value=0.0, step=0.1)
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Salvează", use_container_width=True):
                                cantitate_totala = edit_nr_persoane * edit_cantitate_per_persoana
                                
                                current_cza[st.session_state.edit_mode['cza']] = {
                                    'ingredient': edit_ingredient,
                                    'nr_persoane': edit_nr_persoane,
                                    'um': edit_um,
                                    'cantitate_per_persoana': edit_cantitate_per_persoana,
                                    'cantitate_totala': cantitate_totala
                                }
                                
                                cza_data[coords_key] = current_cza
                                save_data(cza_data, CZA_FILE)
                                st.session_state.edit_mode['cza'] = None
                                st.success("CZA actualizat!")
                                st.rerun()
                        
                        with col_cancel:
                            if st.form_submit_button("❌ Anulează", use_container_width=True):
                                st.session_state.edit_mode['cza'] = None
                                st.rerun()
            else:
                st.subheader("Adaugă CZA Nou")
                
                with st.form("add_cza_form"):
                    cza_ingredient = st.selectbox("Ingredient", [''] + alimente_disponibile)
                    cza_nr_persoane = st.number_input("Nr. Persoane", min_value=1, value=1, step=1)
                    cza_um = st.selectbox("UM", ['g', 'kg', 'ml', 'l', 'buc', 'lingură', 'linguriță', 'cană'])
                    cza_cantitate_per_persoana = st.number_input("Cantitate per persoană", min_value=0.0, step=0.1)
                    
                    if st.form_submit_button("➕ Adaugă CZA", use_container_width=True):
                        if cza_ingredient and cza_cantitate_per_persoana > 0:
                            cantitate_totala = cza_nr_persoane * cza_cantitate_per_persoana
                            
                            new_record = {
                                'ingredient': cza_ingredient,
                                'nr_persoane': cza_nr_persoane,
                                'um': cza_um,
                                'cantitate_per_persoana': cza_cantitate_per_persoana,
                                'cantitate_totala': cantitate_totala
                            }
                            
                            if coords_key not in cza_data:
                                cza_data[coords_key] = []
                            cza_data[coords_key].append(new_record)
                            
                            save_data(cza_data, CZA_FILE)
                            st.success("CZA adăugat!")
                            st.rerun()
                        else:
                            st.error("Selectează ingredientul și completează cantitatea!")
        else:
            st.warning("Nu există alimente în rețetar. Adaugă mai întâi alimente în rețetar.")

# TAB 4: LISTĂ ALIMENTE
with tab4:
    st.header("Listă Alimente")
    
    # Selectare dată pentru lista de alimente
    data_lista = st.date_input("Selectează data pentru lista de alimente", 
                              value=datetime.strptime(st.session_state.selected_coords['data'], '%d.%m.%Y'),
                              key="data_lista")
    data_lista_str = data_lista.strftime('%d.%m.%Y')
    
    st.subheader(f"Lista de alimente pentru {data_lista_str}")
    
    # Calculează totalurile pentru data selectată
    cza_data = load_data(CZA_FILE)
    totals = {}
    
    for coords_key, records in cza_data.items():
        # Extrage data din cheia coordonatelor
        parts = coords_key.split('_')
        if len(parts) >= 4 and parts[3] == data_lista_str:
            for record in records:
                ingredient = record['ingredient']
                um = record['um']
                cantitate = record['cantitate_totala']
                
                key = f"{ingredient}_{um}"
                if key not in totals:
                    totals[key] = {'ingredient': ingredient, 'um': um, 'cantitate_totala': 0}
                totals[key]['cantitate_totala'] += cantitate
    
    if totals:
        # Afișează rezultatele
        st.success(f"Găsite {len(totals)} ingrediente pentru data {data_lista_str}")
        
        # Sortează după nume ingredient
        sorted_totals = sorted(totals.values(), key=lambda x: x['ingredient'])
        
        for total in sorted_totals:
            st.write(f"**{total['ingredient']}**: {total['cantitate_totala']:.1f} {total['um']}")
        
        # Opțiune de export
        if st.button("📥 Exportă lista"):
            export_data = []
            for total in sorted_totals:
                export_data.append({
                    'Ingredient': total['ingredient'],
                    'Cantitate Totală': total['cantitate_totala'],
                    'UM': total['um']
                })
            
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="💾 Descarcă CSV",
                data=csv,
                file_name=f"lista_alimente_{data_lista_str.replace('.', '_')}.csv",
                mime="text/csv"
            )
    else:
        st.info(f"Nu există înregistrări CZA pentru data {data_lista_str}")

# Footer
st.markdown("---")
st.markdown("💾 **Stocare**: Toate datele sunt salvate persistent în `$HOME/data/`")