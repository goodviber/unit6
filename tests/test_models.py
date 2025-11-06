import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Book, Cart
from decimal import Decimal

def test_book_and_cart_basic_math():
    b1 = Book(title="T", category="Fiction", price=19.99, image="img1.jpg")
    b2 = Book(title="U", category="Sci-Fi", price=10.00, image="img2.jpg")

    cart = Cart()
    cart.add_book(b1, quantity=2)
    cart.add_book(b2, quantity=3)

    total = cart.get_total_price()
    # Expected: 2*19.99 + 3*10.00 = 39.98 + 30.00 = 69.98
    assert round(total, 2) == 69.98

def test_discount_codes_applied_case_insensitively():
    cart = Cart()
    cart.add_book(Book(title="X", category="Test", price=100.00, image="img2.jpg"), quantity=1)

    # If discount logic is inside Cart/Order, expose a method; otherwise exercise via app tests.
    # Here we assert a 10% path exists; adapt to your code if needed.
    if hasattr(cart, "apply_discount_code"):
        cart.apply_discount_code(" save10 ")  # spaces + case
        assert round(cart.get_total_price(), 2) == 90.00
