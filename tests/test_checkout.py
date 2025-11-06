import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from models import Order
from app import orders, cart, BOOKS

class TestCheckout:
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        cart.clear()
        orders.clear()
        cart.add_book(BOOKS[0], 2)  # Add items for checkout tests
    
    def test_process_checkout_missing_fields(self, client):
        """Test checkout with missing required fields"""
        response = client.post('/process-checkout', data={
            'name': '',  # Missing required field
            'email': 'test@test.com',
            'payment_method': 'credit_card'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please fill in the name field' in response.data
    
    def test_process_checkout_valid_data(self, client):
        """Test successful checkout process"""
        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@test.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '1234567890123456',
            'expiry_date': '12/25',
            'cvv': '123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Your order has been successfully processed' in response.data
        assert cart.is_empty() 
    
    def test_process_checkout_with_discount(self, client):
        """Test checkout with valid discount code"""
        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@test.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '1234567890123456',
            'expiry_date': '12/25',
            'cvv': '123',
            'discount_code': 'SAVE10'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'$19.78' in response.data
    
    def test_process_checkout_invalid_discount(self, client):
        """Test checkout with invalid discount code"""
        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@test.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '1234567890123456',
            'expiry_date': '12/25',
            'cvv': '123',
            'discount_code': 'INVALID'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'$21.98' in response.data
    
    def test_discount_code_lowercase(self, client):
        """Test discount code in lowercase"""
        response = client.post('/process-checkout', data={
            'name': 'Test User',
            'email': 'test@test.com',
            'address': '123 Test St',
            'city': 'Test City',
            'zip_code': '12345',
            'payment_method': 'credit_card',
            'card_number': '4532015112830366',
            'expiry_date': '12/25',
            'cvv': '123',
            'discount_code': 'save10'  # Lowercase
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'$19.78' in response.data
    
    def test_order_confirmation_invalid_order(self, client):
        """Test order confirmation page with invalid order ID"""
        response = client.get('/order-confirmation/INVALID', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Order not found' in response.data