import streamlit as st
import pandas as pd
import os
import json
import time
from datetime import datetime

# --- CONFIGURATION ---
# NOM OFFICIEL DE L'APPLICATION
APP_NAME = "Nutri Saf" 

st.set_page_config(
 page_title=APP_NAME,
 page_icon=" ",
 layout="wide"
)

# --- 3. BASE DE DONNÉES ALIMENTAIRE INTELLIGENTE (Pour 100g) ---
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
# C'est ici que tu crées les comptes pour tes amis !
# Format : "NomUtilisateur": "MotDePasse"
USERS = {
 "saf": "admin", # Ton compte perso
 "coach": "fit2024", # Un autre compte
 "invite": "1234", # Compte pour un ami
 "julie": "password" # Compte pour une amie
}

def check_login(username, password):
 """Vérifie si le nom et le mot de passe correspondent"""
 if username in USERS and USERS[username] == password:
 return True
 return False

def get_user_data_file(username):
 """Génère un nom de fichier unique pour chaque utilisateur (ex: data_saf.json)"""
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
 st.markdown("<p style='text-align: center;'>Connecte-toi pour suivre tes perfs et tes macros.</p>", unsafe_allow_html=True)
 
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
 
 with st.expander(" Infos de connexion (pour tester)"):
 st.write("Essaie avec : **saf** / **admin**")

# --- APPLICATION PRINCIPALE ---
def main_app():
 # Barre latérale
 with st.sidebar:
 st.title(f" Profil : {st.session_state['username'].capitalize()}")
 st.metric("Application", APP_NAME)
 
 if st.button("Se déconnecter", type="primary"):
 st.session_state['logged_in'] = False
 st.session_state['username'] = ''
 st.rerun()
 
 st.markdown("---")
 menu = st.radio("Menu", [" Entraînement", " Nutrition (Smart)", " Mes Progrès"])

 # Chargement des données spécifiques à l'utilisateur connecté
 data = load_data(st.session_state['username'])

 # -----------------------
 # PAGE ENTRAÎNEMENT
 # -----------------------
 if menu == " Entraînement":
 st.header(f"Séance de {st.session_state['username'].capitalize()}")
 
 with st.expander(" Ajouter un exercice", expanded=True):
 with st.form("workout_form"):
 col1, col2 = st.columns(2)
 with col1:
 date = st.date_input("Date", datetime.now())
 exercise = st.text_input("Exercice (ex: Développé Couché)")
 with col2:
 series = st.number_input("Séries", min_value=1, value=4)
 reps = st.number_input("Répétitions", min_value=1, value=10)
 weight = st.number_input("Poids (kg)", min_value=0.0, value=0.0, step=0.5)
 
 submitted = st.form_submit_button("Enregistrer la perf", use_container_width=True)
 if submitted:
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
 st.success(f" {exercise} ajouté !")
 else:
 st.warning("N'oublie pas de nommer l'exercice.")

 st.divider()
 
 # MINUTEUR INTELLIGENT
 st.subheader(" Minuteur de Repos")
 col_min, col_sec, col_btn = st.columns([1, 1, 2])
 
 with col_min:
 minutes = st.number_input("Minutes", min_value=0, max_value=59, value=1)
 with col_sec:
 seconds = st.number_input("Secondes", min_value=0, max_value=59, value=30)
 
 total_seconds = (minutes * 60) + seconds
 
 with col_btn:
 st.write("###") # Espace visuel
 if st.button("Lancer le chrono", use_container_width=True):
 progress_text = f"Repos : {minutes}m {seconds}s"
 my_bar = st.progress(0, text=progress_text)
 
 step = 100 / total_seconds if total_seconds > 0 else 100
 
 for i in range(total_seconds):
 time.sleep(1)
 current_progress = int((i + 1) * step)
 if current_progress > 100: current_progress = 100
 remaining = total_seconds - (i + 1)
 mins_rem = remaining // 60
 secs_rem = remaining % 60
 my_bar.progress(current_progress, text=f"Reste : {mins_rem}m {secs_rem}s")
 
 st.balloons()
 st.success("C'est reparti ! ")

 # -----------------------
 # PAGE NUTRITION
 # -----------------------
 elif menu == " Nutrition (Smart)":
 st.header("Calculateur de Calories & Macros")
 
 with st.expander(" Ajouter un repas", expanded=True):
 col_food, col_qty = st.columns([2, 1])
 
 with col_food:
 food_choice = st.selectbox("Choisir un aliment", list(FOOD_DB.keys()))
 
 with col_qty:
 quantity = st.number_input("Quantité (grammes)", min_value=0, value=100, step=10)

 # Calculs automatiques
 infos_100g = FOOD_DB[food_choice]
 
 if food_choice != "Autre (Entrée manuelle)":
 ratio = quantity / 100
 calc_kcal = round(infos_100g["kcal"] * ratio)
 calc_prot = round(infos_100g["prot"] * ratio, 1)
 calc_carbs = round(infos_100g["carbs"] * ratio, 1)
 calc_fat = round(infos_100g["fat"] * ratio, 1)
 
 st.info(f" **{quantity}g de {food_choice}** apportent :")
 c1, c2, c3, c4 = st.columns(4)
 c1.metric("Kcal", calc_kcal)
 c2.metric("Prot", f"{calc_prot}g")
 c3.metric("Glucides", f"{calc_carbs}g")
 c4.metric("Lipides", f"{calc_fat}g")
 
 else:
 col1, col2, col3, col4 = st.columns(4)
 calc_kcal = col1.number_input("Kcal", value=0)
 calc_prot = col2.number_input("Prot (g)", value=0.0)
 calc_carbs = col3.number_input("Glucides (g)", value=0.0)
 calc_fat = col4.number_input("Lipides (g)", value=0.0)

 if st.button("Manger ce repas", use_container_width=True):
 if quantity > 0:
 nutri_entry = {
 "date": datetime.now().strftime("%Y-%m-%d"),
 "food": food_choice,
 "quantity": quantity,
 "calories": calc_kcal,
 "protein": calc_prot,
 "carbs": calc_carbs,
 "fats": calc_fat
 }
 data["nutrition"].append(nutri_entry)
 save_data(data, st.session_state['username'])
 st.success("Repas ajouté ! ")
 else:
 st.error("La quantité doit être supérieure à 0.")

 st.divider()
 st.subheader("Bilan Journalier")
 
 today = datetime.now().strftime("%Y-%m-%d")
 df_nutri = pd.DataFrame(data["nutrition"])
 
 if not df_nutri.empty:
 today_data = df_nutri[df_nutri["date"] == today]
 
 if not today_data.empty:
 total_cal = int(today_data["calories"].sum())
 total_prot = round(today_data["protein"].sum(), 1)
 total_carbs = round(today_data["carbs"].sum(), 1)
 total_fat = round(today_data["fats"].sum(), 1)
 
 # Affichage visuel avec des barres de progression simulées
 k1, k2, k3, k4 = st.columns(4)
 k1.metric(" Total Calories", total_cal)
 k2.metric(" Protéines", f"{total_prot}g")
 k3.metric(" Glucides", f"{total_carbs}g")
 k4.metric(" Lipides", f"{total_fat}g")
 
 st.dataframe(today_data[["food", "quantity", "calories", "protein", "carbs", "fats"]], use_container_width=True)
 else:
 st.info("Rien mangé aujourd'hui ? Ajoute un repas ci-dessus !")
 else:
 st.info("Ton historique nutritionnel est vide.")

 # -----------------------
 # PAGE PROGRÈS
 # -----------------------
 elif menu == " Mes Progrès":
 st.header("Suivi des performances")
 df = pd.DataFrame(data["workouts"])
 
 if not df.empty:
 unique_exercises = df["exercise"].unique()
 exo_choice = st.selectbox("Voir la progression sur :", unique_exercises)
 
 df_exo = df[df["exercise"] == exo_choice].copy()
 df_exo["date"] = pd.to_datetime(df_exo["date"])
 df_exo = df_exo.sort_values("date")
 
 st.line_chart(df_exo, x="date", y="weight")
 
 max_weight = df_exo['weight'].max()
 st.success(f" Ton record personnel sur **{exo_choice}** est de **{max_weight} kg** !")
 else:
 st.info("Enregistre ta première séance pour voir les graphiques apparaître ici.")

# --- LOGIQUE DE LANCEMENT ---
if st.session_state['logged_in']:
 main_app()
else:
 login_page()
