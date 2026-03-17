import requests

print("Testing Register...")
try:
    res = requests.post('http://127.0.0.1:8000/api/auth/register/', json={'email':'test2@x.com','password':'pw'})
    print(res.status_code, res.text)
except Exception as e:
    print("Connection failed:", e)

print("Testing Forgot Password...")
try:
    res2 = requests.post('http://127.0.0.1:8000/api/auth/forgot-password/', json={'email':'test2@x.com'})
    print(res2.status_code, res2.text)
except Exception as e:
    print("Connection failed:", e)
