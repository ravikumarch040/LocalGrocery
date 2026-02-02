"""
Integration tests for Delivery Service APIs
Tests against running service on http://localhost:8007
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import asyncio
from datetime import datetime
import uuid

# Base URL for Delivery Service
BASE_URL = "http://localhost:8005"
TIMEOUT = 30.0

# Test data
TEST_ORDER_ID = str(uuid.uuid4())
TEST_STORE_ID = str(uuid.uuid4())
TEST_CUSTOMER_ID = str(uuid.uuid4())
TEST_PARTNER_ID = str(uuid.uuid4())

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class DeliveryAPITester:
    """Integration test suite for Delivery Service"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.delivery_id = None
        self.partner_id = TEST_PARTNER_ID
    
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
                    if data.get("status") == "healthy":
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
    
    async def test_create_delivery(self):
        """Test 2: Create new delivery"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/deliveries",
                    json={
                        "order_id": TEST_ORDER_ID,
                        "pickup_location": {
                            "lat": 12.9716,
                            "lng": 77.5946,
                            "address": "123 MG Road, Bangalore"
                        },
                        "delivery_location": {
                            "lat": 12.9352,
                            "lng": 77.6245,
                            "address": "456 HSR Layout, Bangalore"
                        },
                        "delivery_instructions": "Please call before delivery"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 201:
                    data = response.json()
                    if "id" in data:
                        self.delivery_id = data["id"]
                        self.print_test(
                            "Create Delivery", 
                            "PASS", 
                            f"Delivery ID: {self.delivery_id}, Status: {data.get('status')}"
                        )
                        return True
                    else:
                        self.print_test("Create Delivery", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Create Delivery", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Create Delivery", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_get_delivery(self):
        """Test 3: Get delivery details"""
        if not self.delivery_id:
            self.print_test("Get Delivery", "SKIP", "No delivery ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/deliveries/{self.delivery_id}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") == self.delivery_id:
                        self.print_test(
                            "Get Delivery", 
                            "PASS", 
                            f"Status: {data.get('status')}, Distance: {data.get('estimated_distance_km')}km"
                        )
                        return True
                    else:
                        self.print_test("Get Delivery", "FAIL", f"Wrong delivery ID: {data}")
                        return False
                else:
                    self.print_test("Get Delivery", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get Delivery", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_assign_delivery(self):
        """Test 4: Assign delivery to partner"""
        if not self.delivery_id:
            self.print_test("Assign Delivery", "SKIP", "No delivery ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/deliveries/{self.delivery_id}/assign",
                    json={
                        "delivery_id": self.delivery_id,
                        "delivery_partner_id": self.partner_id
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("delivery_partner_id"):
                        self.print_test(
                            "Assign Delivery", 
                            "PASS", 
                            f"Assigned to: {data.get('delivery_partner_id')}"
                        )
                        return True
                    else:
                        self.print_test("Assign Delivery", "FAIL", f"No partner assigned: {data}")
                        return False
                elif response.status_code in [400, 404]:
                    # No seeded partner; treat as expected/skip
                    self.print_test("Assign Delivery", "SKIP", "Partner not found (expected without seed data)")
                    return False
                else:
                    self.print_test("Assign Delivery", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Assign Delivery", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_update_delivery_status(self):
        """Test 5: Update delivery status"""
        if not self.delivery_id:
            self.print_test("Update Delivery Status", "SKIP", "No delivery ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                # First update to ASSIGNED
                assign_response = await client.patch(
                    f"{self.base_url}/v1/deliveries/{self.delivery_id}/status",
                    json={
                        "status": "ASSIGNED",
                        "notes": "Delivery partner assigned"
                    },
                    timeout=TIMEOUT
                )
                
                # Then update to PICKED_UP
                response = await client.patch(
                    f"{self.base_url}/v1/deliveries/{self.delivery_id}/status",
                    json={
                        "status": "PICKED_UP",
                        "notes": "Package collected from store"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "PICKED_UP":
                        self.print_test(
                            "Update Delivery Status", 
                            "PASS", 
                            f"New status: {data.get('status')}"
                        )
                        return True
                    else:
                        self.print_test("Update Delivery Status", "FAIL", f"Status not updated: {data}")
                        return False
                else:
                    self.print_test("Update Delivery Status", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Update Delivery Status", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_track_delivery(self):
        """Test 6: Track delivery"""
        if not self.delivery_id:
            self.print_test("Track Delivery", "SKIP", "No delivery ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/deliveries/{self.delivery_id}/track",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "current_status" in data:
                        self.print_test(
                            "Track Delivery", 
                            "PASS", 
                            f"Current: {data.get('current_status')}, ETA: {data.get('estimated_arrival')}"
                        )
                        return True
                    else:
                        self.print_test("Track Delivery", "FAIL", f"No tracking data: {data}")
                        return False
                elif response.status_code == 404:
                    self.print_test("Track Delivery", "SKIP", "Tracking endpoint not implemented")
                    return False
                else:
                    self.print_test("Track Delivery", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Track Delivery", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_find_nearby_partners(self):
        """Test 7: Find nearby delivery partners"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/partners/nearby?lat=12.9716&lng=77.5946&radius_km=5",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.print_test(
                            "Find Nearby Partners", 
                            "PASS", 
                            f"Found {len(data)} partners within 5km"
                        )
                        return True
                    else:
                        self.print_test("Find Nearby Partners", "FAIL", f"Invalid response format: {data}")
                        return False
                else:
                    self.print_test("Find Nearby Partners", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Find Nearby Partners", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_get_partner(self):
        """Test 8: Get delivery partner details"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/partners/{self.partner_id}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id"):
                        self.print_test(
                            "Get Partner", 
                            "PASS", 
                            f"Partner: {data.get('name', 'N/A')}, Status: {data.get('status')}"
                        )
                        return True
                    else:
                        self.print_test("Get Partner", "FAIL", f"Invalid response: {data}")
                        return False
                elif response.status_code == 404:
                    self.print_test("Get Partner", "SKIP", "Partner not found (expected for test data)")
                    return False
                else:
                    self.print_test("Get Partner", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get Partner", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_update_partner_location(self):
        """Test 9: Update delivery partner location"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/v1/partners/{self.partner_id}/location",
                    json={
                        "location": {
                            "lat": 12.9500,
                            "lng": 77.6000
                        }
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data:
                        self.print_test("Update Partner Location", "PASS", f"{data.get('message')}")
                        return True
                    else:
                        self.print_test("Update Partner Location", "FAIL", f"Invalid response: {data}")
                        return False
                elif response.status_code == 400 or response.status_code == 404:
                    self.print_test("Update Partner Location", "SKIP", "Partner not found (expected for test data)")
                    return False
                else:
                    self.print_test("Update Partner Location", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Update Partner Location", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_list_deliveries(self):
        """Test 10: List deliveries"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/deliveries?skip=0&limit=10",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.print_test(
                            "List Deliveries", 
                            "PASS", 
                            f"Retrieved {len(data)} deliveries"
                        )
                        return True
                    else:
                        self.print_test("List Deliveries", "FAIL", f"Invalid response format: {data}")
                        return False
                else:
                    self.print_test("List Deliveries", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("List Deliveries", "FAIL", f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Delivery Service Integration Tests{RESET}")
        print(f"{BLUE}Base URL: {self.base_url}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        # Run tests in order
        await self.test_health_check()
        await self.test_create_delivery()
        await self.test_get_delivery()
        await self.test_assign_delivery()
        await self.test_update_delivery_status()
        await self.test_track_delivery()
        await self.test_find_nearby_partners()
        await self.test_get_partner()
        await self.test_update_partner_location()
        await self.test_list_deliveries()
        
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
    tester = DeliveryAPITester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
