/* ============================================================
   FINEST GLOBAL — Système de traduction FR / EN
   Basé sur index.html (anglais par défaut)
   ============================================================ */

const TRANSLATIONS = {
  fr: {
    // Navigation
    "nav.home": "Accueil",
    "nav.marketplace": "Marketplace",
    "nav.about": "À propos",
    "nav.search_placeholder": "Rechercher un produit, une boutique...",
    "nav.login": "Se connecter",
    "nav.register": "S'inscrire",
    "nav.dashboard": "Mon dashboard",
    "nav.dashboard_admin": "Dashboard admin",
    "nav.orders": "Mes commandes",
    "nav.become_seller": "Devenir vendeur",
    "nav.logout": "Se déconnecter",
    "nav.profile": "Mon profil",
    
    // Rôles
    "role.admin": "Admin",
    "role.seller": "Vendeur",
    "role.client": "Client",
    
    // ============================================================
    // ACCUEIL (index.html)
    // ============================================================
    "home.hero_1": "Be Findable.",
    "home.hero_2": "Devenez Visible.",
    "home.hero_p": "Finest Global rend les commerçants du marché visibles, trouvables et connectés à leurs clients. Sans remplacer le marché physique — en le rendant simplement accessible.",
    "home.explore": "Explorer la marketplace →",
    "home.become_seller": "Devenir vendeur",
    
    // Catégories
    "home.categories_title": "Catégories populaires",
    "home.categories_p": "Explorez les produits et services par catégorie pour trouver ce que vous cherchez.",
    
    // Tendances
    "home.trending_title": "Découvrez Produits & Services",
    "home.trending_p": "Explorez les produits et services disponibles des entreprises de la marketplace.",
    
    // Boutiques
    "home.shops_title": "Nouveau sur Finest Global",
    "home.shops_p": "Découvrez les entreprises récemment inscrites et explorez leurs vitrines.",
    
    // CTA vendeur
    "home.cta_title": "Vous avez quelque chose à vendre ou un service à proposer ?",
    "home.cta_p": "Créez votre vitrine gratuite sur Finest Global et commencez à présenter ce que vous proposez.",
    "home.cta_btn": "Devenir Vendeur",
    "home.cta_1": "Vitrine en ligne gratuite",
    "home.cta_2": "Restez informé de l'activité",
    "home.cta_3": "Atteignez des clients potentiels",
    "home.cta_4": "Inscription gratuite",
    "home.cta_5": "Support en français",
    
    // Near you
    "home.near_you_title": "Découvrez Près de Chez Vous",
    "home.near_you_p": "Trouvez des produits, boutiques et services près de votre position actuelle.",
    "home.detect_location": "Détecter ma position",
    "home.detecting": "Détection en cours...",
    "home.location_detected": "Position détectée",
    "home.location_denied": "Impossible de détecter votre position. Vérifiez vos paramètres.",
    "home.see_nearby": "Voir les boutiques proches →",
    "home.search_by_code": "Recherche par code business",
    "home.enter_code": "Vous cherchez une entreprise en particulier ? Entrez son code business Finest Global pour trouver sa vitrine.",
    "home.find_shop": "Trouver",
    "home.code_not_found": "Aucune boutique trouvée avec ce code.",
    
    // Footer
    "footer.tagline": "Une marketplace digitale connectant les personnes, les entreprises, les produits et les services. Découvrez des opportunités, atteignez des clients et créez des connexions au-delà des frontières physiques.",
    "footer.navigation": "Navigation",
    "footer.sellers": "Vendeurs",
    "footer.contact": "Contactez-nous",
    "footer.create_shop": "Créer une vitrine",
    "footer.my_dashboard": "Mon dashboard",
    "footer.my_orders": "Mes commandes",
    "footer.rights": "Tous droits réservés.",
    
    // ============================================================
    // MARKETPLACE
    // ============================================================
    "marketplace.filters": "Filtres",
    "marketplace.clear_all": "Tout effacer",
    "marketplace.categories": "Catégories",
    "marketplace.colors": "Couleurs",
    "marketplace.price": "Prix (FCFA)",
    "marketplace.apply": "Appliquer",
    "marketplace.min": "Min",
    "marketplace.max": "Max",
    "marketplace.sort_sales": "🔥 Plus vendus",
    "marketplace.sort_recent": "🆕 Plus récents",
    "marketplace.sort_views": "👁️ Plus vus",
    "marketplace.sort_price_asc": "💰 Prix croissant",
    "marketplace.sort_price_desc": "💎 Prix décroissant",
    "marketplace.sort_distance": "📍 Plus proches",
    "marketplace.products_found": "produit(s) trouvé(s)",
    "marketplace.no_products": "Aucun produit trouvé",
    "marketplace.no_products_p": "Essayez avec d'autres mots-clés ou réinitialisez les filtres.",
    "marketplace.reset_filters": "Réinitialiser les filtres",
    "marketplace.previous": "← Précédent",
    "marketplace.next": "Suivant →",
    "marketplace.close_filters": "✕ Fermer les filtres",
    
    // Filtres géographiques
    "marketplace.locality": "Localité",
    "marketplace.market": "Marché / Zone",
    "marketplace.all_localities": "Toutes les localités",
    "marketplace.all_markets": "Tous les marchés",
    "marketplace.near_me": "📍 Autour de moi",
    "marketplace.radius": "Rayon (km)",
    "marketplace.detecting_location": "Détection de votre position...",
    "marketplace.location_detected": "Position détectée",
    "marketplace.distance": "Distance",
    "marketplace.no_location": "Position non disponible",
    
    // ============================================================
    // PRODUIT / BOUTIQUE
    // ============================================================
    "product.order_now": "🛒 Commander maintenant",
    "product.out_of_stock": "Produit indisponible",
    "product.sold_by": "Vendu par",
    "product.see_shop": "Voir →",
    "product.quantity": "Quantité :",
    "product.sales": "Ventes",
    "product.views": "Vues",
    "product.stock": "Stock",
    "product.related": "📦 Vous aimerez aussi",
    "product.all_products": "Tous les produits",
    "product.confirm_order": "Confirmer la commande",
    "product.order_summary": "Récapitulatif",
    "product.price_unit": "Prix unitaire",
    "product.total": "Total",
    "product.note": "Note pour le vendeur (optionnel)",
    "product.note_placeholder": "Ex: Livraison à Cotonou, quartier Fidjrossè...",
    "product.confirm": "Confirmer la commande",
    "product.cancel": "Annuler",
    "product.no_products": "Aucun produit",
    "product.no_products_p": "Cette boutique n'a pas encore de produits.",
    "product.similar": "📦 Vous aimerez aussi",
    "product.how_it_works": "💡 Comment ça marche ?",
    "product.how_it_works_p": "Le vendeur reçoit votre commande instantanément. Il vous contactera pour organiser la livraison.",
    
    // Disponibilité
    "product.in_stock": "En stock",
    "product.out_of_stock_label": "Rupture de stock",
    "product.to_confirm": "Disponibilité à confirmer",
    "product.availability": "Disponibilité",
    
    // Localisation boutique
    "product.shop_code": "Code boutique",
    "product.shop_locality": "Localité",
    "product.shop_market": "Marché",
    "product.distance_from_you": "Distance",
    
    // ============================================================
    // CONNEXION / INSCRIPTION
    // ============================================================
    "login.title": "Bon retour 👋",
    "login.subtitle": "Connectez-vous à votre compte Finest Global",
    "login.phone": "Numéro de téléphone",
    "login.password": "Mot de passe",
    "login.submit": "Se connecter",
    "login.no_account": "Pas encore de compte ?",
    "login.signup_link": "S'inscrire",
    
    "register.title": "Créer un compte",
    "register.subtitle": "Rejoignez Finest Global en quelques secondes",
    "register.client": "Client",
    "register.client_desc": "Acheter",
    "register.seller": "Vendeur",
    "register.seller_desc": "Vendre",
    "register.firstname": "Prénom",
    "register.lastname": "Nom",
    "register.email": "Email",
    "register.phone": "Numéro de téléphone",
    "register.password": "Mot de passe",
    "register.submit_client": "Créer mon compte client",
    "register.submit_seller": "Créer mon compte vendeur",
    "register.has_account": "Déjà un compte ?",
    "register.login_link": "Se connecter",
    "register.phone_hint": "Format : 01 + 8 chiffres.",
    "register.password_hint": "Au moins 6 caractères.",
    
    // ============================================================
    // COMMANDES
    // ============================================================
    "orders.title": "📦 Mes commandes",
    "orders.subtitle": "Suivez l'état de vos commandes en temps réel.",
    "orders.all": "Toutes",
    "orders.pending": "⏳ En attente",
    "orders.confirmed": "✅ Confirmées",
    "orders.delivered": "📦 Livrées",
    "orders.cancelled": "❌ Annulées",
    "orders.empty": "Vous n'avez pas encore de commandes",
    "orders.empty_p": "Parcourez la marketplace et passez votre première commande.",
    "orders.explore": "Explorer la marketplace →",
    "orders.no_in_category": "Aucune commande dans cette catégorie",
    "orders.try_other": "Essayez un autre filtre.",
    "orders.status_pending": "En attente",
    "orders.status_confirmed": "Confirmée",
    "orders.status_delivered": "Livrée",
    "orders.status_cancelled": "Annulée",
    "orders.cancel": "Annuler",
    "orders.quantity": "Quantité",
    "orders.order_id": "Commande",
    "orders.shop": "Boutique",
    
    // ============================================================
    // DASHBOARD VENDEUR
    // ============================================================
    "seller.hello": "Bonjour",
    "seller.overview": "Vue d'ensemble",
    "seller.orders": "Commandes",
    "seller.products": "Mes produits",
    "seller.shop": "Ma boutique",
    "seller.revenue": "Chiffre d'affaires",
    "seller.total_sales": "Ventes totales",
    "seller.product_views": "Vues produits",
    "seller.pending": "En attente",
    "seller.top_products": "🏆 Top produits",
    "seller.orders_by_status": "📊 Commandes par statut",
    "seller.add_product": "➕ Ajouter un produit",
    "seller.no_products": "Aucun produit pour l'instant",
    "seller.no_products_p": "Ajoutez votre premier produit pour commencer à vendre.",
    "seller.no_orders": "Aucune commande pour l'instant",
    "seller.no_orders_p": "Vous recevrez une notification dès qu'un client commande.",
    "seller.orders_received": "📦 Commandes reçues",
    "seller.orders_received_p": "Gérez vos commandes clients en temps réel.",
    "seller.my_products": "🛍️ Mes produits",
    "seller.my_products_p": "produit(s) dans votre boutique",
    "seller.my_shop": "🏪 Ma boutique",
    "seller.my_shop_p": "Personnalisez les informations de votre boutique.",
    "seller.confirm": "✅ Confirmer",
    "seller.cancel": "❌ Annuler",
    "seller.deliver": "📦 Marquer livrée",
    "seller.notifications_active": "Notifications actives",
    "seller.new_order": "Nouvelle commande",
    "seller.product": "Produit",
    "seller.edit": "✏️ Éditer",
    
    // Dashboard vendeur - Localisation
    "seller.shop_location": "Localisation de la boutique",
    "seller.shop_location_p": "Déplacez le marqueur sur la carte pour changer la position de votre boutique.",
    "seller.save_location": "Enregistrer la position",
    "seller.location_saved": "Position mise à jour",
    "seller.shop_code": "Code boutique",
    "seller.shop_code_p": "Partagez ce code avec vos clients pour qu'ils trouvent facilement votre boutique.",
    
    // Dashboard vendeur - Disponibilité
    "seller.availability": "Disponibilité",
    "seller.availability_in_stock": "En stock",
    "seller.availability_out_of_stock": "Rupture de stock",
    "seller.availability_to_confirm": "Disponibilité à confirmer",
    
    // ============================================================
    // DASHBOARD ADMIN
    // ============================================================
    "admin.sidebar_title": "👑 Admin",
    "admin.title": "Vue d'ensemble 👑",
    "admin.subtitle": "Statistiques globales de la plateforme Finest Global.",
    "admin.overview": "Vue d'ensemble",
    "admin.users": "👥 Utilisateurs",
    "admin.shops": "🏪 Boutiques",
    "admin.products": "🛍️ Produits",
    "admin.orders": "📦 Commandes",
    "admin.categories": "🏷️ Catégories",
    "admin.rankings": "🏆 Classements",
    "admin.revenue": "Chiffre d'affaires",
    "admin.pending": "En attente",
    "admin.sellers": "Vendeurs",
    "admin.clients": "Clients",
    "admin.visitors": "📈 Visiteurs",
    "admin.day": "Jour",
    "admin.week": "Semaine",
    "admin.month": "Mois",
    "admin.visits": "visites",
    "admin.unique_visitors": "visiteurs uniques",
    "admin.top_sellers": "🥇 Top vendeurs",
    "admin.top_products": "🔥 Top produits",
    "admin.all_users": "Liste des utilisateurs",
    "admin.all_shops": "Toutes les boutiques",
    "admin.all_orders": "Toutes les commandes",
    "admin.all_roles": "Tous les rôles",
    "admin.all_status": "Tous les statuts",
    "admin.add_category": "➕ Ajouter une catégorie",
    "admin.seed_categories": "⚡ Créer les catégories de base",
    "admin.no_categories": "Aucune catégorie",
    "admin.no_categories_p": "Créez les catégories de base pour permettre aux vendeurs de classer leurs produits.",
    "admin.no_users": "Aucun utilisateur.",
    "admin.no_shops": "Aucune boutique.",
    "admin.no_orders": "Aucune commande.",
    
    // Admin - Nouvelles clés
    "admin.users_label": "Utilisateurs",
    "admin.shops_label": "Boutiques",
    "admin.products_label": "Produits",
    "admin.orders_label": "Commandes",
    "admin.users_count": "utilisateur(s) sur la plateforme",
    "admin.shops_count": "boutique(s) active(s)",
    "admin.orders_count": "commande(s) sur la plateforme",
    "admin.categories_count": "catégorie(s) au total",
    "admin.id": "ID",
    "admin.name": "Nom",
    "admin.phone": "Téléphone",
    "admin.email": "Email",
    "admin.role": "Rôle",
    "admin.date": "Inscription",
    "admin.description": "Description",
    "admin.views": "Vues",
    "admin.view": "Voir →",
    "admin.product": "Produit",
    "admin.quantity": "Quantité",
    "admin.total": "Total",
    "admin.status": "Statut",
    "admin.emoji": "Emoji",
    "admin.order_label": "Ordre",
    "admin.actions": "Actions",
    "admin.active": "Active",
    "admin.inactive": "Inactive",
    "admin.edit": "Modifier",
    "admin.delete": "Supprimer",
    "admin.save": "Enregistrer",
    "admin.create": "Créer",
    "admin.no_visits": "Aucune donnée de visite pour cette période.",
    "admin.rankings_p": "Les meilleurs vendeurs et produits de la plateforme.",
    "admin.no_sales": "Aucune vente pour l'instant.",
    "admin.no_products_sold": "Aucun produit vendu pour l'instant.",
    "admin.shop_label": "Boutique",
    
    // Admin - Localités / Marchés / Code
    "admin.locality": "Localité",
    "admin.market": "Marché",
    "admin.shop_code": "Code",
    
    // ============================================================
    // BOUTIQUE (CRÉATION)
    // ============================================================
    "shop.create_title": "Créez votre boutique",
    "shop.create_p": "C'est la dernière étape avant de pouvoir vendre. Donnez un nom à votre boutique et commencez à ajouter des produits.",
    "shop.benefits": "Ce que vous obtenez :",
    "shop.benefit_1": "Vitrine en ligne gratuite et personnalisable",
    "shop.benefit_2": "Notifications en temps réel des commandes",
    "shop.benefit_3": "Tableau de bord avec statistiques",
    "shop.benefit_4": "Visible par des milliers d'acheteurs",
    "shop.name": "Nom de la boutique",
    "shop.name_hint": "Choisissez un nom court et mémorable.",
    "shop.description": "Description (optionnel)",
    "shop.description_placeholder": "Décrivez votre boutique en quelques mots...",
    "shop.photo": "Photo de la boutique (optionnel)",
    "shop.photo_click": "Cliquez pour ajouter une photo",
    "shop.create_btn": "Créer ma boutique →",
    
    // Localisation boutique
    "shop.location": "Localisation de la boutique",
    "shop.location_hint": "Cliquez sur la carte pour placer votre boutique. Vous pouvez aussi déplacer le marqueur.",
    "shop.locality": "Localité (auto-rempli)",
    "shop.market": "Marché / zone commerciale (optionnel)",
    "shop.code_label": "Code boutique",
    
    // ============================================================
    // DEVENIR VENDEUR
    // ============================================================
    "upgrade.title": "Devenez vendeur",
    "upgrade.subtitle": "Ajoutez quelques informations et commencez à vendre sur Finest Global.",
    "upgrade.benefits": "Ce que vous obtenez :",
    "upgrade.submit": "Devenir vendeur",
    "upgrade.firstname": "Prénom",
    "upgrade.lastname": "Nom",
    "upgrade.email": "Email",
    "upgrade.password": "Mot de passe",
    "upgrade.password_hint": "Ce mot de passe vous servira pour les connexions futures.",
    
    // ============================================================
    // À PROPOS (about.html)
    // ============================================================
    "about.hero_title": "Rendre le commerce",
    "about.hero_visible": "plus simple.",
    "about.hero_slogan": "Soyez Trouvable.",
    "about.hero_p1": "Finest Global est une marketplace digitale qui connecte les personnes, les entreprises, les produits, les services et les opportunités commerciales dans un écosystème connecté.",
    "about.hero_p2": "Notre objectif est de créer davantage d'opportunités économiques, de rendre le commerce plus simple et de faciliter la circulation de l'argent au sein des pays et au-delà des frontières.",
    "about.hero_tagline": "Connecter les Personnes • Valoriser les Entreprises • Créer des Possibilités.",
    
    "about.stats_sellers": "Vendeurs actifs",
    "about.stats_products": "Produits en ligne",
    "about.stats_networks": "Réseaux supportés",
    "about.stats_free": "Gratuit pour démarrer",
    
    "about.problem_title": "Le Problème Que Nous Résolvons",
    "about.problem_subtitle": "Le commerce devrait être plus simple.",
    "about.problem_1_title": "Les entreprises peinent",
    "about.problem_1_p": "Les entreprises ont du mal à atteindre les clients qui ont besoin de leurs produits et services. Les clients ont du mal à trouver ce dont ils ont besoin, tandis que les prestataires de services font face à des difficultés pour connecter leurs compétences aux opportunités commerciales.",
    "about.problem_2_title": "Des plateformes dispersées",
    "about.problem_2_p": "Avec la découverte d'entreprises, la communication et les services de support souvent dispersés sur différentes plateformes, connecter les bonnes personnes peut être inutilement difficile.",
    "about.problem_3_title": "Combler les écarts",
    "about.problem_3_p": "Finest Global vise à combler ces écarts en rapprochant les activités commerciales.",
    
    "about.solution_title": "Notre Solution",
    "about.solution_subtitle": "Rassembler le Commerce dans un Seul Écosystème Digital.",
    "about.solution_intro": "Finest Global est une marketplace digitale dédiée au commerce, connectant :",
    "about.solution_1_title": "Les entreprises",
    "about.solution_1_p": "Présentez vos produits et services et devenez plus facile à découvrir.",
    "about.solution_2_title": "Les clients",
    "about.solution_2_p": "Trouvez les produits, services et entreprises qui répondent à vos besoins.",
    "about.solution_3_title": "Les prestataires de services",
    "about.solution_3_p": "Connectez-vous aux opportunités commerciales grâce à des services tels que la livraison, le marketing digital, la création de contenu, la consultation et autres supports professionnels.",
    
    "about.after_solution_1": "Nous ne remplaçons pas le marché physique. Nous l'adaptons à la réalité digitale.",
    "about.after_solution_2": "Les marchés continueront d'exister — mais leurs commerçants seront visibles, trouvables et connectés à leurs clients.",
    "about.after_solution_3": "Notre objectif : créer un écosystème fort entre les entreprises, les clients et les créateurs de contenu.",
    
    "about.vision_title": "Notre Vision",
    "about.vision_subtitle": "Un Marché Digital Connectant les Personnes à Travers les Pays.",
    "about.vision_1": "Notre vision est de construire un marché digital qui puisse servir de pont commercial entre les personnes, les entreprises et les opportunités à travers les pays.",
    "about.vision_2": "Notre mission est de connecter les personnes, les entreprises, les produits, les services et les opportunités à travers des solutions digitales qui créent de la valeur et facilitent des connexions significatives.",
    "about.vision_3": "Nous visons à rendre le commerce plus accessible, à soutenir la croissance des entreprises et à aider à créer des opportunités économiques à travers un écosystème digital plus connecté.",
    
    "about.cta_title": "Rejoignez l'Écosystème Finest Global",
    "about.cta_tagline": "Il Y a une Place Pour Vous sur Finest Global.",
    "about.cta_p": "Que vous souhaitiez découvrir des produits et services, présenter votre entreprise ou proposer des services professionnels, Finest Global est conçu pour connecter les personnes à ce dont elles ont besoin et aux opportunités qu'elles recherchent.",
    "about.explore": "Explorer la marketplace →",
    "about.become_seller": "Devenir vendeur",
  },
  
  en: {
    // Navigation
    "nav.home": "Home",
    "nav.marketplace": "Marketplace",
    "nav.about": "About",
    "nav.search_placeholder": "Search for a product, a shop...",
    "nav.login": "Log in",
    "nav.register": "Sign up",
    "nav.dashboard": "My dashboard",
    "nav.dashboard_admin": "Admin dashboard",
    "nav.orders": "My orders",
    "nav.become_seller": "Become a seller",
    "nav.logout": "Log out",
    "nav.profile": "My profile",
    
    // Rôles
    "role.admin": "Admin",
    "role.seller": "Seller",
    "role.client": "Customer",
    
    // ============================================================
    // HOME (index.html)
    // ============================================================
    "home.hero_1": "Be Findable.",
    "home.hero_2": "Become Visible.",
    "home.hero_p": "Finest Global makes market vendors visible, findable and connected to their customers. Without replacing the physical market — simply making it accessible.",
    "home.explore": "Explore marketplace →",
    "home.become_seller": "Become a seller",
    
    // Categories
    "home.categories_title": "Explore Categories",
    "home.categories_p": "Browse products and services by category to find what you're looking for.",
    
    // Trending
    "home.trending_title": "Discover Products & Services",
    "home.trending_p": "Explore available products and services from businesses across the marketplace.",
    
    // Shops
    "home.shops_title": "New on Finest Global",
    "home.shops_p": "Discover newly registered businesses and explore their storefronts.",
    
    // CTA seller
    "home.cta_title": "Have something to sell or a service to offer?",
    "home.cta_p": "Create your free storefront on Finest Global and start showcasing what you offer.",
    "home.cta_btn": "Become a Seller",
    "home.cta_1": "Free Online Storefront",
    "home.cta_2": "Stay Updated on Activity",
    "home.cta_3": "Reach Potential Customers",
    "home.cta_4": "Free to Join",
    "home.cta_5": "French-Language Support",
    
    // Near you
    "home.near_you_title": "Discover Near You",
    "home.near_you_p": "Find products, shops and services near your current location.",
    "home.detect_location": "Detect my location",
    "home.detecting": "Detecting...",
    "home.location_detected": "Location detected",
    "home.location_denied": "Unable to detect your location. Check your settings.",
    "home.see_nearby": "See nearby shops →",
    "home.search_by_code": "Business-code search",
    "home.enter_code": "Looking for a Specific Business? Enter its Finest Global business code to find its storefront.",
    "home.find_shop": "Find",
    "home.code_not_found": "No shop found with this code.",
    
    // Footer
    "footer.tagline": "A digital marketplace connecting people, businesses, products and services. Discover opportunities, reach customers and make connections beyond physical boundaries.",
    "footer.navigation": "Navigation",
    "footer.sellers": "Sellers",
    "footer.contact": "Connect with us",
    "footer.create_shop": "Create a storefront",
    "footer.my_dashboard": "My dashboard",
    "footer.my_orders": "My orders",
    "footer.rights": "All rights reserved.",
    
    // ============================================================
    // MARKETPLACE
    // ============================================================
    "marketplace.filters": "Filters",
    "marketplace.clear_all": "Clear all",
    "marketplace.categories": "Categories",
    "marketplace.colors": "Colors",
    "marketplace.price": "Price (FCFA)",
    "marketplace.apply": "Apply",
    "marketplace.min": "Min",
    "marketplace.max": "Max",
    "marketplace.sort_sales": "🔥 Best sellers",
    "marketplace.sort_recent": "🆕 Newest",
    "marketplace.sort_views": "👁️ Most viewed",
    "marketplace.sort_price_asc": "💰 Price: low to high",
    "marketplace.sort_price_desc": "💎 Price: high to low",
    "marketplace.sort_distance": "📍 Closest",
    "marketplace.products_found": "product(s) found",
    "marketplace.no_products": "No product found",
    "marketplace.no_products_p": "Try other keywords or reset the filters.",
    "marketplace.reset_filters": "Reset filters",
    "marketplace.previous": "← Previous",
    "marketplace.next": "Next →",
    "marketplace.close_filters": "✕ Close filters",
    
    // Geographic filters
    "marketplace.locality": "Locality",
    "marketplace.market": "Market / Area",
    "marketplace.all_localities": "All localities",
    "marketplace.all_markets": "All markets",
    "marketplace.near_me": "📍 Near me",
    "marketplace.radius": "Radius (km)",
    "marketplace.detecting_location": "Detecting your location...",
    "marketplace.location_detected": "Location detected",
    "marketplace.distance": "Distance",
    "marketplace.no_location": "Location unavailable",
    
    // ============================================================
    // PRODUCT / SHOP
    // ============================================================
    "product.order_now": "🛒 Order now",
    "product.out_of_stock": "Product unavailable",
    "product.sold_by": "Sold by",
    "product.see_shop": "View →",
    "product.quantity": "Quantity:",
    "product.sales": "Sales",
    "product.views": "Views",
    "product.stock": "Stock",
    "product.related": "📦 You may also like",
    "product.all_products": "All products",
    "product.confirm_order": "Confirm order",
    "product.order_summary": "Summary",
    "product.price_unit": "Unit price",
    "product.total": "Total",
    "product.note": "Note for the seller (optional)",
    "product.note_placeholder": "Ex: Delivery in Cotonou, Fidjrossè district...",
    "product.confirm": "Confirm order",
    "product.cancel": "Cancel",
    "product.no_products": "No products",
    "product.no_products_p": "This shop doesn't have any products yet.",
    "product.similar": "📦 You may also like",
    "product.how_it_works": "💡 How does it work?",
    "product.how_it_works_p": "The seller receives your order instantly. They will contact you to organize the delivery.",
    
    // Availability
    "product.in_stock": "In stock",
    "product.out_of_stock_label": "Out of stock",
    "product.to_confirm": "Availability to confirm",
    "product.availability": "Availability",
    
    // Shop location
    "product.shop_code": "Shop code",
    "product.shop_locality": "Locality",
    "product.shop_market": "Market",
    "product.distance_from_you": "Distance",
    
    // ============================================================
    // LOGIN / REGISTER
    // ============================================================
    "login.title": "Welcome back 👋",
    "login.subtitle": "Log in to your Finest Global account",
    "login.phone": "Phone number",
    "login.password": "Password",
    "login.submit": "Log in",
    "login.no_account": "Don't have an account yet?",
    "login.signup_link": "Sign up",
    
    "register.title": "Create an account",
    "register.subtitle": "Join Finest Global in a few seconds",
    "register.client": "Customer",
    "register.client_desc": "Buy",
    "register.seller": "Seller",
    "register.seller_desc": "Sell",
    "register.firstname": "First name",
    "register.lastname": "Last name",
    "register.email": "Email",
    "register.phone": "Phone number",
    "register.password": "Password",
    "register.submit_client": "Create my customer account",
    "register.submit_seller": "Create my seller account",
    "register.has_account": "Already have an account?",
    "register.login_link": "Log in",
    "register.phone_hint": "Format: 01 + 8 digits.",
    "register.password_hint": "At least 6 characters.",
    
    // ============================================================
    // ORDERS
    // ============================================================
    "orders.title": "📦 My orders",
    "orders.subtitle": "Track your orders in real time.",
    "orders.all": "All",
    "orders.pending": "⏳ Pending",
    "orders.confirmed": "✅ Confirmed",
    "orders.delivered": "📦 Delivered",
    "orders.cancelled": "❌ Cancelled",
    "orders.empty": "You don't have any orders yet",
    "orders.empty_p": "Browse the marketplace and place your first order.",
    "orders.explore": "Explore marketplace →",
    "orders.no_in_category": "No order in this category",
    "orders.try_other": "Try another filter.",
    "orders.status_pending": "Pending",
    "orders.status_confirmed": "Confirmed",
    "orders.status_delivered": "Delivered",
    "orders.status_cancelled": "Cancelled",
    "orders.cancel": "Cancel",
    "orders.quantity": "Quantity",
    "orders.order_id": "Order",
    "orders.shop": "Shop",
    
    // ============================================================
    // SELLER DASHBOARD
    // ============================================================
    "seller.hello": "Hello",
    "seller.overview": "Overview",
    "seller.orders": "Orders",
    "seller.products": "My products",
    "seller.shop": "My shop",
    "seller.revenue": "Revenue",
    "seller.total_sales": "Total sales",
    "seller.product_views": "Product views",
    "seller.pending": "Pending",
    "seller.top_products": "🏆 Top products",
    "seller.orders_by_status": "📊 Orders by status",
    "seller.add_product": "➕ Add a product",
    "seller.no_products": "No products yet",
    "seller.no_products_p": "Add your first product to start selling.",
    "seller.no_orders": "No orders yet",
    "seller.no_orders_p": "You will receive a notification as soon as a customer orders.",
    "seller.orders_received": "📦 Orders received",
    "seller.orders_received_p": "Manage your customer orders in real time.",
    "seller.my_products": "🛍️ My products",
    "seller.my_products_p": "product(s) in your shop",
    "seller.my_shop": "🏪 My shop",
    "seller.my_shop_p": "Customize your shop information.",
    "seller.confirm": "✅ Confirm",
    "seller.cancel": "❌ Cancel",
    "seller.deliver": "📦 Mark as delivered",
    "seller.notifications_active": "Notifications active",
    "seller.new_order": "New order",
    "seller.product": "Product",
    "seller.edit": "✏️ Edit",
    
    // Seller location
    "seller.shop_location": "Shop location",
    "seller.shop_location_p": "Move the marker on the map to change your shop position.",
    "seller.save_location": "Save location",
    "seller.location_saved": "Location updated",
    "seller.shop_code": "Shop code",
    "seller.shop_code_p": "Share this code with your customers so they can easily find your shop.",
    
    // Seller availability
    "seller.availability": "Availability",
    "seller.availability_in_stock": "In stock",
    "seller.availability_out_of_stock": "Out of stock",
    "seller.availability_to_confirm": "Availability to confirm",
    
    // ============================================================
    // ADMIN DASHBOARD
    // ============================================================
    "admin.sidebar_title": "👑 Admin",
    "admin.title": "Overview 👑",
    "admin.subtitle": "Global statistics of the Finest Global platform.",
    "admin.overview": "Overview",
    "admin.users": "👥 Users",
    "admin.shops": "🏪 Shops",
    "admin.products": "🛍️ Products",
    "admin.orders": "📦 Orders",
    "admin.categories": "🏷️ Categories",
    "admin.rankings": "🏆 Rankings",
    "admin.revenue": "Revenue",
    "admin.pending": "Pending",
    "admin.sellers": "Sellers",
    "admin.clients": "Customers",
    "admin.visitors": "📈 Visitors",
    "admin.day": "Day",
    "admin.week": "Week",
    "admin.month": "Month",
    "admin.visits": "visits",
    "admin.unique_visitors": "unique visitors",
    "admin.top_sellers": "🥇 Top sellers",
    "admin.top_products": "🔥 Top products",
    "admin.all_users": "Users list",
    "admin.all_shops": "All shops",
    "admin.all_orders": "All orders",
    "admin.all_roles": "All roles",
    "admin.all_status": "All statuses",
    "admin.add_category": "➕ Add a category",
    "admin.seed_categories": "⚡ Create default categories",
    "admin.no_categories": "No categories",
    "admin.no_categories_p": "Create default categories to let sellers classify their products.",
    "admin.no_users": "No users.",
    "admin.no_shops": "No shops.",
    "admin.no_orders": "No orders.",
    
    // Admin - New keys
    "admin.users_label": "Users",
    "admin.shops_label": "Shops",
    "admin.products_label": "Products",
    "admin.orders_label": "Orders",
    "admin.users_count": "user(s) on the platform",
    "admin.shops_count": "active shop(s)",
    "admin.orders_count": "order(s) on the platform",
    "admin.categories_count": "categor(ies) total",
    "admin.id": "ID",
    "admin.name": "Name",
    "admin.phone": "Phone",
    "admin.email": "Email",
    "admin.role": "Role",
    "admin.date": "Registration",
    "admin.description": "Description",
    "admin.views": "Views",
    "admin.view": "View →",
    "admin.product": "Product",
    "admin.quantity": "Quantity",
    "admin.total": "Total",
    "admin.status": "Status",
    "admin.emoji": "Emoji",
    "admin.order_label": "Order",
    "admin.actions": "Actions",
    "admin.active": "Active",
    "admin.inactive": "Inactive",
    "admin.edit": "Edit",
    "admin.delete": "Delete",
    "admin.save": "Save",
    "admin.create": "Create",
    "admin.no_visits": "No visit data for this period.",
    "admin.rankings_p": "The best sellers and products on the platform.",
    "admin.no_sales": "No sales yet.",
    "admin.no_products_sold": "No product sold yet.",
    "admin.shop_label": "Shop",
    
    // Admin locality/market/code
    "admin.locality": "Locality",
    "admin.market": "Market",
    "admin.shop_code": "Code",
    
    // ============================================================
    // SHOP (CREATION)
    // ============================================================
    "shop.create_title": "Create your shop",
    "shop.create_p": "This is the last step before you can sell. Give your shop a name and start adding products.",
    "shop.benefits": "What you get:",
    "shop.benefit_1": "Free and customizable online storefront",
    "shop.benefit_2": "Real-time order notifications",
    "shop.benefit_3": "Dashboard with statistics",
    "shop.benefit_4": "Visible to thousands of buyers",
    "shop.name": "Shop name",
    "shop.name_hint": "Choose a short and memorable name.",
    "shop.description": "Description (optional)",
    "shop.description_placeholder": "Describe your shop in a few words...",
    "shop.photo": "Shop photo (optional)",
    "shop.photo_click": "Click to add a photo",
    "shop.create_btn": "Create my shop →",
    
    // Shop location
    "shop.location": "Shop location",
    "shop.location_hint": "Click on the map to place your shop. You can also drag the marker.",
    "shop.locality": "Locality (auto-filled)",
    "shop.market": "Market / commercial area (optional)",
    "shop.code_label": "Shop code",
    
    // ============================================================
    // BECOME SELLER
    // ============================================================
    "upgrade.title": "Become a seller",
    "upgrade.subtitle": "Add a few information and start selling on Finest Global.",
    "upgrade.benefits": "What you get:",
    "upgrade.submit": "Become a seller",
    "upgrade.firstname": "First name",
    "upgrade.lastname": "Last name",
    "upgrade.email": "Email",
    "upgrade.password": "Password",
    "upgrade.password_hint": "This password will be used for future logins.",
    
    // ============================================================
    // ABOUT (about.html)
    // ============================================================
    "about.hero_title": "Making commerce",
    "about.hero_visible": "easier.",
    "about.hero_slogan": "Be Findable.",
    "about.hero_p1": "Finest Global is a digital marketplace connecting people, businesses, products, services and commercial opportunities in one connected ecosystem.",
    "about.hero_p2": "Our goal is to create more economic opportunities, make commerce easier and facilitate the circulation of money within countries and across borders.",
    "about.hero_tagline": "Connecting People • Empowering Businesses • Creating Possibilities.",
    
    "about.stats_sellers": "Active sellers",
    "about.stats_products": "Online products",
    "about.stats_networks": "Supported networks",
    "about.stats_free": "Free to get started",
    
    "about.problem_title": "The Problem We Solve",
    "about.problem_subtitle": "Commerce Should Be Easier.",
    "about.problem_1_title": "Businesses struggle",
    "about.problem_1_p": "Businesses struggle to reach the customers who need their products and services. Customers struggle to find what they need, while service providers face challenges connecting their skills with commercial opportunities.",
    "about.problem_2_title": "Scattered platforms",
    "about.problem_2_p": "With business discovery, communication and supporting services often scattered across different platforms, connecting the right people can be unnecessarily difficult.",
    "about.problem_3_title": "Bridging the gaps",
    "about.problem_3_p": "Finest Global aims to bridge these gaps by bringing commercial activities closer together.",
    
    "about.solution_title": "Our Solution",
    "about.solution_subtitle": "Bringing Commerce Together in One Digital Ecosystem.",
    "about.solution_intro": "Finest Global is a digital marketplace dedicated to commerce, connecting:",
    "about.solution_1_title": "Businesses",
    "about.solution_1_p": "Showcase products and services and become easier to discover.",
    "about.solution_2_title": "Customers",
    "about.solution_2_p": "Find products, services and businesses that meet their needs.",
    "about.solution_3_title": "Service Providers",
    "about.solution_3_p": "Connect with commercial opportunities through services such as delivery, digital marketing, content creation, consultation and other professional support.",
    
    "about.after_solution_1": "We don't replace the physical market. We adapt it to digital reality.",
    "about.after_solution_2": "Markets will continue to exist — but their merchants will be visible, findable and connected to their customers.",
    "about.after_solution_3": "Our goal: create a strong ecosystem between businesses, customers and content creators.",
    
    "about.vision_title": "Our Vision",
    "about.vision_subtitle": "A Digital Market Connecting People Across Countries.",
    "about.vision_1": "Our vision is to build a digital market that can serve as a commercial bridge between people, businesses and opportunities across countries.",
    "about.vision_2": "Our mission is to connect people, businesses, products, services and opportunities through digital solutions that create value and facilitate meaningful connections.",
    "about.vision_3": "We aim to make commerce more accessible, support business growth and help create economic opportunities through a more connected digital ecosystem.",
    
    "about.cta_title": "Join the Finest Global Ecosystem",
    "about.cta_tagline": "There Is a Place for You on Finest Global.",
    "about.cta_p": "Whether you want to discover products and services, showcase your business or offer professional services, Finest Global is being built to connect people with what they need and the opportunities they seek.",
    "about.explore": "Explore the marketplace →",
    "about.become_seller": "Become a seller",
  }
};


// ============================================================
// GESTION DE LA LANGUE
// ============================================================

const LANG_KEY = 'fg_language';

function getCurrentLanguage() {
  const stored = localStorage.getItem(LANG_KEY);
  if (stored && (stored === 'fr' || stored === 'en')) {
    return stored;
  }
  
  const browserLang = (navigator.language || 'fr').toLowerCase();
  if (browserLang.startsWith('en')) return 'en';
  return 'fr';
}

function setLanguage(lang) {
  if (lang !== 'fr' && lang !== 'en') return;
  localStorage.setItem(LANG_KEY, lang);
  window.location.reload();
}

function t(key) {
  const lang = getCurrentLanguage();
  const dict = TRANSLATIONS[lang] || TRANSLATIONS.fr;
  return dict[key] || TRANSLATIONS.fr[key] || key;
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const translation = t(key);
    
    const attr = el.getAttribute('data-i18n-attr');
    if (attr) {
      el.setAttribute(attr, translation);
    } else {
      el.textContent = translation;
    }
  });
  
  document.documentElement.setAttribute('lang', getCurrentLanguage());
}

document.addEventListener('DOMContentLoaded', () => {
  applyTranslations();
});