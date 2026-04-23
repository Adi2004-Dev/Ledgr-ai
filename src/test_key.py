import requests

# Put your API key inside the quotes below
API_KEY = "AIzaSyDxL-eE0u2HyMCKPxhafEdmxI7aO44mjSk"

print("🔍 Pinging Google's Servers...")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("\n✅ SUCCESS! Your key is valid. Here are the models you are allowed to use:\n")
    for model in data.get("models", []):
        if "generateContent" in model.get("supportedGenerationMethods", []):
            print(f" - {model['name']}")
else:
    print(f"\n❌ FAILED. Google is blocking this key. Error {response.status_code}:")
    print(response.text)