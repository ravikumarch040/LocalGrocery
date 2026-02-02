"""
Integration tests for Cart Service APIs
Tests against running service on http://localhost:8005
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import asyncio
from datetime import datetime
import uuid

# Base URL for Cart Service
BASE_URL = "http://localhost:8008"
TIMEOUT = 30.0

# Test data
TEST_CUSTOMER_ID = f"customer-{uuid.uuid4()}"
TEST_PRODUCT_ID = "prod-test-001"
TEST_STORE_ID = "store-test-001"
TEST_PRICE = 99.99

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class CartAPITester:
    """Integration test suite for Cart Service"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.cart_id = None
        self.item_id = None
    
    def print_test(self, name: str, status: str, details: str = ""):
        """Print test result"""
        color = GREEN if status == "PASS" else RED if status == "FAIL" else YELLOW
        symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"{color}{symbol} {name}{RESET}")
        if details:
            print(f"  {details}")
        
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "SKIP":
            self.skipped += 1
    
    async def test_health_check(self):
        """Test 1: Health check endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    service_name = data.get("service", "")
                    if data.get("status") == "healthy" and ("cart" in service_name.lower()):
                        self.print_test("Health Check", "PASS", f"Status: {data.get('status')}")
                        return True
                    else:
                        self.print_test("Health Check", "FAIL", f"Unexpected response: {data}")
                        return False
                else:
                    self.print_test("Health Check", "FAIL", f"Status: {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("Health Check", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_create_cart(self):
        """Test 2: Create new cart"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/carts/",
                    json={"customer_id": TEST_CUSTOMER_ID},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 201:
                    data = response.json()
                    if "id" in data and data.get("customer_id") == TEST_CUSTOMER_ID:
                        self.cart_id = data["id"]
                        self.print_test("Create Cart", "PASS", f"Cart ID: {self.cart_id}")
                        return True
                    else:
                        self.print_test("Create Cart", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Create Cart", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Create Cart", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_add_item(self):
        """Test 3: Add item to cart"""
        if not self.cart_id:
            self.print_test("Add Item to Cart", "SKIP", "No cart ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/carts/{self.cart_id}/items",
                    json={
                        "product_id": TEST_PRODUCT_ID,
                        "store_id": TEST_STORE_ID,
                        "quantity": 2,
                        "unit_price": TEST_PRICE,
                        "product_name": "Test Product",
                        "product_image_url": "https://example.com/image.jpg"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 201:
                    data = response.json()
                    if "id" in data and data.get("product_id") == TEST_PRODUCT_ID:
                        self.item_id = data["id"]
                        self.print_test("Add Item to Cart", "PASS", f"Item ID: {self.item_id}, Qty: {data.get('quantity')}")
                        return True
                    else:
                        self.print_test("Add Item to Cart", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Add Item to Cart", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Add Item to Cart", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_get_cart(self):
        """Test 4: Get cart with items"""
        if not self.cart_id:
            self.print_test("Get Cart", "SKIP", "No cart ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/carts/{self.cart_id}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") == self.cart_id and "items" in data:
                        items_count = len(data["items"])
                        total_amount = data.get("total_amount", 0)
                        self.print_test("Get Cart", "PASS", f"Items: {items_count}, Total: ₹{total_amount}")
                        return True
                    else:
                        self.print_test("Get Cart", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Get Cart", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get Cart", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_get_customer_cart(self):
        """Test 5: Get customer's active cart"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/carts/customer/{TEST_CUSTOMER_ID}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("customer_id") == TEST_CUSTOMER_ID:
                        self.print_test("Get Customer Cart", "PASS", f"Cart ID: {data.get('id')}")
                        return True
                    else:
                        self.print_test("Get Customer Cart", "FAIL", f"Wrong customer_id: {data}")
                        return False
                else:
                    self.print_test("Get Customer Cart", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get Customer Cart", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_update_item_quantity(self):
        """Test 6: Update cart item quantity"""
        if not self.cart_id or not self.item_id:
            self.print_test("Update Item Quantity", "SKIP", "No cart/item ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/v1/carts/{self.cart_id}/items/{self.item_id}",
                    json={"quantity": 5},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("quantity") == 5:
                        self.print_test("Update Item Quantity", "PASS", f"New quantity: {data.get('quantity')}")
                        return True
                    else:
                        self.print_test("Update Item Quantity", "FAIL", f"Quantity not updated: {data}")
                        return False
                else:
                    self.print_test("Update Item Quantity", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Update Item Quantity", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_bulk_add_items(self):
        """Test 7: Add multiple items in bulk"""
        if not self.cart_id:
            self.print_test("Bulk Add Items", "SKIP", "No cart ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/carts/{self.cart_id}/items/bulk",
                    json={
                        "items": [
                            {
                                "product_id": "prod-bulk-001",
                                "store_id": TEST_STORE_ID,
                                "quantity": 1,
                                "unit_price": 49.99,
                                "product_name": "Bulk Product 1"
                            },
                            {
                                "product_id": "prod-bulk-002",
                                "store_id": TEST_STORE_ID,
                                "quantity": 3,
                                "unit_price": 29.99,
                                "product_name": "Bulk Product 2"
                            }
                        ]
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 201:
                    data = response.json()
                    if "added_count" in data and data["added_count"] == 2:
                        self.print_test("Bulk Add Items", "PASS", f"Added {data['added_count']} items")
                        return True
                    else:
                        self.print_test("Bulk Add Items", "FAIL", f"Unexpected response: {data}")
                        return False
                else:
                    self.print_test("Bulk Add Items", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Bulk Add Items", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_validate_cart(self):
        """Test 8: Validate cart items"""
        if not self.cart_id:
            self.print_test("Validate Cart", "SKIP", "No cart ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/carts/{self.cart_id}/validate",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "is_valid" in data:
                        self.print_test("Validate Cart", "PASS", f"Valid: {data.get('is_valid')}, Items validated: {data.get('items_validated', 0)}")
                        return True
                    else:
                        self.print_test("Validate Cart", "FAIL", f"Missing is_valid: {data}")
                        return False
                else:
                    self.print_test("Validate Cart", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Validate Cart", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_remove_item(self):
        """Test 9: Remove item from cart"""
        if not self.cart_id or not self.item_id:
            self.print_test("Remove Item", "SKIP", "No cart/item ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/v1/carts/{self.cart_id}/items/{self.item_id}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 204:
                    self.print_test("Remove Item", "PASS", f"Item {self.item_id} removed")
                    return True
                else:
                    self.print_test("Remove Item", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Remove Item", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_clear_cart(self):
        """Test 10: Clear all items from cart"""
        if not self.cart_id:
            self.print_test("Clear Cart", "SKIP", "No cart ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/carts/{self.cart_id}/clear",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 204:
                    self.print_test("Clear Cart", "PASS", "All items cleared")
                    return True
                else:
                    self.print_test("Clear Cart", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Clear Cart", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_delete_cart(self):
        """Test 11: Delete cart"""
        if not self.cart_id:
            self.print_test("Delete Cart", "SKIP", "No cart ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/v1/carts/{self.cart_id}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 204:
                    self.print_test("Delete Cart", "PASS", f"Cart {self.cart_id} deleted")
                    return True
                else:
                    self.print_test("Delete Cart", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Delete Cart", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_checkout(self):
        """Test 12: Prepare checkout (create new cart for this test)"""
        try:
            # Create a fresh cart with items for checkout
            test_customer = f"checkout-customer-{uuid.uuid4()}"
            async with httpx.AsyncClient() as client:
                # Create cart
                cart_response = await client.post(
                    f"{self.base_url}/v1/carts/",
                    json={"customer_id": test_customer},
                    timeout=TIMEOUT
                )
                
                if cart_response.status_code != 201:
                    self.print_test("Checkout Preparation", "FAIL", f"Could not create cart: {cart_response.status_code}")
                    return False
                
                checkout_cart_id = cart_response.json()["id"]
                
                # Add an item
                item_response = await client.post(
                    f"{self.base_url}/v1/carts/{checkout_cart_id}/items",
                    json={
                        "product_id": "checkout-prod-001",
                        "store_id": TEST_STORE_ID,
                        "quantity": 1,
                        "unit_price": 199.99,
                        "product_name": "Checkout Test Product"
                    },
                    timeout=TIMEOUT
                )
                
                if item_response.status_code != 201:
                    self.print_test("Checkout Preparation", "FAIL", f"Could not add item: {item_response.status_code}")
                    return False
                
                # Now try checkout
                checkout_response = await client.post(
                    f"{self.base_url}/v1/carts/{checkout_cart_id}/checkout",
                    timeout=TIMEOUT
                )
                
                if checkout_response.status_code == 200:
                    data = checkout_response.json()
                    self.print_test("Checkout Preparation", "PASS", f"Orders prepared: {data.get('orders_count', 0)}")
                    return True
                else:
                    self.print_test("Checkout Preparation", "FAIL", f"Status: {checkout_response.status_code}, Body: {checkout_response.text}")
                    return False
        except Exception as e:
            self.print_test("Checkout Preparation", "FAIL", f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Cart Service Integration Tests{RESET}")
        print(f"{BLUE}Base URL: {self.base_url}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        # Run tests in order
        await self.test_health_check()
        await self.test_create_cart()
        await self.test_add_item()
        await self.test_get_cart()
        await self.test_get_customer_cart()
        await self.test_update_item_quantity()
        await self.test_bulk_add_items()
        await self.test_validate_cart()
        await self.test_remove_item()
        await self.test_clear_cart()
        await self.test_delete_cart()
        await self.test_checkout()
        
        # Print summary
        total = self.passed + self.failed + self.skipped
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Test Summary{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{YELLOW}Skipped: {self.skipped}{RESET}")
        print(f"Pass Rate: {(self.passed/total*100) if total > 0 else 0:.1f}%")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        return self.failed == 0


async def main():
    """Main entry point"""
    tester = CartAPITester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
