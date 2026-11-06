/* ============================================================
   FINEST GLOBAL — Navbar dynamique (Desktop + Mobile 2-barres)
   Version corrigée avec Recherche Vocale et Image (Gemini)
   ============================================================ */

/* État partagé */
let _lastIsMobile = window.innerWidth <= 900;
let _lastScrollY = 0;
let _navbarsHidden = false;
let _scrollBound = false;
let _scrollTicking = false;
let _navbarObserver = null;
let _notifWs = null;
let _globalListenersBound = false;

function renderNavbar() {
  const navContainer = document.getElementById('navbar');
  if (!navContainer) return;
  
  const isMobile = window.innerWidth <= 900;
  _lastIsMobile = isMobile;
  
  if (isMobile) {
    renderMobileNavbar(navContainer);
  } else {
    renderDesktopNavbar(navContainer);
  }
  
  document.body.classList.add('has-navbar');
  syncNavbarHeight();
  observeNavbarHeight();
  initNavbarScrollBehavior();
}

/* ============================================================
   UTILITAIRES UTILISATEUR
   ============================================================ */
function getUserInitials(user) {
  if (!user) return '👤';
  const first = (user.first_name && user.first_name[0]) || '';
  const last = (user.last_name && user.last_name[0]) || '';
  const initials = (first + last).toUpperCase();
  if (initials) return initials;
  return user.phone ? String(user.phone).slice(-2) : '👤';
}

/* ============================================================
   DESKTOP NAVBAR
   ============================================================ */
function renderDesktopNavbar(navContainer) {
  const user = Auth.getUser();
  const isAuth = Auth.isAuthenticated() && !!user;
  const currentLang = getCurrentLanguage();
  
  const langSelector = `
    <div class="lang-selector">
      <button class="lang-btn ${currentLang === 'fr' ? 'active' : ''}" onclick="setLanguage('fr')" aria-label="Français" title="Français">🇫🇷</button>
      <button class="lang-btn ${currentLang === 'en' ? 'active' : ''}" onclick="setLanguage('en')" aria-label="English" title="English">🇬🇧</button>
    </div>
  `;
  
  let notificationBell = '';
  if (isAuth) {
    notificationBell = `
      <div class="nav-notifications" id="nav-notifications-menu">
        <button class="nav-notif-btn" onclick="toggleNotifications(event)" aria-label="Notifications">
          🔔
          <span class="nav-notif-badge hidden" id="notif-badge">0</span>
        </button>
        <div class="nav-notif-dropdown" id="nav-notif-dropdown">
          <div class="notif-header">
            <span>Notifications</span>
            <button class="notif-mark-all" onclick="markAllNotificationsRead()">Tout marquer lu</button>
          </div>
          <div class="notif-list" id="notif-list">
            <div class="notif-empty">Chargement...</div>
          </div>
          <div class="notif-footer"><a href="/notifications.html">Voir tout</a></div>
        </div>
      </div>
    `;
  }
  
  let rightSection = '';
  
  if (!isAuth) {
    rightSection = `
      <div class="nav-auth">
        <a href="/login.html" class="btn btn-ghost btn-sm">${t('nav.login')}</a>
        <a href="/register.html" class="btn btn-primary btn-sm">${t('nav.register')}</a>
      </div>
    `;
  } else {
    const initials = getUserInitials(user);
    
    let dashboardLink = '';
    if (user.role === 'admin') {
      dashboardLink = `<a href="/dashboard-admin.html" class="dropdown-item">👑 ${t('nav.dashboard_admin')}</a>`;
    } else if (user.role === 'seller') {
      dashboardLink = `<a href="/dashboard-seller.html" class="dropdown-item">📊 ${t('nav.dashboard')}</a>`;
    } else {
      dashboardLink = `<a href="/become-seller.html" class="dropdown-item">🚀 ${t('nav.become_seller')}</a>`;
    }
    
    const roleBadgeClass = user.role === 'admin' ? 'danger' : user.role === 'seller' ? 'orange' : 'blue';
    
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
            <div class="dropdown-phone">${user.phone || ''}</div>
            <div class="dropdown-role badge badge-${roleBadgeClass}">${t('role.' + user.role)}</div>
          </div>
          <div class="dropdown-divider"></div>
          ${dashboardLink}
          <a href="/orders.html" class="dropdown-item">📦 ${t('nav.orders')}</a>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item dropdown-item-danger" onclick="Auth.logout()">🚪 ${t('nav.logout')}</button>
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
      
      <!-- 🆕 BARRE DE RECHERCHE AVEC BOUTONS VOCAL ET IMAGE -->
      <div class="navbar-search">
        <input type="text" id="navbar-search-input" placeholder="${t('nav.search_placeholder')}" autocomplete="off" />
        <div class="navbar-suggestions" id="navbar-suggestions"></div>
        <div class="search-actions">
          <button type="button" class="search-action-btn" onclick="startVoiceSearch()" title="Recherche vocale">🎤</button>
          <button type="button" class="search-action-btn" onclick="triggerImageSearch()" title="Recherche par image">📸</button>
          <input type="file" id="image-search-input" accept="image/*" style="display:none" onchange="handleImageSearch(event)" />
        </div>
      </div>
      
      <div class="navbar-links">${baseLinksForScreen()}</div>
      ${langSelector}
      ${notificationBell}
      ${rightSection}
    </div>
  `;
  
  initNavbarSearch();
  if (isAuth) initNotifications();
  
  document.body.classList.remove('mobile-nav-active');
}

/* ============================================================
   MOBILE NAVBAR (2 barres : haut + bas)
   ============================================================ */
function renderMobileNavbar(navContainer) {
  const user = Auth.getUser();
  const isAuth = Auth.isAuthenticated() && !!user;
  const currentPath = window.location.pathname;
  
  const profileUrl = getProfileUrl();
  const initials = getUserInitials(user);
  
  navContainer.innerHTML = `
    <!-- ===== NAVBAR HAUT ===== -->
    <div class="mobile-topbar">
      <button class="mobile-menu-btn" onclick="toggleMobileMenu(event)" aria-label="Menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      
      <a href="/index.html" class="mobile-logo" aria-label="Finest Global">
        <img src="/assets/finest.png" alt="Finest Global" class="mobile-logo-img">
      </a>
      
      <button class="mobile-search-btn" onclick="toggleMobileSearch(event)" aria-label="Rechercher">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </button>
      
      <a href="${profileUrl}" class="mobile-profile-btn" onclick="goToProfile(event)" aria-label="${t('nav.profile')}">
        ${isAuth 
          ? `<span class="mobile-profile-avatar">${initials}</span>`
          : `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>`
        }
      </a>
    </div>
    
    <!-- ===== BARRE DE RECHERCHE MOBILE (avec boutons) ===== -->
    <div class="mobile-search-bar" id="mobile-search-bar">
      <input type="text" id="mobile-search-input" placeholder="${t('nav.search_placeholder')}" autocomplete="off" />
      <div class="search-actions-mobile">
        <button type="button" class="search-action-btn" onclick="startVoiceSearch()" title="Recherche vocale">🎤</button>
        <button type="button" class="search-action-btn" onclick="triggerImageSearch()" title="Recherche par image">📸</button>
        <input type="file" id="mobile-image-search-input" accept="image/*" style="display:none" onchange="handleImageSearch(event)" />
      </div>
      <button class="mobile-search-close" onclick="toggleMobileSearch()">✕</button>
    </div>
    
    <!-- ===== DRAWER MENU ===== -->
    <div class="mobile-drawer-overlay" id="mobile-drawer-overlay" onclick="closeMobileMenu()"></div>
    <aside class="mobile-drawer" id="mobile-drawer">
      <div class="mobile-drawer-header">
        ${isAuth ? `
          <div class="mobile-drawer-avatar">${initials}</div>
          <div class="mobile-drawer-user">
            <div class="mobile-drawer-name">${escapeHtml(user.first_name || user.phone || '')}</div>
            <div class="mobile-drawer-role">${t('role.' + user.role)}</div>
          </div>
        ` : `
          <div class="mobile-drawer-avatar">👤</div>
          <div class="mobile-drawer-user">
            <div class="mobile-drawer-name">${t('nav.login')}</div>
            <div class="mobile-drawer-role">${t('nav.register')}</div>
          </div>
        `}
      </div>
      
      <nav class="mobile-drawer-nav">
        <a href="/index.html" class="mobile-drawer-link ${currentPath.endsWith('/index.html') || currentPath === '/' ? 'active' : ''}">
          🏠 <span>${t('nav.home')}</span>
        </a>
        <a href="/marketplace.html" class="mobile-drawer-link ${currentPath.endsWith('/marketplace.html') ? 'active' : ''}">
          🏪 <span>${t('nav.marketplace')}</span>
        </a>
        <a href="/about.html" class="mobile-drawer-link ${currentPath.endsWith('/about.html') ? 'active' : ''}">
          ℹ️ <span>${t('nav.about')}</span>
        </a>
        
        <div class="mobile-drawer-divider"></div>
        
        ${isAuth ? `
          <a href="/orders.html" class="mobile-drawer-link">📦 <span>${t('nav.orders')}</span></a>
          <a href="/notifications.html" class="mobile-drawer-link">🔔 <span>Notifications</span></a>
          ${user.role === 'admin' ? `<a href="/dashboard-admin.html" class="mobile-drawer-link">👑 <span>${t('nav.dashboard_admin')}</span></a>` : ''}
          ${user.role === 'seller' ? `<a href="/dashboard-seller.html" class="mobile-drawer-link">📊 <span>${t('nav.dashboard')}</span></a>` : ''}
          ${user.role === 'client' ? `<a href="/become-seller.html" class="mobile-drawer-link">🚀 <span>${t('nav.become_seller')}</span></a>` : ''}
          
          <div class="mobile-drawer-divider"></div>
          
          <a href="${profileUrl}" class="mobile-drawer-link" onclick="goToProfile(event)">👤 <span>${t('nav.profile')}</span></a>
          <button class="mobile-drawer-link mobile-drawer-logout" onclick="Auth.logout()">
            🚪 <span>${t('nav.logout')}</span>
          </button>
        ` : `
          <a href="/login.html" class="mobile-drawer-link">🔐 <span>${t('nav.login')}</span></a>
          <a href="/register.html" class="mobile-drawer-link">✨ <span>${t('nav.register')}</span></a>
        `}
        
        <div class="mobile-drawer-divider"></div>
        
        <div class="mobile-drawer-langs">
          <button class="mobile-lang-btn ${getCurrentLanguage() === 'fr' ? 'active' : ''}" onclick="setLanguage('fr')">🇫🇷 Français</button>
          <button class="mobile-lang-btn ${getCurrentLanguage() === 'en' ? 'active' : ''}" onclick="setLanguage('en')">🇬🇧 English</button>
        </div>
      </nav>
    </aside>
    
    <!-- ===== NAVBAR BAS ===== -->
    <nav class="mobile-bottombar">
      <a href="/index.html" class="mobile-tab ${currentPath.endsWith('/index.html') || currentPath === '/' ? 'active' : ''}" aria-label="${t('nav.home')}">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
        <span>${t('nav.home')}</span>
      </a>
      
      <a href="/marketplace.html" class="mobile-tab ${currentPath.endsWith('/marketplace.html') ? 'active' : ''}" aria-label="${t('nav.marketplace')}">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <path d="M16 10a4 4 0 0 1-8 0"></path>
        </svg>
        <span>${t('nav.marketplace')}</span>
      </a>
      
      <button class="mobile-tab mobile-tab-add" onclick="handleAddButton()" aria-label="Ajouter">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
      </button>
      
      <a href="/notifications.html" class="mobile-tab ${currentPath.endsWith('/notifications.html') ? 'active' : ''}" aria-label="Notifications">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        <span>Notifs</span>
        <span class="mobile-tab-badge hidden" id="mobile-notif-badge">0</span>
      </a>
      
      <a href="${profileUrl}" class="mobile-tab ${currentPath.endsWith('/profile.html') || currentPath.endsWith('/register.html') || currentPath.endsWith('/dashboard-seller.html') || currentPath.endsWith('/dashboard-admin.html') ? 'active' : ''}" onclick="goToProfile(event)" aria-label="${t('nav.profile')}">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
        <span>${t('nav.profile')}</span>
      </a>
    </nav>
  `;
  
  initMobileSearch();
  initMobileMenuEvents();
  if (isAuth) initNotifications();
  
  document.body.classList.add('mobile-nav-active');
}

/* ============================================================
   URL DU PROFIL SELON LE RÔLE
   ============================================================ */
function getProfileUrl() {
  let isAuth = false;
  let user = null;
  
  try {
    isAuth = Auth.isAuthenticated();
    user = Auth.getUser();
  } catch (e) {
    return '/register.html';
  }
  
  if (!isAuth || !user) return '/register.html';
  
  if (user.role === 'admin') return '/dashboard-admin.html';
  if (user.role === 'seller') return '/dashboard-seller.html';
  return '/profile.html';
}

function goToProfile(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  closeMobileMenu();
  window.location.href = getProfileUrl();
}

/* ============================================================
   INIT MENU MOBILE
   ============================================================ */
function initMobileMenuEvents() {
  const drawer = document.getElementById('mobile-drawer');
  const overlay = document.getElementById('mobile-drawer-overlay');
  
  if (drawer) drawer.classList.remove('open');
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
  
  if (drawer) {
    drawer.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        closeMobileMenu();
      });
    });
  }
}

/* ============================================================
   SCROLL HIDE / SHOW
   ============================================================ */
function getScrollY() {
  return Math.max(
    0,
    window.pageYOffset ||
    (document.documentElement && document.documentElement.scrollTop) ||
    (document.body && document.body.scrollTop) ||
    0
  );
}

function showMobileNavbars() {
  const topbar = document.querySelector('.mobile-topbar');
  const bottombar = document.querySelector('.mobile-bottombar');
  if (topbar) topbar.classList.remove('nav-hidden');
  if (bottombar) bottombar.classList.remove('nav-hidden');
  _navbarsHidden = false;
}

function hideMobileNavbars() {
  const topbar = document.querySelector('.mobile-topbar');
  const bottombar = document.querySelector('.mobile-bottombar');
  if (topbar) topbar.classList.add('nav-hidden');
  if (bottombar) bottombar.classList.add('nav-hidden');
  
  const searchBar = document.getElementById('mobile-search-bar');
  if (searchBar) searchBar.classList.remove('open');
  
  _navbarsHidden = true;
}

function initNavbarScrollBehavior() {
  _lastScrollY = getScrollY();
  _navbarsHidden = false;
  
  if (!_scrollBound) {
    document.addEventListener('scroll', onAnyScroll, { passive: true, capture: true });
    _scrollBound = true;
  }
}

function onAnyScroll(e) {
  const target = e.target;
  if (
    target &&
    target !== document &&
    target !== document.documentElement &&
    target !== document.body
  ) {
    return;
  }
  
  if (_scrollTicking) return;
  _scrollTicking = true;
  window.requestAnimationFrame(() => {
    handleNavbarScroll();
    _scrollTicking = false;
  });
}

function handleNavbarScroll() {
  if (window.innerWidth > 900) return;
  
  const topbar = document.querySelector('.mobile-topbar');
  const bottombar = document.querySelector('.mobile-bottombar');
  if (!topbar || !bottombar) return;
  
  const drawer = document.getElementById('mobile-drawer');
  if (drawer && drawer.classList.contains('open')) return;
  
  const currentScrollY = getScrollY();
  const scrollDiff = currentScrollY - _lastScrollY;
  
  if (currentScrollY < 60) {
    if (_navbarsHidden || topbar.classList.contains('nav-hidden') || bottombar.classList.contains('nav-hidden')) {
      showMobileNavbars();
    }
    _lastScrollY = currentScrollY;
    return;
  }
  
  if (scrollDiff > 6 && !_navbarsHidden) {
    hideMobileNavbars();
  }
  else if (scrollDiff < -4 && _navbarsHidden) {
    showMobileNavbars();
  }
  
  _lastScrollY = currentScrollY;
}

/* ============================================================
   BOUTON ➕
   ============================================================ */
function handleAddButton() {
  const isAuth = Auth.isAuthenticated();
  const user = Auth.getUser();
  
  if (!isAuth || !user) {
    showToast('🔐 Créez un compte pour ajouter un produit', 'info');
    setTimeout(() => { window.location.href = '/register.html'; }, 800);
    return;
  }
  
  if (user.role === 'admin') {
    showToast('👑 Redirection vers le dashboard admin', 'info');
    setTimeout(() => { window.location.href = '/dashboard-admin.html'; }, 600);
    return;
  }
  
  if (user.role === 'seller') {
    showToast('📦 Redirection vers vos produits', 'info');
    setTimeout(() => { window.location.href = '/dashboard-seller.html?tab=products'; }, 600);
    return;
  }
  
  showToast('🚀 Devenez vendeur pour ajouter des produits', 'info');
  setTimeout(() => { window.location.href = '/become-seller.html'; }, 800);
}

/* ============================================================
   MENU MOBILE
   ============================================================ */
function toggleMobileMenu(event) {
  if (event) event.stopPropagation();
  const drawer = document.getElementById('mobile-drawer');
  const overlay = document.getElementById('mobile-drawer-overlay');
  if (!drawer || !overlay) return;
  
  const isOpen = drawer.classList.contains('open');
  
  if (isOpen) {
    closeMobileMenu();
  } else {
    showMobileNavbars();
    drawer.classList.add('open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeMobileMenu() {
  const drawer = document.getElementById('mobile-drawer');
  const overlay = document.getElementById('mobile-drawer-overlay');
  if (drawer) drawer.classList.remove('open');
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
}

/* ============================================================
   BARRE DE RECHERCHE MOBILE
   ============================================================ */
function toggleMobileSearch(event) {
  if (event) event.stopPropagation();
  const bar = document.getElementById('mobile-search-bar');
  if (!bar) return;
  
  showMobileNavbars();
  bar.classList.toggle('open');
  
  if (bar.classList.contains('open')) {
    setTimeout(() => {
      const input = document.getElementById('mobile-search-input');
      if (input) input.focus();
    }, 100);
  }
}

function initMobileSearch() {
  const input = document.getElementById('mobile-search-input');
  if (!input) return;
  
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const q = input.value.trim();
      if (q) {
        window.location.href = `/marketplace.html?q=${encodeURIComponent(q)}`;
      }
    }
  });
}

/* ============================================================
   🆕 RECHERCHE VOCALE
   ============================================================ */
function startVoiceSearch() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  
  if (!SpeechRecognition) {
    showToast('❌ La recherche vocale n\'est pas supportée par votre navigateur.', 'error');
    return;
  }
  
  const recognition = new SpeechRecognition();
  recognition.lang = 'fr-FR';
  recognition.continuous = false;
  recognition.interimResults = false;
  
  showToast('🎤 Parlez maintenant...', 'info');
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    showToast(`✅ "${transcript}"`, 'success');
    window.location.href = `/marketplace.html?q=${encodeURIComponent(transcript)}&semantic=1`;
  };
  
  recognition.onerror = (event) => {
    console.error('Erreur vocale:', event.error);
    showToast('❌ Impossible de vous entendre. Vérifiez votre micro.', 'error');
  };
  
  recognition.start();
}

/* ============================================================
   🆕 RECHERCHE PAR IMAGE
   ============================================================ */
function triggerImageSearch() {
  const input = document.getElementById('image-search-input') || document.getElementById('mobile-image-search-input');
  if (input) input.click();
}

async function handleImageSearch(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  showToast('🔍 Analyse de l\'image...', 'info');
  
  try {
    const data = await SearchAPI.semantic(null, file);
    
    if (data.results && data.results.length > 0) {
      showToast(`✅ ${data.results.length} résultat(s) trouvé(s)`, 'success');
      sessionStorage.setItem('image_search_results', JSON.stringify(data.results));
      window.location.href = '/marketplace.html?image_search=1';
    } else {
      showToast('❌ Aucun produit similaire trouvé.', 'warning');
    }
  } catch (error) {
    console.error(error);
    showToast('❌ Erreur : ' + (error.message || 'Recherche impossible'), 'error');
  }
  
  event.target.value = '';
}

/* ============================================================
   NOTIFICATIONS (partagé desktop/mobile)
   ============================================================ */
async function initNotifications() {
  await loadNotifications();
  startNotificationWebSocket();
}

async function loadNotifications() {
  try {
    const countData = await NotificationsAPI.getUnreadCount();
    updateNotifBadge(countData.unread_count);
    const notifs = await NotificationsAPI.getMine();
    renderNotifList(notifs);
  } catch (error) {
    console.error('Erreur chargement notifications:', error);
  }
}

function updateNotifBadge(count) {
  const badge = document.getElementById('notif-badge');
  if (badge) {
    if (count > 0) {
      badge.textContent = count > 9 ? '9+' : count;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  }
  
  const mobileBadge = document.getElementById('mobile-notif-badge');
  if (mobileBadge) {
    if (count > 0) {
      mobileBadge.textContent = count > 9 ? '9+' : count;
      mobileBadge.classList.remove('hidden');
    } else {
      mobileBadge.classList.add('hidden');
    }
  }
}

function renderNotifList(notifs) {
  const list = document.getElementById('notif-list');
  if (!list) return;
  
  if (notifs.length === 0) {
    list.innerHTML = `<div class="notif-empty">Aucune notification</div>`;
    return;
  }
  
  list.innerHTML = notifs.slice(0, 10).map(n => `
    <div class="notif-item ${n.is_read ? 'read' : 'unread'}" onclick="handleNotifClick(${n.id}, '${n.link || ''}')">
      <div class="notif-title">${escapeHtml(n.title)}</div>
      <div class="notif-message">${escapeHtml(n.message)}</div>
      <div class="notif-time">${formatDate(n.created_at)}</div>
    </div>
  `).join('');
}

async function handleNotifClick(id, link) {
  try {
    await NotificationsAPI.markRead(id, true);
    await loadNotifications();
    if (link && link !== '') window.location.href = link;
  } catch (error) {
    console.error(error);
  }
}

async function markAllNotificationsRead() {
  try {
    await NotificationsAPI.markAllRead();
    await loadNotifications();
  } catch (error) {
    console.error(error);
  }
}

function toggleNotifications(event) {
  event.stopPropagation();
  const dropdown = document.getElementById('nav-notif-dropdown');
  if (dropdown) dropdown.classList.toggle('open');
}

/* ============================================================
   WEBSOCKET
   ============================================================ */
function startNotificationWebSocket() {
  const token = Auth.getToken();
  if (!token || _notifWs) return;
  
  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const API_HOST = isLocal ? '127.0.0.1:8000' : 'finest-global-guh4.onrender.com';
  const WS_PROTOCOL = isLocal ? 'ws' : 'wss';
  
  const wsUrl = `${WS_PROTOCOL}://${API_HOST}/ws/notifications?token=${token}`;
  _notifWs = new WebSocket(wsUrl);
  
  _notifWs.onopen = () => console.log('🟢 WebSocket notifications connecté');
  
  _notifWs.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      if (message.type === 'new_order' || message.type === 'order_status_changed') {
        loadNotifications();
        showToast(`🔔 ${message.title}`, 'info');
      }
    } catch (e) {}
  };
  
  _notifWs.onerror = (err) => console.warn('⚠️ WebSocket notifications erreur:', err);
  
  _notifWs.onclose = () => {
    _notifWs = null;
    setTimeout(startNotificationWebSocket, 5000);
  };
}

/* ============================================================
   UTILITAIRES
   ============================================================ */
function syncNavbarHeight() {
  const isMobile = window.innerWidth <= 900;
  const target = isMobile
    ? document.querySelector('.mobile-topbar')
    : document.getElementById('navbar');
  if (!target) return;
  document.documentElement.style.setProperty('--navbar-h', target.offsetHeight + 'px');
}

function observeNavbarHeight() {
  if (!('ResizeObserver' in window)) return;
  
  if (_navbarObserver) _navbarObserver.disconnect();
  _navbarObserver = new ResizeObserver(syncNavbarHeight);
  
  const nav = document.getElementById('navbar');
  const topbar = document.querySelector('.mobile-topbar');
  if (nav) _navbarObserver.observe(nav);
  if (topbar) _navbarObserver.observe(topbar);
}

function baseLinksForScreen() {
  return `
    <a href="/index.html" class="nav-link">${t('nav.home')}</a>
    <a href="/marketplace.html" class="nav-link">${t('nav.marketplace')}</a>
    <a href="/about.html" class="nav-link">${t('nav.about')}</a>
  `;
}

function updateNavLinksForScreenSize() {
  const linksContainer = document.querySelector('.navbar-links');
  if (!linksContainer) return;
  linksContainer.innerHTML = baseLinksForScreen();
}

function toggleUserMenu(event) {
  event.stopPropagation();
  const dropdown = document.getElementById('nav-dropdown');
  if (dropdown) dropdown.classList.toggle('open');
}

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
  
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') goToSearch(input.value.trim());
  });
}

function goToSearch(query) {
  if (!query) return;
  window.location.href = `/marketplace.html?q=${encodeURIComponent(query)}`;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/* ============================================================
   RESIZE
   ============================================================ */
let _navbarResizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(_navbarResizeTimer);
  _navbarResizeTimer = setTimeout(() => {
    const wasMobile = _lastIsMobile;
    _lastIsMobile = window.innerWidth <= 900;
    if (wasMobile !== _lastIsMobile) {
      renderNavbar();
    } else {
      updateNavLinksForScreenSize();
      syncNavbarHeight();
    }
  }, 200);
});

window.addEventListener('load', syncNavbarHeight);

/* ============================================================
   ÉCOUTEURS GLOBAUX
   ============================================================ */
function bindGlobalNavbarListeners() {
  if (_globalListenersBound) return;
  _globalListenersBound = true;
  
  document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('nav-dropdown');
    const userMenu = document.getElementById('nav-user-menu');
    if (dropdown && userMenu && !userMenu.contains(e.target)) dropdown.classList.remove('open');
    
    const notifDropdown = document.getElementById('nav-notif-dropdown');
    const notifMenu = document.getElementById('nav-notifications-menu');
    if (notifDropdown && notifMenu && !notifMenu.contains(e.target)) notifDropdown.classList.remove('open');
    
    const suggestions = document.getElementById('navbar-suggestions');
    if (suggestions) suggestions.classList.remove('open');
  });
  
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeMobileMenu();
      const bar = document.getElementById('mobile-search-bar');
      if (bar) bar.classList.remove('open');
    }
  });
  
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) {
      document.body.style.overflow = '';
      if (document.getElementById('navbar')) {
        try { renderNavbar(); } catch (err) { console.error(err); }
      }
    }
  });
}

/* ============================================================
   INIT AU CHARGEMENT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  const isHomePage = window.location.pathname === '/' || window.location.pathname.endsWith('/index.html');
  if (isHomePage) document.body.classList.add('page-home');
  
  bindGlobalNavbarListeners();
  
  const navContainer = document.getElementById('navbar');
  if (
    navContainer &&
    !navContainer.querySelector('.navbar-inner, .mobile-topbar') &&
    typeof Auth !== 'undefined' &&
    typeof t === 'function'
  ) {
    try { renderNavbar(); } catch (err) { console.error('Erreur renderNavbar:', err); }
  }
  
  const applyNavScrolled = () => {
    if (getScrollY() > 40) document.body.classList.add('nav-scrolled');
    else document.body.classList.remove('nav-scrolled');
  };
  
  applyNavScrolled();
  document.addEventListener('scroll', (e) => {
    const target = e.target;
    if (
      target &&
      target !== document &&
      target !== document.documentElement &&
      target !== document.body
    ) return;
    applyNavScrolled();
  }, { passive: true, capture: true });
});