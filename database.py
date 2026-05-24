import os
from supabase import create_client
import traceback

class Database:
    _instance = None
    supabase = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        print(f"DEBUG: URL = {url[:30]}..." if url else "DEBUG: URL = NONE")
        print(f"DEBUG: KEY = {key[:20]}..." if key else "DEBUG: KEY = NONE")
        print(f"DEBUG: KEY length = {len(key) if key else 0}")
        
        if url and key:
            try:
                self.supabase = create_client(url, key)
                print("✅ Supabase conectado exitosamente")
            except Exception as e:
                print(f"❌ ERROR conectando a Supabase: {e}")
                traceback.print_exc()
                raise
        else:
            print("❌ ERROR: SUPABASE_URL o SUPABASE_KEY no encontradas")
            raise Exception("Credenciales de Supabase no configuradas")
    
    def get_cursor(self):
        return None
    
    def execute_query(self, query, params=None):
        return None
    
    def close(self):
        pass
