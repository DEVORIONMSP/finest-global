/* ============================================================
   Composant : champ catégorie avec autocomplétion
   ============================================================ */

let _allCategories = null;

async function getAllCategories() {
  if (_allCategories) return _allCategories;
  try {
    _allCategories = await CategoriesAPI.list();
    return _allCategories;
  } catch {
    return [];
  }
}

/**
 * Retourne le HTML d'un input catégorie avec suggestions.
 * @param {string} inputId - id unique de l'input
 * @param {string} initialValue - valeur de départ
 */
function categoryInputHtml(inputId, initialValue = '') {
  return `
    <div class="category-input-wrapper" style="position: relative;">
      <input 
        type="text" 
        class="form-input" 
        id="${inputId}"
        placeholder="Ex: mode, chaussures, électronique..."
        autocomplete="off"
        value="${escapeHtml(initialValue)}"
      >
      <div class="category-suggestions" id="${inputId}-suggestions"></div>
    </div>
  `;
}

/**
 * Initialise l'autocomplétion sur un input catégorie.
 */
async function initCategoryInput(inputId) {
  const input = document.getElementById(inputId);
  const suggestions = document.getElementById(`${inputId}-suggestions`);
  if (!input || !suggestions) return;
  
  const categories = await getAllCategories();
  
  // Style des suggestions
  suggestions.style.cssText = `
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin-top: 4px;
    background: white;
    border: 1.5px solid var(--gray-200);
    border-radius: var(--radius);
    box-shadow: 0 8px 24px rgba(15,23,42,0.1);
    max-height: 240px;
    overflow-y: auto;
    z-index: 100;
    display: none;
  `;
  
  function renderSuggestions(filter = '') {
    const q = filter.toLowerCase();
    const filtered = categories.filter(c => 
      c.name.toLowerCase().includes(q) ||
      (c.description && c.description.toLowerCase().includes(q))
    );
    
    if (filtered.length === 0) {
      suggestions.innerHTML = `
        <div style="padding: 12px 16px; color: var(--gray-500); font-size: 0.85rem;">
          Aucune catégorie trouvée. Contactez l'admin.
        </div>
      `;
      suggestions.style.display = 'block';
      return;
    }
    
    suggestions.innerHTML = filtered.slice(0, 8).map(c => `
      <div 
        class="category-suggestion-item"
        data-name="${escapeHtml(c.name)}"
        style="padding: 10px 16px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.15s;"
        onmouseover="this.style.background='var(--blue-50)'"
        onmouseout="this.style.background='white'"
      >
        <span style="font-size: 1.2rem;">${c.emoji || '🏷️'}</span>
        <div style="flex: 1; min-width: 0;">
          <div style="font-weight: 600; color: var(--blue-900); text-transform: capitalize;">${escapeHtml(c.name)}</div>
          ${c.description ? `<div style="font-size: 0.75rem; color: var(--gray-500);">${escapeHtml(c.description)}</div>` : ''}
        </div>
      </div>
    `).join('');
    
    suggestions.style.display = 'block';
    
    // Click handlers
    suggestions.querySelectorAll('.category-suggestion-item').forEach(item => {
      item.addEventListener('click', () => {
        input.value = item.dataset.name;
        suggestions.style.display = 'none';
      });
    });
  }
  
  // Focus → afficher toutes les catégories
  input.addEventListener('focus', () => renderSuggestions(input.value));
  
  // Frappe → filtrer
  input.addEventListener('input', () => renderSuggestions(input.value));
  
  // Clic ailleurs → fermer
  document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !suggestions.contains(e.target)) {
      suggestions.style.display = 'none';
    }
  });
  
  // Touche Entrée → valider si une suggestion est visible
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      suggestions.style.display = 'none';
    }
    if (e.key === 'Enter') {
      e.preventDefault();
      // Prendre la première suggestion si input vide ou partiel
      const first = suggestions.querySelector('.category-suggestion-item');
      if (first && suggestions.style.display !== 'none') {
        input.value = first.dataset.name;
        suggestions.style.display = 'none';
      }
    }
  });
}