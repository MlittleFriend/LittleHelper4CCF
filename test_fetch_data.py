import requests
import json

REFRESH_TOKEN = "eyJzaWduX3RpbWUiOiIyMDI2LTA3LTIxIDEwOjQ1OjA2In0=.eyJ1aWQiOiI4NDk0ODUwMjQiLCJ1c2VyIjp7InJlZnJlc2hUb2tlbkV4cGlyZWRUaW1lIjoiMjAyNi0wOC0yNiAxMTowNTozNSIsInVzZXJJZCI6Ijg0OTQ4NTAyNCJ9fQ==.0AF0CD4BB670A3537058B646BBF8208238D02C050FB60C16CA503F22ED7DB6EB"
BASE = "https://quantapi.51ifind.com/api/v1"


def get_access_token():
    resp = requests.post(
        f"{BASE}/get_access_token",
        headers={"Content-Type": "application/json", "refresh_token": REFRESH_TOKEN},
        timeout=10,
    )
    data = resp.json()
    if data.get("errorcode") != 0:
        raise RuntimeError(f"获取access_token失败: {data}")
    return data["data"]["access_token"]


def realtime_quotation(access_token, codes, indicators):
    resp = requests.post(
        f"{BASE}/real_time_quotation",
        headers={"Content-Type": "application/json", "access_token": access_token},
        json={"codes": codes, "indicators": indicators},
        timeout=10,
    )
    return resp.json()


if __name__ == "__main__":
    token = get_access_token()
    print("access_token 获取成功:", token[:8] + "...(已隐藏)")

    result = realtime_quotation(token, "600519.SH,000001.SZ", "open,high,low,latest,volume,amount")
    print(json.dumps(result, indent=2, ensure_ascii=False))
