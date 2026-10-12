/* ============================================================
   FINEST GLOBAL — Navbar dynamique
   ============================================================ */

/**
 * Affiche la navbar dans l'élément #navbar.
 * S'adapte selon connecté / non connecté et le rôle.
 */
function renderNavbar() {
  const navContainer = document.getElementById('navbar');
  if (!navContainer) return;
  
  const user = Auth.getUser();
  const isAuth = Auth.isAuthenticated();
  
  // Liens de base (toujours visibles)
  const baseLinks = `
    <a href="/index.html" class="nav-link">Accueil</a>
    <a href="/marketplace.html" class="nav-link">Marketplace</a>
    <a href="/about.html" class="nav-link">À propos</a>
`;
  
  // Partie droite : auth ou profil
  let rightSection = '';
  
  if (!isAuth) {
    // Non connecté
    rightSection = `
      <div class="nav-auth">
        <a href="/login.html" class="btn btn-ghost btn-sm">Se connecter</a>
        <a href="/register.html" class="btn btn-primary btn-sm">S'inscrire</a>
      </div>
    `;
  } else {
    // Connecté
    const initials = (
      (user.first_name?.[0] || '') + (user.last_name?.[0] || '')
    ).toUpperCase() || user.phone.slice(-2);
    
    // Menu selon le rôle
    let dashboardLink = '';
    if (user.role === 'admin') {
      dashboardLink = `<a href="/dashboard-admin.html" class="dropdown-item">👑 Dashboard admin</a>`;
    } else if (user.role === 'seller') {
      dashboardLink = `<a href="/dashboard-seller.html" class="dropdown-item">📊 Mon dashboard</a>`;
    } else {
      dashboardLink = `<a href="/become-seller.html" class="dropdown-item">🚀 Devenir vendeur</a>`;
    }
    
    rightSection = `
      <div class="nav-user" id="nav-user-menu">
        <button class="nav-user-btn" onclick="toggleUserMenu(event)">
          <span class="nav-avatar">${initials}</span>
          <span class="nav-user-name">${user.first_name || user.phone}</span>
          <span class="nav-chevron">▾</span>
        </button>
        <div class="nav-dropdown" id="nav-dropdown">
          <div class="dropdown-header">
            <div class="dropdown-name">${user.first_name || ''} ${user.last_name || ''}</div>
            <div class="dropdown-phone">${user.phone}</div>
            <div class="dropdown-role badge badge-${user.role === 'admin' ? 'danger' : user.role === 'seller' ? 'orange' : 'blue'}">
              ${user.role === 'admin' ? 'Admin' : user.role === 'seller' ? 'Vendeur' : 'Client'}
            </div>
          </div>
          <div class="dropdown-divider"></div>
          ${dashboardLink}
          <a href="/orders.html" class="dropdown-item">📦 Mes commandes</a>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item dropdown-item-danger" onclick="Auth.logout()">
            🚪 Se déconnecter
          </button>
        </div>
      </div>
    `;
  }
  
  navContainer.innerHTML = `
    <div class="navbar-inner">
      <a href="/index.html" class="navbar-logo">
        Finest<span>Global</span>
      </a>
      
      <div class="navbar-search">
        <input 
          type="text" 
          id="navbar-search-input"
          placeholder="Rechercher un produit, une boutique..."
          autocomplete="off"
        />
        <div class="navbar-suggestions" id="navbar-suggestions"></div>
      </div>
      
      <div class="navbar-links">
        ${baseLinks}
      </div>
      
      ${rightSection}
    </div>
  `;
  
  // Initialiser l'autocomplétion de la navbar
  initNavbarSearch();
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
  
  // Fermer au clic ailleurs
  document.addEventListener('click', () => {
    suggestions.classList.remove('open');
  });
  
  // Aller à la marketplace avec la recherche
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

// Fermer le menu au clic ailleurs
document.addEventListener('click', () => {
  const dropdown = document.getElementById('nav-dropdown');
  if (dropdown) dropdown.classList.remove('open');
});