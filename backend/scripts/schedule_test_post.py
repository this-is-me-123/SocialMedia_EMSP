import requests
import datetime

url = "http://127.0.0.1:8000/api/posts/"
payload = {
    "platform": "facebook",
    "content": "test_image.jpg",
    "caption": "This is a test post from API",
    "scheduled_time": (datetime.datetime.now() + datetime.timedelta(minutes=1)).isoformat(),
    "user_id": 1,
    "media_urls": ["https://example.com/image.jpg"],
    "metadata": {"hashtags": ["test", "api"]}
}

try:
    response = requests.post(url, json=payload)
    print("Status code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)