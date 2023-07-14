import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
plt.style.use('fivethirtyeight')
import streamlit_authenticator as stauth
import database as db
st.set_page_config(page_title="Acceuil",page_icon="📈",layout="wide")
        
html_temp = """
<div style="background-color: #D92F21; padding:10px; border-radius:10px">
<h1 style="color: white; text-align:center">BIENVENU SUR LA PLATEFORME DE PRÉVISION DES RACHATS</h1>
</div>
<p style="font-size: 20px; font-weight: bold; text-align:center">Cette application web a pour but d'aider les commerciaux pour un meilleur suivi de leurs recouvrement...</p>
"""

st.markdown(html_temp, unsafe_allow_html=True)

st.markdown("***")


Linkedin="Merci d'avoir parcouru cette application Web !! si vous voulez me contacter, vous pouvez me trouver sur [Linkedin](https://www.linkedin.com/in/essohanam-laokpezi/)* ❤️"
st.markdown(Linkedin,unsafe_allow_html=True)

