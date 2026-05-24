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
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        
        print(f"DEBUG: SUPABASE_URL existe = {url is not None}")
        print(f"DEBUG: SUPABASE_KEY existe = {key is not None}")
        
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
