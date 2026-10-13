/* ============================================================
   FINEST GLOBAL — Navbar dynamique
   Desktop : recherche + Accueil + Marketplace + À propos + profil + langue
   Mobile : logo + Marketplace + langue + avatar
   ============================================================ */

function renderNavbar() {
  const navContainer = document.getElementById('navbar');
  if (!navContainer) return;
  
  const user = Auth.getUser();
  const isAuth = Auth.isAuthenticated();
  const currentLang = getCurrentLanguage();
  
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
    rightSection = `
      <div class="nav-auth">
        <a href="/login.html" class="btn btn-ghost btn-sm">${t('nav.login')}</a>
        <a href="/register.html" class="btn btn-primary btn-sm">${t('nav.register')}</a>
      </div>
    `;
  } else {
    const initials = (
      (user.first_name?.[0] || '') + (user.last_name?.[0] || '')
    ).toUpperCase() || user.phone.slice(-2);
    
    // Lien dashboard selon le rôle
    let dashboardLink = '';
    if (user.role === 'admin') {
      dashboardLink = `<a href="/dashboard-admin.html" class="dropdown-item">👑 ${t('nav.dashboard_admin')}</a>`;
    } else if (user.role === 'seller') {
      dashboardLink = `<a href="/dashboard-seller.html" class="dropdown-item">📊 ${t('nav.dashboard')}</a>`;
    } else {
      dashboardLink = `<a href="/become-seller.html" class="dropdown-item">🚀 ${t('nav.become_seller')}</a>`;
    }
    
    // Badge rôle
    const roleBadgeClass = user.role === 'admin' ? 'danger' : user.role === 'seller' ? 'orange' : 'blue';
    const roleLabel = t('role.' + user.role);
    
    rightSection = `
      <div class="nav-user" id="nav-user-menu">
        <button class="nav-user-btn" onclick="toggleUserMenu(event)" aria-label="${t('nav.profile')}">
          <span class="nav-avatar">${initials}</span>
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
      <a href="/index.html" class="navbar-logo" aria-label="Finest Global">
        <img src="/assets/logo.png" alt="Finest Global" class="navbar-logo-img">
      </a>
      
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
  
  // Initialiser l'autocomplétion (uniquement si la barre existe)
  initNavbarSearch();
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
 * Autocomplétion dans la navbar (desktop uniquement).
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
  }, 200);
});

// Fermer le menu au clic ailleurs
document.addEventListener('click', (e) => {
  const dropdown = document.getElementById('nav-dropdown');
  const userMenu = document.getElementById('nav-user-menu');
  if (dropdown && userMenu && !userMenu.contains(e.target)) {
    dropdown.classList.remove('open');
  }
});