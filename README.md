# Find Your Creator — Projet IHM (Dash)

Application web réalisée avec **Dash** (Plotly) et **Dash Bootstrap Components**.

Le projet **Find Your Creator** permet d’**explorer**, **rechercher**, et **analyser** des créateurs de contenu (TikTok / YouTube) via un petit tableau de bord interactif : KPIs, filtres, cartes, profils détaillés, top vidéos, analytics.

## Fonctionnalités

- **Navigation multi-pages** (Dash Pages)
  - Accueil : KPIs + carte monde + filtres
  - Recherche : filtres multi-critères + tri + pagination
  - Découverte : tendances / nouveautés (selon les données simulées)
  - Profil créateur : KPIs, évolution, top vidéos, analytique avancée
  - Favoris : gestion d’une liste persistée côté navigateur
  - Contact : page de contact
- **Authentification simulée (UI)**
  - Modale Login / Signup / Profil
  - Persistance locale de l’état utilisateur (localStorage)
- **Favoris**
  - Stockage local via `dcc.Store(..., storage_type="local")`
  - Ajout/retrait depuis les pages (ex: profil)
- **Visualisations Plotly**
  - Graphiques et compos composants analytiques (dans `functions.py`)

## Stack

- Python
- Dash (`dash`)
- Dash Bootstrap Components (`dash-bootstrap-components`)
- Plotly (`plotly`)
- Pandas / NumPy

Dépendances exactes : voir `requirements.txt`.

## Prérequis

- Python 3.10+ recommandé
- macOS / Linux / Windows.

## Installation

### macOS / Linux (bash, zsh)

```zsh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (Invite de commandes / cmd)

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Lancement

*(Pensez à activer l’environnement virtuel avant de lancer.)*

Le point d’entrée est :
- `main_dash.py` : lance simplement le serveur en important `app`

### Lancer `main_dash.py`

```zsh
python main_dash.py
```

Ensuite ouvrez : http://127.0.0.1:8050

## Structure du projet

```
Projet_IHM/
├─ app.py                 # Instance Dash + layout global (navbar/footer/pages/stores)
├─ main_dash.py           # Entry-point minimal (importe app et lance)
├─ auth.py                # Modale + logique d’authentification simulée (callbacks)
├─ constants.py           # Données simulées (créateurs, stats pays, top vidéos…)
├─ functions.py           # UI réutilisable, DataManager, AnalyticsEngine…
├─ requirements.txt       # Dépendances
├─ assets/
│  ├─ styles.css          # Styles globaux
│  └─ scroll_to_top.js    # JS côté client (UI)
└─ pages/
   ├─ home.py             # Accueil (dashboard)
   ├─ search.py           # Recherche
   ├─ discover.py         # Découverte
   ├─ favorites.py        # Favoris
   ├─ profile.py          # Profil créateur
   └─ contact.py          # Contact
```

## Données et “backend”

Le projet fonctionne **sans base de données** ni API externe.

- Les données sont **simulées** dans `constants.py` :
  - `ALL_CREATORS` (créateurs + stats + historique)
  - `COUNTRY_STATS` (stats par pays pour la carte)
  - `TOP_VIDEOS` / `TRENDING_*` / `NEW_*` …

Cela rend l’app **autonome** et simple à exécuter, au prix d’un dataset statique.

## Authentification (fonctionnement)

L’authentification est une **simulation** côté UI :

- La modale est définie dans `auth.py` (`auth_modal`)
- L’état utilisateur est persisté dans `dcc.Store(id="auth-user-store", storage_type="local")`
- Le store contient (ex.) :

```text
{ is_logged_in: bool, firstname: str, lastname: str, email: str }
```

- Certaines fonctionnalités (ex: marquage des favoris) sont conditionnées à l’état connecté.

## Favoris (fonctionnement)

- Persistés dans le navigateur : `dcc.Store(id="favorites-ids-store", storage_type="local")`
- Initialisés depuis `constants.py` :
  - `initial_fav_ids = [c["id"] for c in ALL_CREATORS if c.get("is_favorite")]`
- Utilisés pour afficher les badges “Favori” et permettre l’ajout/retrait.

## Personnalisation

### Modifier/ajouter des créateurs

Tout est centralisé dans `constants.py` → `ALL_CREATORS`.

Champs importants :

- `id`, `name`, `username`, `avatar`, `bio`
- `country`, `language`, `region`, `tags`
- `platforms` (TikTok/YouTube) avec `followers`, `views`, `likes`, …
- `history` (par mois) pour alimenter les graphs

### Styles

- CSS : `assets/styles.css`
- JS : `assets/scroll_to_top.js`

Dash charge automatiquement le dossier `assets/`.

## Dépannage

- **La page est blanche / callbacks non trouvés**
  - Vérifier que vous lancez bien `python main_dash.py` depuis la racine.
  - Vérifier que les dépendances sont installées dans le bon environnement.

- **ImportError / ModuleNotFoundError**
  - Relancer l’installation : `pip install -r requirements.txt`

- **Le style ne s’applique pas**
  - Vérifier la présence de `assets/styles.css`.
  - Forcer un refresh (cache navigateur).

## Notes pédagogiques

- Projet orienté **IHM** : accent sur la navigation, les filtres, l’UX, et les dashboards.
- Le “backend” est simulé car non demandé dans le cadre du projet.

## Auteurs

- BEYELER Elie
- DESCHAMPS Kylian
- ERAMIL Kadir


## MESSAGE POUR MR PELLIER : ## 
Nous avons mis à jour notre sujet de tp car nous avions eu un problème avec le jour de la présentation, il se trouve dans le dossier TP