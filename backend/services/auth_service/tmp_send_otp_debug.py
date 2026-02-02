from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
resp = client.post('/api/v1/auth/send-otp', json={'phone': '+919123456789', 'purpose': 'LOGIN'})
with open('debug_out.txt', 'w', encoding='utf-8') as f:
	f.write(f"status {resp.status_code}\n")
	f.write(resp.text)
