"""UI Router for web interface with Jinja2 templates."""

import calendar
from datetime import date, datetime

from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from database.session import get_session
from models.user import User
from models.stock_movement import MovementType, StockMovement
from models.warehouse import Warehouse
from models.product import Product

from services.auth_service import authenticate_user, create_access_token, decode_access_token
router = APIRouter(tags=["UI"])


def get_templates(request: Request):
    """Get templates from app state."""
    return request.app.state.templates


def render_template(request: Request, template_name: str, context: dict = None):
    """Helper function to render Jinja2 templates."""
    if context is None:
        context = {}
    templates = get_templates(request)
    context["request"] = request
    return HTMLResponse(templates.get_template(template_name).render(**context))


class StockStats:
    """Helper class to compute stock statistics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_stats(self):
        """Get overall stock statistics."""
        total_products = self.db.query(Product).count()

        net_quantity = func.sum(
            case(
                (StockMovement.type == "IN", StockMovement.quantity),
                (StockMovement.type == "OUT", -StockMovement.quantity),
                else_=0,
            )
        )
        total_quantity = self.db.query(net_quantity).scalar() or 0
        total_quantity = max(int(total_quantity), 0)

        product_quantities = (
            self.db.query(
                Product.id,
                func.coalesce(net_quantity, 0).label("quantity"),
            )
            .outerjoin(StockMovement, StockMovement.product_id == Product.id)
            .group_by(Product.id)
            .subquery()
        )

        low_stock_count = (
            self.db.query(func.count())
            .select_from(product_quantities)
            .filter(product_quantities.c.quantity < 10)
            .scalar()
        )

        warehouses_count = self.db.query(Warehouse).count()
        
        return {
            "total_products": total_products,
            "total_quantity": int(total_quantity) if total_quantity else 0,
            "low_stock_count": low_stock_count,
            "warehouses_count": warehouses_count,
        }
    
    def get_stock_by_warehouse(self):
        """Get stock statistics by warehouse."""
        warehouses = self.db.query(Warehouse).all()
        result = []

        for warehouse in warehouses:
            product_count = (
                self.db.query(func.count(func.distinct(StockMovement.product_id)))
                .filter(StockMovement.warehouse_id == warehouse.id)
                .scalar() or 0
            )

            total_quantity = (
                self.db.query(
                    func.coalesce(
                        func.sum(
                            case(
                                (StockMovement.type == "IN", StockMovement.quantity),
                                (StockMovement.type == "OUT", -StockMovement.quantity),
                                else_=0,
                            )
                        ),
                        0,
                    )
                )
                .filter(StockMovement.warehouse_id == warehouse.id)
                .scalar() or 0
            )
            total_quantity = max(int(total_quantity), 0)

            result.append({
                "id": warehouse.id,
                "name": warehouse.name,
                "product_count": product_count,
                "total_quantity": int(total_quantity) if total_quantity else 0,
            })
        
        return result
    
    def get_movement_history(self):
        """Get full movement history."""
        movements = (
            self.db.query(StockMovement)
            .order_by(StockMovement.id.desc())
            .all()
        )
        
        result = []
        for movement in movements:
            result.append({
                "product_name": movement.product.name if movement.product else "Unknown",
                "movement_type": movement.type.value if movement.type else "Unknown",
                "quantity": movement.quantity,
                "price": float(movement.price) if movement.price is not None else 0.0,
                "total_amount": float(movement.price * movement.quantity) if movement.price is not None else 0.0,
                "warehouse_name": movement.warehouse.name if movement.warehouse else "Unknown",
                "created_at": movement.created_at,
                "source_module": movement.source_module.value if movement.source_module else "Unknown",
                "reason": movement.reason or "-",
            })
        
        return result

    def get_movement_history_page(self, page: int = 1, limit: int = 20):
        """Get paged movement history."""
        total_movements = self.db.query(func.count(StockMovement.id)).scalar() or 0
        total_pages = max((total_movements + limit - 1) // limit, 1)
        page = min(max(page, 1), total_pages)
        offset = (page - 1) * limit

        movements = (
            self.db.query(StockMovement)
            .order_by(StockMovement.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        result = []
        for movement in movements:
            result.append({
                "product_name": movement.product.name if movement.product else "Unknown",
                "movement_type": movement.type.value if movement.type else "Unknown",
                "quantity": movement.quantity,
                "price": float(movement.price) if movement.price is not None else 0.0,
                "total_amount": float(movement.price * movement.quantity) if movement.price is not None else 0.0,
                "warehouse_name": movement.warehouse.name if movement.warehouse else "Unknown",
                "created_at": movement.created_at,
                "source_module": movement.source_module.value if movement.source_module else "Unknown",
                "reason": movement.reason or "-",
            })

        return {
            "items": result,
            "total": total_movements,
            "page": page,
            "pages": total_pages,
            "limit": limit,
        }

    def get_financial_summary(self):
        """Get revenue, cost, and profit metrics."""
        revenue_expr = func.sum(
            case(
                (StockMovement.type == MovementType.OUT, StockMovement.quantity * StockMovement.price),
                else_=0,
            )
        )
        cost_expr = func.sum(
            case(
                (StockMovement.type == MovementType.IN, StockMovement.quantity * StockMovement.price),
                else_=0,
            )
        )

        total_revenue = self.db.query(func.coalesce(revenue_expr, 0)).scalar() or 0
        total_cost = self.db.query(func.coalesce(cost_expr, 0)).scalar() or 0
        total_profit = float(total_revenue - total_cost)
        total_movements = self.db.query(func.count(StockMovement.id)).scalar() or 0
        gross_margin = float((total_profit / total_revenue) * 100) if total_revenue else 0.0
        avg_profit = float(total_profit / total_movements) if total_movements else 0.0

        return {
            "total_revenue": float(total_revenue),
            "total_cost": float(total_cost),
            "total_profit": total_profit,
            "total_movements": total_movements,
            "gross_margin": round(gross_margin, 2),
            "avg_profit": round(avg_profit, 2),
        }

    def get_monthly_summary(self, year: int, month: int):
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        revenue_expr = func.sum(
            case(
                (StockMovement.type == MovementType.OUT, StockMovement.quantity * StockMovement.price),
                else_=0,
            )
        )
        cost_expr = func.sum(
            case(
                (StockMovement.type == MovementType.IN, StockMovement.quantity * StockMovement.price),
                else_=0,
            )
        )

        monthly_revenue, monthly_cost = self.db.query(
            func.coalesce(revenue_expr, 0),
            func.coalesce(cost_expr, 0),
        ).filter(StockMovement.created_at >= start_date, StockMovement.created_at < end_date).one()

        total_revenue = float(monthly_revenue or 0)
        total_cost = float(monthly_cost or 0)
        total_profit = float(total_revenue - total_cost)
        movement_count = self.db.query(func.count(StockMovement.id)).filter(StockMovement.created_at >= start_date, StockMovement.created_at < end_date).scalar() or 0
        gross_margin = float((total_profit / total_revenue) * 100) if total_revenue else 0.0
        avg_profit = float(total_profit / movement_count) if movement_count else 0.0

        return {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "gross_margin": round(gross_margin, 2),
            "movement_count": movement_count,
            "avg_profit": round(avg_profit, 2),
        }

    def get_monthly_trend(self, months: int = 12):
        def month_delta(year: int, month: int, delta: int) -> tuple[int, int]:
            total_months = year * 12 + month - 1 + delta
            return divmod(total_months, 12)[0], divmod(total_months, 12)[1] + 1

        month_expr = func.date_trunc("month", StockMovement.created_at).label("month")

        rows = (
            self.db.query(
                month_expr,
                func.coalesce(
                    func.sum(
                        case(
                            (StockMovement.type == MovementType.OUT, StockMovement.quantity * StockMovement.price),
                            else_=0,
                        )
                    ), 0,
                ).label("revenue"),
                func.coalesce(
                    func.sum(
                        case(
                            (StockMovement.type == MovementType.IN, StockMovement.quantity * StockMovement.price),
                            else_=0,
                        )
                    ), 0,
                ).label("cost"),
            )
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )

        row_map = {
            (row.month.year, row.month.month): (float(row.revenue or 0), float(row.cost or 0))
            for row in rows
        }

        today = date.today()
        labels = []
        revenues = []
        costs = []
        profits = []

        for offset in range(months - 1, -1, -1):
            year, month = month_delta(today.year, today.month, -offset)
            label = f"{month:02d}/{year}"
            revenue, cost = row_map.get((year, month), (0.0, 0.0))
            labels.append(label)
            revenues.append(revenue)
            costs.append(cost)
            profits.append(round(revenue - cost, 2))

        return {
            "labels": labels,
            "revenue": revenues,
            "cost": costs,
            "profit": profits,
        }

    def get_daily_trend(self, year: int, month: int):
        """Get daily revenue/cost/profit for a given month."""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        day_expr = func.date_trunc("day", StockMovement.created_at).label("day")

        rows = (
            self.db.query(
                day_expr,
                func.coalesce(
                    func.sum(
                        case(
                            (StockMovement.type == MovementType.OUT, StockMovement.quantity * StockMovement.price),
                            else_=0,
                        )
                    ), 0,
                ).label("revenue"),
                func.coalesce(
                    func.sum(
                        case(
                            (StockMovement.type == MovementType.IN, StockMovement.quantity * StockMovement.price),
                            else_=0,
                        )
                    ), 0,
                ).label("cost"),
            )
            .filter(StockMovement.created_at >= start_date, StockMovement.created_at < end_date)
            .group_by(day_expr)
            .order_by(day_expr)
            .all()
        )

        row_map = {
            (row.day.day, row.day.month): (float(row.revenue or 0), float(row.cost or 0))
            for row in rows
        }

        num_days = calendar.monthrange(year, month)[1]
        labels = []
        revenues = []
        costs = []
        profits = []

        for day in range(1, num_days + 1):
            label = f"{day:02d}/{month:02d}"
            revenue, cost = row_map.get((day, month), (0.0, 0.0))
            labels.append(label)
            revenues.append(revenue)
            costs.append(cost)
            profits.append(round(revenue - cost, 2))

        return {
            "labels": labels,
            "revenue": revenues,
            "cost": costs,
            "profit": profits,
        }

    def get_monthly_revenue_chart_data(self, year: int, month: int):
        summary = self.get_monthly_summary(year, month)
        return {
            "labels": ["CA", "Coût"],
            "values": [summary["total_revenue"], summary["total_cost"]],
        }

    def get_monthly_movement_breakdown(self, year: int, month: int):
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        counts_by_type = {movement_type.value: 0 for movement_type in MovementType}

        rows = (
            self.db.query(
                StockMovement.type,
                func.count().label("count"),
            )
            .filter(StockMovement.created_at >= start_date, StockMovement.created_at < end_date)
            .group_by(StockMovement.type)
            .all()
        )

        for movement_type, count in rows:
            type_value = movement_type.value if movement_type else "Unknown"
            counts_by_type[type_value] = int(count or 0)

        return {
            "labels": list(counts_by_type.keys()),
            "counts": list(counts_by_type.values()),
        }

    def get_revenue_chart_data(self):
        summary = self.get_financial_summary()
        return {
            "labels": ["CA", "Coût"],
            "values": [summary["total_revenue"], summary["total_cost"]],
        }

    def get_movement_breakdown(self):
        """Get aggregated movement counts by type."""
        counts_by_type = {movement_type.value: 0 for movement_type in MovementType}
        quantities_by_type = {movement_type.value: 0 for movement_type in MovementType}

        rows = (
            self.db.query(
                StockMovement.type,
                func.count().label("count"),
                func.sum(StockMovement.quantity).label("quantity"),
            )
            .group_by(StockMovement.type)
            .all()
        )

        for movement_type, count, quantity in rows:
            type_value = movement_type.value if movement_type else "Unknown"
            counts_by_type[type_value] = int(count or 0)
            quantities_by_type[type_value] = int(quantity or 0)

        return {
            "labels": list(counts_by_type.keys()),
            "counts": list(counts_by_type.values()),
            "quantities": list(quantities_by_type.values()),
        }
    
    def get_warehouse_activity(self):
        """Get movement counts aggregated by warehouse."""
        warehouses = self.db.query(Warehouse).all()
        warehouse_names = [w.name for w in warehouses]
        warehouse_ids = [w.id for w in warehouses]
        
        movement_counts = (
            self.db.query(
                StockMovement.warehouse_id,
                func.count().label("count"),
            )
            .group_by(StockMovement.warehouse_id)
            .all()
        )
        
        # Map counts to warehouse IDs
        count_map = {wh_id: 0 for wh_id in warehouse_ids}
        for wh_id, count in movement_counts:
            if wh_id in count_map:
                count_map[wh_id] = int(count or 0)
        
        counts = [count_map[wh_id] for wh_id in warehouse_ids]
        
        return {
            "labels": warehouse_names,
            "counts": counts,
        }


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Render login page."""
    # Check if user is already logged in
    token = request.cookies.get("access_token")
    if token and decode_access_token(token):
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return render_template(request, "login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse)
def login_handler(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    """Handle login form submission."""
    user = authenticate_user(db, username, password)
    
    if not user:
        return render_template(request, "login.html", {"error": "Invalid credentials"})
    
    # Create access token
    access_token = create_access_token({"sub": user.username})
    
    # Create response with redirect and cookie
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("access_token", access_token, httponly=True, max_age=3600*24)
    
    return response


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_session)):
    """Render dashboard page."""
    token = request.cookies.get("access_token")
    
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    username = decode_access_token(token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get statistics
    stats = StockStats(db)
    finance_summary = stats.get_financial_summary()
    current_month_summary = stats.get_monthly_summary(date.today().year, date.today().month)
    monthly_trend = stats.get_monthly_trend()
    daily_trend = stats.get_daily_trend(date.today().year, date.today().month)
    monthly_revenue_chart = stats.get_monthly_revenue_chart_data(date.today().year, date.today().month)
    monthly_movement_breakdown = stats.get_monthly_movement_breakdown(date.today().year, date.today().month)
    revenue_chart = stats.get_revenue_chart_data()
    movement_breakdown = stats.get_movement_breakdown()
    
    return render_template(
        request,
        "dashboard.html",
        {
            "user": user,
            "finance_summary": finance_summary,
            "current_month_summary": current_month_summary,
            "monthly_trend": monthly_trend,
            "daily_trend": daily_trend,
            "monthly_revenue_chart": monthly_revenue_chart,
            "monthly_movement_breakdown": monthly_movement_breakdown,
            "revenue_chart": revenue_chart,
            "movement_breakdown": movement_breakdown,
            "current_date": date.today().strftime("%d/%m/%Y"),
        },
    )
@router.get("/stock", response_class=HTMLResponse)
def stock_page(request: Request, page: int = Query(1, ge=1), db: Session = Depends(get_session)):
    """Render stock overview page."""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)

    username = decode_access_token(token)
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    stats = StockStats(db)
    stock_stats = stats.get_stats()
    stock_by_warehouse = stats.get_stock_by_warehouse()
    movement_info = stats.get_movement_history_page(page)
    warehouse_activity = stats.get_warehouse_activity()
    movement_breakdown = stats.get_movement_breakdown()

    return render_template(
        request,
        "stock.html",
        {
            "user": user,
            "stock_stats": stock_stats,
            "stock_by_warehouse": stock_by_warehouse,
            "movement_history": movement_info["items"],
            "warehouse_activity": warehouse_activity,
            "movement_breakdown": movement_breakdown,
            "current_date": date.today().strftime("%d/%m/%Y"),
            "movement_page": movement_info["page"],
            "movement_pages": movement_info["pages"],
            "movement_limit": movement_info["limit"],
            "movement_total": movement_info["total"],
        },
    )


@router.get("/logout", response_class=RedirectResponse)
def logout():
    """Logout user by clearing session cookie."""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
