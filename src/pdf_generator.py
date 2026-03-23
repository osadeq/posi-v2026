# -*- coding: utf-8 -*-
"""
Generateur de PDF - Programme de formation personnalise
"""
import os

# Check if WeasyPrint is available
WEASYPRINT_AVAILABLE = False

def _check_weasyprint():
    """Lazy check for WeasyPrint availability"""
    global WEASYPRINT_AVAILABLE
    if WEASYPRINT_AVAILABLE:
        return True
    try:
        from weasyprint import HTML
        WEASYPRINT_AVAILABLE = True
        return True
    except ImportError:
        return False


from datetime import datetime
from flask import render_template

def generer_pdf_programme(programme, candidat, output_path=None):
    """Génère le PDF du programme de formation en utilisant un template Jinja2"""

    if not _check_weasyprint():
        raise RuntimeError("WeasyPrint n'est pas disponible. Installez GTK3 pour activer la génération PDF.")

    from weasyprint import HTML

    # Préparation du contexte pour le template
    # On s'assure que candidat est un dictionnaire
    if candidat is None:
        candidat = {}

    # Rendu du HTML via le template Flask
    html_content = render_template(
        'pdf/programme.html',
        programme=programme,
        candidat=candidat,
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    # Conversion HTML vers PDF avec WeasyPrint
    # Note: On specifie explicitement l'encodage UTF-8 pour eviter les problemes
    html = HTML(string=html_content, encoding='UTF-8')
    pdf_bytes = html.write_pdf()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes


def is_pdf_available():
    """Verifie si la generation PDF est disponible"""
    return _check_weasyprint()
