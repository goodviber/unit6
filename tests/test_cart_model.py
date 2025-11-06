import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from models import Book, Cart, CartItem

class TestBook:
    
    def test_book_creation(self):
        book = Book("Test Title", "Fiction", 19.99, "test.jpg")
        assert book.title == "Test Title"
        assert book.category == "Fiction"
        assert book.price == 19.99
        assert book.image == "test.jpg"
        
class TestCartItem:
    
    def test_cart_item_creation(self):
        book = Book("Test Book", "Fiction", 15.99, "test.jpg")
        item = CartItem(book, 3)
        assert item.book == book
        assert item.quantity == 3
    
    def test_cart_item_default_quantity(self):
        book = Book("Test Book", "Fiction", 15.99, "test.jpg")
        item = CartItem(book)
        assert item.quantity == 1
    
    def test_get_total_price(self):
        book = Book("Test Book", "Fiction", 10.00, "test.jpg")
        item = CartItem(book, 4)
        assert item.get_total_price() == 40.00

class TestCart:
    
    def setup_method(self):
        self.cart = Cart()
        self.book1 = Book(title="Book One", category="Fiction", price=15.00, image="img1.jpg")
        self.book2 = Book(title="Book Two", category="Non-Fiction", price=25.00, image="img2.jpg")

    def test_add_book(self):
        self.cart.add_book(self.book1, quantity=2)
        assert self.cart.items[self.book1.title].quantity == 2

    def test_remove_book(self):
        self.cart.add_book(self.book1, quantity=1)
        self.cart.remove_book(self.book1.title)
        assert self.book1.title not in self.cart.items

    def test_update_quantity(self):
        self.cart.add_book(self.book1, quantity=1)
        self.cart.update_quantity(self.book1.title, quantity=5)
        assert self.cart.items[self.book1.title].quantity == 5

    def test_get_total_price(self):
        self.cart.add_book(self.book1, quantity=2)  # 2 * 15.00 = 30.00
        self.cart.add_book(self.book2, quantity=1)  # 1 * 25.00 = 25.00
        total_price = self.cart.get_total_price()
        assert total_price == 55.00

    def test_get_total_items(self):
        self.cart.add_book(self.book1, quantity=3)
        self.cart.add_book(self.book2, quantity=2)
        total_items = self.cart.get_total_items()
        assert total_items == 5

    def test_clear_cart(self):
        self.cart.add_book(self.book1, quantity=1)
        self.cart.clear()
        assert self.cart.is_empty()

    def test_update_quantity_to_zero_removes_item(self):
        self.cart.add_book(self.book1, quantity=2)
        assert "Book One" in self.cart.items
        self.cart.update_quantity("Book One", 0)
        assert "Book One" not in self.cart.items

    def test_update_quantity_negative_removes_item(self):
        self.cart.add_book(self.book1, quantity=1)
        self.cart.update_quantity("Book One", -3)
        assert "Book One" not in self.cart.items

    def test_update_quantity_non_integer_raises(self):
        self.cart.add_book(self.book1, quantity=1)
        assert "Book One" in self.cart.items
        
        with pytest.raises(ValueError):
           self.cart.update_quantity("Book One", None)
           
    def test_update_quantity_nonexistent_book_returns_false(self):
        result = self.cart.update_quantity("Not Here", 2)
        assert result is False