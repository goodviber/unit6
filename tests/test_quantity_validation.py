import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app import cart, BOOKS

class TestQuantityValidation:
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        cart.clear()
    
    def test_add_to_cart_invalid_quantity_string(self, client):
        """Test adding book with invalid string quantity"""
        response = client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': 'invalid'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid quantity. Please enter a valid number.' in response.data
        assert cart.is_empty()
    
    def test_add_to_cart_negative_quantity(self, client):
        """Test adding book with negative quantity"""
        response = client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '-5'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Quantity must be a positive number' in response.data
        assert cart.is_empty()
    
    def test_add_to_cart_zero_quantity(self, client):
        """Test adding book with zero quantity"""
        response = client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '0'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Quantity must be a positive number' in response.data
        assert cart.is_empty()
    
    def test_add_to_cart_excessive_quantity(self, client):
        """Test adding book with excessive quantity"""
        response = client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '999'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Quantity cannot exceed 100 items' in response.data
        assert cart.is_empty()
    
    def test_add_to_cart_empty_quantity(self, client):
        """Test adding book with empty quantity (should default to 1)"""
        response = client.post('/add-to-cart', data={
            'title': 'The Great Gatsby'
            # No quantity field
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert cart.get_total_items() == 1
    
    def test_update_cart_invalid_quantity_string(self, client):
        """Test updating cart with invalid string quantity"""
        # Add book first
        cart.add_book(BOOKS[0], 1)
        
        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': 'abc'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid quantity. Please enter a valid number.' in response.data
        # Original quantity should remain unchanged
        assert cart.items['The Great Gatsby'].quantity == 1
    
    def test_update_cart_negative_quantity(self, client):
        """Test updating cart with negative quantity"""
        cart.add_book(BOOKS[0], 2)
        
        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '-1'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Quantity cannot be negative' in response.data
        # Original quantity should remain unchanged
        assert cart.items['The Great Gatsby'].quantity == 2
    
    def test_update_cart_zero_quantity_removes_item(self, client):
        """Test updating cart with zero quantity removes item"""
        cart.add_book(BOOKS[0], 2)
        
        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '0'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'The Great Gatsby' not in cart.items
    
    def test_update_cart_float_quantity(self, client):
        """Test updating cart with decimal quantity"""
        cart.add_book(BOOKS[0], 1)
        
        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2.5'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid quantity. Please enter a valid number.' in response.data
        assert cart.items['The Great Gatsby'].quantity == 1