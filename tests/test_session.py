import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from app import cart

class TestSession:
    #@pytest.fixture(autouse=True)
    def setup_method(self):
        cart.clear()
        
    def test_cart_persistence_across_requests(self, client):
        """Test that cart state persists across requests"""
        # Add item to cart
        client.post('/add-to-cart', data={
            'title': 'The Great Gatsby',
            'quantity': '2'
        })
        
        # Check cart in separate request
        response = client.get('/cart')
        assert response.status_code == 200
        assert cart.get_total_items() == 2
