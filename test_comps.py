import sys
sys.path.append('C:/Users/sadeq/Desktop/posi-2026-v3/')
from data.analyse_besoins import creer_programme_personnalise

for cand_id, prog_name in [
    ('CAND_O_b_20260319_203318', 'PROG_EXCEL_INIT'), 
    ('CAND_O_s_20260319_202900', 'PROG_EXCEL_INTER')
]:
    prog_perso = creer_programme_personnalise(cand_id, prog_name)
    if not prog_perso:
        continue
    print(f"\n--- Candidate {cand_id} Program: {prog_name} ---")
    for t in prog_perso.get('themes_a_former', []):
        print(f"Theme: {t['nom']} - hours: {t['duree_estimee']}, items: {len(t.get('contenu_programme', []))}")
