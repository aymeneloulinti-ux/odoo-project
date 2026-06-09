from __future__ import annotations

import os
import sys
from datetime import date, datetime

# Ensure src package is on path when running the script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.session import get_session

from models.role import Role, RoleName
from models.permission import Permission
from models.warehouse import Warehouse
from models.category import Category
from models.product import Product
from models.user import User
from models.stock_movement import StockMovement, MovementType, SourceModule
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def seed():
    session = get_session()
    try:
        from sqlalchemy import select, text

        # Permissions (idempotent)
        perm_codes = ["read_product", "write_product", "manage_users", "manage_stock"]
        perms: list[Permission] = []
        for code in perm_codes:
            existing = session.execute(select(Permission).filter_by(code=code)).scalars().first()
            if existing is None:
                p = Permission(code=code, roles=[])
                session.add(p)
                session.commit()
                perms.append(p)
            else:
                perms.append(existing)

        # Roles (idempotent)
        def get_or_create_role(role_enum: RoleName) -> Role:
            existing = session.execute(select(Role).filter_by(role_name=role_enum)).scalars().first()
            if existing:
                return existing
            r = Role(role_name=role_enum, permissions=[], users=[])
            session.add(r)
            session.commit()
            return r

        admin = get_or_create_role(RoleName.ADMIN)
        manager = get_or_create_role(RoleName.MANAGER)
        warehouse_role = get_or_create_role(RoleName.WAREHOUSE)

        # Ensure association table exists (migration may be missing it)
        session.execute(text(
            """
            CREATE TABLE IF NOT EXISTS role_permission (
                role_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                PRIMARY KEY (role_id, permission_id),
                FOREIGN KEY (role_id) REFERENCES roles(id),
                FOREIGN KEY (permission_id) REFERENCES permissions(id)
            )
            """
        ))
        session.commit()

        # Assign permissions to roles
        admin.permissions = perms
        manager.permissions = [perms[0], perms[1]]  # read/write
        warehouse_role.permissions = [perms[3]]
        session.commit()

        # Warehouses (idempotent)
        def get_or_create_warehouse(name: str, location: str) -> Warehouse:
            existing = session.execute(select(Warehouse).filter_by(name=name)).scalars().first()
            if existing:
                return existing
            w = Warehouse(name=name, location=location, stock_movements=[])
            session.add(w)
            session.commit()
            return w

        w1 = get_or_create_warehouse("Main", "Paris")
        w2 = get_or_create_warehouse("Secondary", "Lyon")

        # Categories (idempotent)
        def get_or_create_category(name: str, location: str) -> Category:
            existing = session.execute(select(Category).filter_by(name=name)).scalars().first()
            if existing:
                return existing
            c = Category(name=name, location=location, products=[])
            session.add(c)
            session.commit()
            return c

        c1 = get_or_create_category("Electronics", "A1")
        c2 = get_or_create_category("Stationery", "B2")

        # Products (idempotent)
        def get_or_create_product(name: str, unit_price: float, category: Category) -> Product:
            existing = session.execute(select(Product).filter_by(name=name)).scalars().first()
            if existing:
                return existing
            prod = Product(name=name, unit_price=unit_price, category_id=category.id, category=category, stock_movements=[])
            session.add(prod)
            session.commit()
            return prod

        p1 = get_or_create_product("Laptop", 1200.0, c1)
        p2 = get_or_create_product("Pen", 1.5, c2)
        p3 = get_or_create_product("Monitor", 350.0, c1)
        p4 = get_or_create_product("Keyboard", 89.99, c1)
        p5 = get_or_create_product("Mouse", 45.0, c1)
        p6 = get_or_create_product("Notebook", 5.0, c2)
        p7 = get_or_create_product("Desk Lamp", 65.0, c1)
        p8 = get_or_create_product("USB Cable", 12.0, c1)
        p9 = get_or_create_product("Printer Paper", 8.5, c2)
        p10 = get_or_create_product("Headset", 120.0, c1)

        # Users (idempotent)
        def get_or_create_user(username: str, role: Role) -> User:
            existing = session.execute(select(User).filter_by(username=username)).scalars().first()
            today = date.today()
            # If user exists but has a non-hashed password (from older seed), fix it
            if existing:
                pw = getattr(existing, 'password_ash', None)
                # Only re-hash the default plain password injected by older seeds
                if pw == "changeme":
                    existing.password_ash = pwd_context.hash(pw)
                    session.add(existing)
                    session.commit()
                return existing
            # Create new user with hashed default password
            hashed = pwd_context.hash("changeme")
            u = User(username=username, password_ash=hashed, is_active=True, updated_at=today, created_at=today, role=role, role_id=role.id, stock_movements=[])
            session.add(u)
            session.commit()
            return u

        u1 = get_or_create_user("admin", admin)
        u2 = get_or_create_user("warehouse_user", warehouse_role)

        # Stock movements (idempotent-ish)
        def month_delta(year: int, month: int, delta: int) -> tuple[int, int]:
            total_months = year * 12 + month - 1 + delta
            return divmod(total_months, 12)[0], divmod(total_months, 12)[1] + 1

        def create_stock_movement_if_missing(product: Product, warehouse: Warehouse, user: User, quantity: int, mtype: MovementType, source: SourceModule, reason: str | None = None, price: float | None = None, created_at: datetime | None = None):
            filters = {
                "product_id": product.id,
                "warehouse_id": warehouse.id,
                "user_id": user.id,
                "quantity": quantity,
                "type": mtype,
            }
            if created_at is not None:
                filters["created_at"] = created_at

            existing = session.execute(
                select(StockMovement).filter_by(**filters)
            ).scalars().first()
            if existing:
                return existing

            if price is None:
                price = product.unit_price if mtype == MovementType.OUT else round(product.unit_price * 0.75, 2)

            sm = StockMovement(
                product_id=product.id,
                warehouse_id=warehouse.id,
                user_id=user.id,
                quantity=quantity,
                price=price,
                type=mtype,
                source_module=source,
                reason=reason,
                created_at=created_at or datetime.utcnow(),
            )
            session.add(sm)
            session.commit()
            return sm

        # Add opening stock at the beginning of the year
        today = date.today()
        start_of_year = datetime(today.year, 1, 5, 9, 0)
        create_stock_movement_if_missing(p1, w1, u2, 20, MovementType.IN, SourceModule.MANUAL, "Opening stock", price=round(p1.unit_price * 0.55, 2), created_at=start_of_year)
        create_stock_movement_if_missing(p2, w1, u2, 300, MovementType.IN, SourceModule.MANUAL, "Opening stock", price=round(p2.unit_price * 0.40, 2), created_at=start_of_year)
        create_stock_movement_if_missing(p3, w1, u2, 18, MovementType.IN, SourceModule.MANUAL, "Opening stock", price=round(p3.unit_price * 0.55, 2), created_at=start_of_year)
        create_stock_movement_if_missing(p6, w1, u2, 220, MovementType.IN, SourceModule.MANUAL, "Opening stock", price=round(p6.unit_price * 0.40, 2), created_at=start_of_year)

        monthly_patterns = [
            (p1, w1, 12, 8, 0.60, 1.30),
            (p3, w1, 14, 10, 0.60, 1.30),
            (p2, w2, 140, 120, 0.45, 1.10),
            (p6, w2, 120, 98, 0.40, 1.15),
        ]

        for offset in range(12):
            year, month = month_delta(today.year, today.month, -offset)
            month_date = datetime(year, month, 15, 10, 0)

            for product, warehouse, base_in, base_out, cost_factor, sell_multiplier in monthly_patterns:
                in_qty = max(base_in + (offset % 3) * 2, 1)
                out_qty = max(base_out + (offset % 4) * 2, 0)
                purchase_price = round(product.unit_price * cost_factor, 2)
                sale_price = round(product.unit_price * sell_multiplier, 2)

                create_stock_movement_if_missing(
                    product,
                    warehouse,
                    u2,
                    in_qty,
                    MovementType.IN,
                    SourceModule.PURCHASE,
                    f"Monthly purchase for {product.name}",
                    price=purchase_price,
                    created_at=month_date,
                )
                create_stock_movement_if_missing(
                    product,
                    warehouse,
                    u2,
                    out_qty,
                    MovementType.OUT,
                    SourceModule.SALES,
                    f"Monthly sale for {product.name}",
                    price=sale_price,
                    created_at=month_date,
                )

        print("Seeding completed successfully")
    except Exception as exc:
        session.rollback()
        print("Seeding failed:", exc)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
