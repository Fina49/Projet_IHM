"""
Module de fonctions utilitaires et de logique métier.

Ce module contient :
1. Des fonctions de formatage et d'aide UI (Helpers).
2. Des composants Dash réutilisables (Cartes Créateurs, Vidéos, KPIs).
3. AnalyticsEngine : Classe gérant la création des graphiques Plotly.
4. DataManager : Classe gérant le filtrage, le tri et l'agrégation des données.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np
import pandas as pd

from constants import ALL_CREATORS, COUNTRY_STATS, TOP_VIDEOS

# ==============================================================================
# 1. HELPERS FORMATAGE & UI
# ==============================================================================

def short_number(n):
    """
    Formate un grand nombre en format court (ex: 1.5M, 10K).
    """
    if n is None: 
        return "0"
    try: 
        n = float(n)
    except (ValueError, TypeError): 
        return str(n)
    
    if n >= 1_000_000: 
        val = f"{n/1_000_000:.1f}"
        return (val[:-2] if val.endswith(".0") else val) + "M"
    if n >= 1_000: 
        val = f"{n/1_000:.1f}"
        return (val[:-2] if val.endswith(".0") else val) + "K"
    return str(int(n))

def get_creator_by_id(cid):
    """Récupère un objet créateur complet via son ID."""
    # Conversion en string pour comparaison robuste
    return next((c for c in ALL_CREATORS if str(c["id"]) == str(cid)), None)

def get_platform_stats(creator, platform_filter):
    """
    Agrège les statistiques (vues, likes, etc.) selon le filtre de plateforme.
    
    Args:
        creator (dict): Données du créateur.
        platform_filter (str): "combined", "both" ou nom spécifique (ex: "TikTok").
    """
    totals = {"followers": 0, "views": 0, "likes": 0, "videos": 0, "comments": 0, "shares": 0}
    platforms_to_sum = []
    available = creator.get("platforms", {})
    
    if platform_filter in ["combined", "both"]:
        platforms_to_sum = available.values()
    elif platform_filter in available:
        platforms_to_sum = [available[platform_filter]]
        
    for p_data in platforms_to_sum:
        for k in totals.keys():
            totals[k] += int(p_data.get(k, 0))
    return totals

def render_kpi_card(label, value, icon=None, color="text-dark"):
    """
    Rendu standardisé d'une carte KPI (Label + Valeur).
    Utilisé dans Home et Profile.
    """
    return dbc.Card(
        dbc.CardBody([
            html.Div(label, className="text-muted small"),
            html.H3(str(value), className="fw-bold")
        ])
    )

def make_stat_span(metric_key, value):
    """Génère un span avec icône et valeur formatée."""
    METRIC_ICONS = {"followers": "👥", "views": "👁️", "likes": "👍", "shares": "↪", "videos": "🎬"}
    icon = METRIC_ICONS.get(metric_key, "")
    return html.Span(f"{icon} {short_number(value)}", className="me-3")

def creator_avatar(c, size_class="creator-avatar"):
    """
    Affiche l'avatar (image) ou une initiale si pas d'image.
    """
    if c.get("avatar"): 
        return html.Img(src=c["avatar"], className=size_class)
    return html.Div(c["name"][0].upper(), className="favorite-avatar-initial")

def platform_block(name, stats, mode="search"):
    """
    Affiche un bloc de statistiques pour une plateforme donnée (dans la carte recherche).
    """
    metrics = ["followers", "views", "likes", "shares", "videos"]

    # En-tête de la plateforme (nom + statut)
    header_children = [
        html.Span(name, className="favorite-platform-pill"),
        html.Span(
            "Actif" if stats.get("active") == "oui" else "Inactif",
            className="creator-status-pill ms-2",
        ),
    ]
    return html.Div(
        className="search-platform-block",
        children=[
            html.Div(header_children, className="mb-1"),
            html.Div(
                className="favorite-meta-row",
                children=[
                    make_stat_span(m, stats.get(m, 0))
                    for m in metrics
                    if m in stats
                ],
            ),
        ],
    )


# ==============================================================================
# 2. COMPOSANTS UI (CARTES)
# ==============================================================================

def render_creator_card_search(c, is_favorite=False, mode="search"):
    """
    Génère la grande carte créateur utilisée dans la Recherche et l'en-tête de Profil.
    """
    totals = c.get("totals", {})
    global_metrics = ["followers", "views", "likes", "shares", "videos"]

    # --- Gestion des Badges ---
    badges = []
    
    # Badge Certifié
    is_certified = any(p.get("certified") == "oui" for p in c.get("platforms", {}).values())
    if is_certified:
        badges.append(html.Span([html.I(className="bi bi-patch-check-fill me-1"), "Certifié"], className="badge bg-primary text-white me-1"))

    # Badges New / Tendance / Favori
    if c.get("is_new"): 
        badges.append(html.Span("🆕 New", className="badge bg-info text-dark me-1"))
    if c.get("is_trending"): 
        badges.append(html.Span("🔥 Tendance", className="badge bg-warning text-dark me-1"))
    if is_favorite:
        badges.append(html.Span("❤️ Favori", className="badge bg-danger text-white ms-1"))

    # --- Contenu de la carte ---
    card_content = dbc.Row(
        className="g-3", 
        align="center", 
        children=[
            dbc.Col(width="auto", children=creator_avatar(c)),
            dbc.Col(
                md=5, 
                children=[
                    html.Div(c["name"], className="favorite-name"),
                    html.Div(c["username"], className="favorite-username"),
                    html.Div(
                        className="favorite-meta-row", 
                        children=[
                            html.Span(f"🌍 {c.get('country')}", className="me-3"),
                            html.Span(f"💬 {c.get('language')}")
                        ]
                    ),
                    html.Div(
                        className="favorite-meta-row mt-2", 
                        children=[make_stat_span(m, totals.get(m, 0)) for m in global_metrics]
                    ),
                    html.Div(
                        className="creator-tags mt-2", 
                        children=[html.Span(t, className="creator-tag-pill") for t in c.get("tags", [])]
                    ),
                    html.Div(className="mt-2", children=badges)
                ]
            ),
            # Colonne droite : Détails par plateforme
            dbc.Col(
                md=5, 
                children=[
                    platform_block(k, v, mode=mode) for k, v in c.get("platforms", {}).items()
                ]
            )
        ]
    )

    # --- Variante : Mode PROFIL (avec bouton d'action) ---
    if mode == "profile":
        if is_favorite:
            btn_label = "Retirer des favoris"
            btn_icon = "bi bi-heart-fill text-danger"
        else:
            btn_label = "Ajouter aux favoris"
            btn_icon = "bi bi-heart"
        
        # Styles extraits dans .profile-fav-action-btn
        return html.Div(
            className="search-card mb-4 position-relative profile-header-wrapper",
            children=[
                card_content,
                html.Button(
                    children=[html.I(className=f"{btn_icon} me-2"), btn_label],
                    id={"type": "profile-fav-btn", "id": c['id']},
                    className="btn btn-light border shadow-sm profile-fav-action-btn"
                )
            ]
        )

    # --- Variante : Mode RECHERCHE (Lien global) ---
    return dcc.Link(
        href=f"/profile/{c['id']}",
        className="text-decoration-none text-inherit",
        children=html.Div(className="search-card mb-4", children=card_content)
    )

def render_creator_card_compact(c, is_favorite=False):
    """
    Génère la carte compacte (Découverte / Favoris).
    """
    totals = c.get("totals", {})
    compact_metrics = ["followers", "views", "likes"] 
    
    badges = []
    if c.get("is_new"): badges.append(html.Span("🆕 New", className="badge bg-info text-dark me-1"))
    if c.get("is_trending"): badges.append(html.Span("🔥 Tendance", className="badge bg-warning text-dark me-1"))
    if is_favorite: badges.append(html.Span("❤️ Favori", className="badge bg-danger text-white ms-1"))

    # Gestion Avatar (Image vs Initiale) via classes CSS
    if c.get("avatar"):
        avatar_comp = html.Img(src=c["avatar"], className="creator-avatar compact-avatar-img") 
    else:
        avatar_comp = html.Div(c["name"][0].upper(), className="favorite-avatar-initial compact-avatar-initial")

    return dcc.Link(
        href=f"/profile/{c['id']}",
        className="text-decoration-none text-inherit",
        children=dbc.Card(
            className="mb-3 border shadow-sm hover-shadow h-100", 
            children=[
                dbc.CardBody(children=[
                    dbc.Row(align="center", children=[
                        dbc.Col(width="auto", children=[avatar_comp]),
                        dbc.Col(children=[
                            html.Div(c["name"], className="fw-bold text-dark"),
                            html.Div(c["username"], className="text-muted small mb-1"),
                            
                            html.Div(
                                className="d-flex align-items-center mb-2 text-muted small", 
                                children=[
                                    html.Span(f"🌍 {c.get('country')}", className="me-3"),
                                    html.Span(f"💬 {c.get('language')}") 
                                ]
                            ),
                            
                            html.Div(
                                className="d-flex align-items-center", 
                                children=[make_stat_span(m, totals.get(m, 0)) for m in compact_metrics]
                            ),
                            html.Div(className="mt-1", children=badges)
                        ])
                    ])
                ])
            ]
        )
    )

def render_topic_card(topic):
    """Carte simple pour afficher un Tag ou Hashtag."""
    return html.Div(
        className="topic-card", 
        children=[
            html.Div(
                className="topic-title-row", 
                children=[
                    html.Span(f"#{topic['rank']}", className="topic-rank"),
                    html.Span(topic["name"], className="topic-title"),
                ]
            ),
            html.Div(f"{topic['creators']} créateurs", className="topic-subtitle"),
            html.Div(topic["growth"], className="topic-growth-pill"),
        ]
    )

def render_video_card(video):
    """Carte vidéo avec miniature (Découverte)."""
    if video.get("thumbnail"):
        thumb = html.Img(src=video.get("thumbnail"), className="img-fluid rounded-top video-card-thumb")
    else:
        thumb = html.Div("🎬", className="d-flex align-items-center justify-content-center bg-light rounded-top video-card-fallback")
    
    return dbc.Card(
        className="h-100 shadow-sm border-0 hover-shadow", 
        children=[
            thumb,
            dbc.CardBody([
                html.H6(video.get("title"), className="fw-bold text-truncate mb-2", title=video.get("title")),
                html.Div([
                    dbc.Badge(
                        video.get("platform"), 
                        color="danger" if video.get("platform")=="YouTube" else "dark", 
                        className="me-2"
                    ),
                    html.Small(f"{short_number(video.get('views'))} vues", className="text-muted")
                ], className="d-flex align-items-center mb-2"),
                html.Div([
                    html.Span(
                        [html.I(className="bi bi-person-circle me-1"), video.get("creator")], 
                        className="text-truncate me-auto", 
                        style={"maxWidth": "70%"} # Style structurel conservé
                    ),
                    html.Span(video.get("duration"), className="badge bg-light text-dark border")
                ], className="d-flex align-items-center small text-muted")
            ])
        ]
    )

def render_top_video_card(video, rank):
    """Carte ligne pour les Top Vidéos (Profil)."""
    thumb = html.Img(src=video.get("thumbnail"), className="top-video-thumb") if video.get("thumbnail") else html.Div("🎬", className="top-video-thumb")
    stats = [("👁", video.get('views')), ("👍", video.get('likes')), ("↪", video.get('shares')), ("💬", video.get('comments'))]
    
    return html.Div(
        className="top-video-card", 
        children=[
            html.Div(f"#{rank}", className="top-video-rank"),
            thumb,
            html.Div(
                className="top-video-info", 
                children=[
                    html.Div([
                        html.Span(video.get("title"), className="top-video-title"), 
                        dbc.Badge(
                            video.get("platform"), 
                            color="danger" if video.get("platform")=="YouTube" else "dark", 
                            className="ms-2"
                        )
                    ]),
                    html.Div(
                        className="top-video-stats", 
                        children=[html.Span(f"{icon} {short_number(val)}") for icon, val in stats if val is not None]
                    )
                ]
            )
        ]
    )

# ==============================================================================
# 3. MOTEUR ANALYTIQUE
# ==============================================================================

class AnalyticsEngine:
    """
    Gère la création des graphiques Plotly pour la page Profil.
    Supporte les modes : Valeurs brutes, Progression %, et Ratios.
    """
    def __init__(self):
        self.labels = {
            "views": "Vues", "likes": "Likes", "shares": "Partages", 
            "comments": "Commentaires", "followers": "Abonnés", "videos": "Vidéos"
        }
        self.metric_colors = {
            "views": "#0d6efd", "likes": "#dc3545", "shares": "#198754", 
            "comments": "#ffc107", "followers": "#6f42c1", "videos": "#fd7e14"
        }

    def build_figure(self, creator, mode, x_axis, y_metrics, num, den, platform, advanced, compare_mode=None):
        """Construit l'objet go.Figure complet."""
        fig = go.Figure()
        advanced = advanced or []
        y_metrics = y_metrics or ["views"]
        
        # 1. Groupe de référence (Comparaison)
        ref_group_type = None
        ref_value = None
        if compare_mode == "country":
            ref_group_type = "country"
            ref_value = creator.get("country")
        elif compare_mode == "tag":
            ref_group_type = "tag"
            tags = creator.get("tags", [])
            ref_value = tags[0] if tags else None
        
        # 2. Données Créateur
        target_platforms = []
        if platform == "combined":
            self._process_combined_view(fig, creator, mode, x_axis, y_metrics, num, den, advanced, ref_group_type, ref_value)
        else:
            if platform == "both": 
                target_platforms = ["youtube", "tiktok"]
            else: 
                target_platforms = [platform.lower()]

            for p_name in target_platforms:
                # Trace principale
                history = creator.get("history", {}).get(p_name, [])
                if not history: continue
                
                label_prefix = p_name.capitalize()
                dash_style = "dash" if (platform == "both" and p_name == "tiktok") else "solid"
                
                self._add_traces_for_data(fig, history, label_prefix, mode, x_axis, y_metrics, num, den, advanced, dash_style)

                # Trace comparaison (si activée)
                if ref_group_type and ref_value:
                    avg_history = data_manager.get_average_history(ref_group_type, ref_value, p_name, y_metrics)
                    if avg_history:
                        avg_prefix = f"Moy. {ref_value} ({label_prefix})"
                        self._add_traces_for_data(fig, avg_history, avg_prefix, mode, x_axis, y_metrics, num, den, [], "dot", is_comparison=True)

        fig.update_layout(
            template="plotly_white", 
            margin=dict(l=20, r=20, t=30, b=20), 
            legend=dict(orientation="h", y=-0.2), 
            hovermode="x unified"
        )
        return fig

    def _process_combined_view(self, fig, creator, mode, x_axis, y_metrics, num, den, advanced, ref_group_type, ref_value):
        """Logique spécifique pour le mode Combiné (somme des plateformes)."""
        # Créateur combiné
        agg_history = self._aggregate_platforms(creator.get("history", {}), ["youtube", "tiktok"])
        self._add_traces_for_data(fig, agg_history, "Global", mode, x_axis, y_metrics, num, den, advanced, "solid")
        
        # Comparaison combinée
        if ref_group_type and ref_value:
            avg_history = data_manager.get_average_history(ref_group_type, ref_value, "combined", y_metrics)
            if avg_history:
                self._add_traces_for_data(fig, avg_history, f"Moy. {ref_value}", mode, x_axis, y_metrics, num, den, [], "dot", is_comparison=True)

    def _aggregate_platforms(self, history_dict, platforms):
        """Fusionne les historiques (somme) de plusieurs plateformes."""
        agg = []
        for i in range(12): # Simulation sur 12 mois
            row = {"month": f"M{i+1}"}
            for m in ["views", "likes", "shares", "comments", "followers", "videos"]:
                row[m] = 0
            
            for p in platforms:
                p_hist = history_dict.get(p, [])
                if i < len(p_hist):
                    for m in row.keys():
                        if m != "month":
                            row[m] += p_hist[i].get(m, 0)
            agg.append(row)
        return agg

    def _add_traces_for_data(self, fig, history, label_prefix, mode, x_axis, y_metrics, num, den, advanced, dash_style, is_comparison=False):
        """Ajoute les courbes au graphique selon le mode (Valeur, Ratio, Progression)."""
        months = [d["month"] for d in history]
        # x_vals = list(range(len(months))) # Si besoin d'index numérique

        # Mode RATIO
        if mode == "ratio" and num and den:
            y_vals = [(d.get(num,0)/d.get(den,1) if d.get(den,0)>0 else 0) for d in history]
            trace_name = f"{label_prefix} {self.labels.get(num,num)}/{self.labels.get(den,den)}"
            color = "#6c757d" if is_comparison else "#343a40"
            self._plot_line(fig, months, y_vals, trace_name, color, advanced, dash_style, is_comparison)
            return

        # Mode VALEURS ou PROGRESSION
        for m in y_metrics:
            raw_vals = [d.get(m, 0) for d in history]
            
            if mode == "progression":
                y_vals = [0]
                for i in range(1, len(raw_vals)):
                    prev = raw_vals[i-1]
                    curr = raw_vals[i]
                    pct = ((curr - prev) / prev * 100) if prev > 0 else 0
                    y_vals.append(pct)
                suffix = "(%)"
            else:
                y_vals = raw_vals
                suffix = ""
            
            lbl = self.labels.get(m, m)
            color = "#adb5bd" if is_comparison else self.metric_colors.get(m, "#000000")
            
            final_name = f"{label_prefix} {lbl} {suffix}"
            self._plot_line(fig, months, y_vals, final_name, color, advanced, dash_style, is_comparison)

    def _plot_line(self, fig, x_labels, y_vals, name, color, advanced, dash_style, is_comparison):
        """Helper bas niveau pour dessiner une ligne Plotly."""
        opacity = 0.6 if is_comparison else 1.0
        width = 2 if is_comparison else 3
        
        fig.add_trace(go.Scatter(
            x=x_labels, y=y_vals, mode='lines+markers', name=name,
            line=dict(shape='spline', smoothing=1.3, color=color, dash=dash_style, width=width),
            opacity=opacity,
            hovertemplate=f"<b>{name}</b><br>Val: %{{y:,.2f}}<extra></extra>"
        ))
        
        # Lignes de tendance (Régression linéaire) et Prévisions
        if not is_comparison and len(y_vals) > 1:
            X = np.arange(len(y_vals))
            try:
                slope, intercept = np.polyfit(X, y_vals, 1)
                
                if "reg" in advanced:
                    fig.add_trace(go.Scatter(
                        x=x_labels, y=slope*X+intercept, 
                        mode='lines', 
                        line=dict(dash='dot', width=1, color=color), 
                        name=f"Tend. {name}", showlegend=False, hoverinfo='skip'
                    ))
                
                if "forecast" in advanced:
                    next_months = [f"M{12 + k}" for k in range(1, 4)]
                    next_Y = slope * np.arange(len(y_vals), len(y_vals)+3) + intercept
                    fig.add_trace(go.Scatter(
                        x=next_months, y=next_Y, 
                        mode='lines+markers', 
                        line=dict(dash='dash', color=color), 
                        name=f"Prév. {name}", hovertemplate="%{y:,.2f}"
                    ))
            except Exception: 
                pass


# ==============================================================================
# 4. GESTIONNAIRE DE DONNÉES (DATA MANAGER)
# ==============================================================================

class DataManager:
    """
    Centralise l'accès et le filtrage des données de l'application.
    Simule une base de données en mémoire.
    """
    def __init__(self):
        self.creators = ALL_CREATORS

        # Préparation du DataFrame pour la carte du monde
        data_list = []
        for iso, stats in COUNTRY_STATS.items():
            row = {k: v for k, v in stats.items() if k not in ["platform_split", "theme_split"]}
            row["iso_alpha"] = iso
            data_list.append(row)

        self.df_initial = pd.DataFrame(data_list)
        self.df_initial = self._calculate_ranks(self.df_initial)

        # Calcul des totaux globaux pour l'accueil
        platform_totals = {"tiktok": 0, "youtube": 0}
        for creator in self.creators:
            for plat_name, pstats in creator.get("platforms", {}).items():
                key = plat_name.lower()
                if key in platform_totals:
                    videos = pstats.get("videos") or pstats.get("total", 0)
                    platform_totals[key] += videos
        self.global_platforms = platform_totals

    def _calculate_ranks(self, df):
        """Ajoute une colonne de rang basée sur les vues."""
        if df.empty: return df
        if df["views"].sum() == 0:
            df['rank'] = 0
            df['rank_label'] = "-"
            return df
        df = df.sort_values(by="views", ascending=False)
        df['rank'] = range(1, len(df) + 1)
        df['rank_label'] = "#" + df['rank'].astype(str)
        return df

    def get_filtered_df(self, platform="all", themes=None, countries=None):
        """
        Retourne un DataFrame filtré pour la carte (Home).
        Applique des coefficients de pondération (splits) si une plateforme est choisie.
        """
        themes = themes or []
        countries = countries or []
        rows = []
        
        for iso, stats in COUNTRY_STATS.items():
            if countries and iso not in countries: continue
            
            base_data = {k: v for k, v in stats.items() if k not in ["platform_split", "theme_split"]}
            base_data["iso_alpha"] = iso
            
            # Calcul du coefficient de réduction
            coeff = 1.0
            p_split = stats.get("platform_split", {"TikTok": 0.5, "YouTube": 0.5})
            
            if platform == "TikTok": 
                coeff *= p_split.get("TikTok", 0)
            elif platform == "YouTube": 
                coeff *= p_split.get("YouTube", 0)
            
            if themes:
                t_split = stats.get("theme_split", {})
                theme_share = sum(t_split.get(t, 0) for t in themes)
                coeff *= theme_share
            
            # Application du coefficient
            metrics = ["views", "videos", "likes", "shares", "comments", "creators"]
            for m in metrics:
                if m in base_data: 
                    base_data[m] = int(base_data[m] * coeff)
            rows.append(base_data)
            
        dff = pd.DataFrame(rows)
        # Sécurité pour colonnes manquantes
        for col in ["views", "videos", "likes", "shares", "comments", "creators"]:
            if col not in dff.columns: dff[col] = 0
            
        return self._calculate_ranks(dff)

    def get_kpi_stats(self, dff):
        """Somme les colonnes du DataFrame filtré pour obtenir les KPIs globaux."""
        if dff.empty: 
            return {"videos": 0, "views": 0, "likes": 0, "shares": 0, "comments": 0, "creators": 0}
        return dff[["videos", "views", "likes", "shares", "comments", "creators"]].sum().to_dict()

    def get_unique_values(self, key):
        """Récupère les listes uniques pour les filtres (Pays, Tags, Langues)."""
        if key == "platforms": 
            return sorted({p for c in self.creators for p in c.get("platforms", {}).keys()})
        if key == "region": 
            return sorted({c.get("region") for c in self.creators if c.get("region")})
        if key == "language": 
            return sorted({c.get("language") for c in self.creators if c.get("language")})
        if key == "tags": 
            return sorted({t for c in self.creators for t in c.get("tags", [])})
        return []

    def filter_creators(self, query, platform, region, theme, lang, certif, active):
        """Filtre la liste principale des créateurs (Page Recherche)."""
        query = (query or "").lower()
        filtered = []
        for c in self.creators:
            # Calculs préliminaires
            platforms_dict = c.get("platforms", {})
            is_certif = "oui" if any(p.get("certified") == "oui" for p in platforms_dict.values()) else "non"
            is_active = "oui" if any(p.get("active") == "oui" for p in platforms_dict.values()) else "non"
            
            # Conditions
            if query and query not in (c["name"] + c["username"]).lower(): continue
            if platform != "all" and platform not in platforms_dict: continue
            if region != "all" and c.get("region") != region: continue
            if theme != "all" and theme not in c.get("tags", []): continue
            if lang != "all" and c.get("language") != lang: continue
            if certif != "all" and is_certif != certif: continue
            if active != "all" and is_active != active: continue
            
            filtered.append(c)
        return filtered

    def sort_creators(self, creators_list, sort_value):
        """Trie la liste des créateurs selon la clé fournie (ex: views_desc)."""
        sort_value = sort_value or "views_desc"
        metric, order = sort_value.split("_")
        reverse = (order == "desc")
        
        creators_list.sort(key=lambda x: x.get("totals", {}).get(metric, 0), reverse=reverse)
        return creators_list

    def get_average_history(self, group_type, group_value, platform, metrics_list=None):
        """
        Calcule l'historique moyen pour un groupe donné (Pays ou Tag).
        Utilisé pour les courbes de comparaison dans le Profil.
        """
        relevant_creators = []
        for c in self.creators:
            if group_type == "country" and c.get("country") == group_value:
                relevant_creators.append(c)
            elif group_type == "tag" and group_value in c.get("tags", []):
                relevant_creators.append(c)
        
        if not relevant_creators: return []

        target_platforms = []
        if platform == "combined":
            target_platforms = ["youtube", "tiktok"]
        elif platform.lower() in ["youtube", "tiktok"]:
            target_platforms = [platform.lower()]
        else:
            return []

        # Initialisation structure accumulation
        monthly_totals = {f"M{i}": {} for i in range(1, 13)}
        metrics_to_sum = metrics_list if metrics_list else ["views", "likes", "shares", "comments", "followers", "videos"]
        
        for m_key in monthly_totals:
            for met in metrics_to_sum:
                monthly_totals[m_key][met] = [] 

        # Accumulation
        for c in relevant_creators:
            for i in range(1, 13):
                m_key = f"M{i}"
                for met in metrics_to_sum:
                    val = 0
                    for p in target_platforms:
                        hist = c.get("history", {}).get(p, [])
                        if i <= len(hist):
                            record = hist[i-1]
                            val += record.get(met, 0)
                    
                    monthly_totals[m_key][met].append(val)

        # Moyennage
        avg_history = []
        for i in range(1, 13):
            m_key = f"M{i}"
            row = {"month": m_key}
            for met in metrics_to_sum:
                vals = monthly_totals[m_key][met]
                row[met] = sum(vals) / len(vals) if vals else 0
            avg_history.append(row)
            
        return avg_history

# ==============================================================================
# 5. INSTANCIATION (SINGLETONS)
# ==============================================================================

data_manager = DataManager()
analytics_engine = AnalyticsEngine()