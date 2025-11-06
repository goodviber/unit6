import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from models import Book, Cart, User, Order
from app import app, users, orders, cart, BOOKS


class TestAppRoutes:
    """Test cases for Flask app routes"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test method"""
        # Clear global state before each test
        cart.clear()
        users.clear()
        orders.clear()
        
        # Re-add demo user for tests that need it
        demo_user = User("demo@bookstore.com", "demo123", "Demo User", "123 Demo Street")
        users["demo@bookstore.com"] = demo_user
    
    def test_index_page(self, client):
        """Test the homepage loads correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b"The Great Gatsby" in response.data
        assert b"1984" in response.data
        assert b"I Ching" in response.data
        assert b"Moby Dick" in response.data
    
    def test_add_to_cart_valid_book(self, client):
        """Test adding a valid book to cart"""
        response = client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert cart.get_total_items() == 2
        assert 'The Great Gatsby' in cart.items
    
    def test_add_to_cart_invalid_book(self, client):
        """Test adding an invalid book to cart"""
        response = client.post('/add-to-cart', data={
            'title': 'Nonexistent Book',
            'quantity': '1'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert cart.is_empty()
        assert b'Book not found!' in response.data
    
    def test_add_to_cart_default_quantity(self, client):
        """Test adding book with default quantity"""
        response = client.post('/add-to-cart', data={
            'title': '1984'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert cart.get_total_items() == 1
        assert cart.items['1984'].quantity == 1
    
    def test_view_cart_empty(self, client):
        """Test viewing empty cart"""
        response = client.get('/cart')
        assert response.status_code == 200
    
    def test_view_cart_with_items(self, client):
        """Test viewing cart with items"""
        # Add items to cart first
        cart.add_book(BOOKS[0], 2)
        cart.add_book(BOOKS[1], 1)
        
        response = client.get('/cart')
        assert response.status_code == 200
    
    def test_remove_from_cart(self, client):
        """Test removing item from cart"""
        # Add item first
        cart.add_book(BOOKS[0], 2)
        assert not cart.is_empty()
        
        response = client.post('/remove-from-cart', data={
            'title': 'The Great Gatsby'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'The Great Gatsby' not in cart.items
    
    def test_update_cart_quantity(self, client):
        """Test updating item quantity in cart"""
        # Add item first
        cart.add_book(BOOKS[0], 2)
        
        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '5'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert cart.items['The Great Gatsby'].quantity == 5

    def test_update_cart_zero_quantity(self, client):
        """Test updating item quantity to zero (removal)"""
        # Add item first
        cart.add_book(BOOKS[0], 2)

        response = client.post('/update-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '0'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'The Great Gatsby' not in cart.items

    def test_clear_cart(self, client):
        """Test clearing entire cart"""
        # Add items first
        cart.add_book(BOOKS[0], 2)
        cart.add_book(BOOKS[1], 1)
        assert not cart.is_empty()
        
        response = client.post('/clear-cart', follow_redirects=True)
        
        assert response.status_code == 200
        assert cart.is_empty()
        assert b'Cart cleared!' in response.data
    
    def test_checkout_empty_cart(self, client):
        """Test checkout with empty cart redirects"""
        response = client.get('/checkout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Your cart is empty!' in response.data
    
    def test_checkout_with_items(self, client):
        """Test checkout page with items in cart"""
        # Add items to cart
        cart.add_book(BOOKS[0], 1)
        
        response = client.get('/checkout')
        assert response.status_code == 200
    
    def test_register_new_user(self, client):
        """Test user registration with valid data"""
        response = client.post('/register', data={
            'email': 'newuser@test.com',
            'password': 'password123',
            'name': 'New User',
            'address': '123 Test Street'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'newuser@test.com' in users
        assert b'Account created successfully!' in response.data
    
    def test_register_existing_email(self, client):
        """Test registration with existing email"""
        response = client.post('/register', data={
            'email': 'demo@bookstore.com',  # Already exists
            'password': 'password123',
            'name': 'Test User'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'An account with this email already exists' in response.data
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post('/register', data={
            'email': 'test@test.com',
            # Missing password and name
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please fill in all required fields' in response.data
    
    def test_login_valid_credentials(self, client):
        """Test login with valid credentials"""
        response = client.post('/login', data={
            'email': 'demo@bookstore.com',
            'password': 'demo123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Logged in successfully!' in response.data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/login', data={
            'email': 'demo@bookstore.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post('/login', data={
            'email': 'nonexistent@test.com',
            'password': 'password'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_logout(self, client):
        """Test user logout"""
        # Login first
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'
        
        response = client.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Logged out successfully!' in response.data
    
    def test_account_page_requires_login(self, client):
        """Test account page redirects when not logged in"""
        response = client.get('/account', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please log in to access this page.' in response.data
    
    def test_account_page_logged_in(self, client):
        """Test account page when logged in"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'
        
        response = client.get('/account')
        assert response.status_code == 200
    
    def test_update_profile(self, client):
        """Test updating user profile"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'
        
        response = client.post('/update-profile', data={
            'name': 'Updated Name',
            'address': 'Updated Address'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert users['demo@bookstore.com'].name == 'Updated Name'
        assert users['demo@bookstore.com'].address == 'Updated Address'
        assert b'Profile updated successfully!' in response.data
    
    def test_update_password(self, client):
        """Test updating user password"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'demo@bookstore.com'
        
        response = client.post('/update-profile', data={
            'new_password': 'newpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert users['demo@bookstore.com'].password == 'newpassword123'
        assert b'Password updated successfully!' in response.data


        