// products.js
// Expects `canWriteProduct` global from template

const canWrite = !!window.canWriteProduct;
let categories = [];
let currentProductId = null;

(async function initProductsPage() {
    await loadCategories();
    attachProductSearchListener();
})();

async function loadCategories() {
    try {
        const response = await fetch('/categories/', { headers: { 'Accept': 'application/json' } });
        if (response.ok) {
            categories = await response.json();
            const select = document.getElementById('productCategory');
            categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erreur lors du chargement des catégories:', error);
    }
}

function attachProductSearchListener() {
    const searchInput = document.getElementById('productSearch');
    if (!searchInput) return;
    let searchTimeout;
    searchInput.addEventListener('input', (event) => {
        clearTimeout(searchTimeout);
        const query = event.target.value.trim();
        if (!query) { location.reload(); return; }
        searchTimeout = setTimeout(() => { searchProducts(query); }, 300);
    });
}

async function searchProducts(query) {
    try {
        const response = await fetch(`/ui/products/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            const html = await response.text();
            const container = document.getElementById('products-list-container');
            if (container) container.innerHTML = html;
        }
    } catch (error) { console.error('Erreur lors de la recherche:', error); }
}

function openProductModal() {
    currentProductId = null;
    document.getElementById('modalTitle').textContent = 'Ajouter un produit';
    document.getElementById('productId').value = '';
    document.getElementById('productForm').reset();
    document.getElementById('deleteBtn').style.display = 'none';
    document.getElementById('productModal').style.display = 'flex';
}

function closeProductModal() { document.getElementById('productModal').style.display = 'none'; currentProductId = null; }

async function editProduct(productId) {
    try {
        const response = await fetch(`/products/${productId}`);
        if (response.ok) {
            const product = await response.json();
            currentProductId = productId;
            document.getElementById('modalTitle').textContent = 'Modifier le produit';
            document.getElementById('productId').value = productId;
            document.getElementById('productName').value = product.name;
            document.getElementById('productPrice').value = product.unit_price;
            document.getElementById('productCategory').value = product.category_id || '';
            const deleteBtn = document.getElementById('deleteBtn');
            if (canWrite) deleteBtn.style.display = 'inline-block';
            document.getElementById('productModal').style.display = 'flex';
        }
    } catch (error) { console.error('Erreur lors du chargement du produit:', error); alert('Erreur lors du chargement du produit'); }
}

const productFormEl = document.getElementById('productForm');
if (productFormEl) {
    productFormEl.addEventListener('submit', async (event) => {
        event.preventDefault();
        const productId = document.getElementById('productId').value;
        const payload = { name: document.getElementById('productName').value, unit_price: parseFloat(document.getElementById('productPrice').value), category_id: parseInt(document.getElementById('productCategory').value) };
        try {
            const method = productId ? 'PUT' : 'POST';
            const url = productId ? `/products/${productId}` : '/products/';
            const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            if (response.ok) { closeProductModal(); location.reload(); } else { const error = await response.json(); alert('Erreur: ' + (error.detail || 'Une erreur s\'est produite')); }
        } catch (error) { console.error('Erreur lors de l\'enregistrement:', error); alert('Erreur lors de l\'enregistrement'); }
    });
}

async function deleteProduct() {
    if (!currentProductId || !confirm('Êtes-vous sûr de vouloir supprimer ce produit?')) return;
    try {
        const response = await fetch(`/products/${currentProductId}`, { method: 'DELETE' });
        if (response.ok) { closeProductModal(); location.reload(); } else { const error = await response.json().catch(() => null); alert('Erreur lors de la suppression: ' + (error?.detail || 'Une erreur s\'est produite')); }
    } catch (error) { console.error('Erreur lors de la suppression:', error); alert('Erreur lors de la suppression'); }
}

window.onclick = function(event) { const modal = document.getElementById('productModal'); if (event.target === modal) modal.style.display = 'none'; };
