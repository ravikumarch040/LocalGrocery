"""
Test-specific configuration override for test isolation
"""
import os

# Override DB pool for tests to avoid concurrent operation issues
os.environ["DB_POOL_SIZE"] = "2"
os.environ["DB_MAX_OVERFLOW"] = "0"
