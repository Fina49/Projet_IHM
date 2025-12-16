# main_dash.py
"""
Point d'entrée de l'application Dash.

Ce fichier se contente de récupérer l'instance `app`
définie dans app.py et de lancer le serveur.
"""

from app import app  # app = dash.Dash(...) défini dans app.py


if __name__ == "__main__":
    # debug=True pour le développement ; en prod tu mettras False
    app.run(debug=True)
