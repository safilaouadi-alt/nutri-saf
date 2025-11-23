import streamlit as st
import pandas as pd
import os
import json
import time
from datetime import datetime

# --- CONFIGURATION ---
APP_NAME = "Nutri Saf" 

st.set_page_config(
 page_title=APP_NAME,
 page_icon=" ",
 layout="wide"
)

# --- BASE DE DONNÉES ALIMENTAIRE (Pour 100g) ---
FOOD_DB = {
 "Riz Basmati (cuit)": {"kcal": 120, "prot": 3.5, "carbs": 25, "fat": 0.4},
 "Blanc de Poulet (cuit)": {"kcal": 165, "prot": 31, "carbs": 0, "fat": 3.6},
 "Oeuf (entier)": {"kcal": 140, "prot": 12, "carbs": 1, "fat": 10},
 "Pâtes (cuites)": {"kcal": 131, "prot": 5, "carbs": 25, "fat": 1},
 "Avoine": {"kcal": 389, "prot": 16.9, "carbs": 66, "fat": 6.9},
 "Brocoli": {"kcal": 34, "prot": 2.8, "carbs": 7, "fat": 0.4},
 "Huile d'Olive": {"kcal": 884, "prot": 0, "carbs": 0, "fat": 100},
 "Whey Protein (poudre)": {"kcal": 370, "prot": 75, "carbs": 5, "fat": 4},
 "Banane": {"kcal": 89, "prot": 1.1, "carbs": 22.8, "fat": 0.3},
 "Amandes": {"kcal": 579, "prot": 21, "carbs": 22, "fat": 50},
 "Autre (Entrée manuelle)": {"kcal": 0, "prot": 0, "carbs": 0, "fat": 0} 
}

# --- GESTION DES UTILISATEURS ---
USERS = {
 "saf": "admin",
 "coach": "fit2024",
 "invite": "1234",
 "julie": "password"
}

def check_login(username, password):
 """Vérifie si le nom et le mot de passe correspondent"""
 if username in USERS and USERS[username] == password:
     return True
 return False

def get_user_data_file(username):
 clean_name = "".join(x for x in username if x.isalnum())
 return f"data_{clean_name}.json"

# --- FONCTIONS DE DONNÉES ---
def load_data(username):
 filename = get_user_data_file(username)
 if not os.path.exists(filename):
     return {"workouts": [], "nutrition": []}
 try:
 with open(filename, "r") as f:
 return json.load(f)
 except (json.JSONDecodeError, ValueError):
     return {"workouts": [], "nutrition": []}

def save_data(data, username):
 filename = get_user_data_file(username)
 with open(filename, "w") as f:
 json.dump(data, f, indent=4)

# --- INTERFACE DE LOGIN ---
if 'logged_in' not in st.session_state:
 st.session_state['logged_in'] = False
if 'username' not in st.session_state:
 st.session_state['username'] = ''

def login_page():
 st.markdown(f"<h1 style='text-align: center;'>Bienvenue sur {APP_NAME} </h1>", unsafe_allow_html=True)
 
 col1, col2, col3 = st.columns([1, 1, 1])
 with col2:
 with st.form("login_form"):
 username_input = st.text_input("Nom d'utilisateur")
 password_input = st.text_input("Mot de passe", type="password")
 submit_login = st.form_submit_button("Se connecter", use_container_width=True)
 
 if submit_login:
 if check_login(username_input, password_input):
 st.session_state['logged_in'] = True
 st.session_state['username'] = username_input
 st.success("Connexion réussie !")
 st.rerun()
 else:
 st.error("Identifiants incorrects.")
 
 with st.expander(" Infos de connexion"):
 st.write("Test : saf / admin")

# --- APPLICATION PRINCIPALE ---
def main_app():
 with st.sidebar:
 st.title(f" {st.session_state['username'].capitalize()}")
 if st.button("Se déconnecter", type="primary"):
 st.session_state['logged_in'] = False
 st.session_state['username'] = ''
 st.rerun() 
 st.markdown("---")
 menu = st.radio("Menu", [" Entraînement", " Nutrition", " Progrès"])

 data = load_data(st.session_state['username'])

 # PAGE ENTRAÎNEMENT
 if menu == " Entraînement":
 st.header("Séance du jour")
 with st.expander(" Ajouter un exercice", expanded=True):
 with st.form("workout_form"):
 col1, col2 = st.columns(2)
 with col1:
 date = st.date_input("Date", datetime.now())
 exercise = st.text_input("Nom de l'exercice")
 with col2:
 series = st.number_input("Séries", 1, 10, 4)
 reps = st.number_input("Reps", 1, 100, 10)
 weight = st.number_input("Poids (kg)", 0.0, 500.0, 0.0, 0.5)
 
 if st.form_submit_button("Valider"):
 if exercise:
 new_entry = {
 "date": date.strftime("%Y-%m-%d"),
 "exercise": exercise,
 "series": series,
 "reps": reps,
 "weight": weight
 }
 data["workouts"].append(new_entry)
 save_data(data, st.session_state['username'])
 st.success("Enregistré !")

 st.divider()
 st.subheader(" Minuteur")
 c1, c2, c3 = st.columns([1,1,2])
 with c1:
 mins = st.number_input("Minutes", 0, 59, 1)
 with c2:
 secs = st.number_input("Secondes", 0, 59, 30)
 with c3:
 st.write("##")
 if st.button("Lancer"):
 tot = mins * 60 + secs
 bar = st.progress(0)
 for i in range(tot):
 time.sleep(1)
 bar.progress((i+1)/tot, text=f"Reste : {tot-i-1}s")
 st.success("Go !")

 # PAGE NUTRITION
 elif menu == " Nutrition":
 st.header("Calculateur Macros")
 with st.expander(" Ajouter un repas", expanded=True):
 c_food, c_qty = st.columns([2, 1])
 with c_food:
 choix = st.selectbox("Aliment", list(FOOD_DB.keys()))
 with c_qty:
 qty = st.number_input("Grammes", 0, 1000, 100, 10)

 info = FOOD_DB[choix]
 if choix != "Autre (Entrée manuelle)":
 ratio = qty/100
 kcal = round(info["kcal"]*ratio)
 prot = round(info["prot"]*ratio, 1)
 st.info(f"{qty}g = {kcal} kcal | {prot}g prot")
 else:
 kcal = st.number_input("Kcal", 0)
 prot = st.number_input("Prot", 0.0)
 # On simplifie pour l'affichage manuel
 carbs = 0
 fat = 0

 if st.button("Manger"):
 # Si manuel, on met 0 pour carbs/fat par défaut pour éviter les erreurs
 if choix == "Autre (Entrée manuelle)":
 c_val, f_val = 0, 0
 else:
 c_val = round(info["carbs"]*ratio, 1)
 f_val = round(info["fat"]*ratio, 1)
 
 entry = {
 "date": datetime.now().strftime("%Y-%m-%d"),
 "food": choix,
 "quantity": qty,
 "calories": kcal,
 "protein": prot,
 "carbs": c_val,
 "fats": f_val
 }
 data["nutrition"].append(entry)
 save_data(data, st.session_state['username'])
 st.success("Ajouté !")

 st.divider()
 st.subheader("Aujourd'hui")
 df = pd.DataFrame(data["nutrition"])
 if not df.empty:
 today = datetime.now().strftime("%Y-%m-%d")
 df_uj = df[df["date"] == today]
 if not df_uj.empty:
 k1, k2, k3 = st.columns(3)
 k1.metric("Kcal", int(df_uj["calories"].sum()))
 k2.metric("Prot", round(df_uj["protein"].sum(), 1))
 st.dataframe(df_uj, use_container_width=True)

 # PAGE PROGRÈS
 elif menu == " Progrès":
 st.header("Graphiques")
 df = pd.DataFrame(data["workouts"])
 if not df.empty:
 exos = df["exercise"].unique()
 choix = st.selectbox("Exercice", exos)
 df_g = df[df["exercise"] == choix].sort_values("date")
 st.line_chart(df_g, x="date", y="weight")
 st.success(f"Max : {df_g['weight'].max()} kg")
 else:
 st.info("Pas encore de données.")

if st.session_state['logged_in']:
 main_app()
else:
 login_page()




