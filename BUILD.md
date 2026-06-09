# BUILD.md — Analyse et guide du projet Mini ERP

Ce document fournit une analyse complète du projet : comment il fonctionne, les composants clés, des extraits de code et des explications pratiques pour un développeur qui reprend le projet.

## Outils et rôles

 - Alembic : gestion des migrations de schéma. Les fichiers de migration sont dans le dossier `migrations/versions/`. Utilisez `alembic upgrade head` pour appliquer les migrations.
 - SQLAlchemy : ORM utilisé pour déclarer les modèles et interagir avec la base. Les modèles sont dans `src/models/` et la session est configurée dans `src/database/session.py`.
 - Jinja2 : moteur de templates utilisé par FastAPI pour le rendu server-side (fichiers dans `templates/`). Permet des templates conditionnels selon l'utilisateur.
 - FastAPI : framework web pour exposer API et vues. Les routes sont dans `src/api/`.
 - Uvicorn : serveur ASGI léger pour exécuter l'application FastAPI (`uvicorn src.api.main:app --reload`).
 - PostgreSQL (ou autre SGBD) : base de données, configurée via `DB_URL` dans `.env` (exemple dans `exemple.env`).
 - Pytest : suite de tests (`pytest`) avec config dans `pytest.ini`.

## Commandes rapides

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp exemple.env .env
alembic upgrade head
python src/scripts/seed.py
uvicorn src.api.main:app --reload
pytest
```

---

## Architecture générale

Arborescence (principale) :

- `src/api/` : définition des routes et vues (login, UI, API REST).
- `src/services/` : logique métier (services appelés par les routes).
- `src/models/` : définitions SQLAlchemy (User, Role, Product, ...).
- `src/database/` : configuration de la session et moteur SQLAlchemy.
- `templates/` : templates Jinja2 pour les pages HTML.
- `static/` : CSS et JS statiques.

Le projet suit un pattern simple :

- Les routes reçoivent la requête, résolvent les dépendances (ex : `get_db`, `get_current_user`), appellent un service et renvoient un template ou JSON.
- Les services encapsulent la logique d'accès aux modèles et règles métiers (création, validation, filtrage, ...).
- Les modèles représentent le schéma de la base et contiennent des helpers si nécessaire.

Exemple issu du projet :

```py
@router.get("/products", response_class=HTMLResponse)
def products_page(request: Request, db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    username = decode_access_token(token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    stats = ProductStats(db)
    all_products = stats.get_all_products_with_stock()
    low_stock_products = stats.get_low_stock_products()

    return render_template(
        request,
        "products.html",
        {
            "user": user,
            "all_products": all_products,
            "low_stock_products": low_stock_products,
            "current_date": date.today().strftime("%d/%m/%Y"),
        },
    )
```

Service métier séparé dans `src/services/product_service.py` :

```py
def delete_product(product_id: int, db: Session) -> None:
    prod = get_product(product_id, db)
    movement_count = db.execute(
        select(func.count())
        .select_from(StockMovement)
        .filter(StockMovement.product_id == product_id)
    ).scalar() or 0
    if movement_count:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer un produit qui possède des ventes ou des mouvements de stock enregistrés.",
        )
    db.delete(prod)
    db.commit()
```

Ce pattern montre la séparation claire : la route gère la requête, le service gère la règle métier et le modèle gère l'accès à la base.

---

## Modèles (src/models)

Les entités principales sont : `User`, `Role`, `Permission`, `Product`, `Warehouse`, `StockMovement`.

Concepts clés à retenir :

- Chaque modèle est une classe SQLAlchemy (hérite de `Base` depuis `src/models/base.py`).
- Les relations Many-to-Many (ex : `Role` <-> `Permission`) sont définies via des tables d'association (`role_permission_table.py`).

Exemple simplifié (pattern) :

```py
class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	email = Column(String, unique=True, index=True)
	hashed_password = Column(String)
	is_active = Column(Boolean, default=True)
	roles = relationship('Role', secondary=role_user_table, back_populates='users')

	def has_permission(self, name: str) -> bool:
		for r in self.roles:
			if any(p.name == name for p in r.permissions):
				return True
		return False
```

Points importants :

- `is_active` : champ utilisé pour bloquer la connexion des comptes désactivés (vérifier côté UI et API).
- Indexation sur `email` pour accélérer les requêtes de login.
- Les helpers de modèle (p.ex. `has_permission`) centralisent la logique d'autorisation côté domaine.

Fichiers :

- `src/models/user.py` — gestion des utilisateurs et propriétés (email, mot de passe, is_active).
- `src/models/role.py`, `src/models/permission.py`, `src/models/role_permission_table.py` — RBAC.

---

## Routes (src/api)

Responsabilités :

- `src/api/main.py` : point d'entrée FastAPI et montage des sous-routers.
- `src/api/auth.py` : endpoints API liés à l'auth (login via API, token refresh si présent, dépendances pour obtenir l'utilisateur courant et vérifier permissions).
- `src/api/ui.py` : endpoints qui rendent les templates HTML (login page, dashboard, listes).

Pattern d'une route UI :

```py
@router.post('/login')
def post_login(email: str = Form(...), password: str = Form(...), db=Depends(get_db)):
	user = get_user_by_email(db, email)
	if not user or not verify_password(password, user.hashed_password):
		return templates.TemplateResponse('login.html', {'error': 'Identifiants invalides'})
	if not user.is_active:
		return templates.TemplateResponse('login.html', {'error': 'Utilisateur inactif'})
	# créer token, cookie, rediriger vers dashboard

```

Dépendances utiles : `get_db()` (session), `get_current_user()` (décode token et cherche user), `require_permissions(...)` (validation RBAC).

---

## Authentification et `auth_service` (src/services/auth_service.py)

Composants :

- Hashing des mots de passe : généralement `bcrypt` ou `passlib`.
- Création de JWT (ou autre token) : `create_access_token(payload)` avec une clé `SECRET_KEY` et une durée d'expiration.
- Décodage et validation du token : `decode_access_token(token)`.

Flux de connexion (simplifié) :

1. L'utilisateur soumet email + mot de passe (via UI ou API).
2. Le code récupère l'utilisateur en base : `get_user_by_email(db, email)`.
3. Vérification du mot de passe : `verify_password(plain, hashed)` — si faux, erreur générique.
4. Vérification du statut `is_active` — si faux, renvoyer message spécifique (UI) ou HTTP 403 (API).
5. Si OK, `create_access_token({'sub': user.id})` et renvoyer le token (ou le placer dans un cookie de session selon l'implémentation).

Extrait-type :

```py
def authenticate_user(db, email: str, password: str):
	user = user_service.get_by_email(db, email)
	if not user:
		return None
	if not verify_password(password, user.hashed_password):
		return None
	if not user.is_active:
		raise InactiveUserError()
	return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
	to_encode = data.copy()
	# ajouter exp
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt
```

Remarques pratiques :

- Gardez la logique d'auth dans `src/services/auth_service.py` pour pouvoir la tester isolément.
- Pour l'API, renvoyez des codes HTTP précis (401 pour non authentifié, 403 pour non autorisé, 400 pour données invalides).
- Pour l'UI, affichez un message clair si l'utilisateur est inactif — cela a déjà été ajusté dans `src/api/ui.py`.

---

## Services (pattern général, `src/services`)

Organisation : un fichier par domaine (ex : `user_service.py`, `product_service.py`, `role_service.py`).

Responsabilités typiques d'un service :

- encapsuler l'accès aux modèles (CRUD),
- appliquer les règles métiers (p.ex. protection de suppression si product lié à stock),
- orchestrer transactions et validations.

Exemple d'API publique d'un service :

```py
def create_product(db, payload):
	# validations métier
	p = Product(**payload)
	db.add(p)
	db.commit()
	db.refresh(p)
	return p

def delete_product(db, product_id):
	p = db.get(Product, product_id)
	if p.is_linked_to_stock():
		raise DomainError('Impossible de supprimer un produit lié')
	db.delete(p)
	db.commit()

```

Conseils :

- Renvoyez des exceptions métiers claires pour permettre aux routes d'afficher des erreurs compréhensibles.
- Testez les services sans dépendre de FastAPI (unit tests rapides en utilisant une session DB en mémoire ou fixtures pytest).

---

## Templates, HTML et JS (frontend léger)

Organisation :

- `templates/` contient les pages principales (`login.html`, `dashboard.html`, `products.html`, ...).
- `templates/partials/` contient des fragments réutilisables (liste produits, barre utilisateur, etc.).
- `static/js/` contient des petits scripts pour enrichir l'UI (recherche asynchrone, manipulation DOM, appels fetch API).

Exemple d'utilisation Jinja2 pour afficher conditionnellement des sections selon l'utilisateur :

```html
{% if current_user and current_user.has_permission('products.view') %}
  <a href="/products">Produits</a>
{% endif %}
```

Dans `src/api/ui.py`, on passe typiquement `{'request': request, 'current_user': current_user}` au template afin que Jinja puisse examiner `current_user`.

Exemple simple côté JS pour recherche asynchrone :

```js
document.querySelector('#search').addEventListener('input', async (e) => {
  const q = e.target.value
  const res = await fetch(`/api/products?q=${encodeURIComponent(q)}`)
  const data = await res.json()
  renderResults(data)
})
```

Bonnes pratiques :

- Laissez la logique critique côté serveur (validation, autorisation). Le JS doit rester une amélioration progressive.
- Utilisez des templates partiels pour éviter la duplication.

---

## Templates conditionnels selon l'utilisateur

Cas d'usage : afficher/masquer des actions selon rôle/permission.

Implémentation :

1. Dans la dépendance `get_current_user()` (ou dans la route UI), charger l'utilisateur avec ses rôles et permissions.
2. Passer `current_user` au template :

```py
return templates.TemplateResponse('dashboard.html', {'request': request, 'current_user': current_user})
```

3. Dans Jinja :

```html
{% if current_user and current_user.is_active and current_user.has_permission('product.create') %}
  <button id="create-product">Créer un produit</button>
{% endif %}
```

Astuce : évitez d'exposer des données sensibles dans les templates. Les templates sont destinés à l'affichage ; toute autorisation critique doit être revalidée côté API/service.

---

## Tests et qualité

- `tests/` contient des tests unitaires et d'intégration. Utilisez `pytest` pour exécuter la suite.
- Fixtures utiles : une DB temporaire (SQLite en mémoire ou une base de test Postgres), `client` FastAPI TestClient, sessions fixtures de SQLAlchemy.

Exemple d'un test d'authentification :

```py
def test_login_inactive_user(client, db_session, seed_users):
	# seed_users crée un utilisateur inactive
	res = client.post('/login', data={'email':'inactive@example.com','password':'x'})
	assert 'Utilisateur inactif' in res.text
```

---

## Checklist d'opérations fréquentes

- Créer/activer l'environnement : voir section Commandes rapides.
- Appliquer migrations : `alembic upgrade head`.
- Remplir la base pour dev : `python src/scripts/seed.py`.
- Lancer l'app : `uvicorn src.api.main:app --reload`.
- Exécuter les tests : `pytest`.

---

## Où regarder dans le code (repères rapides)

- Routes UI : [src/api/ui.py](src/api/ui.py)
- Routes API / Auth : [src/api/auth.py](src/api/auth.py)
- Entrée app : [src/api/main.py](src/api/main.py)
- Sessions DB : [src/database/session.py](src/database/session.py)
- Services : [src/services/](src/services/)
- Modèles : [src/models/](src/models/)
- Templates : [templates/](templates/)

---

Si tu veux, je peux :

- ajouter des extraits de code plus détaillés extraits directement des fichiers du projet,
- annoter chaque modèle/route avec des liens vers des lignes précises,
- ajouter une section « guide de contribution » pour expliquer comment ajouter une nouvelle entité (modèle + migration + route + service + template).

Dis-moi quelle précision tu veux en plus, et je complète `BUILD.md`.

---

## Extraits de code depuis le projet (avec liens)

Voici des extraits choisis directement depuis le code, avec un lien vers les lignes correspondantes pour consultation rapide.

- `User` (modèle) — champs essentiels et méthode de permission : [src/models/user.py](src/models/user.py#L15-L33)

```py
class User(Base):
	__tablename__ ="users"
	id: Mapped[int] = mapped_column(primary_key=True, init=False)
	username: Mapped[str] = mapped_column(nullable=False)
	password_ash: Mapped[str] = mapped_column(nullable=False)
	is_active: Mapped[bool] = mapped_column(nullable=False)
	...
	def has_permission(self, permission_code: str) -> bool:
		if not self.role:
			return False
		return any(p.code == permission_code for p in self.role.permissions)
```

- Auth service — authentification et création/décodage de token : [src/services/auth_service.py](src/services/auth_service.py#L33-L47)

```py
def authenticate_user(db: Session, username: str, password: str) -> User | None:
	user = get_user(db, username)
	if not user:
		return None
	if not verify_password(password, user.password_ash):
		return None
	return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
	to_encode = data.copy()
	expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode.update({"exp": expire})
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

- Dépendances d'auth API (validation du token et utilisateur courant) : [src/api/auth.py](src/api/auth.py#L28-L36) et login token endpoint : [src/api/auth.py](src/api/auth.py#L81-L84)

```py
def get_current_user(request: Request, token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
	if not token:
		token = request.cookies.get("access_token")
	# decode token, extraire 'sub' puis charger user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	user = authenticate_user(db, form_data.username, form_data.password)
	...
```

- Exemple de route UI / helpers de templates : [src/api/ui.py](src/api/ui.py#L18-L26)

```py
def get_templates(request: Request):
	"""Get templates from app state."""
	return request.app.state.templates

def render_template(request: Request, template_name: str, context: dict = None):
	templates = get_templates(request)
	context["request"] = request
	return HTMLResponse(templates.get_template(template_name).render(**context))
```

- Exemple de logique métier dans un service (protection suppression produit) : [src/services/product_service.py](src/services/product_service.py#L1-L20) et suppression : [src/services/product_service.py](src/services/product_service.py#L55-L67)

```py
def create_product(payload, db: Session) -> Product:
	cat = db.execute(select(Category).filter_by(id=payload.category_id)).scalars().first()
	if not cat:
		raise HTTPException(status_code=400, detail="Category not found")
	...

def delete_product(product_id: int, db: Session) -> None:
	prod = get_product(product_id, db)
	movement_count = db.execute(...).scalar() or 0
	if movement_count:
		raise HTTPException(status_code=400, detail="Impossible de supprimer un produit qui possède des ventes ou des mouvements de stock enregistrés.")
```

- Templates conditionnels (extrait) : [templates/dashboard.html](templates/dashboard.html#L12-L18)

```html
{% if user.role and user.has_permission('read_product') %}
<li><a href="/products">Produits</a></li>
{% endif %}
```

- JS côté produit (recherche asynchrone et modal produit) : [static/js/products.js](static/js/products.js#L1-L40) (recherche et chargement), et édition/suppression plus bas.

```js
async function searchProducts(query) {
  const response = await fetch(`/products/search?q=${encodeURIComponent(query)}`)
  if (response.ok) {
	const html = await response.text()
	document.getElementById('products-list-container').innerHTML = html
  }
}
```

---

Si tu veux d'autres extraits (par exemple chaque modèle complet ou chaque route avec lien), je peux les ajouter et référencer précisément les lignes souhaitées.

