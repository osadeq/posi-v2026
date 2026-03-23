# ═══════════════════════════════════════════════════════════════
# SPÉCIFICATION DU FORMAT CSV D'IMPORT — v2
# eS@deq - Plateforme de Positionnement
# Version : 2.0 — Février 2026
# ═══════════════════════════════════════════════════════════════

## 1. CONTEXTE

Le CSV est le format d'échange entre Moodle (plateforme de test)
et eS@deq (plateforme de positionnement).

Moodle est une "boîte noire" : il gère le test, recueille les 
réponses et exporte un CSV. eS@deq importe ce CSV pour analyser 
les besoins et générer le programme personnalisé.

## 2. ARCHITECTURE v2 — Alignement Questions ↔ Programme

### Principe fondamental
Les questions sont **alignées directement sur les thèmes du programme**.
L'ID de la question **porte le thème** : `TX_QNN` → thème `TX`.

### Conséquences
- **Plus de fichier de mapping** (02_mapping.json supprimé)
- Le mapping question→thème est **implicite**
- Le mapping questionnaire→programme est dans 00_questions.json
- Les réponses sont stockées **par candidat** (pas dans 03_candidats.json)

## 3. FORMAT DU CSV

### Encodage : UTF-8
### Séparateur : point-virgule (;) — la virgule (,) est aussi acceptée
### Entête obligatoire (ligne 1)

### Colonnes :

| Colonne            | Obligatoire | Valeurs possibles                    | Description                                       |
|--------------------|-------------|--------------------------------------|-------------------------------------------------|
| id_questionnaire   | OUI         | QUEST_WORD, QUEST_EXCEL, ...         | Identifie le questionnaire → déduit le programme  |
| id_question        | OUI         | T1_Q01, T2_Q03, ET1_Q02, ...        | ID unique = Thème + Question                      |
| acquisition        | NON*        | Aucun, Moyen, Acquis                 | Niveau d'acquisition auto-évalué par le candidat  |
| besoin             | NON*        | Oui, Non                             | Le candidat souhaite-t-il une formation ?          |

*Note : Un champ vide est autorisé (= absence de réponse).

### Convention de nommage des questions :

| Préfixe    | Thème du programme         | Exemple          |
|------------|----------------------------|------------------|
| T1_Q01     | Prise en main Word         | T1_Q01 à T1_Q10  |
| T2_Q01     | Mise en forme Word         | T2_Q01 à T2_Q07  |
| ET1_Q01    | Environnement Excel        | ET1_Q01 à ET1_Q04 |
| ET2_Q01    | Fonctions Excel            | ET2_Q01 à ET2_Q04 |

### Règles métier appliquées à l'import :

| acquisition | besoin    | Résultat          |
|-------------|-----------|-------------------|
| Aucun       | Oui       | **Besoin fort**   |
| Aucun       | (vide)    | **Besoin fort**   |
| Moyen       | Oui       | **Besoin moyen**  |
| Moyen       | (vide)    | **Besoin moyen**  |
| Acquis      | Oui       | **À revoir**      |
| (toute)     | Non       | **Ignoré**        |
| (vide)      | Non       | **Ignoré**        |
| (vide)      | (vide)    | **Ignoré**        |

## 4. EXEMPLE COMPLET

```csv
id_questionnaire;id_question;acquisition;besoin
QUEST_WORD;T1_Q01;Acquis;Non
QUEST_WORD;T1_Q02;Acquis;Non
QUEST_WORD;T2_Q03;Moyen;Oui
QUEST_WORD;T5_Q01;Aucun;Oui
QUEST_WORD;T9_Q03;;Non
```

## 5. CORRESPONDANCE MOODLE

### Structure recommandée dans Moodle :

Pour chaque compétence, créer UNE question Moodle (approche compacte) :

**Question** (choix multiple, 1 seule réponse) :
- Intitulé : "[T1_Q01] Manipuler la fenêtre Word"
- Choix :
  1. Non acquis — J'ai besoin de formation        → acquisition=Aucun, besoin=Oui
  2. Moyennement acquis — J'ai besoin de formation → acquisition=Moyen, besoin=Oui
  3. Acquis — Je souhaite revoir                   → acquisition=Acquis, besoin=Oui
  4. Acquis — Pas de besoin                        → acquisition=Acquis, besoin=Non
  5. Non concerné                                  → acquisition=, besoin=Non

### Nommage Moodle recommandé :
Noms courts des questions = IDs de notre système : T1_Q01, T2_Q03, etc.
Cela permet un export/conversion Moodle→CSV automatique.

## 6. FLUX DE DONNÉES

```
[Moodle]                    [eS@deq]
   │                           │
   │  Export CSV (par candidat) │
   ├──────────────────────────►│
   │                           │ 1. Lecture du CSV
   │                           │ 2. Extraction de id_questionnaire
   │                           │ 3. Déduction du programme (QUEST_WORD → PROG_WORD)
   │                           │ 4. Extraction du thème depuis l'ID (T5_Q01 → T5)
   │                           │ 5. Sauvegarde dans :
   │                           │    data/candidats/{id}/questionnaire.json
   │                           │ 6. Analyse des besoins par thème
   │                           │ 7. Génération du programme :
   │                           │    data/candidats/{id}/programme_perso.json
   │                           │ 8. Export PDF
```

## 7. FICHIERS DE L'APPLICATION

### data/bd/ — Modèles (en lecture seule)
- `00_questions.json` — Questionnaires avec questions alignées par thème
  - Contient aussi le mapping questionnaire → programme (id_programme)
- `01_programmes.json` — Programmes de formation avec thèmes et items
- `03_candidats.json` — Index des candidats (métadonnées, PAS de réponses)

### data/candidats/{id_candidat}/ — Données par candidat
- `questionnaire.json` — Réponses du candidat (converti du CSV)
- `questionnaire.csv` — Fichier CSV source (archivé)
- `programme_perso.json` — Programme personnalisé généré

### Supprimé
- ~~02_mapping.json~~ — Le mapping est désormais implicite via les IDs
