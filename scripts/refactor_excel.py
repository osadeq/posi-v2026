import json
import copy

with open('data/bd/00_questions.json', 'r', encoding='utf-8') as f:
    quest_data = json.load(f)
with open('data/bd/01_programmes.json', 'r', encoding='utf-8') as f:
    prog_data = json.load(f)

def get_domain_id(text):
    text = text.lower()
    if 'calcul' in text or 'formule' in text or 'fonction' in text: return 'D2'
    if 'forme' in text: return 'D3'
    if 'donn' in text or 'tableau' in text or 'plage' in text or 'graphique' in text: return 'D4'
    return 'D1'

def read_file_safe(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='cp1252') as f:
            return f.read()

def parse_ref_file(filename, level_id, prefix):
    questions = []
    current_domain = 'D1'
    content = read_file_safe(filename)
    lines = content.splitlines()
        
    q_index = 1
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('*'):
            # The ref files use precise names: Environnement, Calculs, Mise en forme, Gestion des données
            if 'environnement' in line.lower(): current_domain = 'D1'
            elif 'calcul' in line.lower(): current_domain = 'D2'
            elif 'forme' in line.lower(): current_domain = 'D3'
            elif 'donn' in line.lower(): current_domain = 'D4'
        elif line.startswith('o '):
            texte = line[2:].strip()
            q_id = f"{prefix}_{current_domain}_{level_id}_Q{q_index:02d}"
            questions.append({
                "id_question": q_id,
                "id_theme": "", # Assigned later dynamically
                "texte": texte,
                "id_domaine": current_domain,
                "id_niveau": level_id
            })
            q_index += 1
    return questions

q_n1_master = parse_ref_file('data/modeles/Ref_TOSA_EXCEL_Initiation.txt', 'N1', 'INIT')
q_n2_master = parse_ref_file('data/modeles/Ref_TOSA_EXCEL_Intermediaire.txt', 'N2', 'INTER')
q_n3_master = parse_ref_file('data/modeles/Ref_TOSA_EXCEL_Perfectionnement.txt', 'N3', 'PERF')

quest_init = {
    "id_questionnaire": "QUEST_EXCEL_INIT",
    "id_programme": "PROG_EXCEL_INIT",
    "titre": "Positionnement Excel - Initiation (Tosa)",
    "description": "Auto-évaluation des compétences Excel Novice/Initiation",
    "questions": copy.deepcopy(q_n1_master)
}
quest_inter = {
    "id_questionnaire": "QUEST_EXCEL_INTER",
    "id_programme": "PROG_EXCEL_INTER",
    "titre": "Positionnement Excel - Intermédiaire (Tosa)",
    "description": "Auto-évaluation des compétences Excel Intermédiaire",
    "questions": copy.deepcopy(q_n1_master) + copy.deepcopy(q_n2_master)
}
quest_perf = {
    "id_questionnaire": "QUEST_EXCEL_PERF",
    "id_programme": "PROG_EXCEL_PERF",
    "titre": "Positionnement Excel - Perfectionnement (Tosa)",
    "description": "Auto-évaluation des compétences Excel Avancé/Perfectionnement",
    "questions": copy.deepcopy(q_n1_master) + copy.deepcopy(q_n2_master) + copy.deepcopy(q_n3_master)
}

for q in [quest_init, quest_inter, quest_perf]:
    q['reponses_possibles'] = quest_data['questionnaires'][0]['reponses_possibles']
    q['regles_besoin'] = quest_data['questionnaires'][0]['regles_besoin']

def parse_prog_file(filename, prog_id, title_prefix, target_quest):
    content = read_file_safe(filename)

    lines = content.split('\n')
    themes = []
    current_theme = None
    prog_start = False
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith("Programme"):
            prog_start = True
            continue
        
        if prog_start:
            if not line.startswith('*') and not line.startswith('o '):
                d_id = get_domain_id(line)
                theme_id = f"{title_prefix}_T{len(themes)+1}"
                current_theme = {
                    "id_theme": theme_id,
                    "nom": line,
                    "domaine_tosa": [d_id],
                    "competences_tosa": [],
                    "duree_heures": 2,
                    "items": []
                }
                themes.append(current_theme)
            else:
                if current_theme:
                    item_text = line[1:].strip()
                    current_theme['items'].append(item_text)

    # Force generic themes for missing domains if any
    domains_present = set([t['domaine_tosa'][0] for t in themes])
    for required_d in ['D1', 'D2', 'D3', 'D4']:
        if required_d not in domains_present:
            theme_id = f"{title_prefix}_T{len(themes)+1}"
            themes.append({
                "id_theme": theme_id,
                "nom": f"Thème générique {required_d}",
                "domaine_tosa": [required_d],
                "competences_tosa": [],
                "duree_heures": 2,
                "items": ["Pratique et révision"]
            })
                    
    for q in target_quest['questions']:
        d = q['id_domaine']
        m_themes = [t for t in themes if d in t['domaine_tosa']]
        if m_themes:
            for m in m_themes:
                m['competences_tosa'].append(q['id_question'])
            q['id_theme'] = m_themes[0]['id_theme']
        else:
            print(f"ERROR: missing theme for domain {d} in prog {prog_id}")
            
    if themes:
        avg = round(14.0 / len(themes), 1)
        for t in themes: t['duree_heures'] = avg

    prog = {
        "id_programme": prog_id,
        "intitule": f"Exploiter les fonctionnalités de Microsoft Excel - {title_prefix}",
        "duree": "14h",
        "duree_par_defaut": "14",
        "duree_min": "14",
        "unite_duree": "heure",
        "duree_seance": 3.5,
        "unite_seance": "heure",
        "cout_horaire": 45,
        "certification_optionnelle": True,
        "certification": {
            "incluse": False,
            "duree_heures": 1,
            "cout_supplementaire": 0
        },
        "themes": themes,
        "blocs_objectifs": [
            {
                "id": "B1",
                "nom": "Parcours complet",
                "themes": [t["id_theme"] for t in themes]
            }
        ]
    }
    return prog

prog_init = parse_prog_file('data/modeles/Programme_formation_Excel_Tosa_Initiation.txt', 'PROG_EXCEL_INIT', 'INIT', quest_init)
prog_inter = parse_prog_file('data/modeles/Programme_formation_Excel_Tosa_Intermediaire.txt', 'PROG_EXCEL_INTER', 'INTER', quest_inter)
prog_perf = parse_prog_file('data/modeles/Programme_formation_Excel_Tosa_Perfectionnement_Avance.txt', 'PROG_EXCEL_PERF', 'PERF', quest_perf)

quest_data['questionnaires'] = [q for q in quest_data['questionnaires'] if not q['id_questionnaire'].startswith('QUEST_EXCEL')]
quest_data['questionnaires'].extend([quest_init, quest_inter, quest_perf])

with open('data/bd/00_questions.json', 'w', encoding='utf-8') as f:
    json.dump(quest_data, f, ensure_ascii=False, indent=4)

prog_data['programmes'] = [p for p in prog_data['programmes'] if not p['id_programme'].startswith('PROG_EXCEL')]
prog_data['programmes'].extend([prog_init, prog_inter, prog_perf])

with open('data/bd/01_programmes.json', 'w', encoding='utf-8') as f:
    json.dump(prog_data, f, ensure_ascii=False, indent=4)

print("SUCCESS")
