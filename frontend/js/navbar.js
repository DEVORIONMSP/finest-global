/* ============================================================
   FINEST GLOBAL — Navbar dynamique (version simplifiée)
   Logo (gauche) + Marketplace (centre) + Profil (droite)
   ============================================================ */

function renderNavbar() {
  const navContainer = document.getElementById('navbar');
  if (!navContainer) return;
  
  const user = Auth.getUser();
  const isAuth = Auth.isAuthenticated();
  
  // Lien de navigation principal (Marketplace uniquement)
  const baseLinks = `
    <a href="/marketplace.html" class="nav-link">Marketplace</a>
  `;
  
  // Partie droite : auth ou profil
  let rightSection = '';
  
  if (!isAuth) {
    // Non connecté
    rightSection = `
      <div class="nav-auth">
        <a href="/login.html" class="btn btn-ghost btn-sm">Connexion</a>
        <a href="/register.html" class="btn btn-primary btn-sm">Inscription</a>
      </div>
    `;
  } else {
    // Connecté
    const initials = (
      (user.first_name?.[0] || '') + (user.last_name?.[0] || '')
    ).toUpperCase() || user.phone.slice(-2);
    
    // Lien dashboard selon le rôle
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
        <button class="nav-user-btn" onclick="toggleUserMenu(event)" aria-label="Mon profil">
          <span class="nav-avatar">${initials}</span>
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
      <a href="/index.html" class="navbar-logo" aria-label="Accueil Finest Global">
        <img src="/assets/logo.png" alt="Finest Global" class="navbar-logo-img">
      </a>
      
      <div class="navbar-links">
        ${baseLinks}
      </div>
      
      ${rightSection}
    </div>
  `;
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
 * Échappe le HTML.
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Redirige vers la marketplace avec la recherche.
 * (gardé pour compatibilité avec d'autres pages)
 */
function goToSearch(query) {
  if (!query) return;
  window.location.href = `/marketplace.html?q=${encodeURIComponent(query)}`;
}

// Fermer le menu au clic ailleurs
document.addEventListener('click', (e) => {
  const dropdown = document.getElementById('nav-dropdown');
  const userMenu = document.getElementById('nav-user-menu');
  if (dropdown && userMenu && !userMenu.contains(e.target)) {
    dropdown.classList.remove('open');
  }
});