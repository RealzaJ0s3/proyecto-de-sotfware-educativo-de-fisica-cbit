import os
from supabase import create_client
import traceback

class Database:
    _instance = None
    supabase = None
    
    def __new__(cls):
        if cls._instance is None:
            try:
                instance = super(Database, cls).__new__(cls)
                instance._initialize()
                cls._instance = instance
            except Exception as e:
                print(f"FATAL ERROR en Database.__new__: {e}")
                traceback.print_exc()
                cls._instance = None
        return cls._instance
    
    def _initialize(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        print(f"DEBUG: URL = {url}")
        print(f"DEBUG: KEY = {key[:30]}..." if key else "DEBUG: KEY = None")
        print(f"DEBUG: KEY length = {len(key) if key else 0}")
        
        if not url or not key:
            raise Exception("Faltan SUPABASE_URL o SUPABASE_KEY")
        
        try:
            self.supabase = create_client(url, key)
            print("✅ Supabase conectado exitosamente")
        except Exception as e:
            print(f"❌ ERROR conectando a Supabase: {e}")
            traceback.print_exc()
            raise
    
    def get_cursor(self):
        return None
    
    def execute_query(self, query, params=None):
        return None
    
    def close(self):
        pass
