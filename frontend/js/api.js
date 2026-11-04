/* ============================================================
   FINEST GLOBAL — API Client
   Wrapper fetch centralisé pour parler au backend FastAPI
   ============================================================ */

const API_BASE_URL = 'https://finest-global-guh4.onrender.com';

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
  
  const headers = {
    ...options.headers,
  };
  
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  
  const token = localStorage.getItem('fg_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
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
    
    if (response.status === 204) {
      return null;
    }
    
    const data = await response.json();
    
    if (!response.ok) {
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
  registerClient: (data) =>
    apiFetch('/api/users/register', {
      method: 'POST',
      body: data,
    }),
  
  registerSeller: (data) =>
    apiFetch('/api/users/register-seller', {
      method: 'POST',
      body: data,
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
  // ---- CRUD ----
  create: (data) =>
    apiFetch('/api/shops/', { method: 'POST', body: data }),
  
  getMine: () => apiFetch('/api/shops/me'),
  
  updateMine: (data) =>
    apiFetch('/api/shops/me', { method: 'PATCH', body: data }),

  // 🆕 Changer le statut (Actif / Inactif)
  updateStatus: (isActive) =>
    apiFetch('/api/shops/me/status', { 
      method: 'PATCH', 
      body: { is_active: isActive } 
    }),
  
  uploadPhoto: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch('/api/shops/me/photo', {
      method: 'POST',
      body: formData,
    });
  },
  
  // ---- Liste avec filtres ----
  list: (filters = {}) => {
    const params = new URLSearchParams();
    
    if (typeof filters === 'number') {
      params.append('skip', filters);
      if (arguments[1]) params.append('limit', arguments[1]);
    } else {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          params.append(key, value);
        }
      });
    }
    
    const qs = params.toString();
    return apiFetch(`/api/shops/${qs ? '?' + qs : ''}`);
  },
  
  getById: (id) => apiFetch(`/api/shops/${id}`),
  
  listLocalities: () => apiFetch('/api/shops/localities'),
  
  listMarkets: () => apiFetch('/api/shops/markets'),
  
  getByCode: (code) => apiFetch(`/api/shops/by-code/${encodeURIComponent(code)}`),
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

  // 🆕 Upload Vidéo
  uploadVideo: (productId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch(`/api/products/${productId}/video`, {
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
// 🆕 API — SERVICES
// ============================================================

const ServicesAPI = {
  create: (data) =>
    apiFetch('/api/services/', { method: 'POST', body: data }),
  
  uploadPhoto: (serviceId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch(`/api/services/${serviceId}/photo`, {
      method: 'POST',
      body: formData,
    });
  },

  uploadVideo: (serviceId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch(`/api/services/${serviceId}/video`, {
      method: 'POST',
      body: formData,
    });
  },
  
  getMine: () => apiFetch('/api/services/me'),
  
  getByShop: (shopId, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    const qs = params.toString();
    return apiFetch(`/api/services/shop/${shopId}${qs ? '?' + qs : ''}`);
  },
  
  getById: (id) => apiFetch(`/api/services/${id}`),
  
  update: (id, data) =>
    apiFetch(`/api/services/${id}`, { method: 'PATCH', body: data }),
  
  delete: (id) =>
    apiFetch(`/api/services/${id}`, { method: 'DELETE' }),
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
// 🆕 API — NOTIFICATIONS
// ============================================================

const NotificationsAPI = {
  getMine: (unreadOnly = false) => 
    apiFetch(`/api/notifications/?unread_only=${unreadOnly}`),
  
  getUnreadCount: () => 
    apiFetch('/api/notifications/unread-count'),
  
  markRead: (id, isRead = true) =>
    apiFetch(`/api/notifications/${id}/read`, { 
      method: 'PATCH', 
      body: { is_read: isRead } 
    }),
  
  markAllRead: () => 
    apiFetch('/api/notifications/read-all', { method: 'POST' }),
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

  // 🆕 Recherche par Image
  byImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch('/api/search/by-image', {
      method: 'POST',
      body: formData,
    });
  },

  // 🆕 Recherche par Code Vendeur
  bySellerCode: (code) => 
    apiFetch(`/api/search/by-seller-code/${encodeURIComponent(code)}`),
  
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
// API — CATÉGORIES
// ============================================================

const CategoriesAPI = {
  // 🆕 On peut filtrer par type ("product" ou "service")
  list: (type = null) => {
    const url = type ? `/api/categories/?type=${type}` : '/api/categories/';
    return apiFetch(url);
  },
  
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
  if (price === null || price === undefined) return '—';
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

/**
 * Formate une distance (m ou km).
 */
function formatDistance(km) {
  if (km === null || km === undefined) return '';
  if (km < 1) {
    return `${Math.round(km * 1000)} m`;
  }
  return `${km.toFixed(1)} km`;
}

/**
 * Récupère l'availability traduite d'un produit.
 */
function getAvailabilityLabel(availability) {
  const labels = {
    'in_stock': typeof t === 'function' ? t('product.in_stock') : 'En stock',
    'out_of_stock': typeof t === 'function' ? t('product.out_of_stock') : 'Rupture',
    'to_confirm': typeof t === 'function' ? t('product.to_confirm') : 'À confirmer',
  };
  return labels[availability] || availability;
}

/**
 * Récupère la classe CSS de l'availability.
 */
function getAvailabilityClass(availability) {
  const classes = {
    'in_stock': 'badge-success',
    'out_of_stock': 'badge-danger',
    'to_confirm': 'badge-warning',
  };
  return classes[availability] || 'badge-blue';
}