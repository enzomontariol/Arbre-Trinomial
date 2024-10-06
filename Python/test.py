import streamlit as st

from datetime import datetime

st.markdown("""
    <style>
    /* Changer la couleur de fond de la page */
    .stApp {
        background-color: #215C98;
    }

    /* Changer la couleur des titres */
    .stApp h1, h2, h3 {
        color: #FFFFFF; 
    }

    /* Changer la couleur des textes */
    .stApp p {
        color: #FFFFFF; /* Gris foncé */
    }

    /* Personnalisation des boutons */
    button {
        background-color: #DAE9F8; /* Vert */
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
    }

    button:hover {
        background-color: #DAE9F8;
    }

    </style>
    """, unsafe_allow_html=True)

# Titre de l'application
st.title("Trinomial Tree")

# Instructions à l'utilisateur
st.write("Entrez les caractéristiques du marché, de l'option et du modèle: ")

# Utilisation des colonnes pour contrôler l'espacement et la "largeur"
col1, col2, col3 = st.columns([1, 1, 1])  # Ajuste les valeurs pour contrôler la largeur relative

# Champs de saisie pour les deux nombres dans des colonnes
"""with col1:
    StockPrice = st.text_input("Stock Price S :", value=0.0)
    Volatility = st.text_input("Volatility (%) : ex: pour 3 mettre 3", value=0.0)
    InterestRate = st.number_input("Interest Rate (%) :", value=0.0)
    Dividend = st.number_input("Dividend :", value=0.0)
    ExDateDividend = st.number_input("Ex-Date Dividend :", value=0.0)

with col2:
    Maturity = st.number_input("Maturity :", value= 0)
    Type = st.number_input("Type : Call or Put", value=0.0)
    Exercise = st.number_input("Exercise : European or American", value=0.0)
    Strike = st.number_input("Strike :", value=0.0)

with col3:
    Princing_Date = st.number_input("Princing Date :", value= 0)
    Nb_Steps = st.number_input("Nb Steps", value=0.0)
    Alpha = st.number_input("Alpha Parameter", value=0.0)
    Strike = st.number_input("Year Base :", value=0.0)"""

dico_variable_market = {"StockPrice":["Stock Price S :","Entrez un nombre"],
                 "Volatility":["Volatility (%) : ","ex: entrez 3 une volatilité de 3%"],
                 "InterestRate":["Interest Rate (%)","ex: entrez 2 un taux d'intérêt de 2%"],
                 "Dividend":["Dividend :","Entrez un nombre"],
                 "ExDateDividend":["Ex-Date Dividend :","Entrez une date"],
                 }

dico_variable_option = {"Maturity":["Maturity :","Entrez une date"],
                 "Type":["Type : ","Entrez Call ou Put"],
                 "Exercise":["Exercise : ","Entrez European ou American"],
                 "Strike":["Strike :","Entrez un nombre"],
                 }

dico_variable_modele = {"Princing_Date":["Princing Date :","Entrez une date"], # mettre aujd par défaut
                 "Nb_Steps":["Nb Steps :","Entrez un nombre"],
                 "Alpha":["Alpha Parameter :","Entrez un nombre"],
                 "Year_Base":["Year Base :","Entrez un nombre"], # mettre 365 par défaut
                 }

dico_variable_market_input = {}
dico_variable_option_input = {}
dico_variable_modele_input = {}

colonne_input = {col1:[dico_variable_market,dico_variable_market_input],
                 col2:[dico_variable_option,dico_variable_option_input],
                 col3:[dico_variable_modele,dico_variable_modele_input]}
# colonne : [data[0],data[1]]

for colonne, data in colonne_input.items():
    with colonne:
        for k, v in data[0].items():

            locals()[f'{k}'] = st.text_input(f'{v[0]}', value="",placeholder=v[1])
            data[1][k] = locals()[f'{k}']
            
            conversion_failed = False
            var_float = False
            var_pourcentage = False
            var_date = False
            var_str = False

            if data[1][k]:
                #float
                try:
                    # Tenter de convertir l'entrée en float
                    locals()[f'{k}'] = float(data[1][k])
                    data[1][k] = locals()[f'{k}']
                    var_float = True
                    #st.markdown('<p style="color:green;">Veuillez entrer des nombres valides.</p>', unsafe_allow_html=True)
                except ValueError:
                    conversion_failed = True
            
            # si la conversion en float failed, on essaie de convertir en date
            if conversion_failed:
                # date
                try:
                    locals()[f'{k}'] = datetime.strptime(data[1][k],  "%d/%m/%Y")
                    data[1][k] = locals()[f'{k}']
                    var_date = True
                    conversion_failed = False
                except ValueError:
                    pass
            
            # si la conversion en date failed, on essaie de convertir le pourcentage en float
            if conversion_failed:
                # pourcentage
                try:
                    locals()[f'{k}'] = float(data[1][k].replace('%', '').strip())
                    data[1][k] = locals()[f'{k}']
                    var_pourcentage = True
                    conversion_failed = False
                except ValueError:
                    pass

            # si c'est ni un float, ni une valeur en pourcentage, ni une date
            if conversion_failed:
                # str
                if k in ['Exercise'] and data[1][k] in ['European','American']:
                    var_str = True
                    conversion_failed = False
                elif k in ['Type'] and data[1][k] in ['Call','Put']:
                    var_str = True
                    conversion_failed = False
                else:
                    # Si erreur, cela signifie que l'entrée n'est pas un nombre valide
                    data[1][k] = ''
                    st.markdown('<p style="color:red;">Veuillez entrer des nombres valides.</p>', unsafe_allow_html=True)

        print(data[1])

print(StockPrice)
print(Volatility)
###############################################################


exit()
with col2:
    # Affiche le contenu des variables
    for k, v in dico_variable_option.items():
        dico_variable_option[f'{k}'] = st.text_input(f'{v[0]}', value="",placeholder=v[1])
        #locals()[f'{var_name}'] = float(dico_variable_option[f'{var_name}'])

with col3:
    # Affiche le contenu des variables
    for k, v in dico_variable_modele.items():
        dico_variable_modele[f'{k}'] = st.text_input(f'{v[0]}', value="",placeholder=v[1])
        #locals()[f'{var_name}'] = float(dico_variable_modele[f'{var_name}'])



# Vérification que les entrées sont des nombres avant de faire le calcul
if st.button("Calculer la somme"):
    try:
        # Conversion des chaînes de caractères en nombres
        for var_name, value in dico_variable_market.items():
            dico_variable_market[f'{var_name}'] = float(st.text_input(f'{value}', value="ssffa"))
            print(var_name)
        
        # Calcul de la somme
        resultat = StockPrice + Volatility
        
        # Afficher le résultat
        st.write(f"Résultat : {resultat}")
    
    except ValueError:
        st.write("Veuillez entrer des nombres valides.")


# Bouton pour lancer le calcul
def compte(a,b):
    return a+b
# Bouton pour lancer le calcu
exit()
import streamlit as st

st.markdown("""
    <style>
    div[data-baseweb="input"] > div {
        width: 50px !important;  /* Réduit la largeur du conteneur */
    }
    input[type="number"] {
        font-size: 14px !important;
        height: 30px !important;  /* Ajuster la hauteur si besoin */
    }
    </style>
    """, unsafe_allow_html=True)



# Champs de saisie pour les deux nombres





