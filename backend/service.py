"""Deterministic local order service. No real customer data or purchases."""
import secrets
import time
from threading import Lock


class OrderService:
    def __init__(self):
        self.orders = {
            "ORD-9182": {"owner": "demo-nishant", "status": "processing", "delivery": "Monday"},
            "ORD-7710": {"owner": "other-customer", "status": "processing", "delivery": "Tuesday"},
        }
        self.pending = {}
        self.lock = Lock()

    def owned(self, user, order_id):
        order = self.orders.get(order_id)
        if not order or order["owner"] != user:
            return None
        return order

    def execute(self, user, name, order_id):
        with self.lock:
            order = self.owned(user, order_id)
            if order is None:
                return {"error": "Order unavailable for this account."}
            if name == "get_order_status":
                return {"order_id": order_id, "status": order["status"], "delivery": order["delivery"]}
            if name == "request_cancellation":
                if order["status"] != "processing":
                    return {"error": "Order is not eligible for cancellation."}
                token = secrets.token_urlsafe(24)
                self.pending[token] = (user, order_id, time.monotonic() + 60)
                return {"pending_confirmation": True, "order_id": order_id, "confirmation_id": token,
                        "message": "Use the on-screen confirmation button. No cancellation has occurred."}
            return {"error": "Tool is not allowed."}

    def confirm(self, user, token):
        with self.lock:
            item = self.pending.get(token)
            if not item or item[0] != user or item[2] < time.monotonic():
                return {"error": "Confirmation invalid or expired."}
            self.pending.pop(token)
            order = self.owned(user, item[1])
            if not order or order["status"] != "processing":
                return {"error": "Order is not eligible for cancellation."}
            order["status"] = "cancelled"
            return {"order_id": item[1], "status": "cancelled"}
