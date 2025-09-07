import requests
import json
import os
from dotenv import load_dotenv

def test_gemini_api_key():
    """Test Gemini API key status and functionality"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Make sure your .env file contains: GEMINI_API_KEY=your_key_here")
        return False
    
    print(f"🔑 API Key found: {api_key[:10]}...{api_key[-10:]}")
    print("=" * 50)
    
    # Test 1: Basic API connectivity
    print("🧪 Test 1: Basic API connectivity...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hello! Can you respond with 'API is working'?"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Key is VALID and working!")
            
            # Parse response
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                print(f"📝 Response: {content}")
            
            return True
            
        elif response.status_code == 400:
            print("❌ API Key is INVALID")
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
            
        elif response.status_code == 403:
            print("❌ API Key is valid but access is forbidden")
            print("Check if Gemini API is enabled for your project")
            
        elif response.status_code == 429:
            print("⚠️ Rate limit exceeded")
            print("Your API key is valid but you've hit usage limits")
            
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    
    return False

def test_model_availability():
    """Test which Gemini models are available"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return
    
    print("\n🧪 Test 2: Model availability...")
    
    # List available models
    models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(models_url, timeout=30)
        
        if response.status_code == 200:
            models_data = response.json()
            print("✅ Available models:")
            
            for model in models_data.get('models', []):
                model_name = model.get('name', 'Unknown')
                display_name = model.get('displayName', 'No display name')
                print(f"  - {model_name} ({display_name})")
                
        else:
            print(f"❌ Failed to fetch models: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching models: {e}")

def test_crewai_integration():
    """Test CrewAI integration with Gemini"""
    
    print("\n🧪 Test 3: CrewAI integration test...")
    
    try:
        import litellm
        
        # Test LiteLLM with Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        
        response = litellm.completion(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "user", "content": "Say 'CrewAI integration working!'"}],
            api_key=api_key
        )
        
        print("✅ CrewAI/LiteLLM integration is working!")
        print(f"📝 Response: {response.choices[0].message.content}")
        
    except ImportError:
        print("⚠️ LiteLLM not installed. Install with: pip install litellm")
        
    except Exception as e:
        print(f"❌ CrewAI integration error: {e}")

def main():
    """Run all tests"""
    
    print("🚀 Gemini API Key Status Checker")
    print("=" * 50)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found in current directory")
        print("Make sure you have a .env file with GEMINI_API_KEY=your_key")
    
    print()
    
    # Run tests
    if test_gemini_api_key():
        test_model_availability()
        test_crewai_integration()
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    main()