import json
import os
from collections import defaultdict

def update_programmes_from_questions():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    questions_file = os.path.join(base_dir, 'data', 'bd', '00_questions.json')
    programmes_file = os.path.join(base_dir, 'data', 'bd', '01_programmes.json')

    # Backup programmes
    import shutil
    shutil.copyfile(programmes_file, programmes_file + '.bak')

    print(f"Loading questions from {questions_file}")
    with open(questions_file, 'r', encoding='utf-8') as f:
        quest_data = json.load(f)

    # Build mapping theme -> competences (id_question)
    theme_to_competences = defaultdict(list)
    for q_group in quest_data.get('questionnaires', []):
        for q in q_group.get('questions', []):
            theme_id = q.get('id_theme')
            q_id = q.get('id_question')
            if theme_id and q_id:
                theme_to_competences[theme_id].append(q_id)

    print(f"Found {len(theme_to_competences)} themes with competences.")

    print(f"Loading programmes from {programmes_file}")
    with open(programmes_file, 'r', encoding='utf-8') as f:
        prog_data = json.load(f)

    updated_themes = 0
    cleared_themes = 0

    for prog in prog_data.get('programmes', []):
        prog_id = prog.get('id_programme', '')
        # Only update Excel programs for now, since those were changed
        if not prog_id.startswith('PROG_EXCEL'):
            continue
            
        print(f"Updating programme {prog_id}...")
        for theme in prog.get('themes', []):
            t_id = theme.get('id_theme')
            if t_id in theme_to_competences:
                theme['competences_tosa'] = theme_to_competences[t_id]
                updated_themes += 1
            else:
                # If theme is no longer present in questions, should we clear it?
                # The user says questions map directly to programmes.
                # If a theme has no questions, it might mean it's evaluated elsewhere or removed.
                theme['competences_tosa'] = []
                cleared_themes += 1

    with open(programmes_file, 'w', encoding='utf-8') as f:
        json.dump(prog_data, f, indent=4, ensure_ascii=False)

    print(f"Successfully updated {updated_themes} themes. Cleared {cleared_themes} themes.")
    print("Programmes updated successfully.")

if __name__ == '__main__':
    update_programmes_from_questions()
