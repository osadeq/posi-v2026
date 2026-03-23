import sys
import json
import random
from pathlib import Path
from datetime import datetime

base_dir = Path(r"c:\Users\sadeq\Desktop\posi-v2026.3.1")
sys.path.insert(0, str(base_dir))

from config import CANDIDATS_DIR, CANDIDATS_FILE, QUESTIONS_FILE
from data.analyse_besoins import generer_programme

with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    bd = json.load(f)

def get_questions_for(qid):
    q_def = next((x for x in bd.get('questionnaires', []) if x['id_questionnaire'] == qid), None)
    if q_def: return q_def['questions']
    return bd.get('questions', [])[:15]

def create_cand(nom, prenom, level, qid, maitrise_gen):
    id_candidat = f"CAND_{nom}_{prenom.split(' ')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}".replace('é', 'e').upper()
    dir_path = CANDIDATS_DIR / id_candidat
    dir_path.mkdir(parents=True, exist_ok=True)
    
    cand_info = {
        "id_candidat": id_candidat,
        "nom": nom,
        "prenom": prenom,
        "self_level": level,
        "id_questionnaire": qid,
        "date_reponse": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "programme_genere": True
    }
    
    q_list = get_questions_for(qid)
    answers = []
    for q in q_list:
        m = maitrise_gen()
        s = "Oui" if m in ["Aucune", "Moyenne"] else "Non"
        answers.append({
            "id_question": q['id_question'],
            "niveau_maitrise": m,
            "souhait_formation": s
        })
    
    with open(dir_path / "00_candidat.json", "w", encoding="utf-8") as f:
        json.dump(cand_info, f, indent=4)
        
    with open(dir_path / "02_reponses.json", "w", encoding="utf-8") as f:
        json.dump({"questions": answers}, f, indent=4)
        
    with open(CANDIDATS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["candidats"].append(cand_info)
    with open(CANDIDATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    fichier_sortie = dir_path / 'programme_perso.json'
    generer_programme(id_candidat, fichier_sortie)
    print(f"Created {id_candidat}")

create_cand("Dupont", "Jean (Novice)", "novice", "QUEST_EXCEL_INIT", lambda: "Aucune")
create_cand("Martin", "Sophie (Débutant)", "debutant", "QUEST_EXCEL_INTER", lambda: random.choice(["Aucune", "Aucune", "Moyenne"]))
create_cand("Bernard", "Luc (Intermédiaire)", "intermediaire", "QUEST_EXCEL_PERF", lambda: random.choice(["Moyenne", "Acquise", "Acquise"]))
