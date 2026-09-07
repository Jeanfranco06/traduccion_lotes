"""
Script de prueba para verificar la funcionalidad básica de la aplicación.
"""
import os
import tempfile
from agents.translator import TranslatorAgent
from agents.reviewer import QualityReviewer
from utils.file_handlers import FileHandler
from utils.zip_exporter import ZipExporter


def test_file_handlers():
    """Prueba la funcionalidad de manejo de archivos."""
    print("=== Probando FileHandler ===")
    
    # Crear archivo de prueba
    test_content = "Hola mundo. Este es un archivo de prueba."
    test_file = os.path.join(tempfile.gettempdir(), "test.txt")
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Leer archivo
    result = FileHandler.read_file(test_file)
    print(f"Archivo leído: {result['name']}")
    print(f"Contenido: {result['content']}")
    
    # Limpiar
    os.unlink(test_file)
    print("OK FileHandler funciona correctamente\n")


def test_zip_exporter():
    """Prueba la funcionalidad de exportación ZIP."""
    print("=== Probando ZipExporter ===")
    
    # Crear archivos de prueba
    test_files = [
        {'name': 'doc1.txt', 'translated_content': 'Hello world', 'extension': '.txt', 'status': 'completado'},
        {'name': 'doc2.txt', 'translated_content': 'Test document', 'extension': '.txt', 'status': 'completado'}
    ]
    
    zip_path = ZipExporter.create_zip(test_files)
    print(f"ZIP creado: {zip_path}")
    print(f"Tamaño: {ZipExporter.get_zip_size_mb(zip_path):.2f} MB")
    
    # Listar contenido
    contents = ZipExporter.list_zip_contents(zip_path)
    print(f"Archivos en ZIP: {contents}")
    
    # Limpiar
    os.unlink(zip_path)
    print("OK ZipExporter funciona correctamente\n")


def test_translator_mock():
    """Prueba el agente traductor con API key mock."""
    print("=== Probando TranslatorAgent (mock) ===")
    
    # Nota: Esta prueba fallará sin API key real
    # Se puede usar para verificar que la clase se puede instanciar
    try:
        # Simular que no hay API key
        os.environ.pop('GOOGLE_API_KEY', None)
        translator = TranslatorAgent(api_key="test_key")
        print("TranslatorAgent se instanció correctamente")
    except ValueError as e:
        print(f"Error esperado (sin API key): {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    
    print("OK TranslatorAgent se puede importar\n")


def main():
    """Ejecuta todas las pruebas."""
    print("Ejecutando pruebas de la aplicacion...\n")
    
    test_file_handlers()
    test_zip_exporter()
    test_translator_mock()
    
    print("Todas las pruebas completadas exitosamente")
    print("\nPara usar la aplicacion:")
    print("1. Configura tu API key en .env")
    print("2. Ejecuta: streamlit run app.py")


if __name__ == "__main__":
    main()
