/* ============================================================
   FINEST GLOBAL — Navbar dynamique
   ============================================================ */

function renderNavbar() {
  const navContainer = document.getElementById('navbar');
  if (!navContainer) return;
  
  const user = Auth.getUser();
  const isAuth = Auth.isAuthenticated();
  const currentLang = getCurrentLanguage();
  const isHomePage = window.location.pathname === '/' || window.location.pathname.endsWith('/index.html');
  
  // Sélecteur de langue
  const langSelector = `
    <div class="lang-selector">
      <button 
        class="lang-btn ${currentLang === 'fr' ? 'active' : ''}" 
        onclick="setLanguage('fr')"
        aria-label="Français"
        title="Français"
      >🇫🇷</button>
      <button 
        class="lang-btn ${currentLang === 'en' ? 'active' : ''}" 
        onclick="setLanguage('en')"
        aria-label="English"
        title="English"
      >🇬🇧</button>
    </div>
  `;
  
  // Partie droite : auth ou profil
  let rightSection = '';
  
  if (!isAuth) {
    if (isHomePage) {
      // Sur l'accueil : icône de login
      rightSection = `
        <div class="nav-user">
          <a href="/login.html" class="nav-user-btn" aria-label="Se connecter">
            <span class="nav-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </span>
          </a>
        </div>
      `;
    } else {
      // Sur les autres pages : boutons classiques
      rightSection = `
        <div class="nav-auth">
          <a href="/login.html" class="btn btn-ghost btn-sm">${t('nav.login')}</a>
          <a href="/register.html" class="btn btn-primary btn-sm">${t('nav.register')}</a>
        </div>
      `;
    }
  } else {
    const initials = (
      (user.first_name?.[0] || '') + (user.last_name?.[0] || '')
    ).toUpperCase() || user.phone.slice(-2);
    
    let dashboardLink = '';
    if (user.role === 'admin') {
      dashboardLink = `<a href="/dashboard-admin.html" class="dropdown-item">👑 ${t('nav.dashboard_admin')}</a>`;
    } else if (user.role === 'seller') {
      dashboardLink = `<a href="/dashboard-seller.html" class="dropdown-item">📊 ${t('nav.dashboard')}</a>`;
    } else {
      dashboardLink = `<a href="/become-seller.html" class="dropdown-item">🚀 ${t('nav.become_seller')}</a>`;
    }
    
    const roleBadgeClass = user.role === 'admin' ? 'danger' : user.role === 'seller' ? 'orange' : 'blue';
    const roleLabel = t('role.' + user.role);
    
    rightSection = `
      <div class="nav-user" id="nav-user-menu">
        <button class="nav-user-btn" onclick="toggleUserMenu(event)" aria-label="${t('nav.profile')}">
          <span class="nav-avatar" style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,var(--ginger-400),var(--ginger-600));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;flex-shrink:0;box-shadow:0 2px 8px rgba(217,98,43,0.3);color:white;">${initials}</span>
          <span class="nav-user-name">${user.first_name || user.phone}</span>
          <span class="nav-chevron">▾</span>
        </button>
        <div class="nav-dropdown" id="nav-dropdown">
          <div class="dropdown-header">
            <div class="dropdown-name">${user.first_name || ''} ${user.last_name || ''}</div>
            <div class="dropdown-phone">${user.phone}</div>
            <div class="dropdown-role badge badge-${roleBadgeClass}">
              ${roleLabel}
            </div>
          </div>
          <div class="dropdown-divider"></div>
          ${dashboardLink}
          <a href="/orders.html" class="dropdown-item">📦 ${t('nav.orders')}</a>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item dropdown-item-danger" onclick="Auth.logout()">
            🚪 ${t('nav.logout')}
          </button>
        </div>
      </div>
    `;
  }
  
  navContainer.innerHTML = `
    <div class="navbar-inner">
      <div class="navbar-logo-wrapper">
        <a href="/index.html" class="navbar-logo" aria-label="Finest Global">
          <img src="/assets/finest.png" alt="Finest Global" class="navbar-logo-img">
        </a>
      </div>
      
      <div class="navbar-search">
        <input 
          type="text" 
          id="navbar-search-input"
          placeholder="${t('nav.search_placeholder')}"
          autocomplete="off"
        />
        <div class="navbar-suggestions" id="navbar-suggestions"></div>
      </div>
      
      <div class="navbar-links">
        ${baseLinksForScreen()}
      </div>
      
      ${langSelector}
      
      ${rightSection}
    </div>
  `;
  
  initNavbarSearch();
  
  // La navbar est en position fixe : on indique au CSS sa hauteur
  // pour décaler le contenu des pages (hors accueil)
  document.body.classList.add('has-navbar');
  syncNavbarHeight();
  observeNavbarHeight();
}

/**
 * Mesure la hauteur de la navbar et la publie dans la variable CSS --navbar-h.
 */
function syncNavbarHeight() {
  const nav = document.getElementById('navbar');
  if (!nav) return;
  document.documentElement.style.setProperty('--navbar-h', nav.offsetHeight + 'px');
}

/**
 * Re-mesure automatiquement la navbar si sa taille change
 * (rotation, barre de recherche sur 2 lignes, chargement du logo...).
 */
let _navbarObserver = null;
function observeNavbarHeight() {
  const nav = document.getElementById('navbar');
  if (!nav || _navbarObserver || !('ResizeObserver' in window)) return;
  _navbarObserver = new ResizeObserver(syncNavbarHeight);
  _navbarObserver.observe(nav);
}

/**
 * Retourne les liens selon la taille d'écran.
 */
function baseLinksForScreen() {
  const isMobile = window.innerWidth <= 900;
  
  if (isMobile) {
    return `<a href="/marketplace.html" class="nav-link">${t('nav.marketplace')}</a>`;
  }
  
  return `
    <a href="/index.html" class="nav-link">${t('nav.home')}</a>
    <a href="/marketplace.html" class="nav-link">${t('nav.marketplace')}</a>
    <a href="/about.html" class="nav-link">${t('nav.about')}</a>
  `;
}

/**
 * Met à jour les liens lors du redimensionnement.
 */
function updateNavLinksForScreenSize() {
  const linksContainer = document.querySelector('.navbar-links');
  if (!linksContainer) return;
  linksContainer.innerHTML = baseLinksForScreen();
}

/**
 * Toggle du menu utilisateur.
 */
function toggleUserMenu(event) {
  event.stopPropagation();
  const dropdown = document.getElementById('nav-dropdown');
  if (dropdown) dropdown.classList.toggle('open');
}

/**
 * Autocomplétion dans la navbar.
 */
function initNavbarSearch() {
  const input = document.getElementById('navbar-search-input');
  const suggestions = document.getElementById('navbar-suggestions');
  if (!input || !suggestions) return;
  
  let debounceTimer;
  
  input.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const q = e.target.value.trim();
    
    if (q.length < 2) {
      suggestions.classList.remove('open');
      return;
    }
    
    debounceTimer = setTimeout(async () => {
      try {
        const data = await SearchAPI.suggest(q);
        if (data.suggestions.length === 0) {
          suggestions.classList.remove('open');
          return;
        }
        
        suggestions.innerHTML = data.suggestions.map(s => `
          <div class="suggestion-item" onclick="goToSearch('${escapeHtml(s.text)}')">
            <span class="suggestion-type">${
              s.type === 'product' ? '📦' :
              s.type === 'category' ? '🏷️' :
              s.type === 'color' ? '🎨' : '🏪'
            }</span>
            <span>${escapeHtml(s.text)}</span>
          </div>
        `).join('');
        suggestions.classList.add('open');
      } catch (error) {
        console.error('Erreur suggestions:', error);
      }
    }, 250);
  });
  
  document.addEventListener('click', () => {
    suggestions.classList.remove('open');
  });
  
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      goToSearch(input.value.trim());
    }
  });
}

/**
 * Redirige vers la marketplace avec la recherche.
 */
function goToSearch(query) {
  if (!query) return;
  window.location.href = `/marketplace.html?q=${encodeURIComponent(query)}`;
}

/**
 * Échappe le HTML.
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Mettre à jour la navbar lors du redimensionnement
let _navbarResizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(_navbarResizeTimer);
  _navbarResizeTimer = setTimeout(() => {
    updateNavLinksForScreenSize();
    syncNavbarHeight();
  }, 200);
});

// Re-mesure une fois la page et les images entièrement chargées
window.addEventListener('load', syncNavbarHeight);

// Fermer le menu au clic ailleurs
document.addEventListener('click', (e) => {
  const dropdown = document.getElementById('nav-dropdown');
  const userMenu = document.getElementById('nav-user-menu');
  if (dropdown && userMenu && !userMenu.contains(e.target)) {
    dropdown.classList.remove('open');
  }
});

// ============================================================
// LOGIQUE DE LA NAVBAR AU DÉFILEMENT (TOUTES LES PAGES)
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  const isHomePage = window.location.pathname === '/' || window.location.pathname.endsWith('/index.html');
  
  // Classe spécifique à l'accueil (logo géant, icône login, etc.)
  if (isHomePage) {
    document.body.classList.add('page-home');
  }
  
  // ✅ Scroll listener actif sur TOUTES les pages
  const applyNavScrolled = () => {
    if (window.scrollY > 40) {
      document.body.classList.add('nav-scrolled');
    } else {
      document.body.classList.remove('nav-scrolled');
    }
  };
  
  applyNavScrolled();
  window.addEventListener('scroll', applyNavScrolled, { passive: true });
});