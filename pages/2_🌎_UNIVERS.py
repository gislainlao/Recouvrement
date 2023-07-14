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
import folium

st.set_page_config(page_title="UNIVERS PSDTT", page_icon="🧍",layout="wide")


import requests # Pour effectuer la requête
import pandas as pd # Pour manipuler les données

#Title display
html_temp = """
<div style="background-color: #D92F21; padding:10px; border-radius:10px">
<h1 style="color: white; text-align:center">UNIVERS GLOBAL PSDTT</h1>
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

def formatter_nombre(nombre):
    if isinstance(nombre, str) or math.isnan(nombre):
        return ''
    else:
        return "{: .0f}".format(nombre)
def make_clickable(url):
    if pd.isnull(url):
        return ""
    else:
        return f'<a href="{url}" target="_blank">Lien</a>'

data = requests.get("https://kf.kobotoolbox.org/api/v2/assets/aD6Tu4KaCx7LCsjwoXF5MM/export-settings/esC4zD3xnMKFsNxzKjkhFLe/data.xlsx")

df = pd.read_excel(data.content)

cols_to_drop = ['Section 0 : Produits PSDTT vendus par le PDV', 'Section 0 : Identification du PDV', 'Section 4 : Identification du Responsable', 'SUPERVISEUR', '_id', '_uuid', '_submission_time', '_validation_status', '_notes', '_status', '_submitted_by', '__version__', '_tags', '_index',
                'SUPPORT DE VISIBILITE\n(Chevalet,Potence,autocollant)/CHEVALET',
                'SUPPORT DE VISIBILITE\n(Chevalet,Potence,autocollant)/AUTOCOLLANT',
                'SUPPORT DE VISIBILITE\n(Chevalet,Potence,autocollant)/POTENCE',
                'SUPPORT DE VISIBILITE\n(Chevalet,Potence,autocollant)/Autre',
                'Géolocalisation',
                'FLOOZ','TMONEY','CORIS MONEY',
                'DATE DE REDEPLOIEMENT',
                '_Géolocalisation_altitude',
                '_Géolocalisation_precision',
                'Section 3 : Identification du Proprietaire pdv',
                'Section 2 : Identification du pdv',
                'Signature du formulaire par le PDV.1','Prendre une photo du local.1',
                'Prendre une photo du local_URL.1','Signature du formulaire par le PDV_URL.1',
                'Section 1 : Localisation',
                'start', 'end', 'today', 'username', 'Signature du formulaire par le PDV','Prendre une photo du local','Quel sont les produits PSDTT vendus par le PDV?']

df = df.drop(cols_to_drop, axis=1)
def generate_map_link(row):
    map_link = f"https://www.google.com/maps?q={row['_Géolocalisation_latitude']},{row['_Géolocalisation_longitude']}"
    return map_link

    # Appliquer la fonction pour créer la nouvelle colonne "Lien_Map"
df['Lien_Map'] = df.apply(generate_map_link, axis=1)
def fusioner_numeros(row, numero_colonne, autre_colonne):
    if isinstance(row[numero_colonne], str) and 'Autre' in row[numero_colonne]:
        return row[autre_colonne]
    else:
        return row[numero_colonne]

# Fusion des colonnes Numero FLOOZ
df['SUPPORT DE VISIBILITE'] = df.apply(fusioner_numeros, axis=1, args=('SUPPORT DE VISIBILITE\n(Chevalet,Potence,autocollant)', 'Précisez'))
df = df.drop(['SUPPORT DE VISIBILITE\n(Chevalet,Potence,autocollant)', 'Précisez'], axis=1)

# Fusion des colonnes Numero FLOOZ
df['Numero_FLOOZ'] = df.apply(fusioner_numeros, axis=1, args=('Numero FLOOZ', 'Autre (Numero Flooz)'))
df = df.drop(['Numero FLOOZ', 'Autre (Numero Flooz)'], axis=1)

# Fusion des colonnes Numero TMONEY
df['Numero_TMONEY'] = df.apply(fusioner_numeros, axis=1, args=('Numero TMONEY', 'Autre (Numero Tmoney)'))
df = df.drop(['Numero TMONEY', 'Autre (Numero Tmoney)'], axis=1)

# Fusion des colonnes CodeUO (Coris Money)
df['CodeUO'] = df.apply(fusioner_numeros, axis=1, args=('CodeUO (Coris Money)', 'Autre (code UO)'))
df = df.drop(['CodeUO (Coris Money)', 'Autre (code UO)'], axis=1)
df = df.fillna('')
df['Numero_FLOOZ'] = df['Numero_FLOOZ'].map(formatter_nombre)
df['Numero_TMONEY'] = df['Numero_TMONEY'].map(formatter_nombre)
df['CodeUO'] = df['CodeUO'].map(formatter_nombre)

df["Prendre une photo du local_URL"] = df["Prendre une photo du local_URL"].apply(make_clickable)
df["Signature du formulaire par le PDV_URL"] = df["Signature du formulaire par le PDV_URL"].apply(make_clickable)
df["Lien_Map"] = df["Lien_Map"].apply(make_clickable)

nouvel_ordre = ['Nom COMMERCIAL', 'NOM DU POINT', 'Numero_FLOOZ', 'PROFIL Flooz', 'Numero_TMONEY', 'PROFIL Tmoney', 'CodeUO', 'PROFIL Coris',
                "TYPE D'ACTIVITE", 'DISPOSITIF', 'COULEUR','REGION', 'PREFECTURE', 'COMMUNE', 'CANTON','VILLE','QUARTIER','_Géolocalisation_latitude','_Géolocalisation_longitude',
                'Lien_Map','SUPPORT DE VISIBILITE','ETAT DU SUPPORT DE VISIBILITE\n( BON/MAUVAIS)']


# Liste des colonnes existantes
colonnes_existantes = df.columns.tolist()

# Colonnes réorganisées en conservant l'ordre d'origine pour les autres colonnes
colonnes_reorganisees = nouvel_ordre + [colonne for colonne in colonnes_existantes if colonne not in nouvel_ordre]

# Réindexation du DataFrame avec les colonnes réorganisées
df = df.reindex(columns=colonnes_reorganisees)
comm = pd.DataFrame(df['Nom COMMERCIAL'].unique(), columns=['Nom COMMERCIAL'])

options = ['FLOOZ', 'TMONEY', 'CORIS MONEY']

if st.sidebar.checkbox("UNIVERS PAR COMMERCIAL"):
    commercial = st.sidebar.selectbox("COMMERCIAL", comm)
    if commercial:

        df_com = df.loc[(df['Nom COMMERCIAL'] == commercial)].reset_index()
        df_com_html = df_com.to_html(escape=False, na_rep="")
        st.write (df_com_html,unsafe_allow_html=True)

        st.markdown("<i> </i>", unsafe_allow_html=True)
        df_com = pd.DataFrame(df_com)  # Votre DataFrame

        col1, col2, col3  = st.columns(3)

        with col1:
            pass

        with col3:
            pass

        with col2:
            st.sidebar.download_button(
                label="TELECHARGER",
                data=convert_df(df_com),
                file_name=commercial + '.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    else:
        st.markdown("<i>…</i>", unsafe_allow_html=True)

if  st.sidebar.checkbox("UNIVERS GLOBAL"):

    selection = st.sidebar.multiselect('Sélectionnez les options de filtrage', options)

    df_filtre = df

    if 'FLOOZ' in selection and 'TMONEY' in selection and 'CORIS MONEY' in selection:
        df_filtre = df_filtre[(df_filtre['Numero_FLOOZ'] != '') & (df_filtre['Numero_TMONEY'] != '') & (df_filtre['CodeUO'] != '')]
    elif 'FLOOZ' in selection and 'TMONEY' in selection:
        df_filtre = df_filtre[(df_filtre['Numero_FLOOZ'] != '') & (df_filtre['Numero_TMONEY'] != '')]
        df_filtre = df_filtre.drop(['CodeUO', 'PROFIL Coris'], axis=1)

    elif 'FLOOZ' in selection and 'CORIS MONEY' in selection:
        df_filtre = df_filtre[(df_filtre['Numero_FLOOZ'] != '') & (df_filtre['CodeUO'] != '')]
        df_filtre = df_filtre.drop(['Numero_TMONEY', 'PROFIL Tmoney'], axis=1)

    elif 'TMONEY' in selection and 'CORIS MONEY' in selection:
        df_filtre = df_filtre[(df_filtre['Numero_TMONEY'] != '') & (df_filtre['CodeUO'] != '')]
        df_filtre = df_filtre.drop(['Numero_FLOOZ', 'PROFIL Flooz'], axis=1)

    elif 'FLOOZ' in selection:
        df_filtre = df_filtre[df_filtre['Numero_FLOOZ'] != '']
        df_filtre = df_filtre.drop(['Numero_TMONEY', 'PROFIL Tmoney', 'CodeUO', 'PROFIL Coris'], axis=1)
    elif 'TMONEY' in selection:
        df_filtre = df_filtre[df_filtre['Numero_TMONEY'] != '']
        df_filtre = df_filtre.drop(['Numero_FLOOZ', 'PROFIL Flooz', 'CodeUO', 'PROFIL Coris'], axis=1)
    elif 'CORIS MONEY' in selection:
        df_filtre = df_filtre[df_filtre['CodeUO'] != '']
        df_filtre = df_filtre.drop(['Numero_FLOOZ', 'PROFIL Flooz', 'Numero_TMONEY', 'PROFIL Tmoney'], axis=1)  

    # Afficher le DataFrame avec la nouvelle colonne
    df_html = df.to_html(escape=False, na_rep="")
    st.write(df_html, unsafe_allow_html=True)
   
    st.markdown("<i> </i>", unsafe_allow_html=True)
    df_filtre = pd.DataFrame(df_filtre)  # Votre DataFrame

    col1, col2, col3  = st.columns(3)

    with col1:
        pass

    with col3:
        pass

    with col2:
        st.download_button(
            label="TELECHARGER",
            data=convert_df(df_filtre),
            file_name='UNIVERS.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
else:
     st.markdown("<i>…</i>", unsafe_allow_html=True)

if  st.sidebar.checkbox("CARTE DE NOS PDV"):
    commerciaux = st.sidebar.multiselect('Sélectionnez les options de filtrage', comm)
    
    if commerciaux:

        df = df[df['Nom COMMERCIAL'].isin(commerciaux)].reset_index()
    # Parcourir le DataFrame et ajouter des marqueurs pour chaque point de vente
        from geopy.distance import geodesic
        df = df.dropna(subset=['_Géolocalisation_longitude'])

        # Conversion des valeurs en nombres (floats) et filtrage des valeurs NaN
        df['_Géolocalisation_latitude'] = pd.to_numeric(df['_Géolocalisation_latitude'], errors='coerce')
        df['_Géolocalisation_longitude'] = pd.to_numeric(df['_Géolocalisation_longitude'], errors='coerce')

        # Supprimer les lignes où la conversion a échoué ou contient des valeurs NaN
        df = df.dropna(subset=['_Géolocalisation_latitude', '_Géolocalisation_longitude'])

        # Coordonnées géographiques du Togo
        latitude = 8.6195
        longitude = 0.8248

        # Création de la carte centrée sur le Togo
        m = folium.Map(location=[latitude, longitude], zoom_start=7)

        # Distance équidistante en mètres
        equidistant_distance = 300

        # Convertir les données du DataFrame en une liste de dictionnaires
        data = df.to_dict(orient='records')

        # Variables pour le comptage des points rouges et bleus
        red_count = 0
        blue_count = 0

        # Parcourir tous les points
        for point1 in data:
            marker_color = 'blue'  # Couleur par défaut du marqueur
            for point2 in data:
                if point1 != point2:  # Exclure le point lui-même
                    distance = geodesic((point1['_Géolocalisation_latitude'], point1['_Géolocalisation_longitude']),
                                        (point2['_Géolocalisation_latitude'], point2['_Géolocalisation_longitude'])).meters
                    if distance < equidistant_distance:
                        marker_color = 'red'
                        break  # Sortir de la boucle si une distance est inférieure à 300 mètres
            
            # Ajouter le marqueur avec la couleur appropriée
            folium.Marker(
                location=[point1['_Géolocalisation_latitude'], point1['_Géolocalisation_longitude']],
                popup=point1['NOM DU POINT'],
                icon=folium.Icon(color=marker_color)
            ).add_to(m)
            
            # Incrémenter le compteur de points rouges ou bleus
            if marker_color == 'red':
                red_count += 1
            else:
                blue_count += 1

        # Ajuster la vue de la carte pour inclure tous les marqueurs
        m.fit_bounds([[point['_Géolocalisation_latitude'], point['_Géolocalisation_longitude']] for point in data])

        # Conversion de la carte en HTML
        html_map = m._repr_html_()

        # Affichage de la carte dans Streamlit
        components.html(html_map, width=800, height=1000, scrolling=False)

        # Afficher le nombre de points rouges et bleus
        st.sidebar.write("Nombre de points rouges :", red_count)
        st.sidebar.write("Nombre de points bleus :", blue_count)

if  st.sidebar.checkbox("CARTE DE PSDTT"):

    # Parcourir le DataFrame et ajouter des marqueurs pour chaque point de vente
    from geopy.distance import geodesic
    df = df.dropna(subset=['_Géolocalisation_longitude'])

    # Conversion des valeurs en nombres (floats) et filtrage des valeurs NaN
    df['_Géolocalisation_latitude'] = pd.to_numeric(df['_Géolocalisation_latitude'], errors='coerce')
    df['_Géolocalisation_longitude'] = pd.to_numeric(df['_Géolocalisation_longitude'], errors='coerce')

    # Supprimer les lignes où la conversion a échoué ou contient des valeurs NaN
    df = df.dropna(subset=['_Géolocalisation_latitude', '_Géolocalisation_longitude'])

    # Coordonnées géographiques du Togo
    latitude = 8.6195
    longitude = 0.8248

    # Création de la carte centrée sur le Togo
    m = folium.Map(location=[latitude, longitude], zoom_start=7)

    # Ajout des marqueurs sur la carte
    for index, row in df.iterrows():
        folium.Marker([row['_Géolocalisation_latitude'], row['_Géolocalisation_longitude']], popup=row['NOM DU POINT']).add_to(m)

    # Ajuster la vue de la carte pour inclure tous les marqueurs
    m.fit_bounds([[df['_Géolocalisation_latitude'].min(), df['_Géolocalisation_longitude'].min()],
                [df['_Géolocalisation_latitude'].max(), df['_Géolocalisation_longitude'].max()]])

    # Conversion de la carte en HTML
    html_map = m._repr_html_()

    # Affichage de la carte dans Streamlit
    components.html(html_map, width=800, height=800, scrolling=False)