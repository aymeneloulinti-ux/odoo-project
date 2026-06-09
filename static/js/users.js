// users.js
// Expects `canManageUsers` global from template

const canManage = !!window.canManageUsers;
let roles = [];
let currentUserId = null;

(async function initUsersPage() { if (canManage) await loadRoles(); })();

async function loadRoles() {
    try {
        const response = await fetch('/roles/', { headers: { 'Accept': 'application/json' } });
        if (response.ok) {
            roles = await response.json();
            const select = document.getElementById('userRole');
            roles.forEach(r => { const option = document.createElement('option'); option.value = r.id; option.textContent = r.role_name; select.appendChild(option); });
        }
    } catch (err) { console.error('Erreur chargement roles', err); }
}

function openUserModal() {
    currentUserId = null;
    document.getElementById('userModalTitle').textContent = 'Ajouter un utilisateur';
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('userDeleteBtn').style.display = 'none';
    document.getElementById('userModal').style.display = 'flex';
}

function closeUserModal() { document.getElementById('userModal').style.display = 'none'; currentUserId = null; }

async function editUser(userId) {
    try {
        const response = await fetch(`/users/${userId}`);
        if (response.ok) {
            const user = await response.json();
            currentUserId = userId;
            document.getElementById('userModalTitle').textContent = 'Modifier un utilisateur';
            document.getElementById('userId').value = userId;
            document.getElementById('username').value = user.username;
            document.getElementById('userRole').value = user.role_id || '';
            document.getElementById('isActive').checked = !!user.is_active;
            document.getElementById('userDeleteBtn').style.display = 'inline-block';
            document.getElementById('userModal').style.display = 'flex';
        }
    } catch (err) { console.error('Erreur chargement utilisateur', err); alert('Erreur lors du chargement de l\'utilisateur'); }
}

const userFormEl = document.getElementById('userForm');
if (userFormEl) {
    userFormEl.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userId = document.getElementById('userId').value;
        const payload = { username: document.getElementById('username').value, password: document.getElementById('password').value || undefined, role_id: parseInt(document.getElementById('userRole').value), is_active: document.getElementById('isActive').checked };
        try {
            const method = userId ? 'PUT' : 'POST';
            const url = userId ? `/users/${userId}` : '/users/';
            const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            if (response.ok) { closeUserModal(); location.reload(); } else { const err = await response.json().catch(() => null); alert('Erreur: ' + (err?.detail || 'Une erreur est survenue')); }
        } catch (err) { console.error(err); alert('Erreur lors de l\'enregistrement'); }
    });
}

async function deleteUser() {
    if (!currentUserId || !confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) return;
    try {
        const response = await fetch(`/users/${currentUserId}`, { method: 'DELETE' });
        if (response.ok) { closeUserModal(); location.reload(); } else { const err = await response.json().catch(() => null); alert('Erreur: ' + (err?.detail || 'Une erreur est survenue')); }
    } catch (err) { console.error(err); alert('Erreur lors de la suppression'); }
}
