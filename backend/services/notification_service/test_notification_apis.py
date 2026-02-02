"""
Integration tests for Notification Service APIs
Tests against running service on http://localhost:8008
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import asyncio
from datetime import datetime
import uuid

# Base URL for Notification Service
BASE_URL = "http://localhost:8006"
TIMEOUT = 30.0

# Test data
TEST_USER_ID = str(uuid.uuid4())
TEST_PHONE = "+919876543210"
TEST_EMAIL = "test@localgrocery.com"
TEST_FCM_TOKEN = f"fcm_token_{uuid.uuid4().hex[:16]}"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class NotificationAPITester:
    """Integration test suite for Notification Service"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.notification_id = None
        self.device_token_id = None
    
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
    
    async def test_send_sms(self):
        """Test 2: Send SMS notification"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/notifications/sms",
                    json={
                        "user_id": TEST_USER_ID,
                        "phone_number": TEST_PHONE,
                        "message": "Your order #12345 has been confirmed. Expected delivery in 30 minutes.",
                        "template_id": "ORDER_CONFIRMED",
                        "priority": "HIGH"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "notification_id" in data:
                        self.notification_id = data["notification_id"]
                        self.print_test(
                            "Send SMS", 
                            "PASS", 
                            f"SMS sent, ID: {self.notification_id}, Success: {data.get('success')}"
                        )
                        return True
                    else:
                        self.print_test("Send SMS", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Send SMS", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Send SMS", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_send_push(self):
        """Test 3: Send push notification"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/notifications/push",
                    json={
                        "user_id": TEST_USER_ID,
                        "title": "Order Update",
                        "body": "Your order is out for delivery!",
                        "data": {
                            "order_id": "12345",
                            "status": "OUT_FOR_DELIVERY",
                            "deep_link": "app://orders/12345"
                        },
                        "priority": "HIGH"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "notification_id" in data:
                        self.print_test(
                            "Send Push", 
                            "PASS", 
                            f"Push sent, ID: {data['notification_id']}, Success: {data.get('success')}"
                        )
                        return True
                    else:
                        self.print_test("Send Push", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Send Push", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Send Push", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_send_email(self):
        """Test 4: Send email notification"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/notifications/email",
                    json={
                        "user_id": TEST_USER_ID,
                        "recipient_email": TEST_EMAIL,
                        "subject": "Order Confirmation #12345",
                        "body": "Thank you for your order. Your items will be delivered soon.",
                        "html_body": "<h1>Order Confirmed</h1><p>Thank you for your order.</p>",
                        "priority": "NORMAL"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "notification_id" in data:
                        self.print_test(
                            "Send Email", 
                            "PASS", 
                            f"Email sent, ID: {data['notification_id']}, Success: {data.get('success')}"
                        )
                        return True
                    else:
                        self.print_test("Send Email", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Send Email", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Send Email", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_register_device_token(self):
        """Test 5: Register FCM device token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/notifications/device-tokens",
                    json={
                        "user_id": TEST_USER_ID,
                        "token": TEST_FCM_TOKEN,
                        "device_type": "ANDROID",
                        "device_info": {
                            "model": "Pixel 6",
                            "os_version": "Android 13",
                            "app_version": "1.0.0"
                        }
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 201:
                    data = response.json()
                    if "id" in data:
                        self.device_token_id = data["id"]
                        self.print_test(
                            "Register Device Token", 
                            "PASS", 
                            f"Token ID: {self.device_token_id}, Active: {data.get('is_active')}"
                        )
                        return True
                    else:
                        self.print_test("Register Device Token", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Register Device Token", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Register Device Token", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_get_notification(self):
        """Test 6: Get notification by ID"""
        if not self.notification_id:
            self.print_test("Get Notification", "SKIP", "No notification ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/notifications/{self.notification_id}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") == self.notification_id:
                        self.print_test(
                            "Get Notification", 
                            "PASS", 
                            f"Type: {data.get('type')}, Status: {data.get('status')}"
                        )
                        return True
                    else:
                        self.print_test("Get Notification", "FAIL", f"Wrong notification ID: {data}")
                        return False
                else:
                    self.print_test("Get Notification", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get Notification", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_list_notifications(self):
        """Test 7: List notifications"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/notifications?skip=0&limit=10",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.print_test(
                            "List Notifications", 
                            "PASS", 
                            f"Retrieved {len(data)} notifications"
                        )
                        return True
                    else:
                        self.print_test("List Notifications", "FAIL", f"Invalid response format: {data}")
                        return False
                else:
                    self.print_test("List Notifications", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("List Notifications", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_list_notifications_by_user(self):
        """Test 8: List notifications filtered by user"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/notifications?user_id={TEST_USER_ID}&skip=0&limit=10",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.print_test(
                            "List Notifications by User", 
                            "PASS", 
                            f"User {TEST_USER_ID[:8]}... has {len(data)} notifications"
                        )
                        return True
                    else:
                        self.print_test("List Notifications by User", "FAIL", f"Invalid response format: {data}")
                        return False
                else:
                    self.print_test("List Notifications by User", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("List Notifications by User", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_get_user_preferences(self):
        """Test 9: Get user notification preferences"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/notifications/preferences/{TEST_USER_ID}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "sms_enabled" in data or "push_enabled" in data or "email_enabled" in data:
                        self.print_test(
                            "Get User Preferences", 
                            "PASS", 
                            f"SMS: {data.get('sms_enabled')}, Push: {data.get('push_enabled')}, Email: {data.get('email_enabled')}"
                        )
                        return True
                    else:
                        self.print_test("Get User Preferences", "FAIL", f"Invalid response: {data}")
                        return False
                elif response.status_code == 404:
                    self.print_test("Get User Preferences", "SKIP", "No preferences found (expected for new user)")
                    return False
                else:
                    self.print_test("Get User Preferences", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get User Preferences", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_update_user_preferences(self):
        """Test 10: Update user notification preferences"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/v1/notifications/preferences/{TEST_USER_ID}",
                    json={
                        "sms_enabled": True,
                        "push_enabled": True,
                        "email_enabled": False,
                        "order_updates": True,
                        "promotional": False,
                        "delivery_updates": True
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "sms_enabled" in data:
                        self.print_test(
                            "Update User Preferences", 
                            "PASS", 
                            f"Preferences updated: SMS={data.get('sms_enabled')}, Push={data.get('push_enabled')}"
                        )
                        return True
                    else:
                        self.print_test("Update User Preferences", "FAIL", f"Invalid response: {data}")
                        return False
                else:
                    self.print_test("Update User Preferences", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Update User Preferences", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_list_device_tokens(self):
        """Test 11: List user's device tokens"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/notifications/device-tokens?user_id={TEST_USER_ID}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.print_test(
                            "List Device Tokens", 
                            "PASS", 
                            f"User has {len(data)} registered device(s)"
                        )
                        return True
                    else:
                        self.print_test("List Device Tokens", "FAIL", f"Invalid response format: {data}")
                        return False
                else:
                    self.print_test("List Device Tokens", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("List Device Tokens", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_deactivate_device_token(self):
        """Test 12: Deactivate device token"""
        if not self.device_token_id:
            self.print_test("Deactivate Device Token", "SKIP", "No device token ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/v1/notifications/device-tokens/{self.device_token_id}",
                    timeout=TIMEOUT
                )
                
                if response.status_code == 204 or response.status_code == 200:
                    self.print_test("Deactivate Device Token", "PASS", f"Token {self.device_token_id} deactivated")
                    return True
                else:
                    self.print_test("Deactivate Device Token", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Deactivate Device Token", "FAIL", f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Notification Service Integration Tests{RESET}")
        print(f"{BLUE}Base URL: {self.base_url}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        # Run tests in order
        await self.test_health_check()
        await self.test_send_sms()
        await self.test_send_push()
        await self.test_send_email()
        await self.test_register_device_token()
        await self.test_get_notification()
        await self.test_list_notifications()
        await self.test_list_notifications_by_user()
        await self.test_get_user_preferences()
        await self.test_update_user_preferences()
        await self.test_list_device_tokens()
        await self.test_deactivate_device_token()
        
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
    tester = NotificationAPITester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
