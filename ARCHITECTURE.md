# Architecture du projet Mini ERP

## 1. Vue d'ensemble

Ce projet est une application web backend en Python basée sur FastAPI, SQLAlchemy et Jinja2 pour la partie interface utilisateur.

Objectif : gérer un mini ERP avec produits, catégories, utilisateurs, rôles, permissions, stock, entrepôts et mouvements.

---

## 2. Arborescence principale

- `src/` : code applicatif principal
- `templates/` : pages HTML Jinja2 pour l’interface utilisateur
- `static/` : ressources statiques CSS et JavaScript
- `tests/` : jeux de tests unitaires et d’intégration
- `requirements.txt` : dépendances Python
- `alembic.ini` et `migrations/` : gestion de version de schéma de base de données
- `exemple.env` : exemple de configuration d’environnement

---

## 3. Détail dossier par dossier

### 3.1 `src/`

C’est le cœur de l’application.

#### 3.1.1 `src/api/`

Contient l’API FastAPI et les routes.

- `main.py`
  - Point d’entrée FastAPI.
  - Monte les fichiers statiques `static/` et initialise Jinja2.
  - Inclut tous les routeurs (`auth`, `ui`, `products`, `categories`, `roles`, `permissions`, `warehouses`, `stock_movements`, `users`).
  - Définit une route racine simple `/`.

- `ui.py`
  - Fournit les routes frontend HTML.
  - Rend les pages Jinja2 et prépare les données nécessaires aux vues `dashboard`, `stock`, `products`, `users`, etc.
  - Contient des helpers de calculs de statistiques et de tendances pour l’interface.

- `deps.py`
  - Donne le `dependency injection` pour la session de base de données.
  - Garantit la fermeture propre de la session après chaque requête.

- Autres routeurs (`products.py`, `categories.py`, `roles.py`, `permissions.py`, `warehouses.py`, `stock_movements.py`, `users.py`)
  - Exposent les endpoints RESTful.
  - Utilisent des schémas Pydantic pour valider les requêtes et réponses.
  - Appliquent des permissions via `require_permission(...)` et `get_current_active_user`.

- `schemas.py`
  - Contient les modèles Pydantic utilisés dans les routes API.
  - Sert à définir les payloads d’entrée (`ProductCreate`, `ProductUpdate`, etc.) et les sorties JSON.

- `auth.py`
  - Gère l’authentification, le login, la gestion des tokens JWT et l’autorisation.
  - Protège les endpoints selon les permissions utilisateur.

#### 3.1.2 `src/database/`

- `session.py`
  - Charge les variables d’environnement avec `python-dotenv`.
  - Crée l’engine SQLAlchemy avec `DB_URL`.
  - Définit `SessionLocal` et le helper `get_session()`.

#### 3.1.3 `src/models/`

Contient les modèles SQLAlchemy représentant le schéma de données.

- `base.py` : modèle de base commun avec métaclasse et configuration partagée.
- `category.py`, `product.py`, `warehouse.py`, `stock_movement.py`, `user.py`, `role.py`, `permission.py`
  - Modélisent les entités métier.
  - Définissent les relations (produit ↔ catégorie, stock ↔ entrepôt, utilisateur ↔ rôle, rôle ↔ permissions).
- `role_permission_table.py`
  - Table d’association many-to-many entre rôles et permissions.

#### 3.1.4 `src/services/`

Couche métier.

- Chaque service encapsule la logique de gestion des entités.
- Par exemple `product_service.py` :
  - liste les produits,
  - récupère un produit,
  - crée, met à jour, supprime des produits,
  - vérifie les contraintes métier avant suppression.
- D’autres fichiers de service gèrent les utilisateurs, catégories, permissions, rôles, mouvements et entrepôts.
- `auth_service.py` traite l’authentification et la génération/décodage de JWT.

#### 3.1.5 `src/scripts/`

Scripts utilitaires pour initialiser ou nettoyer la base de données.

- `seed.py` : peupler la base avec des données de démonstration.
- `clear_db.py` : vider ou réinitialiser des données de développement.

---

### 3.2 `templates/`

Interface utilisateur server-side renderisée avec Jinja2.

- `base.html`
  - Layout principal.
  - Charge `static/css/style.css` et expose les blocs `extra_css`, `content`, `extra_js`.

- `dashboard.html`, `stock.html`, `products.html`, `users.html`, `login.html`
  - Pages principales de l’application.
  - Utilisent des blocs de style et de script pour charger du CSS/JS spécifiques.

- `partials/`
  - Composants réutilisables comme les listes de produits, d’utilisateurs ou l’historique des mouvements.
  - Permettent d’inclure du HTML partagé via `{% include %}`.

---

### 3.3 `static/`

Contient les ressources front-end statiques.

- `static/css/`
  - `style.css` : styles globaux et variables CSS.
  - `dashboard.css` : styles UI pour dashboard, tableaux, cartes KPI, sections et graphiques.

- `static/js/`
  - Fichiers JS séparés pour éviter le code inline dans les templates.
  - `dashboard_kpis.js` : logique de rendu des graphiques et du toggle KPI.
  - `stock_charts.js` : logique des graphiques de stock et de pagination.
  - `products.js` : gestion du formulaire produit, recherche, modal, CRUD.
  - `users.js` : gestion du formulaire utilisateur, rôle, modal, CRUD.

---

### 3.4 `tests/`

Contient les tests pour valider le fonctionnement.

- `test_auth_service.py` : tests d’authentification et de permissions.
- `test_rbac_utils.py` : tests de gestion des rôles et permissions.
- `test_rbac_integration.py` : tests d’intégration des règles RBAC.
- `conftest.py` : configurations communes et fixtures pytest.

---

## 4. Flux de requête

### 4.1 Requête web UI

1. L’utilisateur accède à une URL comme `/dashboard`, `/stock`, `/products` ou `/users`.
2. FastAPI utilise `src/api/ui.py` pour préparer les données.
3. Les données sont injectées dans un template Jinja2.
4. Le navigateur reçoit du HTML rendu côté serveur.
5. Les assets CSS et JS statiques sont servis depuis `static/`.

### 4.2 Requête API

1. Le frontend ou un client envoie un appel REST vers `/products`, `/users`, `/stock_movements`, etc.
2. Le routeur `src/api/<module>.py` gère la route.
3. Les dépendances FastAPI injectent une session DB via `src/api/deps.py`.
4. Le routeur appelle le service métier approprié dans `src/services/`.
5. Le service exécute les requêtes SQLAlchemy sur les modèles de `src/models/`.
6. La réponse JSON est renvoyée au client.

---

## 5. Base de données

- `src/database/session.py` gère la connexion via `SQLAlchemy`.
- `DB_URL` est lu depuis l’environnement (`.env` / `exemple.env`).
- `alembic/` contient la configuration et les versions de migrations.
- Les modèles SQLAlchemy représentent le schéma.

---

## 6. Sécurité et RBAC

- Authentification gérée par JWT et `auth_service.py`.
- Les routes API appliquent `require_permission(...)` pour vérifier les actions.
- L’UI est également conditionnée par les permissions utilisateur.

---

## 7. Dépendances clés

- `fastapi` : framework HTTP/API.
- `uvicorn` : serveur ASGI.
- `SQLAlchemy` : ORM.
- `Jinja2` : templates HTML.
- `python-dotenv` : chargement de la configuration.
- `passlib`, `python-jose` : sécurité et JWT.
- `psycopg2` : pilote PostgreSQL.

---

## 8. Exécution locale

1. Activer l’environnement virtuel.
2. Charger la configuration dans `.env` ou `exemple.env`.
3. Lancer le serveur :

```bash
uvicorn src.api.main:app --reload
```

4. Ouvrir le navigateur sur `http://127.0.0.1:8000`.

---

## 9. Points forts à présenter

- Séparation nette entre API, services métier et modèles.
- UI server-side rendu avec Jinja2 + assets statiques.
- Architecture FastAPI standard avec routers et dépendances.
- Usage de SQLAlchemy pour le data layer et Alembic pour les migrations.
- Code frontend organisé dans `static/js/`, ce qui facilite le debug et la maintenance.
- RBAC intégré pour gérer les permissions au niveau des routes.

---

## 10. Exemple de chemin critique

Pour ajouter un produit :

- Route POST `/products/` dans `src/api/products.py`
- Validation via `src/api/schemas.py`
- Permission `write_product` via `api/auth.py`
- Logique métier dans `src/services/product_service.py`
- Persistance via SQLAlchemy dans `src/models/product.py`

---

## 11. Conclusion

Ce projet combine un backend API REST moderne et une interface HTML/Jinja2, avec une structure claire :

- `src/api` pour les routes,
- `src/services` pour le métier,
- `src/models` pour le schéma,
- `templates` et `static` pour le front.

C’est un bon exemple d’architecture Python full-stack légère et bien organisée.
