#!/usr/bin/env python3
"""
Auto-convert test_auth.py to use client fixture.
"""

import re

with open('tests/test_auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace global client usage by injecting client parameter into all test methods
# Pattern: def test_method_name(self):
# Replace with: def test_method_name(self, client):

pattern = r'(\n\s+def test_[a-zA-Z_]+\(self)\):'
replacement = r'\1, client):'

updated_content = re.sub(pattern, replacement, content)

with open('tests/test_auth.py', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("Updated test_auth.py to use client fixture")
