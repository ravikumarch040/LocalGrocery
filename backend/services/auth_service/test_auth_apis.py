"""
Integration tests for Auth Service APIs
Tests against running service on http://localhost:8001
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import httpx
import asyncio
from datetime import datetime

# Base URL for Auth Service
BASE_URL = "http://localhost:8001"
TIMEOUT = 30.0

# Test data
TEST_PHONE = f"+9198765432{datetime.now().strftime('%S')}"  # Unique phone using seconds
TEST_ROLE = "CUSTOMER"
TEST_NAME = "Test User"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class AuthAPITester:
    """Integration test suite for Auth Service"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.passed = 0
        self.failed = 0
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
    
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
                    if data.get("status") == "healthy" and data.get("service") == "auth":
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
    
    async def test_send_otp(self):
        """Test 2: Send OTP to phone number"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/send-otp",
                    json={
                        "phone": TEST_PHONE,
                        "purpose": "LOGIN"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") is True:
                        self.print_test("Send OTP", "PASS", f"Phone: {TEST_PHONE}")
                        return True
                    else:
                        self.print_test("Send OTP", "FAIL", f"Success=False: {data}")
                        return False
                else:
                    self.print_test("Send OTP", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Send OTP", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_verify_otp(self):
        """Test 3: Verify OTP and login (fetch OTP from database)"""
        try:
            # Fetch OTP from database (dev mode stores it)
            import asyncpg
            
            conn = await asyncpg.connect(
                host="localhost",
                port=5432,
                user="localgrocery",
                password="dev_password_change_in_prod",
                database="localgrocery"
            )
            
            # Get the most recent OTP for this phone
            otp_record = await conn.fetchrow(
                """
                SELECT otp_code FROM otps 
                WHERE phone = $1 AND purpose = 'LOGIN' AND is_verified = FALSE
                ORDER BY created_at DESC LIMIT 1
                """,
                TEST_PHONE
            )
            
            await conn.close()
            
            if not otp_record:
                self.print_test("Verify OTP & Login", "FAIL", "No OTP found in database")
                return False
            
            otp_code = otp_record['otp_code']
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/verify-otp",
                    json={
                        "phone": TEST_PHONE,
                        "otp": otp_code,
                        "name": TEST_NAME,
                        "role": TEST_ROLE
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data and "refresh_token" in data:
                        self.access_token = data["access_token"]
                        self.refresh_token = data["refresh_token"]
                        self.user_id = data.get("user_id")
                        self.print_test("Verify OTP & Login", "PASS", f"User ID: {self.user_id}")
                        return True
                    else:
                        self.print_test("Verify OTP & Login", "FAIL", f"Missing tokens: {data}")
                        return False
                else:
                    self.print_test("Verify OTP & Login", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Verify OTP & Login", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_get_profile(self):
        """Test 4: Get user profile using access token"""
        if not self.access_token:
            self.print_test("Get User Profile", "SKIP", "No access token available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("phone") == TEST_PHONE and data.get("role") == TEST_ROLE:
                        self.print_test("Get User Profile", "PASS", f"Phone: {data.get('phone')}, Role: {data.get('role')}")
                        return True
                    else:
                        self.print_test("Get User Profile", "FAIL", f"Unexpected data: {data}")
                        return False
                else:
                    self.print_test("Get User Profile", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Get User Profile", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_refresh_token(self):
        """Test 5: Refresh access token"""
        if not self.refresh_token:
            self.print_test("Refresh Token", "SKIP", "No refresh token available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/refresh",
                    json={"refresh_token": self.refresh_token},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        new_access_token = data["access_token"]
                        self.print_test("Refresh Token", "PASS", f"New token received (len={len(new_access_token)})")
                        # Update access token for subsequent tests
                        self.access_token = new_access_token
                        return True
                    else:
                        self.print_test("Refresh Token", "FAIL", f"Missing access_token: {data}")
                        return False
                else:
                    self.print_test("Refresh Token", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Refresh Token", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_logout(self):
        """Test 6: Logout and revoke refresh token"""
        if not self.refresh_token:
            self.print_test("Logout", "SKIP", "No refresh token available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/logout",
                    headers={"Authorization": f"Bearer {self.refresh_token}"},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") is True:
                        self.print_test("Logout", "PASS", f"Message: {data.get('message')}")
                        return True
                    else:
                        self.print_test("Logout", "FAIL", f"Success=False: {data}")
                        return False
                else:
                    self.print_test("Logout", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
                    return False
        except Exception as e:
            self.print_test("Logout", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_invalid_otp(self):
        """Test 7: Verify OTP with invalid code"""
        try:
            # Send OTP first
            phone = f"+9198765488{datetime.now().strftime('%S')}"
            async with httpx.AsyncClient() as client:
                send_response = await client.post(
                    f"{self.base_url}/api/v1/auth/send-otp",
                    json={"phone": phone, "purpose": "LOGIN"},
                    timeout=TIMEOUT
                )
                
                if send_response.status_code != 200:
                    self.print_test("Invalid OTP (401)", "FAIL", f"Failed to send OTP: {send_response.status_code}")
                    return False
                
                # Try invalid OTP
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/verify-otp",
                    json={
                        "phone": phone,
                        "otp": "000000",  # Invalid OTP
                        "name": "Test",
                        "role": "CUSTOMER"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 401:
                    self.print_test("Invalid OTP (401)", "PASS", "Correctly rejected invalid OTP")
                    return True
                else:
                    self.print_test("Invalid OTP (401)", "FAIL", f"Expected 401, got {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("Invalid OTP (401)", "FAIL", f"Error: {str(e)}")
            return False
    
    async def test_invalid_token(self):
        """Test 8: Access protected endpoint with invalid token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/auth/me",
                    headers={"Authorization": "Bearer invalid_token_here"},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 401:
                    self.print_test("Invalid Token (401)", "PASS", "Correctly rejected invalid token")
                    return True
                else:
                    self.print_test("Invalid Token (401)", "FAIL", f"Expected 401, got {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("Invalid Token (401)", "FAIL", f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Auth Service Integration Tests{RESET}")
        print(f"{BLUE}Base URL: {self.base_url}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        # Run tests in order
        await self.test_health_check()
        await self.test_send_otp()
        await self.test_verify_otp()
        await self.test_get_profile()
        await self.test_refresh_token()
        await self.test_logout()
        await self.test_invalid_otp()
        await self.test_invalid_token()
        
        # Print summary
        total = self.passed + self.failed
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Test Summary{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"Pass Rate: {(self.passed/total*100) if total > 0 else 0:.1f}%")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        return self.failed == 0


async def main():
    """Main entry point"""
    tester = AuthAPITester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
