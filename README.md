# eS@deq — Plateforme de Positionnement

> Génération automatique de programmes de formation personnalisés à partir de l'auto-positionnement des candidats.

**Version** : 3.1 — Mars 2026  
**Stack** : Python 3 · Flask · Jinja2 · WeasyPrint (PDF) · openpyxl (Excel) · JSON  
**Interface web** : Questionnaire intégré (sans Moodle)

---

## 📋 Table des matières

1. [Principe général](#-principe-général)
2. [Architecture v3](#-architecture-v3)
3. [Installation](#-installation)
4. [Lancement](#-lancement)
5. [Structure du projet](#-structure-du-projet)
6. [Base de données JSON](#-base-de-données-json)
7. [Questionnaire intégré](#-questionnaire-intégré)
8. [Moteur d'analyse des besoins](#-moteur-danalyse-des-besoins)
9. [Fonctionnalités de l'application](#-fonctionnalités-de-lapplication)
10. [API REST](#-api-rest)
11. [Design System](#-design-system)
12. [Programmes supportés](#-programmes-supportés)
13. [Scripts utilitaires](#-scripts-utilitaires)
14. [Contribuer / Évolution](#-contribuer--évolution)

---

## 🎯 Principe général

```
┌─────────────────┐   Web Form   ┌──────────────────┐   PDF/Excel   ┌─────────────────┐
│   Candidat      │ ──────────►  │   eS@deq          │ ───────────► │   Formateur     │
│  (navigateur)   │  auto-eval   │  (analyse des     │  programme   │  (programme     │
│                 │              │   besoins + TOSA) │  personnalisé│  sur mesure)    │
└─────────────────┘              └──────────────────┘              └─────────────────┘
```

1. Le **candidat** accède au questionnaire via un lien direct
2. Il choisit son **niveau de départ** (Novice / Débutant / Intermédiaire)
3. Il évalue chaque **compétence TOSA** par domaine (groupes accordéon)
4. L'application **analyse les besoins** selon les règles TOSA et génère un **programme personnalisé**
5. Le programme est exportable en **PDF** ou **Excel** pour le dossier administratif

> ✅ **Nouveauté v3** : Le questionnaire est désormais **intégré à l'application** (plus besoin de Moodle).  
> L'import CSV reste disponible pour compatibilité avec les tests Moodle existants.

---

## 🛠 Architecture v3

### Choix de conception clés

| Décision | Raison |
|----------|--------|
| **Questionnaire intégré** (formulaire web) | Plus besoin de Moodle pour les nouveaux candidats |
| **3 questionnaires Excel distincts** (INIT / INTER / PERF) | Questions ciblées par niveau TOSA |
| **Fusion côté serveur** pour l'affichage | QUEST_EXCEL agrège INIT + INTER + PERF avec `id_niveau` extrait automatiquement |
| **Groupement par domaine + accordéon** | UX claire — compétences regroupées par domaine TOSA (D1 à D4) |
| **Filtrage JS par niveau** | Seules les compétences du niveau choisi s'affichent (N1, N1+N2, N1+N2+N3) |
| **Valeurs par défaut pré-cochées** | Maîtrise = "Aucune", Besoin = "Oui" — rempli intelligemment selon la maîtrise |
| **Design system Navy + Crème + Or** | Palette professionnelle sobre et raffinée |
| **Sidebar de progression** | Navigation deux-colonnes avec indicateur d'étape en temps réel |
| **Export Excel** (openpyxl) | Programme exportable en `.xlsx` en plus du PDF |

### Flux de données

```
00_questions.json (INIT + INTER + PERF) ────────────────────────────┐
   (questions par niveau N1 / N2 / N3)                              │
                                                                     ▼
Formulaire web ──► app.py (submit_questionnaire) ──► data/candidats/{id}/questionnaire.json
                                                             │
data/bd/01_programmes.json ──────────────────────────────────┤
   (thèmes, durées, items)                                   │
                                                             ▼
                                              data/analyse_besoins.py
                                                             │
                                              ┌──────────────┴──────────────┐
                                              ▼                             ▼
                                   src/pdf_generator.py        src/excel_generator.py
                                        │                              │
                                        ▼                              ▼
                                    programme.pdf              programme.xlsx
```

---

## ⚙ Installation

### Prérequis

- **Python 3.9+**
- **pip** (gestionnaire de paquets Python)
- **GTK3** (optionnel, pour la génération PDF)

### Étapes

```bash
# 1. Copier le projet
cd c:\Users\...\posi-2026-v3

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. (Optionnel) Pour la génération PDF
# Exécuter install_gtk3.bat ou télécharger GTK3 depuis :
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
```

### Dépendances

| Paquet | Version | Rôle |
|--------|---------|------|
| Flask | 3.0.0 | Framework web |
| Werkzeug | 3.0.1 | Serveur WSGI |
| WeasyPrint | 60.2 | Génération PDF |
| pydyf | 0.10.0 | Moteur PDF (dépendance WeasyPrint) |
| openpyxl | 3.1.5 | Génération Excel (.xlsx) |
| markdown | 3.5.2 | Traitement de texte |
| python-dotenv | 1.0.0 | Variables d'environnement |

---

## 🚀 Lancement

### Windows (méthode rapide)

```
Double-cliquer sur start.bat
```

### Ligne de commande

```bash
python app.py
```

L'application est accessible sur : **http://localhost:5000**

### Configuration (`config.py`)

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `SECRET_KEY` | `dev-secret-key-posi-2026` | Clé de session Flask |
| `DEBUG` | `True` | Mode développement |
| `ALLOWED_EXTENSIONS` | `csv, txt` | Extensions autorisées à l'import |
| `ITEMS_PER_PAGE` | `20` | Pagination des candidats |
| `MAX_CONTENT_LENGTH` | `16 Mo` | Taille max des fichiers uploadés |

---

## 📁 Structure du projet

```
posi-2026-v3/
├── app.py                          # Application Flask principale
├── config.py                       # Configuration
├── requirements.txt                # Dépendances Python
├── start.bat                       # Lanceur Windows
├── start_silent.bat                # Lanceur Windows silencieux
├── install_gtk3.bat                # Installeur GTK3 pour PDF
│
├── data/
│   ├── bd/                         # 📦 Base de données (modèles)
│   │   ├── 00_questions.json       #   3 questionnaires (INIT / INTER / PERF)
│   │   ├── 01_programmes.json      #   Programmes de formation + thèmes
│   │   ├── 03_candidats.json       #   Index des candidats (métadonnées)
│   │   └── 04_referentiel_excel_origine.json  # Référentiel TOSA Excel (D1→D4, N1→N3)
│   │
│   ├── candidats/                  # 👤 Données par candidat
│   │   └── CAND_xxx/
│   │       ├── questionnaire.json  #   Réponses du candidat
│   │       ├── questionnaire.csv   #   CSV source (archivé)
│   │       └── programme_perso.json#   Programme généré
│   │
│   ├── modeles/                    # 📄 Spécifications et modèles
│   │   ├── SPEC_FORMAT_CSV.md      #   Spécification complète du format
│   │   └── csv_import_format.csv   #   Exemple de CSV d'import
│   │
│   ├── analyse_besoins.py          # 🧠 Moteur d'analyse (cœur métier)
│   ├── upload/                     # Fichiers temporaires d'import
│   └── export/                     # PDFs exportés
│
├── scripts/
│   └── update_programmes.py        # 🔧 Sync compétences 00→01 (maintenance)
│
├── src/
│   ├── pdf_generator.py            # Génération PDF (WeasyPrint)
│   └── excel_generator.py          # Génération Excel (openpyxl)
│
├── static/
│   └── css/
│       ├── style.css               # ✨ Design system global (Navy · Crème · Or)
│       └── pdf.css                 # Styles spécifiques au PDF
│
└── templates/
    ├── base.html                   # Template de base (layout + navbar)
    ├── dashboard.html              # Page d'accueil / statistiques
    ├── candidat/
    │   ├── formulaire.html         # Questionnaire intégré (2 étapes)
    │   ├── liste.html              # Liste des candidats
    │   ├── detail.html             # Fiche candidat + programme
    │   └── import.html             # Formulaire d'import CSV
    └── pdf/
        └── programme.html          # Template du PDF
```

---

## 🗃 Base de données JSON

### `00_questions.json` — Questionnaires Excel (3 niveaux)

Trois questionnaires distincts, chacun ciblant un niveau TOSA :

| ID Questionnaire | Programme associé | Niveau | Nb questions |
|:---|:---|:---:|:---:|
| `QUEST_EXCEL_INIT` | `PROG_EXCEL_INIT` | N1 — Initiation | 21 |
| `QUEST_EXCEL_INTER` | `PROG_EXCEL_INTER` | N2 — Intermédiaire | 15 |
| `QUEST_EXCEL_PERF` | `PROG_EXCEL_PERF` | N3 — Perfectionnement | 16 |

L'ID question suit le format `[DX-NX-CX]` (ex: `[D2-N2-C7]`) qui encode domaine, niveau et compétence.

```json
{
  "questionnaires": [
    {
      "id_questionnaire": "QUEST_EXCEL_INIT",
      "id_programme": "PROG_EXCEL_INIT",
      "titre": "Positionnement Excel - Initiation (Tosa)",
      "questions": [
        { "id_question": "[D1-N1-C1]", "id_theme": "INIT_T2", "texte": "Ouvrir un document Excel" }
      ]
    }
  ]
}
```

> 💡 La route `/questionnaire/QUEST_EXCEL` fusionne automatiquement les 3 questionnaires côté serveur et extrait `id_niveau` / `id_domaine` via regex sur l'`id_question`.

### `01_programmes.json` — Programmes de formation

Trois programmes Excel distincts + un programme Word :

| ID Programme | Intitulé | Niveau cible |
|:---|:---|:---|
| `PROG_EXCEL_INIT` | Excel — Initiation (Tosa) | Novice → Débutant |
| `PROG_EXCEL_INTER` | Excel — Intermédiaire (Tosa) | Débutant → Opérationnel |
| `PROG_EXCEL_PERF` | Excel — Perfectionnement (Tosa) | Intermédiaire → Expert |
| `PROG_WORD` | Word — Rédaction professionnelle (Tosa) | Tous niveaux |

### `03_candidats.json` — Index des candidats

```json
{
  "candidats": [
    {
      "id_candidat": "CAND_DUPONT_JEAN_20260318_143022",
      "nom": "DUPONT", "prenom": "Jean",
      "self_level": "debutant",
      "id_questionnaire": "QUEST_EXCEL_INTER",
      "id_programme": "PROG_EXCEL_INTER",
      "date_reponse": "2026-03-18 14:30:22"
    }
  ]
}
```

---

## 📝 Questionnaire intégré

### Fonctionnement (2 étapes)

**Étape 1 — Profil**
- Saisie du nom / prénom
- Choix du programme (Excel 365, Word 365…)
- Sélection du **niveau de départ** (Novice / Débutant / Intermédiaire)

**Étape 2 — Évaluation**
- Compétences regroupées par **domaine TOSA** (accordéon D1→D4)
- Pour chaque compétence : **Maîtrise actuelle** (Aucune / Moyenne / Acquise) + **Souhait de formation** (Oui / Non)
- **Valeurs par défaut** : Aucune + Oui
- **Automatisation** : si Aucune/Moyenne → Besoin=Oui automatique ; si Acquise → Besoin=Non automatique

### Niveau → Compétences affichées

| Niveau choisi | `id_questionnaire` soumis | Compétences affichées | Nb questions |
|:---:|:---|:---:|:---:|
| Novice | `QUEST_EXCEL_INIT` | Aucune (questionnaire non applicable) | 0 |
| Débutant | `QUEST_EXCEL_INTER` | N1 + N2 | 36 |
| Intermédiaire | `QUEST_EXCEL_PERF` | N1 + N2 + N3 | 52 |

### Accès direct

```
http://localhost:5000/questionnaire/QUEST_EXCEL
http://localhost:5000/questionnaire/QUEST_WORD
```

---

## 🧠 Moteur d'analyse des besoins

Le fichier `data/analyse_besoins.py` est le **cœur métier** de l'application.

### Règles métier

| Acquisition | Besoin | → Résultat | Impact |
|:-----------:|:------:|:----------:|--------|
| `Aucun` | `Oui` | **Besoin fort** | Thème complet : 100% des heures |
| `Aucun` | *(vide)* | **Besoin fort** | Idem |
| `Moyen` | `Oui` | **Besoin moyen** | Thème complet : 100% des heures |
| `Moyen` | *(vide)* | **Besoin moyen** | Idem |
| `Acquis` | `Oui` | **À revoir** | Thème réduit : 50% des heures |
| *(tout)* | `Non` | **Ignoré** | Pas de formation |
| *(vide)* | *(vide)* | **Ignoré** | Pas de formation |

### Profils spéciaux

| Profil | Comportement |
|:---|:---|
| **Novice** | Tous les thèmes du Bloc B1 inclus automatiquement (besoin fort) |
| **Intermédiaire sans besoin** | Orientation automatique vers certification experte |

---

## 🖥 Fonctionnalités de l'application

### Dashboard (`/`)
- Statistiques globales : total candidats, programmes générés, besoins forts/moyens
- Liste des 5 derniers candidats avec actions rapides

### Questionnaire intégré (`/questionnaire/<id>`)
- Layout deux colonnes : sidebar navy fixe + zone de contenu crème
- 3 cartes de niveau avec animation hover (translateY + barre or)
- Accordéons domaines TOSA (D1→D4) avec filtrage par niveau
- Radio pills segmentés : navy pour maîtrise, or pour besoin de formation

### Import candidat (`/candidats/import`)
- Upload du CSV Moodle ou Excel (`.xlsx`) rempli par le candidat
- Détection automatique du programme depuis le fichier
- Génération immédiate et automatique de l'analyse et du programme personnalisé

### Liste des candidats (`/candidats`)
- Tableau avec badges statut colorés
- Pagination (20 par page)

### Fiche candidat (`/candidats/<id>`)
- Statistiques personnelles (besoins forts, moyens, à revoir)
- Programme personnalisé (thèmes, durées, estimation financière)
- Déroulé pédagogique (séances, horaires, activités)
- Actions : générer/régénérer le programme, exporter PDF ou Excel

---

## 📌 API REST

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/candidats` | GET | Liste des candidats (index) |
| `/api/candidats/<id>` | GET | Détail d'un candidat + réponses |
| `/api/programmes` | GET | Liste des programmes disponibles |
| `/api/questionnaires` | GET | Liste des questionnaires (résumé) |

---

## 🎨 Design System

### Palette

| Token | Valeur | Usage |
|-------|--------|-------|
| `--navy` | `#0f1f3d` | Navbar, sidebar, boutons primaires |
| `--navy-mid` | `#1a3361` | Badges, accents |
| `--gold` | `#c9a84c` | Accents, CTA, pills sélectionnés |
| `--cream` | `#f7f5f0` | Fond de page |
| `--white` | `#ffffff` | Cartes, contenu |

### Typographie

- **Corps** : `DM Sans` (Google Fonts) — lisibilité premium
- **Titres** : `DM Sans` weight 800, letter-spacing négatif

### Composants

- **Navbar** : fond navy, liens dorés au survol
- **Accordéons** : badge domaine navy 3 lettres, chevron animé, gradient subtil à l'ouverture
- **Radio pills** : segmented control style (navy = maîtrise, or = besoin)
- **Boutons** : capsule radius 50px, hover translateY(-1px) + shadow
- **Sidebar questionnaire** : gradient navy, étapes avec cercles or

---

## 📚 Programmes supportés

### Excel (TOSA)

| ID | Programme | Niveau | Domaines |
|----|-----------|:------:|:--------:|
| `PROG_EXCEL_INIT` | Excel — Initiation | N1 | D1→D4 |
| `PROG_EXCEL_INTER` | Excel — Intermédiaire | N2 | D1→D4 |
| `PROG_EXCEL_PERF` | Excel — Perfectionnement | N3 | D1→D4 |

### Référentiel TOSA Excel (compétences par domaine)

| ID | Domaine | N1 (Initiation) | N2 (Inter.) | N3 (Perf.) |
|----|---------|:---:|:---:|:---:|
| D1 | Environnement / Méthodes | 8 | 4 | 4 |
| D2 | Calculs & Formules | 3 | 2 | 3 |
| D3 | Mise en forme | 5 | 3 | 2 |
| D4 | Gestion des données | 5 | 6 | 7 |
| **Total** | | **21** | **15** | **16** |

### Word (TOSA)

| ID | Programme |
|----|-----------|
| `PROG_WORD` | Word — Rédaction et mise en forme professionnelle (Tosa) |

---

## 🔧 Scripts utilitaires

### `scripts/update_programmes.py`

Synchronise les `competences_tosa` dans `01_programmes.json` à partir des `id_question` de `00_questions.json`.

```bash
python scripts/update_programmes.py
```

> ⚠️ Crée un backup `01_programmes.json.bak` avant modification.

---

## 🔨 Contribuer / Évolution

### Ajouter un nouveau programme (ex: PowerPoint)

1. **`01_programmes.json`** : ajouter le programme avec ses thèmes (`PT1`, `PT2`...)
2. **`00_questions.json`** : ajouter un questionnaire `QUEST_POWERPOINT_INIT`, `QUEST_POWERPOINT_INTER`... avec des questions au format `[DX-NX-CX]`
3. **`04_referentiel_ppt.json`** *(optionnel)* : créer le référentiel TOSA correspondant
4. **C'est tout !** Le moteur d'analyse est générique.

### Fichiers clés à modifier

| Besoin | Fichier |
|--------|---------|
| Ajouter des questions | `data/bd/00_questions.json` |
| Synchroniser les programmes | `scripts/update_programmes.py` |
| Modifier un programme | `data/bd/01_programmes.json` |
| Modifier le référentiel TOSA | `data/bd/04_referentiel_excel_origine.json` |
| Changer les règles métier | `data/analyse_besoins.py` → `analyser_reponse()` |
| Modifier le design | `static/css/style.css` |
| Modifier le questionnaire | `templates/candidat/formulaire.html` |
| Modifier le look PDF | `static/css/pdf.css` + `templates/pdf/programme.html` |

### Changelog

| Version | Date | Changements |
|:---:|:---:|:---|
| 3.1.1 | 20 Mars 2026 | Génération automatique du programme dès l'import du fichier candidat · Ajout dynamique de la version dans le pied de page |
| 3.1 | Mars 2026 | Fusion 3 questionnaires Excel côté serveur · Extraction `id_niveau` par regex · Correction bug étape 2 vide · Export Excel (openpyxl) |
| 3.0 | Mars 2026 | Questionnaire intégré · Design premium Navy/Crème/Or · Layout 2 colonnes · Radio pills segmentés |
| 2.x | Fév. 2026 | Architecture JSON · Import CSV Moodle · Moteur d'analyse besoins |

---

*eS@deq — Plateforme de Positionnement © 2026*
