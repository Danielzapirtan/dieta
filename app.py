import streamlit as st
import pandas as pd
from datetime import datetime

# Configurare pagină
st.set_page_config(
    page_title="Aplicația Dieta - Compoziția zilnică a alimentelor",
    page_icon="🍽️",
    layout="wide"
)

# Inițializare session state pentru stocarea datelor
if 'data_storage' not in st.session_state:
    st.session_state.data_storage = {}

def get_key_from_selection(loc, regim, masa, zi, luna, an):
    """Generează cheia pentru stocarea datelor bazată pe selecția utilizatorului"""
    return f"{loc}_{regim}_{masa}_{zi:02d}_{luna:02d}_{an}"

def get_empty_dataframe():
    """Returnează un DataFrame gol cu coloanele necesare"""
    return pd.DataFrame(columns=[
        'Fel de mâncare',
        'Aliment', 
        'Nr. persoane', 
        'Unitate măsură', 
        'Cantitate', 
        'Gramaj/persoană', 
        'Porție/persoană'
    ])

def main():
    st.title("🍽️ Aplicația Dieta - Compoziția zilnică a alimentelor")
    st.markdown("---")
    
    # Layout cu două coloane
    col_left, col_right = st.columns([1, 2])
    
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
        
        # Statistici rapide
        current_key = get_key_from_selection(loc_consum, regim, masa, zi, luna, an)
        total_combinations = len(st.session_state.data_storage)
        current_records = len(st.session_state.data_storage.get(current_key, pd.DataFrame()))
        
        st.markdown("### 📈 Statistici:")
        st.metric("Total combinații", total_combinations)
        st.metric("Înregistrări curente", current_records)
    
    with col_right:
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
                    fel_mancare = st.text_input("Fel de mâncare:")
                    aliment = st.text_input("Aliment:")
                    nr_persoane = st.number_input("Nr. persoane:", min_value=1, value=1)
                    unitate = st.selectbox("Unitate măsură:", ["kg", "g", "l", "ml", "bucăți", "porții"])
                
                with col2:
                    cantitate = st.number_input("Cantitate:", min_value=0.0, step=0.1, format="%.2f")
                    gramaj_persoana = st.number_input("Gramaj/persoană:", min_value=0.0, step=0.1, format="%.2f")
                    portie_persoana = st.number_input("Porție/persoană:", min_value=0.0, step=0.1, format="%.2f")
                
                submitted = st.form_submit_button("Adaugă aliment")
                
                if submitted and fel_mancare and aliment:
                    # Adăugare înregistrare nouă
                    new_record = pd.DataFrame([{
                        'Fel de mâncare': fel_mancare,
                        'Aliment': aliment,
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
                    st.success(f"Alimentul '{aliment}' din categoria '{fel_mancare}' a fost adăugat cu succes!")
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
                    "Fel de mâncare": st.column_config.TextColumn("Fel de mâncare", width="medium"),
                    "Aliment": st.column_config.TextColumn("Aliment", width="medium"),
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
                # Export CSV (simulat)
                if st.button("📄 Export CSV"):
                    csv_data = edited_data.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Descarcă CSV",
                        data=csv_data,
                        file_name=f"dieta_{storage_key}.csv",
                        mime="text/csv"
                    )
            
            # Sumar rapid
            if not edited_data.empty:
                st.markdown("### 📋 Sumar:")
                total_alimente = len(edited_data)
                total_cantitate = edited_data['Cantitate'].sum()
                
                col_sum1, col_sum2 = st.columns(2)
                with col_sum1:
                    st.metric("Total alimente", total_alimente)
                with col_sum2:
                    st.metric("Cantitate totală", f"{total_cantitate:.2f}")
        else:
            st.info("Nu există alimente înregistrate pentru această combinație. Folosește formularul de mai sus pentru a adăuga primul aliment.")
            
            # Informație despre combinațiile posibile
            st.markdown("### ℹ️ Informații despre combinații:")
            total_combinations_possible = 3 * 6 * 5 * 31 * 12 * 11  # C1-C3 × R1-R6 × M1-M5 × zile × luni × ani (2020-2030)
            st.caption(f"Combinații teoretice posibile: **{total_combinations_possible:,}**")
            st.caption("Fiecare combinație de indici (Loc, Regim, Masa, Zi, Luna, An) poate avea propria listă de alimente.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Aplicația Dieta v1.0 - Demo pentru gestionarea compoziției zilnice a alimentelor*")

if __name__ == "__main__":
    main()