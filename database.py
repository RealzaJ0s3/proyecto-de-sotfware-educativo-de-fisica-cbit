import os
import requests

class Database:
    _instance = None
    supabase = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        print(f"DEBUG: URL = {self.url}")
        print(f"DEBUG: KEY = {self.key[:20]}...")
        
        # Probar con requests directamente
        test_url = f"{self.url}/rest/v1/temas?select=*"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
        
        try:
            response = requests.get(test_url, headers=headers)
            print(f"DEBUG: Status code = {response.status_code}")
            print(f"DEBUG: Response = {response.text[:100]}")
            
            if response.status_code == 200:
                print("✅ Conexion exitosa con requests")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    def get_cursor(self):
        return None
    
    def execute_query(self, query, params=None):
        return None
    
    def close(self):
        pass
