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
        # PRUEBA: Poner credenciales directamente
        url = "https://nyihvqzyusipbtynmpzh.supabase.co"
        key = "sb_publishable_wyN3Jd33ZjblZ3L_WD8FOg_4ZgucK-f"
        
        print(f"DEBUG: URL = {url}")
        print(f"DEBUG: KEY = {key[:20]}...")
        
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
