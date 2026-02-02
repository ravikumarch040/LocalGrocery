"""Test configuration and fixtures"""
import pytest
import subprocess
import time
import os

# Set test-specific DB pool config BEFORE importing app
os.environ["DB_POOL_SIZE"] = "1"
os.environ["DB_MAX_OVERFLOW"] = "0"


@pytest.fixture(scope="function", autouse=True)
def reset_db_before_test():
    """
    Reset database state BEFORE each test to ensure clean isolation.
    """
    # Truncate OTP table before test to prevent rate limiting
    db_password = os.getenv("PGPASSWORD", "dev_password_change_in_prod")
    db_host = "localhost"
    db_user = "localgrocery"
    db_name = "localgrocery"
    
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password
    
    try:
        # Clear OTP table before test
        subprocess.run(
            [
                "psql",
                "-h", db_host,
                "-U", db_user,
                "-d", db_name,
                "-c", "TRUNCATE TABLE otps CASCADE;"
            ],
            env=env,
            capture_output=True,
            check=True,
            timeout=5
        )
    except Exception as e:
        # Don't fail the test if cleanup fails
        print(f"Warning: Could not clean OTP table before test: {e}")
    
    # Small delay to allow connections to settle
    time.sleep(0.05)
    
    # Run the test
    yield
    
    # Cleanup AFTER test
    time.sleep(0.05)
    try:
        # Clear OTP table after test
        subprocess.run(
            [
                "psql",
                "-h", db_host,
                "-U", db_user,
                "-d", db_name,
                "-c", "TRUNCATE TABLE otps CASCADE;"
            ],
            env=env,
            capture_output=True,
            check=False,  # Don't fail on error
            timeout=5
        )
    except Exception:
        pass  # Silently ignore cleanup errors
