import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurare pagină
st.set_page_config(
    page_title="Aplicația Dieta - Compoziția zilnică a alimentelor",
    page_icon="🍽️",
    layout="wide"
)

# Inițializare session state pentru stocarea datelor
if 'data_storage' not in st.session_state:
    st.session_state.data_storage = {}

if 'retetar' not in st.session_state:
    st.session_state.retetar = {}

def get_key_from_selection(loc, regim, masa, zi, luna, an):
    """Generează cheia pentru stocarea datelor bazată pe selecția utilizatorului"""
    return f"{loc}_{regim}_{masa}_{zi:02d}_{luna:02d}_{an}"

def get_empty_dataframe():
    """Returnează un DataFrame gol cu coloanele necesare"""
    return pd.DataFrame(columns=[
        'Aliment',
        'Ingredient', 
        'Nr. persoane', 
        'Unitate măsură', 
        'Cantitate', 
        'Gramaj/persoană', 
        'Porție/persoană'
    ])

def get_empty_recipe_dataframe():
    """Returnează un DataFrame gol pentru rețete"""
    return pd.DataFrame(columns=[
        'Ingredient',
        'Cantitate per porție',
        'Unitate măsură'
    ])

def calculate_tomorrow_supplies(zi, luna, an):
    """Calculează lista de aprovizionare pentru mâine"""
    # Calculare data de mâine
    try:
        current_date = datetime(an, luna, zi)
        tomorrow = current_date + timedelta(days=1)
        tomorrow_zi = tomorrow.day
        tomorrow_luna = tomorrow.month
        tomorrow_an = tomorrow.year
    except ValueError:
        return pd.DataFrame(columns=['Ingredient', 'Cantitate totală', 'Unitate măsură'])
    
    supplies = {}
    
    # Iterare prin toate combinațiile pentru data de mâine
    for key, data in st.session_state.data_storage.items():
        parts = key.split('_')
        if len(parts) == 6:
            _, _, _, key_zi, key_luna, key_an = parts
            if (int(key_zi) == tomorrow_zi and 
                int(key_luna) == tomorrow_luna and 
                int(key_an) == tomorrow_an):
                
                # Procesare fiecare înregistrare
                for _, row in data.iterrows():
                    aliment = row['Aliment']
                    nr_persoane = row['Nr. persoane']
                    
                    # Verifică dacă alimentul există în rețetar
                    if aliment in st.session_state.retetar:
                        recipe_df = st.session_state.retetar[aliment]
                        
                        # Calculare cantități pentru ingrediente
                        for _, recipe_row in recipe_df.iterrows():
                            ingredient = recipe_row['Ingredient']
                            cantitate_per_portie = recipe_row['Cantitate per porție']
                            unitate = recipe_row['Unitate măsură']
                            
                            total_cantitate = cantitate_per_portie * nr_persoane
                            
                            if ingredient not in supplies:
                                supplies[ingredient] = {'cantitate': 0, 'unitate': unitate}
                            
                            supplies[ingredient]['cantitate'] += total_cantitate
    
    # Convertire la DataFrame
    supplies_list = []
    for ingredient, data in supplies.items():
        supplies_list.append({
            'Ingredient': ingredient,
            'Cantitate totală': data['cantitate'],
            'Unitate măsură': data['unitate']
        })
    
    return pd.DataFrame(supplies_list)

def main():
    st.title("🍽️ Aplicația Dieta - Compoziția zilnică a alimentelor")
    st.markdown("---")
    
    # Layout cu trei coloane
    col_left, col_middle, col_right = st.columns([1, 1.5, 1.2])
    
    with col_left:
        st.header("📊 Indici de selecție")
        
        # Selectoarele pentru indici
        loc_consum = st.selectbox(
            "Loc de consum:",
            options=["C1", "C2", "C3"],
            key="loc_consum"
        )
        
        regim = st.selectbox(
            "Regim:",
            options=[f"R{i}" for i in range(1, 7)],
            key="regim"
        )
        
        masa = st.selectbox(
            "Masa:",
            options=[f"M{i}" for i in range(1, 6)],
            key="masa"
        )
        
        # Selectoare pentru dată
        col_zi, col_luna = st.columns(2)
        with col_zi:
            zi = st.number_input("Zi:", min_value=1, max_value=31, value=datetime.now().day)
        with col_luna:
            luna = st.number_input("Luna:", min_value=1, max_value=12, value=datetime.now().month)
        
        an = st.number_input("An:", min_value=2020, max_value=2030, value=datetime.now().year)
        
        # Afișare selecția curentă
        st.markdown("### 🔍 Selecția curentă:")
        st.info(f"""
        **Loc:** {loc_consum}  
        **Regim:** {regim}  
        **Masa:** {masa}  
        **Data:** {zi:02d}.{luna:02d}.{an}
        """)
        
        # Calculare și afișare data de mâine
        try:
            tomorrow = datetime(an, luna, zi) + timedelta(days=1)
            st.markdown("### 📅 Data de mâine:")
            st.success(f"{tomorrow.day:02d}.{tomorrow.month:02d}.{tomorrow.year}")
        except ValueError:
            st.error("Data invalidă selectată!")
        
        # Statistici rapide
        current_key = get_key_from_selection(loc_consum, regim, masa, zi, luna, an)
        total_combinations = len(st.session_state.data_storage)
        current_records = len(st.session_state.data_storage.get(current_key, pd.DataFrame()))
        total_recipes = len(st.session_state.retetar)
        
        st.markdown("### 📈 Statistici:")
        st.metric("Total combinații", total_combinations)
        st.metric("Înregistrări curente", current_records)
        st.metric("Rețete în baza de date", total_recipes)
    
    with col_middle:
        st.header("📝 Lista de alimente")
        
        # Generare cheie pentru stocarea datelor
        storage_key = get_key_from_selection(loc_consum, regim, masa, zi, luna, an)
        
        # Inițializare date pentru combinația curentă dacă nu există
        if storage_key not in st.session_state.data_storage:
            st.session_state.data_storage[storage_key] = get_empty_dataframe()
        
        # Obținere date curente
        current_data = st.session_state.data_storage[storage_key]
        
        # Formular pentru adăugare înregistrare nouă
        with st.expander("➕ Adaugă aliment nou", expanded=False):
            with st.form("add_food_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    aliment = st.text_input("Aliment (ex: ciorbă de dovlecei):")
                    ingredient = st.text_input("Ingredient principal:")
                    nr_persoane = st.number_input("Nr. persoane:", min_value=1, value=1)
                    unitate = st.selectbox("Unitate măsură:", ["kg", "g", "l", "ml", "bucăți", "porții"])
                
                with col2:
                    cantitate = st.number_input("Cantitate:", min_value=0.0, step=0.1, format="%.2f")
                    gramaj_persoana = st.number_input("Gramaj/persoană:", min_value=0.0, step=0.1, format="%.2f")
                    portie_persoana = st.number_input("Porție/persoană:", min_value=0.0, step=0.1, format="%.2f")
                
                submitted = st.form_submit_button("Adaugă aliment")
                
                if submitted and aliment and ingredient:
                    # Verifică dacă alimentul există în rețetar
                    if aliment not in st.session_state.retetar:
                        # Creează o rețetă nouă cu ingredientul principal
                        st.session_state.retetar[aliment] = pd.DataFrame([{
                            'Ingredient': ingredient,
                            'Cantitate per porție': cantitate,
                            'Unitate măsură': unitate
                        }])
                        st.info(f"Rețeta pentru '{aliment}' a fost creată automat!")
                    
                    # Adăugare înregistrare nouă
                    new_record = pd.DataFrame([{
                        'Aliment': aliment,
                        'Ingredient': ingredient,
                        'Nr. persoane': nr_persoane,
                        'Unitate măsură': unitate,
                        'Cantitate': cantitate,
                        'Gramaj/persoană': gramaj_persoana,
                        'Porție/persoană': portie_persoana
                    }])
                    
                    st.session_state.data_storage[storage_key] = pd.concat(
                        [current_data, new_record], 
                        ignore_index=True
                    )
                    st.success(f"Alimentul '{aliment}' a fost adăugat cu succes!")
                    st.rerun()
        
        # Afișare și editare date existente
        if not current_data.empty:
            st.markdown("### 🗃️ Alimente înregistrate:")
            
            # Editor de date
            edited_data = st.data_editor(
                current_data,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Aliment": st.column_config.TextColumn("Aliment", width="medium"),
                    "Ingredient": st.column_config.TextColumn("Ingredient", width="medium"),
                    "Nr. persoane": st.column_config.NumberColumn("Nr. persoane", min_value=1),
                    "Unitate măsură": st.column_config.SelectboxColumn(
                        "Unitate măsură",
                        options=["kg", "g", "l", "ml", "bucăți", "porții"]
                    ),
                    "Cantitate": st.column_config.NumberColumn("Cantitate", format="%.2f"),
                    "Gramaj/persoană": st.column_config.NumberColumn("Gramaj/persoană", format="%.2f"),
                    "Porție/persoană": st.column_config.NumberColumn("Porție/persoană", format="%.2f")
                }
            )
            
            # Actualizare date în session state
            st.session_state.data_storage[storage_key] = edited_data
            
            # Butoane de acțiuni
            col_actions = st.columns(3)
            with col_actions[0]:
                if st.button("🗑️ Șterge toate", type="secondary"):
                    st.session_state.data_storage[storage_key] = get_empty_dataframe()
                    st.success("Toate înregistrările au fost șterse!")
                    st.rerun()
            
            with col_actions[1]:
                # Calcul total persoane
                total_persoane = edited_data['Nr. persoane'].sum() if not edited_data.empty else 0
                st.metric("Total persoane", total_persoane)
            
            with col_actions[2]:
                # Export CSV
                if st.button("📄 Export CSV"):
                    csv_data = edited_data.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Descarcă CSV",
                        data=csv_data,
                        file_name=f"dieta_{storage_key}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("Nu există alimente înregistrate pentru această combinație.")
    
    with col_right:
        # Tabs pentru Rețetar și Lista Depozit
        tab_retetar, tab_depozit = st.tabs(["📖 Rețetar", "📋 Lista Depozit"])
        
        with tab_retetar:
            st.markdown("### 👨‍🍳 Gestiunea Rețetarului")
            
            # Selector pentru rețeta de editat
            if st.session_state.retetar:
                selected_recipe = st.selectbox(
                    "Selectează rețeta pentru editare:",
                    options=list(st.session_state.retetar.keys()),
                    key="recipe_selector"
                )
                
                if selected_recipe:
                    st.markdown(f"**Editare rețetă: {selected_recipe}**")
                    
                    # Editor pentru rețetă
                    recipe_data = st.session_state.retetar[selected_recipe]
                    
                    edited_recipe = st.data_editor(
                        recipe_data,
                        num_rows="dynamic",
                        use_container_width=True,
                        column_config={
                            "Ingredient": st.column_config.TextColumn("Ingredient"),
                            "Cantitate per porție": st.column_config.NumberColumn("Cantitate/porție", format="%.2f"),
                            "Unitate măsură": st.column_config.SelectboxColumn(
                                "Unitate",
                                options=["kg", "g", "l", "ml", "bucăți", "porții"]
                            )
                        },
                        key=f"recipe_editor_{selected_recipe}"
                    )
                    
                    # Actualizare rețetă
                    st.session_state.retetar[selected_recipe] = edited_recipe
                    
                    # Butoane pentru rețetă
                    col_recipe1, col_recipe2 = st.columns(2)
                    with col_recipe1:
                        if st.button(f"🗑️ Șterge rețeta", key=f"delete_{selected_recipe}"):
                            del st.session_state.retetar[selected_recipe]
                            st.success(f"Rețeta '{selected_recipe}' a fost ștearsă!")
                            st.rerun()
                    
                    with col_recipe2:
                        total_ingredients = len(edited_recipe) if not edited_recipe.empty else 0
                        st.metric("Ingrediente", total_ingredients)
            else:
                st.info("Nu există rețete în baza de date. Adaugă primul aliment pentru a crea o rețetă!")
            
            # Adăugare rețetă nouă manual
            with st.expander("➕ Creează rețetă nouă", expanded=False):
                with st.form("new_recipe_form"):
                    new_recipe_name = st.text_input("Nume aliment nou:")
                    
                    if st.form_submit_button("Creează rețetă goală") and new_recipe_name:
                        if new_recipe_name not in st.session_state.retetar:
                            st.session_state.retetar[new_recipe_name] = get_empty_recipe_dataframe()
                            st.success(f"Rețeta '{new_recipe_name}' a fost creată!")
                            st.rerun()
                        else:
                            st.warning("Această rețetă există deja!")
        
        with tab_depozit:
            st.markdown("### 🏪 Lista pentru Depozit (Mâine)")
            
            # Calculare listă aprovizionare
            supplies_df = calculate_tomorrow_supplies(zi, luna, an)
            
            if not supplies_df.empty:
                # Afișare listă
                st.dataframe(
                    supplies_df,
                    use_container_width=True,
                    column_config={
                        "Ingredient": st.column_config.TextColumn("Ingredient"),
                        "Cantitate totală": st.column_config.NumberColumn("Cantitate", format="%.2f"),
                        "Unitate măsură": st.column_config.TextColumn("Unitate")
                    }
                )
                
                # Statistici
                total_items = len(supplies_df)
                st.metric("Total ingrediente", total_items)
                
                # Export listă depozit
                if st.button("📄 Export Listă Depozit"):
                    try:
                        tomorrow = datetime(an, luna, zi) + timedelta(days=1)
                        csv_data = supplies_df.to_csv(index=False)
                        st.download_button(
                            label="⬇️ Descarcă Lista",
                            data=csv_data,
                            file_name=f"lista_depozit_{tomorrow.day:02d}{tomorrow.month:02d}{tomorrow.year}.csv",
                            mime="text/csv"
                        )
                    except ValueError:
                        st.error("Eroare la calcularea datei de mâine!")
            else:
                st.info("Nu există înregistrări pentru data de mâine sau nu există rețete complete.")
                
                # Afișare informații despre mâine
                try:
                    tomorrow = datetime(an, luna, zi) + timedelta(days=1)
                    st.caption(f"Se caută înregistrări pentru: {tomorrow.day:02d}.{tomorrow.month:02d}.{tomorrow.year}")
                except ValueError:
                    st.error("Data selectată este invalidă!")
    
    # Footer
    st.markdown("---")
    st.markdown("*Aplicația Dieta v2.0 - Cu Rețetar și Lista Depozit*")

if __name__ == "__main__":
    main()
