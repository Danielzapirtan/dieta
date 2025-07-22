import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# Configurare pagină
st.set_page_config(
    page_title="Aplicație Dieta",
    page_icon="🍽️",
    layout="wide"
)

# Inițializare session state
def init_session_state():
    if 'retetar' not in st.session_state:
        st.session_state.retetar = {}
    if 'cza_data' not in st.session_state:
        st.session_state.cza_data = {}
    if 'alimente_list' not in st.session_state:
        st.session_state.alimente_list = set()

init_session_state()

# Funcții helper
def get_unique_key(prefix=""):
    return f"{prefix}_{str(uuid.uuid4())[:8]}"

def format_date(date_obj):
    return date_obj.strftime("%d.%m.%Y")

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except:
        return date.today()

# Titlu principal
st.title("🍽️ Aplicație Dieta - Nutriționist")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Rețetar", "📍 Coordonate CZA", "📊 CZA", "📝 Listă Alimente"])

# TAB 1: REȚETAR
with tab1:
    st.header("📋 Rețetar")
    
    # Selectare aliment existent sau nou
    col1, col2 = st.columns([2, 1])
    
    with col1:
        existing_foods = list(st.session_state.retetar.keys()) if st.session_state.retetar else []
        selected_food = st.selectbox("Selectează aliment existent:", [""] + existing_foods, key="select_food_retetar")
        
        if not selected_food:
            new_food = st.text_input("Sau adaugă aliment nou:", key="new_food_retetar")
            current_food = new_food
        else:
            current_food = selected_food
    
    with col2:
        st.write("**Acțiuni:**")
        if current_food and current_food in st.session_state.retetar:
            if st.button("🗑️ Șterge Aliment", key="delete_food"):
                del st.session_state.retetar[current_food]
                st.session_state.alimente_list.discard(current_food)
                st.rerun()
    
    if current_food:
        st.subheader(f"Rețete pentru: {current_food}")
        
        # Inițializare aliment în rețetar
        if current_food not in st.session_state.retetar:
            st.session_state.retetar[current_food] = []
            st.session_state.alimente_list.add(current_food)
        
        # Formular pentru adăugare/editare rețetă
        with st.expander("➕ Adaugă/Editează rețetă", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ingredient = st.text_input("Ingredient:", key=f"ingredient_{current_food}")
            with col2:
                um = st.selectbox("UM:", ["g", "kg", "ml", "l", "buc", "lingură", "linguriță", "cană"], key=f"um_{current_food}")
            with col3:
                cantitate = st.number_input("Cantitate/Porție:", min_value=0.0, step=0.1, key=f"cantitate_{current_food}")
            with col4:
                st.write("")
                st.write("")
                if st.button("💾 Adaugă", key=f"add_recipe_{current_food}"):
                    if ingredient and cantitate > 0:
                        new_recipe = {
                            'id': str(uuid.uuid4()),
                            'ingredient': ingredient,
                            'um': um,
                            'cantitate': cantitate
                        }
                        st.session_state.retetar[current_food].append(new_recipe)
                        st.success(f"Rețeta adăugată pentru {current_food}!")
                        st.rerun()
        
        # Afișare rețete existente
        if st.session_state.retetar[current_food]:
            st.subheader("Rețete existente:")
            
            # Creare DataFrame pentru afișare
            recipes_data = []
            for recipe in st.session_state.retetar[current_food]:
                recipes_data.append({
                    'Ingredient': recipe['ingredient'],
                    'UM': recipe['um'],
                    'Cantitate/Porție': recipe['cantitate'],
                    'ID': recipe['id']
                })
            
            df_recipes = pd.DataFrame(recipes_data)
            
            # Selectare rețetă pentru editare/ștergere
            if len(df_recipes) > 0:
                st.dataframe(df_recipes[['Ingredient', 'UM', 'Cantitate/Porție']], use_container_width=True)
                
                # Editare rețetă
                recipe_to_edit = st.selectbox("Selectează rețetă pentru editare:", 
                                            [""] + [f"{r['ingredient']} - {r['cantitate']} {r['um']}" for r in st.session_state.retetar[current_food]], 
                                            key=f"edit_recipe_{current_food}")
                
                if recipe_to_edit:
                    recipe_index = next((i for i, r in enumerate(st.session_state.retetar[current_food]) 
                                       if f"{r['ingredient']} - {r['cantitate']} {r['um']}" == recipe_to_edit), None)
                    
                    if recipe_index is not None:
                        recipe = st.session_state.retetar[current_food][recipe_index]
                        
                        with st.form(f"edit_form_{current_food}_{recipe_index}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                edit_ingredient = st.text_input("Ingredient:", value=recipe['ingredient'])
                            with col2:
                                edit_um = st.selectbox("UM:", ["g", "kg", "ml", "l", "buc", "lingură", "linguriță", "cană"], 
                                                     index=["g", "kg", "ml", "l", "buc", "lingură", "linguriță", "cană"].index(recipe['um']))
                            with col3:
                                edit_cantitate = st.number_input("Cantitate/Porție:", value=recipe['cantitate'], min_value=0.0, step=0.1)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Salvează modificările"):
                                    st.session_state.retetar[current_food][recipe_index] = {
                                        'id': recipe['id'],
                                        'ingredient': edit_ingredient,
                                        'um': edit_um,
                                        'cantitate': edit_cantitate
                                    }
                                    st.success("Rețeta actualizată!")
                                    st.rerun()
                            
                            with col2:
                                if st.form_submit_button("🗑️ Șterge rețeta"):
                                    del st.session_state.retetar[current_food][recipe_index]
                                    st.success("Rețeta ștearsă!")
                                    st.rerun()
        else:
            st.info(f"Nu există rețete pentru {current_food}. Adaugă prima rețetă!")

# TAB 2: COORDONATE CZA
with tab2:
    st.header("📍 Coordonate CZA")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        loc_consum = st.selectbox("Loc consum:", ["C1", "C2", "C3"], key="coord_loc")
    
    with col2:
        masa_zi = st.selectbox("Masa din zi:", ["M1", "M2", "M3", "M4", "M5"], key="coord_masa")
    
    with col3:
        regim = st.selectbox("Regim alimentar:", ["R1", "R2", "R3", "R4", "R5", "R6"], key="coord_regim")
    
    with col4:
        data_coord = st.date_input("Data:", value=date.today(), key="coord_data")
    
    # Afișare coordonate selectate
    st.info(f"**Coordonate selectate:** {loc_consum} - {masa_zi} - {regim} - {format_date(data_coord)}")
    
    # Stocare coordonate în session state pentru utilizare în alte taburi
    st.session_state.current_coords = {
        'loc': loc_consum,
        'masa': masa_zi,
        'regim': regim,
        'data': format_date(data_coord)
    }

# TAB 3: CZA (Cantitate Zilnică Alimente)
with tab3:
    st.header("📊 CZA - Cantitate Zilnică Alimente")
    
    # Verificare dacă există coordonate selectate
    if 'current_coords' not in st.session_state:
        st.warning("Selectează coordonatele în tab-ul 'Coordonate CZA' mai întâi!")
    else:
        coords = st.session_state.current_coords
        coord_key = f"{coords['loc']}_{coords['masa']}_{coords['regim']}_{coords['data']}"
        
        st.info(f"**Coordonate active:** {coords['loc']} - {coords['masa']} - {coords['regim']} - {coords['data']}")
        
        # Inițializare date pentru coordonatele curente
        if coord_key not in st.session_state.cza_data:
            st.session_state.cza_data[coord_key] = {}
        
        # Selectare aliment pentru CZA
        available_foods = list(st.session_state.alimente_list) if st.session_state.alimente_list else []
        
        if not available_foods:
            st.warning("Nu există alimente în rețetar! Adaugă alimente în tab-ul 'Rețetar' mai întâi.")
        else:
            selected_cza_food = st.selectbox("Selectează aliment pentru CZA:", [""] + available_foods, key="cza_food_select")
            
            if selected_cza_food:
                st.subheader(f"CZA pentru: {selected_cza_food}")
                
                # Inițializare aliment pentru coordonatele curente
                if selected_cza_food not in st.session_state.cza_data[coord_key]:
                    st.session_state.cza_data[coord_key][selected_cza_food] = []
                
                # Formular pentru adăugare CZA
                with st.expander("➕ Adaugă înregistrare CZA", expanded=False):
                    if selected_cza_food in st.session_state.retetar and st.session_state.retetar[selected_cza_food]:
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            # Selectare ingredient din rețetar
                            ingredients = [r['ingredient'] for r in st.session_state.retetar[selected_cza_food]]
                            selected_ingredient = st.selectbox("Ingredient:", ingredients, key=f"cza_ingredient_{coord_key}")
                        
                        with col2:
                            nr_persoane = st.number_input("Nr. persoane:", min_value=1, value=1, key=f"cza_persoane_{coord_key}")
                        
                        with col3:
                            # Găsire UM pentru ingredientul selectat
                            ingredient_data = next((r for r in st.session_state.retetar[selected_cza_food] if r['ingredient'] == selected_ingredient), None)
                            if ingredient_data:
                                st.text_input("UM:", value=ingredient_data['um'], disabled=True, key=f"cza_um_display_{coord_key}")
                                current_um = ingredient_data['um']
                            else:
                                current_um = "g"
                        
                        with col4:
                            cantitate_cza = st.number_input("Cantitate:", min_value=0.0, step=0.1, key=f"cza_cantitate_{coord_key}")
                        
                        with col5:
                            st.write("")
                            st.write("")
                            if st.button("💾 Adaugă CZA", key=f"add_cza_{coord_key}"):
                                if cantitate_cza > 0:
                                    new_cza = {
                                        'id': str(uuid.uuid4()),
                                        'ingredient': selected_ingredient,
                                        'nr_persoane': nr_persoane,
                                        'um': current_um,
                                        'cantitate': cantitate_cza,
                                        'total_cantitate': cantitate_cza * nr_persoane
                                    }
                                    st.session_state.cza_data[coord_key][selected_cza_food].append(new_cza)
                                    st.success("Înregistrare CZA adăugată!")
                                    st.rerun()
                    else:
                        st.warning(f"Nu există rețete pentru {selected_cza_food} în rețetar!")
                
                # Afișare înregistrări CZA existente
                if st.session_state.cza_data[coord_key][selected_cza_food]:
                    st.subheader("Înregistrări CZA existente:")
                    
                    # Creare DataFrame pentru afișare
                    cza_data_list = []
                    for cza in st.session_state.cza_data[coord_key][selected_cza_food]:
                        cza_data_list.append({
                            'Ingredient': cza['ingredient'],
                            'Nr. Persoane': cza['nr_persoane'],
                            'UM': cza['um'],
                            'Cantitate': cza['cantitate'],
                            'Total Cantitate': cza['total_cantitate'],
                            'ID': cza['id']
                        })
                    
                    df_cza = pd.DataFrame(cza_data_list)
                    st.dataframe(df_cza[['Ingredient', 'Nr. Persoane', 'UM', 'Cantitate', 'Total Cantitate']], use_container_width=True)
                    
                    # Editare/ștergere CZA
                    cza_to_edit = st.selectbox("Selectează înregistrare pentru editare:", 
                                             [""] + [f"{c['ingredient']} - {c['cantitate']} {c['um']}" for c in st.session_state.cza_data[coord_key][selected_cza_food]], 
                                             key=f"edit_cza_{coord_key}")
                    
                    if cza_to_edit:
                        cza_index = next((i for i, c in enumerate(st.session_state.cza_data[coord_key][selected_cza_food]) 
                                        if f"{c['ingredient']} - {c['cantitate']} {c['um']}" == cza_to_edit), None)
                        
                        if cza_index is not None:
                            cza = st.session_state.cza_data[coord_key][selected_cza_food][cza_index]
                            
                            with st.form(f"edit_cza_form_{coord_key}_{cza_index}"):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    edit_nr_persoane = st.number_input("Nr. persoane:", value=cza['nr_persoane'], min_value=1)
                                with col2:
                                    st.text_input("UM:", value=cza['um'], disabled=True)
                                with col3:
                                    edit_cantitate_cza = st.number_input("Cantitate:", value=cza['cantitate'], min_value=0.0, step=0.1)
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.form_submit_button("💾 Salvează modificările"):
                                        st.session_state.cza_data[coord_key][selected_cza_food][cza_index] = {
                                            'id': cza['id'],
                                            'ingredient': cza['ingredient'],
                                            'nr_persoane': edit_nr_persoane,
                                            'um': cza['um'],
                                            'cantitate': edit_cantitate_cza,
                                            'total_cantitate': edit_cantitate_cza * edit_nr_persoane
                                        }
                                        st.success("Înregistrare CZA actualizată!")
                                        st.rerun()
                                
                                with col2:
                                    if st.form_submit_button("🗑️ Șterge înregistrarea"):
                                        del st.session_state.cza_data[coord_key][selected_cza_food][cza_index]
                                        st.success("Înregistrare CZA ștearsă!")
                                        st.rerun()
                else:
                    st.info(f"Nu există înregistrări CZA pentru {selected_cza_food} la coordonatele selectate.")

# TAB 4: LISTĂ ALIMENTE
with tab4:
    st.header("📝 Listă Alimente")
    
    # Selectare data pentru calculare
    data_lista = st.date_input("Selectează data pentru listă:", value=date.today(), key="data_lista")
    data_lista_str = format_date(data_lista)
    
    st.subheader(f"Lista alimentelor pentru data: {data_lista_str}")
    
    # Calculare totaluri pentru data selectată
    ingredient_totals = {}
    
    # Parcurgere toate coordonatele CZA pentru data selectată
    for coord_key, coord_data in st.session_state.cza_data.items():
        coord_parts = coord_key.split('_')
        if len(coord_parts) == 4 and coord_parts[3] == data_lista_str:
            # Pentru fiecare aliment din această coordonată
            for food, cza_records in coord_data.items():
                for cza in cza_records:
                    ingredient = cza['ingredient']
                    um = cza['um']
                    total_cantitate = cza['total_cantitate']
                    
                    # Cheie unică pentru ingredient + UM
                    key = f"{ingredient}_{um}"
                    
                    if key not in ingredient_totals:
                        ingredient_totals[key] = {
                            'ingredient': ingredient,
                            'um': um,
                            'total': 0
                        }
                    
                    ingredient_totals[key]['total'] += total_cantitate
    
    # Afișare rezultate
    if ingredient_totals:
        lista_data = []
        for key, data in ingredient_totals.items():
            lista_data.append({
                'Ingredient': data['ingredient'],
                'UM': data['um'],
                'Cantitate Totală': round(data['total'], 2)
            })
        
        df_lista = pd.DataFrame(lista_data)
        df_lista = df_lista.sort_values('Ingredient')
        
        st.dataframe(df_lista, use_container_width=True)
        
        # Opțiune de export
        csv = df_lista.to_csv(index=False)
        st.download_button(
            label="📥 Descarcă lista ca CSV",
            data=csv,
            file_name=f"lista_alimente_{data_lista_str.replace('.', '_')}.csv",
            mime='text/csv'
        )
        
        # Statistici
        st.subheader("📈 Statistici")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total ingrediente", len(df_lista))
        
        with col2:
            st.metric("Total înregistrări CZA", sum(len(cza_records) for coord_data in st.session_state.cza_data.values() 
                                                   for cza_records in coord_data.values() 
                                                   if any(coord_key.endswith(data_lista_str) for coord_key in st.session_state.cza_data.keys())))
        
    else:
        st.info(f"Nu există date CZA pentru data {data_lista_str}")

# Sidebar cu informații
with st.sidebar:
    st.header("📊 Rezumat Aplicație")
    st.write(f"**Alimente în rețetar:** {len(st.session_state.retetar)}")
    
    total_recipes = sum(len(recipes) for recipes in st.session_state.retetar.values())
    st.write(f"**Total rețete:** {total_recipes}")
    
    total_coords = len(st.session_state.cza_data)
    st.write(f"**Coordonate CZA:** {total_coords}")
    
    total_cza = sum(len(cza_records) for coord_data in st.session_state.cza_data.values() for cza_records in coord_data.values())
    st.write(f"**Total înregistrări CZA:** {total_cza}")
    
    if st.button("🗑️ Resetează toate datele"):
        st.session_state.retetar = {}
        st.session_state.cza_data = {}
        st.session_state.alimente_list = set()
        st.success("Toate datele au fost resetate!")
        st.rerun()