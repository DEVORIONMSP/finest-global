/* ============================================================
   FINEST GLOBAL — Authentification côté client
   ============================================================ */

const Auth = {
  // ==========================================================
  // STOCKAGE
  // ==========================================================
  
  /**
   * Sauvegarde le token et l'utilisateur après connexion.
   */
  setSession(token, user) {
    localStorage.setItem('fg_token', token);
    localStorage.setItem('fg_user', JSON.stringify(user));
  },
  
  /**
   * Récupère le token stocké.
   */
  getToken() {
    return localStorage.getItem('fg_token');
  },
  
  /**
   * Récupère l'utilisateur stocké (ou null).
   */
  getUser() {
    const user = localStorage.getItem('fg_user');
    if (!user) return null;
    try {
      return JSON.parse(user);
    } catch {
      return null;
    }
  },
  
  /**
   * Vérifie si un utilisateur est connecté.
   */
  isAuthenticated() {
    return !!this.getToken() && !!this.getUser();
  },
  
  /**
   * Vérifie si l'utilisateur est vendeur.
   */
  isSeller() {
    const user = this.getUser();
    return user && (user.role === 'seller' || user.role === 'admin');
  },
  
  /**
   * Vérifie si l'utilisateur est admin.
   */
  isAdmin() {
    const user = this.getUser();
    return user && user.role === 'admin';
  },
  
  /**
   * Vérifie si l'utilisateur est client (uniquement).
   */
  isClient() {
    const user = this.getUser();
    return user && user.role === 'client';
  },
  
  /**
   * Déconnexion : efface tout.
   */
  logout() {
    localStorage.removeItem('fg_token');
    localStorage.removeItem('fg_user');
    window.location.href = '/index.html';
  },
  
  /**
   * Rafraîchit les infos utilisateur depuis le serveur.
   */
  async refreshUser() {
    if (!this.isAuthenticated()) return null;
    try {
      const user = await UsersAPI.me();
      localStorage.setItem('fg_user', JSON.stringify(user));
      return user;
    } catch {
      this.logout();
      return null;
    }
  },
  
  /**
   * Redirige vers login si non connecté.
   */
  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = '/login.html?redirect=' + 
        encodeURIComponent(window.location.pathname);
      return false;
    }
    return true;
  },
  
  /**
   * Redirige si pas vendeur.
   */
  requireSeller() {
    if (!this.requireAuth()) return false;
    if (!this.isSeller()) {
      showToast('Accès réservé aux vendeurs.', 'error');
      window.location.href = '/become-seller.html';
      return false;
    }
    return true;
  },
  
  /**
   * Redirige si pas admin.
   */
  requireAdmin() {
    if (!this.requireAuth()) return false;
    if (!this.isAdmin()) {
      showToast('Accès réservé aux administrateurs.', 'error');
      window.location.href = '/index.html';
      return false;
    }
    return true;
  },
};