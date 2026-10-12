/* ============================================================
   FINEST GLOBAL — API Client
   Wrapper fetch centralisé pour parler au backend FastAPI
   ============================================================ */

const API_BASE_URL = 'https://finest-global.onrender.com';

// ============================================================
// CLASSE D'ERREUR API
// ============================================================

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// ============================================================
// FONCTION FETCH CENTRALE
// ============================================================

async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Headers par défaut
  const headers = {
    ...options.headers,
  };
  
  // Si ce n'est pas un FormData, on met du JSON
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  
  // Ajouter le token si présent
  const token = localStorage.getItem('fg_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Convertir le body en JSON si c'est un objet
  let body = options.body;
  if (body && typeof body === 'object' && !(body instanceof FormData)) {
    body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
      body,
    });
    
    // Gérer les réponses vides (204)
    if (response.status === 204) {
      return null;
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      // Token expiré ou invalide → déconnexion
      if (response.status === 401) {
        localStorage.removeItem('fg_token');
        localStorage.removeItem('fg_user');
      }
      
      const message = data.detail || 'Une erreur est survenue';
      throw new ApiError(message, response.status, data);
    }
    
    return data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError('Erreur de connexion au serveur', 0, error);
  }
}

// ============================================================
// API — UTILISATEURS
// ============================================================

const UsersAPI = {
  registerClient: (phone) => 
    apiFetch('/api/users/register', {
      method: 'POST',
      body: { phone },
    }),
  
  registerSeller: (data) =>
    apiFetch('/api/users/register-seller', {
      method: 'POST',
      body: data,
    }),
  
  requestOtp: (phone) =>
    apiFetch('/api/users/request-otp', {
      method: 'POST',
      body: { phone },
    }),
  
  verifyOtp: (phone, code) =>
    apiFetch('/api/users/verify-otp', {
      method: 'POST',
      body: { phone, code },
    }),
  
  login: (phone, password) =>
    apiFetch('/api/users/login', {
      method: 'POST',
      body: { phone, password },
    }),
  
  upgradeToSeller: (data) =>
    apiFetch('/api/users/upgrade-to-seller', {
      method: 'POST',
      body: data,
    }),
  
  me: () => apiFetch('/api/users/me'),
};

// ============================================================
// API — BOUTIQUES
// ============================================================

const ShopsAPI = {
  create: (data) =>
    apiFetch('/api/shops/', { method: 'POST', body: data }),
  
  getMine: () => apiFetch('/api/shops/me'),
  
  updateMine: (data) =>
    apiFetch('/api/shops/me', { method: 'PATCH', body: data }),
  
  uploadPhoto: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch('/api/shops/me/photo', {
      method: 'POST',
      body: formData,
    });
  },
  
  list: (skip = 0, limit = 50) =>
    apiFetch(`/api/shops/?skip=${skip}&limit=${limit}`),
  
  getById: (id) => apiFetch(`/api/shops/${id}`),
};

// ============================================================
// API — PRODUITS
// ============================================================

const ProductsAPI = {
  create: (data) =>
    apiFetch('/api/products/', { method: 'POST', body: data }),
  
  uploadPhoto: (productId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch(`/api/products/${productId}/photo`, {
      method: 'POST',
      body: formData,
    });
  },
  
  getMine: () => apiFetch('/api/products/me'),
  
  getByShop: (shopId, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    const qs = params.toString();
    return apiFetch(`/api/products/shop/${shopId}${qs ? '?' + qs : ''}`);
  },
  
  getById: (id) => apiFetch(`/api/products/${id}`),
  
  update: (id, data) =>
    apiFetch(`/api/products/${id}`, { method: 'PATCH', body: data }),
  
  delete: (id) =>
    apiFetch(`/api/products/${id}`, { method: 'DELETE' }),
};

// ============================================================
// API — COMMANDES
// ============================================================

const OrdersAPI = {
  create: (data) =>
    apiFetch('/api/orders/', { method: 'POST', body: data }),
  
  getMine: () => apiFetch('/api/orders/me'),
  
  getReceived: () => apiFetch('/api/orders/received'),
  
  getById: (id) => apiFetch(`/api/orders/${id}`),
  
  updateStatus: (id, status) =>
    apiFetch(`/api/orders/${id}/status`, {
      method: 'PATCH',
      body: { status },
    }),
};

// ============================================================
// API — RECHERCHE
// ============================================================

const SearchAPI = {
  search: (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    return apiFetch(`/api/search/?${params.toString()}`);
  },
  
  suggest: (q) =>
    apiFetch(`/api/search/suggest?q=${encodeURIComponent(q)}`),
  
  trending: (limit = 12) =>
    apiFetch(`/api/search/trending?limit=${limit}`),
  
  categories: () => apiFetch('/api/search/categories'),
  
  colors: () => apiFetch('/api/search/colors'),
  
  popular: () => apiFetch('/api/search/popular'),
};

// ============================================================
// API — ADMIN
// ============================================================

const AdminAPI = {
  overview: () => apiFetch('/api/admin/stats/overview'),
  
  visitors: (period = 'day') =>
    apiFetch(`/api/admin/stats/visitors?period=${period}`),
  
  topSellers: (limit = 10) =>
    apiFetch(`/api/admin/stats/top-sellers?limit=${limit}`),
  
  topProducts: (limit = 10) =>
    apiFetch(`/api/admin/stats/top-products?limit=${limit}`),
  
  users: (role = null) =>
    apiFetch(`/api/admin/users${role ? '?role=' + role : ''}`),
  
  shops: () => apiFetch('/api/admin/shops'),
  
  orders: () => apiFetch('/api/admin/orders'),
};

// ============================================================
// API — TRACKING
// ============================================================

const TrackAPI = {
  pageview: (data) =>
    apiFetch('/api/track/pageview', { method: 'POST', body: data }),
};

// ============================================================
// UTILITAIRES
// ============================================================

/**
 * Construit l'URL complète d'une image uploadée.
 */
function imageUrl(path) {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return `${API_BASE_URL}${path}`;
}

/**
 * Formate un prix en FCFA.
 */
function formatPrice(price) {
  return new Intl.NumberFormat('fr-FR').format(price) + ' FCFA';
}

/**
 * Formate une date en français.
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Affiche un toast de notification.
 */
function showToast(message, type = 'info', duration = 4000) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(120%)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}


// ============================================================
// API — CATÉGORIES
// ============================================================

const CategoriesAPI = {
  list: () => apiFetch('/api/categories/'),
  
  suggest: (q) => apiFetch(`/api/categories/suggest?q=${encodeURIComponent(q)}`),
  
  getById: (id) => apiFetch(`/api/categories/${id}`),
};

// ============================================================
// API — ADMIN CATÉGORIES
// ============================================================

const AdminCategoriesAPI = {
  list: () => apiFetch('/api/admin/categories/'),
  
  create: (data) => apiFetch('/api/admin/categories/', { method: 'POST', body: data }),
  
  update: (id, data) => apiFetch(`/api/admin/categories/${id}`, { method: 'PATCH', body: data }),
  
  delete: (id) => apiFetch(`/api/admin/categories/${id}`, { method: 'DELETE' }),
  
  seed: () => apiFetch('/api/admin/categories/seed', { method: 'POST' }),
};