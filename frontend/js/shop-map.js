/* ============================================================
   FINEST GLOBAL — Carte interactive pour vendeur
   Utilise Leaflet + OpenStreetMap (gratuit)
   ============================================================ */

let _map = null;
let _marker = null;

/**
 * Initialise la carte dans l'élément #map.
 * @param {number} defaultLat - Latitude par défaut (Cotonou)
 * @param {number} defaultLng - Longitude par défaut
 * @param {number} initialLat - Latitude initiale (si existante)
 * @param {number} initialLng - Longitude initiale (si existante)
 */
async function initShopMap(defaultLat = 6.3654, defaultLng = 2.4183, initialLat = null, initialLng = null) {
  const mapEl = document.getElementById('map');
  if (!mapEl) return;
  
  // Créer la carte
  _map = L.map('map').setView([defaultLat, defaultLng], 13);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 19,
  }).addTo(_map);
  
  // Si position initiale → placer le marqueur
  if (initialLat && initialLng) {
    placeMarker(initialLat, initialLng);
    _map.setView([initialLat, initialLng], 15);
  } else {
    // Sinon, essayer de centrer sur la position du vendeur
    const pos = await getGPSLocation();
    if (pos) {
      _map.setView([pos.latitude, pos.longitude], 15);
    }
  }
  
  // Clic sur la carte → placer le marqueur
  _map.on('click', (e) => {
    placeMarker(e.latlng.lat, e.latlng.lng);
  });
}

/**
 * Place ou déplace le marqueur.
 */
function placeMarker(lat, lng) {
  if (_marker) {
    _marker.setLatLng([lat, lng]);
  } else {
    _marker = L.marker([lat, lng], { draggable: true }).addTo(_map);
    _marker.on('dragend', () => {
      const pos = _marker.getLatLng();
      updateLocationInputs(pos.lat, pos.lng);
    });
  }
  updateLocationInputs(lat, lng);
}

/**
 * Met à jour les champs cachés + reverse geocoding.
 */
async function updateLocationInputs(lat, lng) {
  const latInput = document.getElementById('shop-latitude');
  const lngInput = document.getElementById('shop-longitude');
  const locInput = document.getElementById('shop-locality');
  
  if (latInput) latInput.value = lat;
  if (lngInput) lngInput.value = lng;
  
  // Reverse geocoding gratuit avec Nominatim
  if (locInput) {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=10`,
        { headers: { 'Accept-Language': 'fr' } }
      );
      const data = await response.json();
      const city = data.address?.city || data.address?.town || data.address?.village || data.address?.municipality || '';
      if (city) {
        locInput.value = city;
      }
    } catch (error) {
      console.warn('Reverse geocoding error:', error);
    }
  }
}

/**
 * Détruit la carte (utile quand on ferme un modal).
 */
function destroyShopMap() {
  if (_map) {
    _map.remove();
    _map = null;
    _marker = null;
  }
}