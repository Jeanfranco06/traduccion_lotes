import os
import zipfile
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime


class ZipExporter:
    """Exportador de archivos traducidos a formato ZIP."""
    
    @staticmethod
    def create_zip(translated_files: List[Dict[str, Any]], 
                   output_dir: str = None) -> str:
        """
        Crea un archivo ZIP con los archivos traducidos.
        
        Args:
            translated_files: Lista de diccionarios con información de archivos traducidos
                Cada diccionario debe tener: 'name', 'content', 'extension', 'status'
            output_dir: Directorio donde guardar el ZIP (opcional)
            
        Returns:
            Ruta al archivo ZIP creado
        """
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"archivos_traducidos_{timestamp}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in translated_files:
                if file_info.get('status') == 'completado':
                    # Crear contenido del archivo
                    filename = file_info['name']
                    content = file_info.get('translated_content', '')
                    
                    # Generar nombre de archivo traducido
                    export_filename = ZipExporter._get_export_filename(filename, file_info.get('extension', '.txt'))
                    
                    # Para PDFs, intentar crear un PDF real
                    if file_info.get('extension') == '.pdf':
                        pdf_content = ZipExporter._create_pdf_bytes(
                            content, filename,
                            references_text=file_info.get('references_text'),
                            file_info=file_info
                        )
                        if pdf_content:
                            zipf.writestr(export_filename, pdf_content)
                        else:
                            # Fallback a TXT
                            export_filename = export_filename.replace('.pdf', '.txt')
                            zipf.writestr(export_filename, content)
                    else:
                        zipf.writestr(export_filename, content)
        
        return zip_path
    
    @staticmethod
    def _create_pdf_bytes(text: str, original_filename: str,
                          references_text: str = None,
                          file_info: Dict[str, Any] = None) -> Optional[bytes]:
        """
        Crea un PDF preservando la maquetación estructurada (2 columnas, tablas, estilos).
        Reutiliza la generación centralizada de FileHandler.write_file.
        """
        if file_info and file_info.get('pdf_bytes'):
            return file_info['pdf_bytes']

        try:
            from utils.file_handlers import FileHandler
            import tempfile

            # Crear archivo temporal para el PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp_path = tmp.name

            orig_data = file_info.copy() if file_info else {}
            orig_data.setdefault('extension', '.pdf')
            orig_data.setdefault('name', original_filename)

            # Generar PDF usando el motor estructurado
            success = FileHandler.write_file(
                file_path=tmp_path,
                content=text,
                original_data=orig_data
            )

            if not success:
                return None

            # Leer el PDF generado como bytes
            with open(tmp_path, 'rb') as f:
                content = f.read()

            # Limpiar archivo temporal
            try:
                os.remove(tmp_path)
            except Exception:
                pass

            return content

        except Exception as e:
            print(f"Error creating PDF: {e}")
            return None
    
    @staticmethod
    def _get_export_filename(original_name: str, extension: str) -> str:
        """
        Genera el nombre del archivo exportado manteniendo la extension original.
        
        Args:
            original_name: Nombre original del archivo
            extension: Extension del archivo original
            
        Returns:
            Nombre del archivo para exportar
        """
        # Obtener el nombre base sin extension
        base_name = os.path.splitext(original_name)[0]
        
        # Para PDFs, intentar mantener como PDF
        if extension.lower() == '.pdf':
            return f"{base_name}_traducido.pdf"
        else:
            # Para otros formatos, mantener la misma extension
            return f"{base_name}_traducido{extension}"
    
    @staticmethod
    def create_zip_from_dict(translated_dict: Dict[str, str], 
                            original_extensions: Dict[str, str],
                            output_dir: str = None,
                            files_info_map: Optional[Dict[str, Dict[str, Any]]] = None) -> str:
        """
        Crea un ZIP desde un diccionario de archivos traducidos.
        
        Args:
            translated_dict: Diccionario {nombre_archivo: contenido_traducido}
            original_extensions: Diccionario {nombre_archivo: extension_original}
            output_dir: Directorio donde guardar el ZIP
            files_info_map: Metadatos de cada archivo para preservación de maquetación
            
        Returns:
            Ruta al archivo ZIP creado
        """
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"archivos_traducidos_{timestamp}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, content in translated_dict.items():
                ext = original_extensions.get(filename, '.txt')
                file_info = files_info_map.get(filename) if files_info_map else None
                
                # Generar nombre de archivo exportado
                export_filename = ZipExporter._get_export_filename(filename, ext)
                
                # Para PDFs, intentar crear un PDF real
                if ext.lower() == '.pdf':
                    pdf_content = ZipExporter._create_pdf_bytes(
                        text=content,
                        original_filename=filename,
                        references_text=file_info.get('references_text') if file_info else None,
                        file_info=file_info
                    )
                    if pdf_content:
                        zipf.writestr(export_filename, pdf_content)
                    else:
                        # Fallback a TXT
                        export_filename = export_filename.replace('.pdf', '.txt')
                        zipf.writestr(export_filename, content)
                else:
                    zipf.writestr(export_filename, content)
        
        return zip_path
    
    @staticmethod
    def get_zip_size_mb(zip_path: str) -> float:
        """Retorna el tamaño del ZIP en megabytes."""
        if os.path.exists(zip_path):
            size_bytes = os.path.getsize(zip_path)
            return size_bytes / (1024 * 1024)
        return 0.0
    
    @staticmethod
    def list_zip_contents(zip_path: str) -> List[str]:
        """Retorna lista de archivos contenidos en el ZIP."""
        if not os.path.exists(zip_path):
            return []
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            return zipf.namelist()
