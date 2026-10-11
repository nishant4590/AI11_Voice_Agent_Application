from backend.service import OrderService


def test_no_cross_account_read_or_write():
    s = OrderService()
    for name in ("get_order_status", "request_cancellation"):
        assert "error" in s.execute("demo-nishant", name, "ORD-7710")
    assert s.orders["ORD-7710"]["status"] == "processing"


def test_confirmation_bound_to_user_and_single_use():
    s = OrderService()
    result = s.execute("demo-nishant", "request_cancellation", "ORD-9182")
    assert s.orders["ORD-9182"]["status"] == "processing"
    token = result["confirmation_id"]
    assert "error" in s.confirm("other-customer", token)
    assert s.confirm("demo-nishant", token)["status"] == "cancelled"
    assert "error" in s.confirm("demo-nishant", token)


def test_expired_confirmation():
    s = OrderService()
    token = s.execute("demo-nishant", "request_cancellation", "ORD-9182")["confirmation_id"]
    s.pending[token] = ("demo-nishant", "ORD-9182", 0)
    assert "error" in s.confirm("demo-nishant", token)
    assert s.orders["ORD-9182"]["status"] == "processing"
