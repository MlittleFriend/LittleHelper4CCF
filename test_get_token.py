import requests
import json

URL = "https://quantapi.51ifind.com/api/v1/get_access_token"
HEADERS = {
    "Content-Type": "application/json",
    "refresh_token": "eyJzaWduX3RpbWUiOiIyMDI2LTA3LTIxIDEwOjQ1OjA2In0=.eyJ1aWQiOiI4NDk0ODUwMjQiLCJ1c2VyIjp7InJlZnJlc2hUb2tlbkV4cGlyZWRUaW1lIjoiMjAyNi0wOC0yNiAxMTowNTozNSIsInVzZXJJZCI6Ijg0OTQ4NTAyNCJ9fQ==.0AF0CD4BB670A3537058B646BBF8208238D02C050FB60C16CA503F22ED7DB6EB"
}

try:
    resp = requests.post(URL, headers=HEADERS, timeout=10)
    print("Status:", resp.status_code)
    print("Response:", resp.text)
    if resp.status_code == 200:
        data = resp.json()
        print("Parsed JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)
