# constants.py

# Noms de mois pour les graphiques
MONTH_NAMES = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]

# ============================================================
# 1. STATS PAYS (HOME)
# ============================================================
COUNTRY_STATS = {
    "FRA": {
        "name": "France", "views": 450000000, "videos": 120000, "likes": 18000000, "shares": 2200000, "comments": 900000, "creators": 2500,
        "platform_split": {"TikTok": 0.60, "YouTube": 0.40},
        "theme_split": {"Fitness": 0.20, "Gaming": 0.15, "Lifestyle": 0.25, "Music": 0.10, "Tech": 0.05, "Food": 0.15, "Fashion": 0.05, "Education": 0.05}
    },
    "USA": {
        "name": "United States", "views": 1200000000, "videos": 450000, "likes": 60000000, "shares": 6000000, "comments": 3000000, "creators": 8500,
        "platform_split": {"TikTok": 0.45, "YouTube": 0.55},
        "theme_split": {"Fitness": 0.10, "Gaming": 0.30, "Lifestyle": 0.15, "Music": 0.15, "Tech": 0.15, "Food": 0.05, "Fashion": 0.05, "Education": 0.05}
    },
    "CAN": {
        "name": "Canada", "views": 150000000, "videos": 60000, "likes": 7500000, "shares": 750000, "comments": 300000, "creators": 1200,
        "platform_split": {"TikTok": 0.50, "YouTube": 0.50},
        "theme_split": {"Fitness": 0.15, "Gaming": 0.20, "Lifestyle": 0.20, "Music": 0.10, "Tech": 0.10, "Food": 0.15, "Fashion": 0.05, "Education": 0.05}
    },
    "ESP": {
        "name": "Spain", "views": 90000000, "videos": 45000, "likes": 4500000, "shares": 450000, "comments": 180000, "creators": 900,
        "platform_split": {"TikTok": 0.70, "YouTube": 0.30},
        "theme_split": {"Fitness": 0.10, "Gaming": 0.15, "Lifestyle": 0.30, "Music": 0.10, "Tech": 0.05, "Food": 0.20, "Fashion": 0.05, "Education": 0.05}
    },
    "DEU": {
        "name": "Germany", "views": 110000000, "videos": 50000, "likes": 5500000, "shares": 550000, "comments": 220000, "creators": 1000,
        "platform_split": {"TikTok": 0.40, "YouTube": 0.60},
        "theme_split": {"Fitness": 0.15, "Gaming": 0.20, "Lifestyle": 0.10, "Music": 0.05, "Tech": 0.20, "Food": 0.10, "Fashion": 0.05, "Education": 0.15}
    },
    "JPN": {
        "name": "Japan", "views": 300000000, "videos": 85000, "likes": 15000000, "shares": 1500000, "comments": 600000, "creators": 1800,
        "platform_split": {"TikTok": 0.30, "YouTube": 0.70},
        "theme_split": {"Fitness": 0.05, "Gaming": 0.25, "Lifestyle": 0.15, "Music": 0.15, "Tech": 0.15, "Food": 0.15, "Fashion": 0.05, "Education": 0.05}
    },
    "GBR": {
        "name": "United Kingdom", "views": 210000000, "videos": 75000, "likes": 10500000, "shares": 1000000, "comments": 400000, "creators": 1500,
        "platform_split": {"TikTok": 0.55, "YouTube": 0.45},
        "theme_split": {"Fitness": 0.10, "Gaming": 0.15, "Lifestyle": 0.20, "Music": 0.20, "Tech": 0.05, "Food": 0.15, "Fashion": 0.10, "Education": 0.05}
    },
    "BRA": {
        "name": "Brazil", "views": 350000000, "videos": 110000, "likes": 17500000, "shares": 1700000, "comments": 700000, "creators": 2200,
        "platform_split": {"TikTok": 0.65, "YouTube": 0.35},
        "theme_split": {"Fitness": 0.25, "Gaming": 0.15, "Lifestyle": 0.25, "Music": 0.15, "Tech": 0.05, "Food": 0.10, "Fashion": 0.05, "Education": 0.00}
    },
}
THEMES = ["Fitness", "Gaming", "Lifestyle", "Music" , "Tech", "Food", "Fashion", "Education"]

MAP_INDICATORS = {
    "Nombre de vues": "views",
    "Nombre de vidéos": "videos",
    "Nombre de likes": "likes",
    "Nombre de partages": "shares",
}

# ============================================================
# 2. DATASET CRÉATEURS UNIFIÉ (AVEC HISTORIQUE COMPLET)
# ============================================================

ALL_CREATORS = [
    {
        "id": 1, "name": "Lucas FitPro", "username": "@lucas_fitpro", "avatar": "https://ui-avatars.com/api/?name=Lucas+FitPro&background=0D6EFD&color=fff",
        "bio": "Coach sportif. HIIT et nutrition.", "country": "France", "language": "Français", "region": "Europe", "tags": ["Fitness", "Lifestyle"],
        "added_date": "03/10/2024", "is_new": False, "is_trending": False, "is_favorite": True,
        "totals": {"followers": 512000, "views": 27800000, "videos": 350, "likes": 1620000, "shares": 118000, "comments": 60000},
        "platforms": {
            "TikTok": {"active": "oui", "certified": "oui", "followers": 350000, "views": 18000000, "videos": 240, "likes": 1000000, "shares": 80000, "comments": 40000},
            "YouTube": {"active": "oui", "certified": "non", "followers": 162000, "views": 9800000, "videos": 110, "likes": 620000, "shares": 38000, "comments": 20000}
        },
        "history": {
            "youtube": [{"month": MONTH_NAMES[i-1], "followers": int(162000 * (i/12)**0.8), "videos": int(110 * (i/12)), "views": int(9800000 * (i/12)**1.5), "likes": int(620000 * (i/12)**1.5), "shares": int(38000 * (i/12)), "comments": int(20000 * (i/12))} for i in range(1, 13)],
            "tiktok": [{"month": MONTH_NAMES[i-1], "followers": int(350000 * (i/12)**1.2), "videos": int(240 * (i/12)), "views": int(18000000 * (i/12)**2), "likes": int(1000000 * (i/12)**2), "shares": int(80000 * (i/12)), "comments": int(40000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 2, "name": "Melody Star", "username": "@melody_star", "avatar": "https://ui-avatars.com/api/?name=Melody+Star&background=E91E63&color=fff",
        "bio": "Chanteuse pop et covers.", "country": "USA", "language": "English", "region": "Amérique du Nord", "tags": ["Music"],
        "added_date": "15/09/2024", "is_new": True, "is_trending": True, "is_favorite": False,
        "totals": {"followers": 920000, "views": 58400000, "videos": 190, "likes": 3500000, "shares": 210000, "comments": 120000},
        "platforms": {
            "YouTube": {"active": "oui", "certified": "oui", "followers": 920000, "views": 58400000, "videos": 190, "likes": 3500000, "shares": 210000, "comments": 120000}
        },
        "history": {
            "youtube": [{"month": MONTH_NAMES[i-1], "followers": int(920000 * (i/12)), "videos": int(190 * (i/12)), "views": int(58400000 * (i/12)**2), "likes": int(3500000 * (i/12)**2), "shares": int(210000 * (i/12)), "comments": int(120000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 3, "name": "TechGuru92", "username": "@techguru92", "avatar": "https://ui-avatars.com/api/?name=Tech+Guru&background=212529&color=fff",
        "bio": "Tests High-Tech et Gaming.", "country": "USA", "language": "English", "region": "Amérique du Nord", "tags": ["Tech", "Gaming"],
        "added_date": "28/09/2024", "is_new": False, "is_trending": True, "is_favorite": True,
        "totals": {"followers": 890000, "views": 45200000, "videos": 156, "likes": 2100000, "shares": 150000, "comments": 80000},
        "platforms": {
            "YouTube": {"active": "oui", "certified": "non", "followers": 890000, "views": 45200000, "videos": 156, "likes": 2100000, "shares": 150000, "comments": 80000}
        },
        "history": {
            "youtube": [{"month": MONTH_NAMES[i-1], "followers": int(890000 * (i/12)**0.9), "videos": int(156 * (i/12)), "views": int(45200000 * (i/12)**1.2), "likes": int(2100000 * (i/12)**1.2), "shares": int(150000 * (i/12)), "comments": int(80000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 4, "name": "CuisinePassion", "username": "@cuisine_passion", "avatar": "https://ui-avatars.com/api/?name=Cuisine+Passion&background=FFC107&color=000",
        "bio": "Recettes faciles pour étudiants.", "country": "France", "language": "Français", "region": "Europe", "tags": ["Food", "Lifestyle"],
        "added_date": "20/09/2024", "is_new": True, "is_trending": False, "is_favorite": False,
        "totals": {"followers": 123000, "views": 8700000, "videos": 98, "likes": 500000, "shares": 12000, "comments": 5000},
        "platforms": {
            "TikTok": {"active": "oui", "certified": "non", "followers": 123000, "views": 8700000, "videos": 98, "likes": 500000, "shares": 12000, "comments": 5000}
        },
        "history": {
            "tiktok": [{"month": MONTH_NAMES[i-1], "followers": int(123000 * (i/12)), "videos": int(98 * (i/12)), "views": int(8700000 * (i/12)**0.8), "likes": int(500000 * (i/12)), "shares": int(12000 * (i/12)), "comments": int(5000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 5, "name": "GamingKing", "username": "@gaming_king_br", "avatar": "https://ui-avatars.com/api/?name=Gaming+King&background=6610f2&color=fff",
        "bio": "Le roi du Battle Royale au Brésil.", "country": "Brazil", "language": "Portuguese", "region": "Amérique du Sud", "tags": ["Gaming"],
        "added_date": "10/10/2024", "is_new": False, "is_trending": True, "is_favorite": False,
        "totals": {"followers": 2500000, "views": 150000000, "videos": 600, "likes": 12000000, "shares": 500000, "comments": 250000},
        "platforms": {
            "YouTube": {"active": "oui", "certified": "oui", "followers": 2500000, "views": 150000000, "videos": 600, "likes": 12000000, "shares": 500000, "comments": 250000}
        },
        "history": {
            "youtube": [{"month": MONTH_NAMES[i-1], "followers": int(2500000 * (i/12)), "videos": int(600 * (i/12)), "views": int(150000000 * (i/12)**1.1), "likes": int(12000000 * (i/12)), "shares": int(500000 * (i/12)), "comments": int(250000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 6, "name": "Sophie Yoga", "username": "@sophie_yoga", "avatar": "https://ui-avatars.com/api/?name=Sophie+Yoga&background=20c997&color=fff",
        "bio": "Bien-être et méditation.", "country": "France", "language": "Français", "region": "Europe", "tags": ["Fitness", "Lifestyle"],
        "added_date": "01/11/2024", "is_new": True, "is_trending": True, "is_favorite": True,
        "totals": {"followers": 45000, "views": 2100000, "videos": 45, "likes": 150000, "shares": 5000, "comments": 3000},
        "platforms": {
            "TikTok": {"active": "oui", "certified": "non", "followers": 45000, "views": 2100000, "videos": 45, "likes": 150000, "shares": 5000, "comments": 3000}
        },
        "history": {
            "tiktok": [{"month": MONTH_NAMES[i-1], "followers": int(45000 * (i/12)), "videos": int(45 * (i/12)), "views": int(2100000 * (i/12)**2.5), "likes": int(150000 * (i/12)**2), "shares": int(5000 * (i/12)), "comments": int(3000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 7, "name": "Tokyo Travel", "username": "@tokyo_vlog", "avatar": "https://ui-avatars.com/api/?name=Tokyo+Travel&background=fd7e14&color=fff",
        "bio": "Découverte du Japon authentique.", "country": "Japan", "language": "English", "region": "Asie", "tags": ["Lifestyle", "Education"],
        "added_date": "12/08/2024", "is_new": False, "is_trending": False, "is_favorite": True,
        "totals": {"followers": 320000, "views": 18500000, "videos": 80, "likes": 980000, "shares": 45000, "comments": 15000},
        "platforms": {
            "YouTube": {"active": "oui", "certified": "oui", "followers": 200000, "views": 12000000, "videos": 30, "likes": 600000, "shares": 30000, "comments": 10000},
            "TikTok": {"active": "oui", "certified": "non", "followers": 120000, "views": 6500000, "videos": 50, "likes": 380000, "shares": 15000, "comments": 5000}
        },
        "history": {
            "youtube": [{"month": MONTH_NAMES[i-1], "followers": int(200000 * (i/12)), "videos": int(30 * (i/12)), "views": int(12000000 * (i/12)), "likes": int(600000 * (i/12)), "shares": int(30000 * (i/12)), "comments": int(10000 * (i/12))} for i in range(1, 13)],
            "tiktok": [{"month": MONTH_NAMES[i-1], "followers": int(120000 * (i/12)), "videos": int(50 * (i/12)), "views": int(6500000 * (i/12)), "likes": int(380000 * (i/12)), "shares": int(15000 * (i/12)), "comments": int(5000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 8, "name": "Science Explain", "username": "@sci_explain", "avatar": "https://ui-avatars.com/api/?name=Science+Ex&background=0dcaf0&color=fff",
        "bio": "La science expliquée simplement.", "country": "United Kingdom", "language": "English", "region": "Europe", "tags": ["Education", "Tech"],
        "added_date": "05/05/2024", "is_new": False, "is_trending": True, "is_favorite": False,
        "totals": {"followers": 670000, "views": 42000000, "videos": 210, "likes": 3100000, "shares": 400000, "comments": 85000},
        "platforms": {
            "TikTok": {"active": "oui", "certified": "oui", "followers": 670000, "views": 42000000, "videos": 210, "likes": 3100000, "shares": 400000, "comments": 85000}
        },
        "history": {
            "tiktok": [{"month": MONTH_NAMES[i-1], "followers": int(670000 * (i/12)), "videos": int(210 * (i/12)), "views": int(42000000 * (i/12)**1.1), "likes": int(3100000 * (i/12)), "shares": int(400000 * (i/12)), "comments": int(85000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 9, "name": "Fashion Spain", "username": "@fashion_es", "avatar": "https://ui-avatars.com/api/?name=Fashion+ES&background=d63384&color=fff",
        "bio": "Mode et tendances 2025.", "country": "Spain", "language": "Spanish", "region": "Europe", "tags": ["Fashion", "Lifestyle"],
        "added_date": "22/10/2024", "is_new": True, "is_trending": False, "is_favorite": False,
        "totals": {"followers": 85000, "views": 3200000, "videos": 120, "likes": 250000, "shares": 10000, "comments": 8000},
        "platforms": {
            "TikTok": {"active": "oui", "certified": "non", "followers": 85000, "views": 3200000, "videos": 120, "likes": 250000, "shares": 10000, "comments": 8000}
        },
        "history": {
            "tiktok": [{"month": MONTH_NAMES[i-1], "followers": int(85000 * (i/12)), "videos": int(120 * (i/12)), "views": int(3200000 * (i/12)), "likes": int(250000 * (i/12)), "shares": int(10000 * (i/12)), "comments": int(8000 * (i/12))} for i in range(1, 13)]
        }
    },
    {
        "id": 10, "name": "Eco Life", "username": "@ecolife_de", "avatar": "https://ui-avatars.com/api/?name=Eco+Life&background=198754&color=fff",
        "bio": "Vivre durablement à Berlin.", "country": "Germany", "language": "German", "region": "Europe", "tags": ["Lifestyle", "Education"],
        "added_date": "14/06/2024", "is_new": False, "is_trending": False, "is_favorite": True,
        "totals": {"followers": 150000, "views": 5600000, "videos": 75, "likes": 420000, "shares": 35000, "comments": 12000},
        "platforms": {
            "YouTube": {"active": "oui", "certified": "non", "followers": 150000, "views": 5600000, "videos": 75, "likes": 420000, "shares": 35000, "comments": 12000}
        },
        "history": {
            "youtube": [{"month": MONTH_NAMES[i-1], "followers": int(150000 * (i/12)), "videos": int(75 * (i/12)), "views": int(5600000 * (i/12)), "likes": int(420000 * (i/12)), "shares": int(35000 * (i/12)), "comments": int(12000 * (i/12))} for i in range(1, 13)]
        }
    }
]

TRENDING_CREATORS = [c for c in ALL_CREATORS if c["is_trending"]]

NEW_CREATORS = [c for c in ALL_CREATORS if c["is_new"]]
TOP_VIDEOS = {
    "TikTok": [
        {"title": "Routine Matin", "likes": 145000, "views": 2800000, "shares": 12000, "comments": 3400, "platform": "TikTok", "thumbnail": "/assets/thumb1.jpg", "duration": "00:45", "creator": "@lucas_fitpro"},
        {"title": "Astuce Cuisine", "likes": 125000, "views": 2100000, "shares": 8000, "comments": 1200, "platform": "TikTok", "thumbnail": "/assets/thumb2.jpg", "duration": "01:20", "creator": "@cuisine_passion"},
        {"title": "Dance Challenge", "likes": 98000, "views": 1500000, "shares": 5000, "comments": 900, "platform": "TikTok", "thumbnail": "/assets/thumb_dance.jpg", "duration": "00:30", "creator": "@lucas_fitpro"},
        {"title": "Yoga Flow", "likes": 45000, "views": 500000, "shares": 2000, "comments": 300, "platform": "TikTok", "thumbnail": "/assets/thumb_yoga.jpg", "duration": "01:00", "creator": "@sophie_yoga"},
        {"title": "Science Fact #42", "likes": 320000, "views": 4500000, "shares": 45000, "comments": 2200, "platform": "TikTok", "thumbnail": "/assets/thumb_sci.jpg", "duration": "00:59", "creator": "@sci_explain"},
    ],
    "YouTube": [
        {"title": "Setup Tour 2025", "likes": 325000, "views": 5200000, "shares": 45000, "comments": 12000, "platform": "YouTube", "thumbnail": "/assets/thumb3.jpg", "duration": "12:30", "creator": "@techguru92"},
        {"title": "HIIT 20 Minutes", "likes": 210000, "views": 3800000, "shares": 15000, "comments": 5000, "platform": "YouTube", "thumbnail": "/assets/thumb_hiit.jpg", "duration": "20:00", "creator": "@lucas_fitpro"},
        {"title": "Vlog Japon", "likes": 180000, "views": 2900000, "shares": 12000, "comments": 3000, "platform": "YouTube", "thumbnail": "/assets/thumb_japon.jpg", "duration": "15:45", "creator": "@tokyo_vlog"},
        {"title": "Battle Royale Highlights", "likes": 500000, "views": 8000000, "shares": 25000, "comments": 15000, "platform": "YouTube", "thumbnail": "/assets/thumb_game.jpg", "duration": "10:20", "creator": "@gaming_king_br"},
        {"title": "Zero Waste Tips", "likes": 80000, "views": 1200000, "shares": 5000, "comments": 1200, "platform": "YouTube", "thumbnail": "/assets/thumb_eco.jpg", "duration": "08:15", "creator": "@ecolife_de"},
    ]
}


# 2. Nouveaux Tags (Pour l'onglet Nouveaux)
NEW_TAGS = [
    {"rank": 1, "name": "Micro-Learning", "creators": 45, "growth": "Nouveau"},
    {"rank": 2, "name": "Slow Travel", "creators": 32, "growth": "Nouveau"},
    {"rank": 3, "name": "Upcycling Déco", "creators": 28, "growth": "Nouveau"},
    {"rank": 4, "name": "BookTok Fantasy", "creators": 150, "growth": "Nouveau"},
]

TRENDING_TOPICS = [
    {"rank": 1, "name": "Intelligence Artificielle", "creators": 1250, "growth": "+45%"},
    {"rank": 2, "name": "Cuisine Végétarienne", "creators": 890, "growth": "+32%"},
    {"rank": 3, "name": "Mode Durable", "creators": 678, "growth": "+67%"},
    {"rank": 4, "name": "Fitness à Domicile", "creators": 1456, "growth": "+23%"},
    {"rank": 5, "name": "Art Digital", "creators": 567, "growth": "+78%"},
    {"rank": 6, "name": "Développement Web", "creators": 789, "growth": "+56%"},
]

# Agrégats pour la page Découverte
TRENDING_VIDEOS = TOP_VIDEOS["TikTok"] + TOP_VIDEOS["YouTube"]
NEW_VIDEOS = TOP_VIDEOS["YouTube"][:2] + TOP_VIDEOS["TikTok"][:2] # Simulation

THEMES_EVOLUTION = [
    {
        "label": "Durabilité & Éco-responsabilité",
        "change": "+89% cette semaine",
        "class": "theme-bar-green",
    },
    {
        "label": "Intelligence Artificielle",
        "change": "+67% cette semaine",
        "class": "theme-bar-blue",
    },
    {
        "label": "Bien-être Mental",
        "change": "+54% cette semaine",
        "class": "theme-bar-purple",
    },
]
