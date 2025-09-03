import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord Financier Mensuel",
    page_icon="📊",
    layout="wide"
)

# Initialisation de l'état de session
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'sheets' not in st.session_state:
    st.session_state.sheets = []
if 'exchange_rates' not in st.session_state:
    st.session_state.exchange_rates = {
        'EUR': 0.875843475231553,  # Exemple de taux
        'GBP': 1.14175652188951,
        # Ajoutez d'autres devises au besoin
    }

# Fonctions de traitement
def process_excel_file(file):
    try:
        excel = pd.ExcelFile(file)
        sheets = excel.sheet_names
        data = {sheet: pd.read_excel(excel, sheet_name=sheet) for sheet in sheets}
        return data, sheets
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier: {str(e)}")
        return None, []

def convert_currency(df, column, from_currency, to_currency='USD'):
    if from_currency in st.session_state.exchange_rates:
        rate = st.session_state.exchange_rates[from_currency]
        df[column] = df[column] * rate
    return df

# Interface principale
st.title("Tableau de Bord Financier Mensuel - Application Streamlit")

# Barre latérale
with st.sidebar:
    st.header("Actions")
    
    # Upload du fichier Excel
    uploaded_file = st.file_uploader(
        "Uploader le fichier Excel Group Report",
        type=['xlsx', 'xls'],
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        if st.button("Charger les données"):
            st.session_state.data, st.session_state.sheets = process_excel_file(uploaded_file)
            st.success("Fichier chargé avec succès!")
    
    # Sélection de l'onglet/sheet
    if st.session_state.sheets:
        selected_sheet = st.selectbox(
            "Sélectionner un onglet",
            st.session_state.sheets
        )
    
    # Mise à jour des taux de change
    st.header("Gestion des Devises")
    currency = st.selectbox("Sélectionner une devise", list(st.session_state.exchange_rates.keys()))
    new_rate = st.number_input(f"Taux pour {currency} vers USD", value=st.session_state.exchange_rates[currency])
    if st.button("Mettre à jour le taux"):
        st.session_state.exchange_rates[currency] = new_rate
        st.success(f"Taux pour {currency} mis à jour!")

# Zone principale
if 'data' in st.session_state and st.session_state.data:
    if 'selected_sheet' in locals() and selected_sheet:
        st.header(f"Onglet: {selected_sheet}")
        df = st.session_state.data[selected_sheet]
        
        # Affichage du tableau
        st.dataframe(df.style.format("{:.2f}"))
        
        # Visualisations spécifiques selon l'onglet
        if selected_sheet == "Budget VS Actual":
            st.subheader("Comparaison Budget vs Forecast vs Actual")
            if 'Revenue' in df.columns and 'Direct Costs' in df.columns:
                fig = px.bar(
                    df,
                    x=df.index,
                    y=['Revenue', 'Direct Costs'],
                    title="Revenue vs Direct Costs",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif selected_sheet == "OPEX Group Analysis":
            st.subheader("Analyse des Dépenses OPEX")
            if 'Account Name' in df.columns and 'Jan 25' in df.columns:
                monthly_cols = [col for col in df.columns if col.endswith('25')]
                fig = px.line(
                    df,
                    x=monthly_cols,
                    y='Account Name',
                    title="Tendances des Dépenses par Compte"
                )
                st.plotly_chart(fig)
        
        elif selected_sheet == "P&L Per Customer":
            st.subheader("Rentabilité par Client")
            if 'Revenue' in df.columns and 'Cost of Sales' in df.columns:
                df['Gross Profit'] = df['Revenue'] - df['Cost of Sales']
                st.dataframe(df[['Revenue', 'Cost of Sales', 'Gross Profit']])
                fig = px.pie(df, values='Gross Profit', names=df.index, title="Répartition du Profit Brut par Client")
                st.plotly_chart(fig)
        
        elif selected_sheet == "Balance Sheet":
            st.subheader("Bilan Comptable")
            if 'Fixed Assets' in df.columns:
                fig = px.bar(df, x=df.index, y='Fixed Assets', title="Actifs Fixes")
                st.plotly_chart(fig)
        
        elif selected_sheet == "Sales Accruals":
            st.subheader("Régularisations des Ventes")
            if 'Amount' in df.columns:
                fig = px.histogram(df, x='Amount', title="Distribution des Montants")
                st.plotly_chart(fig)
        
        elif selected_sheet == "Accounts Receivable":
            st.subheader("Comptes Clients")
            if 'outstandingusd' in df.columns:
                overdue = df[df['statusDays'].str.contains('DUE')]
                st.write("Créances Échues")
                st.dataframe(overdue)
                fig = px.pie(overdue, values='outstandingusd', names='Name', title="Répartition des Créances Échues")
                st.plotly_chart(fig)
        
        # Conversion de devises générique
        if st.checkbox("Convertir en USD"):
            currency_col = st.selectbox("Colonne à convertir", df.select_dtypes(include=['float', 'int']).columns)
            from_currency = st.selectbox("De la devise", list(st.session_state.exchange_rates.keys()))
            df = convert_currency(df, currency_col, from_currency)
            st.dataframe(df)
else:
    st.info("Veuillez uploader un fichier Excel pour commencer.")

# Fonction pour afficher les tendances des devises
def show_currency_trends():
    st.header("Tendances des Devises")
    # Simulation de données de tendances (à remplacer par données réelles si disponibles)
    trend_data = pd.DataFrame({
        'Date': pd.date_range(start='2025-01-01', periods=7, freq='M'),
        'EUR': [0.87, 0.88, 0.875, 0.87, 0.86, 0.85, 0.84],
        'GBP': [1.14, 1.15, 1.14, 1.13, 1.12, 1.11, 1.10]
    })
    fig = px.line(trend_data, x='Date', y=['EUR', 'GBP'], title="Tendances des Taux de Change")
    st.plotly_chart(fig)
if st.sidebar.button("Voir les tendances des devises"):
    show_currency_trends()