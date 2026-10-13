/* ============================================================
   FINEST GLOBAL — Géolocalisation client
   Détection GPS + IP
   ============================================================ */

/**
 * Détecte la position du client.
 * Méthode 1 : GPS (précis)
 * Méthode 2 : IP (automatique, approximatif)
 * Retourne { latitude, longitude, source } ou null.
 */
async function detectClientLocation() {
  // Cache valide 1 heure
  const cached = localStorage.getItem('fg_location');
  if (cached) {
    try {
      const loc = JSON.parse(cached);
      if (Date.now() - loc.timestamp < 3600000) {
        return loc;
      }
    } catch {}
  }
  
  // 1. Essayer le GPS
  const gpsLocation = await getGPSLocation();
  if (gpsLocation) {
    const result = { ...gpsLocation, source: 'gps', timestamp: Date.now() };
    localStorage.setItem('fg_location', JSON.stringify(result));
    return result;
  }
  
  // 2. Fallback : IP
  const ipLocation = await getIPLocation();
  if (ipLocation) {
    const result = { ...ipLocation, source: 'ip', timestamp: Date.now() };
    localStorage.setItem('fg_location', JSON.stringify(result));
    return result;
  }
  
  return null;
}

/**
 * Demande la position GPS du navigateur.
 */
function getGPSLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(null);
      return;
    }
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (error) => {
        console.warn('GPS refusé:', error.message);
        resolve(null);
      },
      {
        enableHighAccuracy: false,
        timeout: 5000,
        maximumAge: 300000,
      }
    );
  });
}

/**
 * Détecte la position par IP.
 */
async function getIPLocation() {
  try {
    const response = await fetch('https://ipwho.is/');
    const data = await response.json();
    
    if (data.success) {
      return {
        latitude: data.latitude,
        longitude: data.longitude,
        city: data.city,
        region: data.region,
        country: data.country,
      };
    }
    return null;
  } catch (error) {
    console.warn('Erreur IP:', error);
    return null;
  }
}

/**
 * Calcule la distance entre 2 points GPS (Haversine).
 * Retourne la distance en km.
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

/**
 * Formate une distance.
 */
function formatDistance(km) {
  if (km === null || km === undefined) return '';
  if (km < 1) {
    return `${Math.round(km * 1000)} m`;
  }
  return `${km.toFixed(1)} km`;
}

/**
 * Vide le cache de position (utile pour tester).
 */
function clearLocationCache() {
  localStorage.removeItem('fg_location');
}