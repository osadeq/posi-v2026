"""
Module d'analyse des besoins de formation
Transforme les reponses candidat en programme personnalise avec deroule pedagogique
"""
import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent
BD_DIR = DATA_DIR / "bd"
CANDIDATS_DIR = DATA_DIR / "candidats"
CANDIDATS_INDEX = BD_DIR / "03_candidats.json"
PROGRAMMES_FILE = BD_DIR / "01_programmes.json"
QUESTIONS_FILE = BD_DIR / "00_questions.json"
REFERENTIEL_EXCEL_FILE = BD_DIR / "04_referentiel_excel_origine.json"

REGLE_BESOIN_FORT = "besoin_fort"
REGLE_BESOIN_MOYEN = "besoin_moyen"
REGLE_A_REVOIR = "a_revoir"
REGLE_IGNORER = "ignorer"


def charger_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur chargement {filepath}: {e}")
        return None


def charger_ressources():
    index = charger_json(CANDIDATS_INDEX)
    programmes = charger_json(PROGRAMMES_FILE)
    questions = charger_json(QUESTIONS_FILE)
    referentiel = charger_json(REFERENTIEL_EXCEL_FILE)
    return index, programmes, questions, referentiel


def construire_lookup_competences():
    """Construit {id_comp: {title, id_domaine, nom_domaine}} depuis le referentiel Excel et les questions."""
    lookup = {}
    domaine_noms = {}
    
    # 1. Charger depuis l'ancien référentiel (pour récupérer les noms de domaines)
    ref_data = charger_json(REFERENTIEL_EXCEL_FILE)
    if ref_data:
        for dom in ref_data.get('competences_visees', []):
            did = dom['id_domaine']
            domaine_noms[did] = dom['title']
            for niveau in dom.get('niveaux', []):
                for comp in niveau.get('competences', []):
                    lookup[comp['id_comp']] = {
                        'title': comp['title'],
                        'id_domaine': did,
                        'nom_domaine': dom['title']
                    }
                    
    # 2. Charger les compétences depuis les questions (nouvelle structure INIT/INTER/PERF)
    quest_data = charger_json(QUESTIONS_FILE)
    if quest_data and 'questionnaires' in quest_data:
        for q_sheet in quest_data['questionnaires']:
            for q in q_sheet.get('questions', []):
                qid = q.get('id_question')
                texte = q.get('texte')
                did = q.get('id_domaine')
                if qid and texte and did:
                    lookup[qid] = {
                        'title': texte,
                        'id_domaine': did,
                        'nom_domaine': domaine_noms.get(did, f"Domaine {did}")
                    }
                    
    return lookup, domaine_noms


def charger_reponses_candidat(id_candidat):
    fichier = CANDIDATS_DIR / id_candidat / "questionnaire.json"
    if not fichier.exists():
        print(f"Pas de questionnaire trouve pour {id_candidat}: {fichier}")
        return None
    return charger_json(fichier)


def extraire_themes_de_question(id_question, comp_to_themes=None):
    """
    Extrait l'ID ou les IDs des thèmes depuis l'ID de la question.
    Pour les IDs Excel [DX-NX-CX], utilise comp_to_themes si fourni.
    Convention classique: TX_QNN -> [TX], ETX_QNN -> [ETX]
    """
    if comp_to_themes and id_question in comp_to_themes:
        return comp_to_themes[id_question]
    parts = id_question.rsplit('_Q', 1)
    if len(parts) == 2:
        return [parts[0]]
    return []


def analyser_reponse(acquisition, besoin):
    acq = str(acquisition).strip().capitalize() if acquisition else ""
    bes = str(besoin).strip().capitalize() if besoin else ""

    if bes == "Non":
        return REGLE_IGNORER
    if not bes and not acq:
        return REGLE_IGNORER
    if acq in ("Aucun", "Non", ""):
        return REGLE_BESOIN_FORT
    if acq == "Moyen":
        return REGLE_BESOIN_MOYEN
    if acq in ("Acquis", "Oui"):
        if bes == "Oui":
            return REGLE_A_REVOIR
        return REGLE_IGNORER
    return None


def trouver_questionnaire(questions_data, id_questionnaire):
    if not questions_data:
        return None
    for q in questions_data.get('questionnaires', []):
        if q['id_questionnaire'] == id_questionnaire:
            return q
    return None


def trouver_programme(programmes_data, id_programme):
    if not programmes_data:
        return None
    for p in programmes_data.get('programmes', []):
        if p['id_programme'] == id_programme:
            return p
    return None


def creer_deroule_pedagogique(themes_a_former, total_heures, programme_info, domaines_lookup=None):
    duree_seance = float(programme_info.get('duree_seance', 3.5))
    duree_min = float(programme_info.get('duree_min', 7))
    total_heures_planifiees = max(total_heures, duree_min)

    nb_seances = int(total_heures_planifiees / duree_seance)
    if total_heures_planifiees % duree_seance > 0.5:
        nb_seances += 1
    if themes_a_former and nb_seances == 0:
        nb_seances = 1

    def priorite_theme(theme):
        niveau = str(theme.get('niveau_besoin', '')).lower()
        if 'fort' in niveau:
            return 0
        if 'moyen' in niveau:
            return 1
        if 'revoir' in niveau:
            return 2
        return 99

    themes_tries = sorted(themes_a_former, key=priorite_theme)
    seances = []
    theme_num_by_id = {t['id_theme']: idx + 1 for idx, t in enumerate(themes_tries)}

    if domaines_lookup is None:
        domaines_lookup = {}

    theme_states = []
    for theme in themes_tries:
        theme_states.append({
            'theme': theme,
            'remaining': float(theme.get('duree_estimee', 0) or 0),
            'next_item_idx': 0
        })

    state_idx = 0
    for i in range(nb_seances):
        seance = {
            'seance_numero': i + 1,
            'duree_heures': duree_seance,
            'activites': [],
            'themes_couverts': [],
            'blocs': []
        }

        capacite = float(duree_seance)
        while capacite > 0.01 and any(s['remaining'] > 0.01 for s in theme_states):
            tours = 0
            while theme_states and theme_states[state_idx]['remaining'] <= 0.01 and tours < len(theme_states):
                state_idx = (state_idx + 1) % len(theme_states)
                tours += 1

            if not theme_states or (tours >= len(theme_states) and theme_states[state_idx]['remaining'] <= 0.01):
                break

            state = theme_states[state_idx]
            theme = state['theme']
            remaining_before = float(state['remaining'])
            duree_theme = float(theme.get('duree_estimee', 0) or 0)
            allocation = round(min(capacite, state['remaining']), 1)
            if allocation <= 0:
                break

            state['remaining'] = round(state['remaining'] - allocation, 3)
            capacite = round(capacite - allocation, 3)

            items = theme.get('contenu_programme', [])
            bloc_items = []
            if items:
                total_items = len(items)
                duree_ref = max(duree_theme, 0.1)
                proportion = allocation / duree_ref
                nb_items = max(1, int(round(proportion * total_items)))
                start = state['next_item_idx']
                end = min(total_items, start + nb_items)
                bloc_items = items[start:end] or items[:1]
                state['next_item_idx'] = 0 if end >= total_items else end

            fait_avant = round(max(duree_theme - remaining_before, 0), 1)
            phase = 'Debut' if fait_avant <= 0.01 else 'Suite'

            domaines_ids = theme.get('domaine_tosa', [])
            domaines_noms = [domaines_lookup.get(did, did) for did in domaines_ids]

            seance['themes_couverts'].append({
                'id': theme['id_theme'],
                'nom': theme['nom'],
                'niveau_besoin': theme['niveau_besoin'],
                'duree_estimee': theme['duree_estimee'],
                'duree_planifiee': allocation,
                'domaines': domaines_noms
            })

            seance['blocs'].append({
                'id': theme['id_theme'],
                'theme_num': theme_num_by_id.get(theme['id_theme'], 0),
                'nom': theme['nom'],
                'niveau_besoin': theme['niveau_besoin'],
                'duree_theme': round(duree_theme, 1),
                'duree_planifiee': allocation,
                'fait': fait_avant,
                'a_faire': allocation,
                'phase': phase,
                'activites': [{'numero': i + 1 + state['next_item_idx'], 'nom': (item['activite'] if isinstance(item, dict) else item)} for i, item in enumerate(bloc_items)],
                'domaines': domaines_noms,
                'comp_par_domaine': theme.get('comp_par_domaine', [])
            })

            duree_item = round(allocation / max(len(bloc_items), 1), 1)
            for i, item in enumerate(bloc_items):
                item_nom = item['activite'] if isinstance(item, dict) else item
                seance['activites'].append({
                    'theme': theme['nom'],
                    'activite': item_nom,
                    'numero': state['next_item_idx'] + i + 1,
                    'duree_estimee': f"~{duree_item}h"
                })

            if state['remaining'] <= 0.01:
                state_idx = (state_idx + 1) % len(theme_states)

        seances.append(seance)

    cert_info = programme_info.get('certification', {})
    certification = None
    if not programme_info.get('certification_optionnelle', True) or cert_info.get('incluse'):
        certification = {
            "type": "Certification TOSA",
            "duree": f"{cert_info.get('duree_heures', 1)}h00",
            "horaire": "Fin de parcours",
            "note": "Session planifiee apres validation des acquis"
        }

    return {
        "nb_seances": nb_seances,
        "total_heures": total_heures_planifiees,
        "duree_seance": duree_seance,
        "seances": seances,
        "certification": certification
    }


def creer_programme_personnalise(id_candidat, id_programme=None):
    index, programmes_data, questions_data, referentiel = charger_ressources()
    if not index or not programmes_data:
        print("Erreur: impossible de charger les ressources de base")
        return None

    domaines_lookup = {}
    competences_lookup = {}

    comp_lookup_excel, domaine_noms_excel = construire_lookup_competences()
    competences_lookup.update({k: v['title'] for k, v in comp_lookup_excel.items()})
    domaines_lookup.update(domaine_noms_excel)

    if referentiel:
        for key in referentiel:
            if key.startswith('domaines'):
                domaines_liste = referentiel[key]
                if isinstance(domaines_liste, list):
                    for dom in domaines_liste:
                        if dom['id'] not in domaines_lookup:
                            domaines_lookup[dom['id']] = dom['nom']
                        for comp in dom.get('competences', []):
                            if comp['id'] not in competences_lookup:
                                competences_lookup[comp['id']] = comp['nom']

    candidat = next((c for c in index['candidats'] if c['id_candidat'] == id_candidat), None)
    if not candidat:
        print(f"Candidat {id_candidat} non trouve dans l'index")
        return None

    questionnaire = charger_reponses_candidat(id_candidat)
    if not questionnaire:
        print(f"Pas de questionnaire pour {id_candidat}")
        return None

    reponses = questionnaire.get('reponses', [])
    id_questionnaire = questionnaire.get('id_questionnaire', candidat.get('id_questionnaire', ''))

    target_prog_id = id_programme or candidat.get('id_programme')
    if not target_prog_id and id_questionnaire and questions_data:
        quest = trouver_questionnaire(questions_data, id_questionnaire)
        if quest:
            target_prog_id = quest.get('id_programme')
    if not target_prog_id:
        target_prog_id = 'PROG_WORD'

    programme = trouver_programme(programmes_data, target_prog_id)
    if not programme:
        print(f"Programme {target_prog_id} non trouve, fallback premier programme")
        programme = programmes_data['programmes'][0]

    print(f"Analyse pour {id_candidat}: questionnaire={id_questionnaire}, programme={programme['id_programme']}")

    self_level = str(questionnaire.get('self_level', candidat.get('self_level', ''))).lower()

    # Mapping comp_id -> [theme_id] pour les questions Excel ([DX-NX-CX])
    comp_to_themes = {}
    for _t in programme.get('themes', []):
        for _cid in _t.get('competences_tosa', []):
            if _cid not in comp_to_themes:
                comp_to_themes[_cid] = []
            comp_to_themes[_cid].append(_t['id_theme'])

    besoins_par_theme = {}

    if self_level == 'novice':
        # Novice : inclure automatiquement tous les themes du bloc B1
        print(f"  Profil NOVICE detecte : inclusion automatique du Bloc B1")
        theme_to_bloc = {}
        if 'blocs_objectifs' in programme:
            for b in programme['blocs_objectifs']:
                for t_id in b.get('themes', []):
                    theme_to_bloc[t_id] = b['id']
        for theme in programme.get('themes', []):
            t_id = theme['id_theme']
            if theme_to_bloc.get(t_id) == 'B1':
                questions_theme = theme.get('competences_tosa', [])
                if not questions_theme:
                    questions_theme = ['INFO_NOVICE']
                besoins_par_theme[t_id] = {'questions': questions_theme, 'types': {REGLE_BESOIN_FORT}}
    else:
        # Analyser toutes les reponses recues (sans filtrage par bloc)
        for rep in reponses:
            id_q = rep['id_question']
            id_themes = extraire_themes_de_question(id_q, comp_to_themes)

            if not id_themes:
                continue

            type_besoin = analyser_reponse(rep.get('acquisition'), rep.get('besoin'))

            if not type_besoin or type_besoin == REGLE_IGNORER:
                continue

            for id_theme in id_themes:
                if id_theme not in besoins_par_theme:
                    besoins_par_theme[id_theme] = {'questions': [], 'types': set()}

                besoins_par_theme[id_theme]['questions'].append(id_q)
                besoins_par_theme[id_theme]['types'].add(type_besoin)

    # Construire les themes a former
    themes_a_former = []
    total_h = 0
    for t_id, t_data in besoins_par_theme.items():
        t_info = next((t for t in programme['themes'] if t['id_theme'] == t_id), None)
        if not t_info:
            continue

        types = t_data['types']
        niveau = "fort" if REGLE_BESOIN_FORT in types else ("moyen" if REGLE_BESOIN_MOYEN in types else "a_revoir")

        duree_ref = float(t_info.get('duree_heures', 0))
        duree_estimee = duree_ref if niveau != 'a_revoir' else round(duree_ref * 0.5, 1)
        total_h += duree_estimee

        domaines_ids = t_info.get('domaine_tosa', [])
        domaines_noms = [domaines_lookup.get(did, did) for did in domaines_ids]

        comp_ids = t_info.get('competences_tosa', [])
        comp_noms = [competences_lookup.get(cid, cid) for cid in comp_ids]

        comp_par_domaine_dict = {}
        for cid in comp_ids:
            info = comp_lookup_excel.get(cid)
            if info:
                did = info['id_domaine']
                
                niveau_str = ""
                if "-N1-" in cid: niveau_str = " (N1)"
                elif "-N2-" in cid: niveau_str = " (N2)"
                elif "-N3-" in cid: niveau_str = " (N3)"
                
                if did not in comp_par_domaine_dict:
                    comp_par_domaine_dict[did] = {
                        'id_domaine': did,
                        'nom_domaine': info['nom_domaine'],
                        'competences': []
                    }
                
                titre_avec_niveau = info['title'] + niveau_str
                if titre_avec_niveau not in comp_par_domaine_dict[did]['competences']:
                    comp_par_domaine_dict[did]['competences'].append(titre_avec_niveau)
        comp_par_domaine = list(comp_par_domaine_dict.values())

        themes_a_former.append({
            'id_theme': t_id,
            'nom': t_info['nom'],
            'niveau_besoin': niveau,
            'duree_estimee': duree_estimee,
            'nb_questions': len(t_data['questions']),
            'contenu_programme': t_info.get('items', []),
            'domaine_tosa': domaines_ids,
            'domaine_noms': domaines_noms,
            'competences_tosa': comp_ids,
            'competences_noms': comp_noms,
            'comp_par_domaine': comp_par_domaine
        })

    print(f"  -> {len(themes_a_former)} themes identifies, {total_h}h estimees")

    orientation_expert = False
    if self_level == 'intermediaire' and len(themes_a_former) == 0:
        orientation_expert = True
        print("  -> Profil Expert detecte : aucun besoin identifie, orientation vers certification experte.")

    # Groupement par domaine pour l'affichage
    themes_par_domaine = []
    if referentiel and 'domaines' in referentiel:
        for dom in referentiel['domaines']:
            dom_id = dom['id']
            themes_du_domaine = [t for t in themes_a_former if dom_id in t['domaine_tosa']]
            if themes_du_domaine:
                themes_par_domaine.append({
                    'id_domaine': dom_id,
                    'nom_domaine': dom['nom'],
                    'themes': themes_du_domaine
                })
    else:
        themes_par_domaine.append({
            'id_domaine': 'UNK',
            'nom_domaine': 'Autres',
            'themes': themes_a_former
        })

    deroule = creer_deroule_pedagogique(themes_a_former, total_h, programme, domaines_lookup)

    cout_h = float(programme.get('cout_horaire', 45))
    cout_cert = float(programme.get('certification', {}).get('cout_supplementaire', 120)) if deroule['certification'] else 0

    return {
        'id_candidat': id_candidat,
        'nom_candidat': candidat.get('nom', ''),
        'prenom_candidat': candidat.get('prenom', ''),
        'id_questionnaire': id_questionnaire,
        'programme_id': programme['id_programme'],
        'programme_nom': programme['intitule'],
        'orientation_expert': orientation_expert,
        'themes_a_former': themes_a_former,
        'themes_par_domaine': themes_par_domaine,
        'reponses_par_domaine': grouper_reponses_par_domaine(id_candidat, reponses),
        'reponses_par_bloc': grouper_reponses_par_bloc(id_candidat, reponses),
        'deroule_pedagogique': deroule,
        'estimation': {
            'total_heures': deroule['total_heures'],
            'nb_seances': deroule['nb_seances'],
            'cout_horaire': cout_h,
            'cout_certification': cout_cert,
            'cout_total': round((deroule['total_heures'] * cout_h) + cout_cert, 2)
        }
    }


def generer_programme(id_candidat, fichier_sortie=None, id_programme=None):
    prog = creer_programme_personnalise(id_candidat, id_programme)
    if prog and fichier_sortie:
        output_dir = os.path.dirname(fichier_sortie)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(fichier_sortie, 'w', encoding='utf-8') as f:
            json.dump(prog, f, ensure_ascii=False, indent=2)
    return prog


def grouper_reponses_par_domaine(id_candidat, reponses=None):
    index, programmes_data, questions_data, referentiel = charger_ressources()
    if not referentiel:
        return []

    if reponses is None:
        questionnaire = charger_reponses_candidat(id_candidat)
        if not questionnaire:
            return []
        reponses = questionnaire.get('reponses', [])

    candidat = next((c for c in index['candidats'] if c['id_candidat'] == id_candidat), None)
    if not candidat:
        return []

    id_programme = candidat.get('id_programme', 'PROG_WORD')
    programme = trouver_programme(programmes_data, id_programme)
    if not programme:
        return []

    # Mapping theme_id -> domaines + comp_to_theme pour Excel
    # comp_to_theme pour Excel -> comp_to_themes
    comp_to_themes = {}
    for _t in programme.get('themes', []):
        for _cid in _t.get('competences_tosa', []):
            if _cid not in comp_to_themes:
                comp_to_themes[_cid] = []
            comp_to_themes[_cid].append(_t['id_theme'])

    theme_to_domaines = {t['id_theme']: t.get('domaine_tosa', []) for t in programme.get('themes', [])}

    reponses_par_domaine = []
    for dom in referentiel.get('domaines', []):
        dom_id = dom['id']
        dom_reponses = []
        for rep in reponses:
            id_themes = extraire_themes_de_question(rep['id_question'], comp_to_themes)
            matched = False
            for id_theme in id_themes:
                if dom_id in theme_to_domaines.get(id_theme, []):
                    matched = True
                    break
            if matched:
                dom_reponses.append(rep)
        if dom_reponses:
            reponses_par_domaine.append({
                'id_domaine': dom_id,
                'nom_domaine': dom['nom'],
                'reponses': dom_reponses
            })

    return reponses_par_domaine


def grouper_reponses_par_bloc(id_candidat, reponses=None):
    index, programmes_data, questions_data, _ = charger_ressources()

    if reponses is None:
        questionnaire = charger_reponses_candidat(id_candidat)
        if not questionnaire:
            return []
        reponses = questionnaire.get('reponses', [])

    candidat = next((c for c in index['candidats'] if c['id_candidat'] == id_candidat), None)
    if not candidat:
        return []

    id_programme = candidat.get('id_programme', 'PROG_WORD')
    programme = trouver_programme(programmes_data, id_programme)
    if not programme or 'blocs_objectifs' not in programme:
        return []

    # comp_to_theme pour Excel
    comp_to_themes = {}
    for _t in programme.get('themes', []):
        for _cid in _t.get('competences_tosa', []):
            if _cid not in comp_to_themes:
                comp_to_themes[_cid] = []
            comp_to_themes[_cid].append(_t['id_theme'])

    reponses_par_bloc = []
    for bloc in programme['blocs_objectifs']:
        bloc_id = bloc['id']
        bloc_themes = bloc.get('themes', [])
        bloc_reponses = []

        for rep in reponses:
            id_themes = extraire_themes_de_question(rep['id_question'], comp_to_themes)
            matched = False
            for id_theme in id_themes:
                if id_theme in bloc_themes:
                    matched = True
                    break
            if matched:
                bloc_reponses.append(rep)

        if bloc_reponses:
            reponses_par_bloc.append({
                'id_bloc': bloc_id,
                'nom_bloc': bloc['nom'],
                'reponses': bloc_reponses
            })

    return reponses_par_bloc
