import os
import requests

class Database:
    _instance = None
    supabase = None  # <-- Esto debe existir
    
    def __new__(cls):
        if cls._instance is None:
            try:
                instance = super(Database, cls).__new__(cls)
                instance._initialize()
                cls._instance = instance
            except Exception as e:
                print(f"FATAL ERROR: {e}")
                cls._instance = None
        return cls._instance
    
    def _initialize(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        # Guardar en supabase para que app.py lo encuentre
        self.supabase = self  # <-- Esto hace que db.supabase no sea None
        
        print(f"DEBUG: URL = {self.url}")
        print(f"DEBUG: KEY = {self.key[:20]}...")
        
        # Probar conexión
        test_url = f"{self.url}/rest/v1/temas?select=*"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
        
        response = requests.get(test_url, headers=headers)
        print(f"DEBUG: Status = {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Supabase conectado")
        else:
            raise Exception(f"Error {response.status_code}")
    
    # Métodos para hacer queries
    def table(self, nombre_tabla):
        return SupabaseTable(self.url, self.key, nombre_tabla)
    
    def get_cursor(self):
        return None
    
    def execute_query(self, query, params=None):
        return None
    
    def close(self):
        pass


class SupabaseTable:
    def __init__(self, url, key, tabla):
        self.url = url
        self.key = key
        self.tabla = tabla
    
    def select(self, columnas='*'):
        self.columnas = columnas
        return self
    
    def eq(self, columna, valor):
        self.filtro_columna = columna
        self.filtro_valor = valor
        return self
    
    def order(self, columna, desc=False):
        self.orden_columna = columna
        self.orden_desc = desc
        return self
    
    def execute(self):
        url = f"{self.url}/rest/v1/{self.tabla}?select={self.columnas}"
        
        if hasattr(self, 'filtro_columna'):
            url += f"&{self.filtro_columna}=eq.{self.filtro_valor}"
        
        if hasattr(self, 'orden_columna'):
            direccion = "desc" if self.orden_desc else "asc"
            url += f"&order={self.orden_columna}.{direccion}"
        
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
        
        response = requests.get(url, headers=headers)
        return type('Response', (), {'data': response.json()})()
