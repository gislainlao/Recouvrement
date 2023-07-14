import os
import pickle
import io
import math
from datetime import datetime
from zipfile import ZipFile
import locale
locale.setlocale(locale.LC_ALL, '')
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import shap
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler 
plt.style.use('fivethirtyeight')
import streamlit_authenticator as stauth
import database as db
import openpyxl
st.set_page_config(page_title="VENTES", page_icon="🧍",layout="wide")


import requests # Pour effectuer la requête
import pandas as pd # Pour manipuler les données

#Title display
html_temp = """
<div style="background-color: #D92F21; padding:10px; border-radius:10px">
<h1 style="color: white; text-align:center"> SUIVI DES VENTES JOURNALIERES</h1>
</div>
<p style="font-size: 20px; font-weight: bold; text-align:center"></p>
"""
st.markdown(html_temp, unsafe_allow_html=True)

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        excel_file.seek(0)
        return excel_file.getvalue()

data = requests.get("https://kf.kobotoolbox.org/api/v2/assets/aTAtvaEaLAsBKe2xssErRV/export-settings/esFTXXcYz64ichR3tshezYJ/data.xlsx")

df = pd.read_excel(data.content)
cols_to_drop = ['Signature','Signature PDV','start','end','Retrait CORIS', 'Moyen de reglement/ESPECES.2', 'Moyen de reglement/VIRTUEL FLOOZ.2', 'Moyen de reglement/VIRTUEL TMONEY.2', 'Moyen de reglement/BANQUE.2', 'Recouvrement CORIS', 'Dotation CORIS','Retrait Tmoney', 'Moyen de reglement/ESPECES.1', 'Moyen de reglement/VIRTUEL FLOOZ.1','Moyen de reglement/VIRTUEL TMONEY.1', 'Moyen de reglement/BANQUE.1', 'Recouvrement Tmoney','Dotation Tmoney', 'Dotation Flooz', 'Recouvrement Flooz', 'Services/DOTATION', 'Retrait Flooz', 'Services/RECOUVREMENT', 'Services/RETRAIT', 'Moyen de reglement/ESPECES', 'Moyen de reglement/VIRTUEL FLOOZ', 'Moyen de reglement/VIRTUEL TMONEY','Moyen de reglement/BANQUE','ma_question_geopoint', '_ma_question_geopoint_latitude', '_ma_question_geopoint_longitude','_ma_question_geopoint_altitude', '_ma_question_geopoint_precision','_id', '_uuid', '_submission_time', '_validation_status', '_notes','_status', '_submitted_by', '__version__', '_tags', '_index']
df = df.drop(columns=cols_to_drop)
# Fusionner les colonnes en une seule colonne pour chaque groupe
df["Num_Commercial"] = df["Num Commercial Flooz"].fillna(df["Num Commercial Tmoney"]).fillna(df["Num Commercial CORIS"])
df["Numero_PDV"] = df["Numero PDV Flooz"].fillna(df["Numero PDV Tmoney"]).fillna(df["Numero PDV CORIS"])
df["Numero_PDV_HR"] = df["Numero PDV Flooz HR"].fillna(df["Numero PDV Tmoney HR"]).fillna(df["Numero PDV CORIS HR"])
df["Montant_Dotation"] = df["Montant Dotation Flooz"].fillna(df["Montant Dotation Tmoney"]).fillna(df["Montant Dotation Coris"])
df["Moyen_reglement"] = df["Moyen de reglement"].fillna(df["Moyen de reglement.1"]).fillna(df["Moyen de reglement.2"])
df["Montant_Espece"] = df["Montant Espece Flooz"].fillna(df["Montant Espece Tmoney"]).fillna(df["Montant Espece CORIS"])
df["Numero_Flooz_Virtuel"] = df["Numero Flooz Virtuel"].fillna(df["Numero Flooz Virtuel.1"]).fillna(df["Numero Flooz Virtuel.2"])
df["Montant_Virtuel_Flooz"] = df["Montant Virtuel Flooz"].fillna(df["Montant Virtuel Flooz.1"]).fillna(df["Montant Virtuel Flooz.2"])
df["Numero_Tmoney_virtuel"] = df["Numero Tmoney virtuel"].fillna(df["Numero Tmoney virtuel.1"]).fillna(df["Numero Tmoney virtuel.2"])
df["Montant_Virtuel_Tmoney"] = df["Montant Virtuel Tmoney"].fillna(df["Montant Virtuel Tmoney.1"]).fillna(df["Montant Virtuel Tmoney.2"])
df["Banque_choisie"] = df["Banque choisie"].fillna(df["Banque choisie.1"]).fillna(df["Banque choisie.2"])
df["Montant_Banque"] = df["Montant Banque Flooz"].fillna(df["Montant Banque Tmoney"]).fillna(df["Montant Banque CORIS"])
df["Montant_Retrait"] = df["Montant Retrait Flooz"].fillna(df["Montant Retrait Tmoney"]).fillna(df["Montant Retrait Coris"])

# Supprimer les colonnes originales
df.drop(["Num Commercial Flooz", "Num Commercial Tmoney", "Num Commercial CORIS"], axis=1, inplace=True)
df.drop(["Numero PDV Flooz", "Numero PDV Tmoney", "Numero PDV CORIS"], axis=1, inplace=True)
df.drop(["Numero PDV Flooz HR", "Numero PDV Tmoney HR","Numero PDV CORIS HR"], axis=1, inplace=True)
df.drop(["Montant Dotation Flooz", "Montant Dotation Tmoney", "Montant Dotation Coris"], axis=1, inplace=True)
df.drop(["Moyen de reglement", "Moyen de reglement.1", "Moyen de reglement.2"], axis=1, inplace=True)
df.drop(["Montant Espece Flooz", "Montant Espece Tmoney", "Montant Espece CORIS"], axis=1, inplace=True)
df.drop(["Numero Flooz Virtuel", "Numero Flooz Virtuel.1", "Numero Flooz Virtuel.2"], axis=1, inplace=True)
df.drop(["Montant Virtuel Flooz", "Montant Virtuel Flooz.1","Montant Virtuel Flooz.2"], axis=1, inplace=True)
df.drop(["Numero Tmoney virtuel", "Numero Tmoney virtuel.1", "Numero Tmoney virtuel.2"], axis=1, inplace=True)
df.drop(["Montant Virtuel Tmoney", "Montant Virtuel Tmoney.1", "Montant Virtuel Tmoney.2"], axis=1, inplace=True)
df.drop(["Banque choisie", "Banque choisie.1", "Banque choisie.2"], axis=1, inplace=True)
df.drop(["Montant Banque Flooz", "Montant Banque Tmoney", "Montant Banque CORIS"], axis=1, inplace=True)
df.drop(["Montant Retrait Flooz", "Montant Retrait Tmoney", "Montant Retrait Coris"], axis=1, inplace=True)
df = df.rename(columns={'NOM COMMERCIAL': 'NOM_COMMERCIAL'})
df = df[[col for col in df.columns if col not in ['Signature_URL','Signature PDV_URL']] + ['Signature_URL','Signature PDV_URL']]

colonnes_somme = [
    "Montant_Dotation",
    "Montant_Espece",
    "Montant_Virtuel_Flooz",
    "Montant_Virtuel_Tmoney",
    "Montant_Banque",
    "Montant_Retrait",
    ]

###############################################################################################

def formatter_nombre(nombre):
    if isinstance(nombre, str) or math.isnan(nombre):
        return ''
    else:
        return "{: .0f}".format(nombre)

def formatter_nombre2(nombre):
    if math.isnan(nombre):
        return ''
    else:
        return locale.format_string("%d", nombre, grouping=True)


comm= pd.DataFrame(df.NOM_COMMERCIAL.unique())
commercial = st.sidebar.selectbox("COMMERCIAL", comm)
d = st.sidebar.date_input("ENTRER LA DATE")
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d') # conversion en format 'YYYY-MM-DD'

reseau=st.sidebar.selectbox("CHOIX RESEAU", ["FLOOZ","TMONEY","CORIS MONEY"])

if commercial or reseau or d:

    df_sum = df.loc[(df['NOM_COMMERCIAL'] == commercial) & (df['Rezeau'] == reseau) & (df['Date'] == d.strftime('%Y-%m-%d'))].groupby(["Date", "Rezeau","Numero_PDV"])[colonnes_somme].sum().reset_index()
# Ajout de la colonne "CREANCE"
    df_sum['CREANCE'] = (df_sum['Montant_Banque']+df_sum['Montant_Espece']+df_sum['Montant_Virtuel_Flooz']+df_sum['Montant_Virtuel_Tmoney']+df_sum['Montant_Retrait'])-df_sum['Montant_Dotation']
    df_total = df_sum[colonnes_somme].sum()
    df_total['Date'] = 'TOTAL'
    df_total['Rezeau'] = ''  # Ajoutez une chaîne vide pour la colonne "Rezeau"
    df_total['Numero_PDV'] = ''  # Ajoutez une chaîne vide pour la colonne "Numero_PDV"
    df_total['CREANCE'] = df_total['Montant_Banque'] + df_total['Montant_Espece'] + df_total['Montant_Virtuel_Flooz'] + df_total['Montant_Virtuel_Tmoney'] + df_total['Montant_Retrait'] - df_total['Montant_Dotation']
    df_sum = df_sum.append(df_total, ignore_index=True)

     
    df_mth = df.loc[(df['NOM_COMMERCIAL'] == commercial) & (df['Rezeau'] == reseau)].groupby(["Date", "Rezeau"])[colonnes_somme].sum().reset_index()
# Ajout de la colonne "CREANCE"
   
    df_mth['CREANCE'] = (df_mth['Montant_Banque'] + df_mth['Montant_Espece'] + df_mth['Montant_Virtuel_Flooz'] + df_mth['Montant_Virtuel_Tmoney'] + df_mth['Montant_Retrait']) - df_mth['Montant_Dotation']

    df_daily_sum = df_mth.groupby('Date')['Montant_Dotation'].sum()

    # Création du graphique d'évolution des montants de dotation par jour
    fig, ax = plt.subplots(figsize=(10, 6))  # Ajuster la taille de la figure selon vos besoins
    ax.plot(df_daily_sum.index, df_daily_sum.values)
    ax.set_xlabel('Date')
    ax.set_ylabel('Montant de Dotation')
    ax.set_title("Évolution des Montants de Dotation par Jour")

    # Désactiver la notation scientifique sur l'axe Y
    plt.gca().yaxis.get_major_formatter().set_scientific(False)

    # Afficher les dates de façon oblique
    plt.xticks(rotation=45)

    # Ajuster la taille du graphique de manière esthétique
    fig.tight_layout()
   # Appliquer le formatage à la colonne Montant_Dotation
    df['Montant_Dotation'] = df['Montant_Dotation'].apply(formatter_nombre2)
    df['Montant_Espece'] = df['Montant_Espece'].apply(formatter_nombre2)
    df['Montant_Virtuel_Flooz'] = df['Montant_Virtuel_Flooz'].apply(formatter_nombre2)
    df['Montant_Virtuel_Tmoney'] = df['Montant_Virtuel_Tmoney'].apply(formatter_nombre2)
    df['Montant_Banque'] = df['Montant_Banque'].apply(formatter_nombre2)
    df['Montant_Retrait'] = df['Montant_Retrait'].apply(formatter_nombre2)

    df_sum['Montant_Dotation'] = df_sum['Montant_Dotation'].apply(formatter_nombre2)
    df_sum['Montant_Espece'] = df_sum['Montant_Espece'].apply(formatter_nombre2)
    df_sum['Montant_Virtuel_Flooz'] = df_sum['Montant_Virtuel_Flooz'].apply(formatter_nombre2)
    df_sum['Montant_Virtuel_Tmoney'] = df_sum['Montant_Virtuel_Tmoney'].apply(formatter_nombre2)
    df_sum['Montant_Banque'] = df_sum['Montant_Banque'].apply(formatter_nombre2)
    df_sum['Montant_Retrait'] = df_sum['Montant_Retrait'].apply(formatter_nombre2)
    df_sum['CREANCE'] = df_sum['CREANCE'].apply(formatter_nombre2)

    df_mth['Montant_Dotation'] = df_mth['Montant_Dotation'].apply(formatter_nombre2)
    df_mth['Montant_Espece'] = df_mth['Montant_Espece'].apply(formatter_nombre2)
    df_mth['Montant_Virtuel_Flooz'] = df_mth['Montant_Virtuel_Flooz'].apply(formatter_nombre2)
    df_mth['Montant_Virtuel_Tmoney'] = df_mth['Montant_Virtuel_Tmoney'].apply(formatter_nombre2)
    df_mth['Montant_Banque'] = df_mth['Montant_Banque'].apply(formatter_nombre2)
    df_mth['Montant_Retrait'] = df_mth['Montant_Retrait'].apply(formatter_nombre2)
    df_mth['CREANCE'] = df_mth['CREANCE'].apply(formatter_nombre2)

    df['Numero_PDV'] = df['Numero_PDV'].map(formatter_nombre)
    df['Num_Commercial'] = df['Num_Commercial'].map(formatter_nombre)
    df['Numero_PDV_HR'] = df['Numero_PDV_HR'].map(formatter_nombre)
    df['Numero_Flooz_Virtuel'] = df['Numero_Flooz_Virtuel'].map(formatter_nombre)
    df['Numero_Tmoney_virtuel'] = df['Numero_Tmoney_virtuel'].map(formatter_nombre)

    filtre = df.loc[(df['NOM_COMMERCIAL'] == commercial) & (df['Rezeau'] == reseau) & (df['Date'] == d.strftime('%Y-%m-%d'))]

    # Définition de la fonction pour rendre les liens cliquables et masqués
    def make_clickable(url):
        if pd.isnull(url):
            return ""
        else:
            return f'<a href="{url}" target="_blank">Lien</a>'

    # Appliquer la fonction aux colonnes "Signature PDV_URL" et "Signature_URL" pour rendre les liens cliquables et masqués
    filtre["Signature PDV_URL"] = filtre["Signature PDV_URL"].apply(make_clickable)
    filtre["Signature_URL"] = filtre["Signature_URL"].apply(make_clickable)
  
    filtre.drop(["today","audit","audit_URL"], axis=1, inplace=True)
    # Remplacer les valeurs NaN par une chaîne vide
    filtre.fillna("", inplace=True)
    df_sum.fillna("", inplace=True)

    # Convertir le DataFrame en HTML avec des liens cliquables et masqués
    df_html = filtre.to_html(escape=False, na_rep="")
    df_sum_html = df_sum.to_html(escape=False, na_rep="")
    df_mth_html= df_mth.to_html(escape=False, na_rep="")
   
    st.markdown("<i> </i>", unsafe_allow_html=True)
    if st.checkbox("Dotation et Recouvrement par PDV"):
        
        # Afficher le DataFrame en tant que HTML
        st.write(df_sum_html, unsafe_allow_html=True)
        st.markdown("<i> </i>", unsafe_allow_html=True)
        df_sum = pd.DataFrame(df_sum)  # Votre DataFrame

        col1, col2, col3  = st.columns(3)

        with col1:
            pass

        with col3:
            pass

        with col2:
            st.download_button(
                label="TELECHARGER",
                data=convert_df(df_sum),
                file_name='Rapport_police_col_1.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    else:
        st.markdown("<i>…</i>", unsafe_allow_html=True)

    if st.checkbox("Afficher les detailes des ventes Journalières"):
        
        st.write(df_html, unsafe_allow_html=True)
        st.markdown("<i>  </i>", unsafe_allow_html=True)
       
        filtre = pd.DataFrame(filtre)  # Votre DataFrame

        col1, col2, col3  = st.columns(3)

        with col1:
            pass

        with col3:
            pass

        with col2:
            st.download_button(
                label="TELECHARGER",
                data=convert_df(filtre),
                file_name='Rapport_police_col_1.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    else:
        st.markdown("<i>…</i>", unsafe_allow_html=True)
   
    if st.checkbox("Suivi de l'evolution des dotation sur les 30 dernier jours"):
        
        st.write(df_mth_html, unsafe_allow_html=True)
        st.markdown("<i>  </i>", unsafe_allow_html=True)
        

        # Affichage du graphique dans Streamlit
        st.pyplot(fig)
        st.markdown("<i> </i>", unsafe_allow_html=True)
   
    else:
        st.markdown("<i>…</i>", unsafe_allow_html=True)
   
    

#######################################################################################################
            