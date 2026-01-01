# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")

# print(f"API Key loaded: {bool(API_KEY)}")
# print(f"API Key length: {len(API_KEY) if API_KEY else 0}")
# print(f"API Key starts with: {API_KEY[:10] if API_KEY else 'None'}...")

# # Test the API with v1 endpoint (NOT v1beta)
# url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# payload = {
#     "contents": [{
#         "parts": [{"text": "Say hello in one word"}]
#     }]
# }

# print("\n🔄 Testing Gemini API...")
# try:
#     response = requests.post(url, json=payload, timeout=10)
#     print(f"Status Code: {response.status_code}")
#     print(f"Response: {response.text}")
    
#     if response.status_code == 200:
#         print("\n✅ API KEY WORKS!")
#         data = response.json()
#         if "candidates" in data:
#             print(f"Gemini says: {data['candidates'][0]['content']['parts'][0]['text']}")
#     else:
#         print("\n❌ API KEY FAILED!")
#         print("Error details:", response.json())
        
# except Exception as e:
#     print(f"\n❌ ERROR: {e}")