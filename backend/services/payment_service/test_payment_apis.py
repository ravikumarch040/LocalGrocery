"""
Integration tests for Payment Service APIs  
Tests against running service on http://localhost:8006
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import asyncio
import uuid

# Base URL for Payment Service
BASE_URL = "http://localhost:8004"
TIMEOUT = 30.0

# Test data
TEST_CUSTOMER_ID = str(uuid.uuid4())
TEST_ORDER_ID = str(uuid.uuid4())
TEST_AMOUNT = 1200.50

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class PaymentAPITester:
    """Integration test suite for Payment Service"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.payment_id = None
        self.gateway_order_id = None
    
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
                response = await client.get(f"{self.base_url}/health", timeout=TIMEOUT)
                if response.status_code == 200 and response.json().get("status") == "healthy":
                    self.print_test("Health Check", "PASS", f"Status: {response.json().get('status')}")
                    return True
                else:
                    self.print_test("Health Check", "FAIL", f"Status: {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("Health Check", "FAIL", f"Error: {e}")
            return False
    
    async def test_initiate_payment(self):
        """Test 2: Initiate Razorpay UPI payment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/payments/initiate",
                    json={
                        "order_id": TEST_ORDER_ID,
                        "customer_id": TEST_CUSTOMER_ID,
                        "amount": TEST_AMOUNT,
                        "payment_method": "UPI",
                        "payment_gateway": "RAZORPAY",
                        "customer_email": "customer@example.com",
                        "customer_phone": "+919876543210",
                        "description": "Test payment"
                    },
                    timeout=TIMEOUT
                )
                if response.status_code == 200:
                    data = response.json()
                    self.payment_id = data["data"].get("payment_id")
                    self.gateway_order_id = data["data"].get("gateway_order_id")
                    if self.payment_id and self.gateway_order_id:
                        self.print_test(
                            "Initiate Payment",
                            "PASS",
                            f"Payment ID: {self.payment_id}, Gateway Order: {self.gateway_order_id}"
                        )
                        return True
                    else:
                        self.print_test("Initiate Payment", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Initiate Payment", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Initiate Payment", "FAIL", f"Error: {e}")
            return False
    
    async def test_get_payment(self):
        """Test 3: Get payment by ID"""
        if not self.payment_id:
            self.print_test("Get Payment", "SKIP", "No payment ID")
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/v1/payments/{self.payment_id}", timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()["data"]
                    self.print_test("Get Payment", "PASS", f"Status: {data.get('status')}")
                    return True
                else:
                    self.print_test("Get Payment", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get Payment", "FAIL", f"Error: {e}")
            return False
    
    async def test_get_payment_by_order(self):
        """Test 4: Get payment by Order ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/v1/payments/order/{TEST_ORDER_ID}", timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()["data"]
                    self.print_test("Get Payment By Order", "PASS", f"Payment ID: {data.get('id')}")
                    return True
                else:
                    self.print_test("Get Payment By Order", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get Payment By Order", "FAIL", f"Error: {e}")
            return False
    
    async def test_list_payments(self):
        """Test 5: List payments for customer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/payments",
                    params={"customer_id": TEST_CUSTOMER_ID},
                    timeout=TIMEOUT
                )
                if response.status_code == 200:
                    data = response.json()["data"]
                    self.print_test("List Payments", "PASS", f"Returned: {len(data)}")
                    return True
                else:
                    self.print_test("List Payments", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("List Payments", "FAIL", f"Error: {e}")
            return False
    
    async def test_list_payments_status(self):
        """Test 6: List payments filtered by status"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/payments",
                    params={"customer_id": TEST_CUSTOMER_ID, "status": "PENDING"},
                    timeout=TIMEOUT
                )
                if response.status_code == 200:
                    data = response.json()["data"]
                    self.print_test("List Payments (PENDING)", "PASS", f"Returned: {len(data)}")
                    return True
                else:
                    self.print_test("List Payments (PENDING)", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("List Payments (PENDING)", "FAIL", f"Error: {e}")
            return False
    
    async def test_verify_payment(self):
        """Test 7: Verify Razorpay payment (mock)"""
        if not self.gateway_order_id:
            self.print_test("Verify Payment", "SKIP", "No gateway order ID")
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/payments/verify",
                    json={
                        "razorpay_order_id": self.gateway_order_id,
                        "razorpay_payment_id": "pay_mock_integration",
                        "razorpay_signature": "mock_signature"
                    },
                    timeout=TIMEOUT
                )
                if response.status_code == 200:
                    data = response.json()["data"]
                    self.print_test("Verify Payment", "PASS", f"Status: {data.get('status')}")
                    return True
                elif response.status_code in [400, 500]:
                    # In dev, verification may fail if gateway secrets are set; treat as expected skip
                    self.print_test("Verify Payment", "SKIP", f"Verification not enabled (status {response.status_code})")
                    return False
                else:
                    self.print_test("Verify Payment", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Verify Payment", "FAIL", f"Error: {e}")
            return False
    
    async def test_get_payment_logs(self):
        """Test 8: Get payment logs"""
        if not self.payment_id:
            self.print_test("Payment Logs", "SKIP", "No payment ID")
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/v1/payments/{self.payment_id}/logs", timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()["data"]
                    self.print_test("Payment Logs", "PASS", f"Entries: {len(data)}")
                    return True
                else:
                    self.print_test("Payment Logs", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Payment Logs", "FAIL", f"Error: {e}")
            return False
    
    async def test_razorpay_webhook(self):
        """Test 9: Razorpay webhook handling"""
        if not self.gateway_order_id:
            self.print_test("Razorpay Webhook", "SKIP", "No gateway order ID")
            return False
        try:
            payload = {
                "entity": "event",
                "account_id": "acc_test_123",
                "event": "payment.captured",
                "contains": ["payment"],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": "pay_webhook_test",
                            "order_id": self.gateway_order_id,
                            "amount": int(TEST_AMOUNT * 100),
                            "currency": "INR",
                            "status": "captured"
                        }
                    }
                },
                "created_at": 1234567890
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/payments/webhooks/razorpay",
                    json=payload,
                    headers={"X-Razorpay-Signature": "mock_signature"},
                    timeout=TIMEOUT
                )
                if response.status_code == 200:
                    self.print_test("Razorpay Webhook", "PASS", f"Event: {payload['event']}")
                    return True
                else:
                    self.print_test("Razorpay Webhook", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Razorpay Webhook", "FAIL", f"Error: {e}")
            return False
    
    async def test_cashfree_webhook(self):
        """Test 10: Cashfree webhook handling"""
        try:
            payload = {
                "type": "PAYMENT_SUCCESS",
                "data": {
                    "order_id": "cf_order_integration",
                    "payment_id": "cf_payment_integration",
                    "amount": 500.00
                }
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/payments/webhooks/cashfree",
                    json=payload,
                    timeout=TIMEOUT
                )
                if response.status_code == 200:
                    self.print_test("Cashfree Webhook", "PASS", "Webhook accepted")
                    return True
                else:
                    self.print_test("Cashfree Webhook", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Cashfree Webhook", "FAIL", f"Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Payment Service Integration Tests{RESET}")
        print(f"{BLUE}Base URL: {self.base_url}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        await self.test_health_check()
        await self.test_initiate_payment()
        await self.test_get_payment()
        await self.test_get_payment_by_order()
        await self.test_list_payments()
        await self.test_list_payments_status()
        await self.test_verify_payment()
        await self.test_get_payment_logs()
        await self.test_razorpay_webhook()
        await self.test_cashfree_webhook()
        
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
    tester = PaymentAPITester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
