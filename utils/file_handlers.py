import os
import json
import pandas as pd
import tempfile
from typing import Dict, Any, Optional
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation
import openpyxl
from bs4 import BeautifulSoup


class FileHandler:
    """Manejador de archivos para lectura y escritura de diferentes formatos."""
    
    @staticmethod
    def read_file(file_path: str) -> Dict[str, Any]:
        """
        Lee un archivo y retorna su contenido y metadatos.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Dict con 'content', 'extension', 'name', y 'metadata'
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo {file_path} no existe")
        
        name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        result = {
            'name': name,
            'extension': ext,
            'content': None,
            'metadata': {},
            'original_file_path': file_path
        }
        
        if ext == '.txt':
            result['content'] = FileHandler._read_text(file_path)
        elif ext == '.pdf':
            # Para PDF, convertir a DOCX primero para preservar formato
            docx_path = FileHandler.pdf_to_docx(file_path)
            if docx_path:
                result['content'] = FileHandler._read_docx(docx_path)
                result['docx_path'] = docx_path
                result['converted_from_pdf'] = True
            else:
                result['content'] = FileHandler._read_pdf(file_path)
        elif ext == '.docx':
            result['content'] = FileHandler._read_docx(file_path)
        elif ext == '.pptx':
            result['content'] = FileHandler._read_pptx(file_path)
        elif ext in ['.xlsx', '.xls']:
            result['content'] = FileHandler._read_excel(file_path)
        elif ext == '.json':
            result['content'] = FileHandler._read_json(file_path)
        elif ext == '.html':
            result['content'] = FileHandler._read_html(file_path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {ext}")
        
        return result
    
    @staticmethod
    def pdf_to_docx(pdf_path: str) -> Optional[str]:
        """
        Convierte un PDF a DOCX preservando el formato.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Ruta al archivo DOCX creado o None si falla
        """
        try:
            import logging
            import warnings
            logging.getLogger("fontTools").setLevel(logging.WARNING)
            logging.getLogger("pdf2docx").setLevel(logging.WARNING)
            warnings.filterwarnings("ignore", message=".*fitz API is deprecated.*")

            from pdf2docx import Converter
            
            # Crear archivo temporal para el DOCX
            temp_dir = tempfile.gettempdir()
            docx_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.docx'
            docx_path = os.path.join(temp_dir, docx_filename)
            
            # Convertir PDF a DOCX
            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()
            
            return docx_path
            
        except Exception as e:
            print(f"Error al convertir PDF a DOCX: {e}")
            return None
    
    @staticmethod
    def docx_to_pdf(docx_path: str, output_dir: str = None) -> Optional[str]:
        """
        Convierte un DOCX a PDF preservando el formato y maquetación fielmente.
        Utiliza COM automation directo con CoInitialize para compatibilidad con hilos de Streamlit.
        
        Args:
            docx_path: Ruta al archivo DOCX
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Ruta al archivo PDF creado o None si falla
        """
        if not os.path.exists(docx_path):
            return None

        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        pdf_filename = os.path.splitext(os.path.basename(docx_path))[0] + '.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)
        abs_docx = os.path.abspath(docx_path)
        abs_pdf = os.path.abspath(pdf_path)

        # 1. Intentar primero con win32com directo (thread-safe y con cierre garantizado)
        try:
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            word = None
            doc = None
            try:
                word = win32com.client.DispatchEx('Word.Application')
                word.Visible = False
                word.DisplayAlerts = 0
                doc = word.Documents.Open(abs_docx)
                doc.SaveAs(abs_pdf, FileFormat=17) # 17 = wdFormatPDF
                if os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 0:
                    return abs_pdf
            finally:
                if doc:
                    try:
                        doc.Close(False)
                    except Exception:
                        pass
                if word:
                    try:
                        word.Quit()
                    except Exception:
                        pass
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
        except Exception as win32_err:
            print(f"[PDF Converter] win32com error: {win32_err}")

        # 2. Fallback a docx2pdf si win32com directo no completó
        try:
            from docx2pdf import convert
            convert(abs_docx, abs_pdf)
            if os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 0:
                return abs_pdf
        except Exception as e:
            print(f"Error al convertir DOCX a PDF con docx2pdf: {e}")

        return None
    
    @staticmethod
    def create_pdf_from_text(text: str, output_path: str,
                            title: str = None, font_size: int = 11,
                            references_text: str = None) -> bool:
        """
        Crea un archivo PDF con formato APA 7ma edicion.

        Args:
            text: Texto a incluir en el PDF (cuerpo del documento)
            output_path: Ruta donde guardar el PDF
            title: Título del documento (opcional)
            font_size: Tamaño de fuente del cuerpo
            references_text: Texto de referencias bibliográficas (opcional)
        """
        try:
            from fpdf import FPDF
            import re
            import os

            # Font paths (Segoe UI - Unicode support)
            FONT_DIR = r"C:\Windows\Fonts"
            FONT_REGULAR = os.path.join(FONT_DIR, "segoeui.ttf")
            FONT_BOLD = os.path.join(FONT_DIR, "segoeuib.ttf")
            FONT_ITALIC = os.path.join(FONT_DIR, "segoeuii.ttf")
            FONT_BOLDITALIC = os.path.join(FONT_DIR, "segoeuiz.ttf")

            class APA7PDF(FPDF):
                def __init__(self):
                    super().__init__()
                    self.add_font("SegoeUI", "", FONT_REGULAR, uni=True)
                    self.add_font("SegoeUI", "B", FONT_BOLD, uni=True)
                    self.add_font("SegoeUI", "I", FONT_ITALIC, uni=True)
                    self.add_font("SegoeUI", "BI", FONT_BOLDITALIC, uni=True)

                def header(self):
                    if self.page_no() > 1:
                        self.set_font('SegoeUI', 'I', 9)
                        self.cell(0, 10, f'Página {self.page_no()}', 0, 1, 'R')
                        self.ln(5)

                def footer(self):
                    self.set_y(-15)
                    self.set_font('SegoeUI', 'I', 9)
                    self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

            pdf = APA7PDF()
            pdf.set_auto_page_break(auto=True, margin=25)
            pdf.add_page()

            # APA margins (1 inch = 25.4mm)
            margin = 25.4
            pdf.set_left_margin(margin)
            pdf.set_right_margin(margin)
            pdf.set_top_margin(margin)
            page_width = 210 - (margin * 2)

            # Compact line height ~5.5mm for 10.5pt font
            line_height = 5.5

            def clean_text(t):
                t = t.replace('\x00', '')
                t = t.replace('\ufffd', '')
                t = t.replace('\t', ' ')
                t = re.sub(r' +', ' ', t)
                return t.strip()

            def is_section_heading(t):
                """Detecta encabezados de sección (ej. Introducción, Métodos, etc.)."""
                t_lower = t.lower().strip()
                SECTION_HEADINGS = {
                    'introduction', 'introduccion', 'introducción',
                    'method', 'methods', 'metodo', 'método', 'metodos', 'métodos',
                    'results', 'resultados',
                    'discussion', 'discusion', 'discusión',
                    'conclusion', 'conclusions', 'conclusiones',
                    'conclusión', 'conclusion', 'conclusiones',
                    'abstract', 'resumen',
                    'references', 'referencias', 'bibliografía', 'bibliography',
                    'appendix', 'apendice', 'apéndice',
                    'antecedentes', 'objetivo', 'objetivos',
                    'marco teorico', 'marco teórico',
                    'metodologia', 'metodología',
                    'analisis', 'análisis',
                    'background', 'purpose', 'findings', 'implications',
                    'titulo', 'título', 'contenido', 'indice', 'índice',
                    'study design', 'diseño del estudio',
                    'search strategy and selection criteria', 'estrategia de búsqueda',
                    'study selection', 'selección de estudios',
                    'data extraction', 'extracción de datos',
                    'data analysis', 'análisis de datos',
                    'principal results', 'resultados principales',
                    'challenges and opportunities', 'desafíos y oportunidades',
                    'future directions', 'direcciones futuras',
                    'limitations', 'limitaciones',
                    'acknowledgments', 'agradecimientos',
                    "authors' contributions", 'contribuciones de los autores',
                    'conflicts of interest', 'conflictos de interés',
                    'keywords', 'palabras clave'
                }
                return t_lower in SECTION_HEADINGS

            def is_reference_line(t):
                """Detecta si una línea parece una referencia bibliográfica."""
                return bool(re.match(r'^\d*\.?\s*[A-ZÁÉÍÓÚÑ][^.]*\s*\(\d{4}\)', t)) or \
                       bool(re.match(r'^\d+\.\s*\S', t) and len(t) > 30) or \
                       bool(re.match(r'^[A-ZÁÉÍÓÚÑ][^.]*\.\s*\([12][0-9]{3}\)', t))

            # Normalize the text
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            text = text.replace('\t', ' ')
            text = re.sub(r' +', ' ', text)

            # Si se pasan referencias separadas, quitar la sección de referencias
            # del cuerpo para evitar duplicados (el texto ya las incluye al final)
            if references_text and references_text.strip():
                # Buscar encabezado de referencias dentro del texto
                ref_header_match = re.search(
                    r'(?im)^\s*(REFERENCES|REFERENCIAS|BIBLIOGRAPHY|BIBLIOGRAFÍA)\s*$',
                    text
                )
                if ref_header_match:
                    text = text[:ref_header_match.start()].rstrip()

            # Split into lines and group into paragraphs
            lines = text.split('\n')
            paragraphs = []
            current_para = []
            has_blank_lines = any(not line.strip() for line in lines)

            for line in lines:
                stripped = line.strip()
                # Empty line = paragraph break
                if not stripped:
                    if current_para:
                        paragraphs.append(' '.join(current_para))
                        current_para = []
                    continue

                prev = current_para[-1].rstrip() if current_para else ''
                ends_delim = prev.endswith(('.', '!', '?', ':', ';'))
                is_ref_line = bool(re.match(r'^\d+\.\s+\S', stripped) and len(stripped) > 30) or \
                              bool(re.match(r'^[A-ZÁÉÍÓÚÑ][^.]*[.]?\s*\([12][0-9]{3}\)', stripped))
                is_heading = is_section_heading(stripped)
                is_bullet = stripped.startswith(('\u2022', '\u2023', '\u25cf', '\u25cb', '-', '*'))
                starts_new_ref = is_ref_line and current_para

                if current_para and not has_blank_lines:
                    # Texto sin líneas vacías: el texto llega sin estructura clara.
                    # Unir la línea si el párrafo actual no termina en un delimitador
                    # y la nueva línea no parece un encabezado/metadato.
                    looks_heading = (
                        is_heading or
                        (len(stripped) < 60 and not stripped.endswith('.') and
                         not re.match(r'^[a-záéíóúüñ]', stripped) and
                         len(current_para) > 0)
                    )

                    if not ends_delim and not looks_heading and not is_ref_line and not is_bullet:
                        current_para.append(stripped)
                        continue
                    else:
                        paragraphs.append(' '.join(current_para))
                        current_para = [stripped]
                        continue
                else:
                    # Texto con líneas vacías: agrupar líneas consecutivas,
                    # pero separar encabezados y nuevas referencias numeradas
                    if starts_new_ref or is_heading:
                        paragraphs.append(' '.join(current_para))
                        current_para = [stripped]
                    else:
                        current_para.append(stripped)

            if current_para:
                paragraphs.append(' '.join(current_para))

            # Clean and filter paragraphs
            paragraphs = [clean_text(p) for p in paragraphs if p.strip()]

            # Remove consecutive duplicates
            cleaned_paragraphs = []
            for para in paragraphs:
                if not cleaned_paragraphs or para != cleaned_paragraphs[-1]:
                    cleaned_paragraphs.append(para)
            paragraphs = cleaned_paragraphs

            # Extract title if not provided: buscar el título real entre los primeros párrafos
            if not title and paragraphs:
                # Etiquetas comunes que NO son títulos (saltar)
                skip_labels = {
                    'revisión', 'revision', 'review', 'abstract', 'resumen',
                    'introducción', 'introduccion', 'introduction',
                    'métodos', 'metodos', 'methods', 'resultados', 'results',
                    'artículo', 'articulo', 'article', 'vol', 'núm', 'num'
                }
                # Buscar en los primeros 3 párrafos un candidato a título
                for first_para in paragraphs[:3]:
                    first_lower = first_para.strip().lower()
                    # Saltar líneas cortas tipo "Revisión" o etiquetas
                    words = first_para.split()
                    is_short_label = len(words) <= 3 and len(first_para) < 40
                    if is_short_label and first_lower.rstrip('.').strip() in skip_labels:
                        continue
                    # Un título: 15-250 chars, no termina en punto/interrogación
                    if 15 <= len(first_para) <= 250 and not first_para.rstrip().endswith(('.', '!', '?')):
                        title = first_para
                        paragraphs = paragraphs[paragraphs.index(first_para) + 1:]
                        break
                # Fallback: primer párrafo corto
                if not title:
                    first_para = paragraphs[0]
                    if len(first_para) < 250 and not first_para.endswith(('.', '!', '?')):
                        title = first_para
                        paragraphs = paragraphs[1:]

            # Render PDF - Title
            if title:
                title_clean = clean_text(title[:150])
                if title_clean:
                    pdf.set_font("SegoeUI", 'B', 12)
                    pdf.ln(20)
                    pdf.multi_cell(page_width, line_height, txt=title_clean, align='C')
                    pdf.ln(line_height * 2)

            # Render body content
            in_references = False

            for para in paragraphs:
                para_clean = clean_text(para)
                if not para_clean:
                    continue

                # Section heading
                if is_section_heading(para_clean):
                    in_references = para_clean.lower() in ('references', 'referencias')
                    pdf.ln(line_height * 2)
                    pdf.set_font("SegoeUI", 'B', 12)
                    heading_text = para_clean.upper()
                    pdf.multi_cell(page_width, line_height, txt=heading_text, align='C')
                    pdf.ln(line_height)
                    continue

                # Reference entry (hanging indent)
                if in_references or is_reference_line(para_clean):
                    pdf.set_font("SegoeUI", '', font_size)
                    pdf.set_x(margin + 5)
                    pdf.multi_cell(page_width - 5, line_height, txt=para_clean)
                    pdf.ln(line_height * 0.5)
                    continue

                # Normal paragraph
                pdf.set_font("SegoeUI", '', font_size)
                pdf.set_x(margin + 5)
                pdf.multi_cell(page_width - 5, line_height, txt=para_clean)
                pdf.ln(3)

            # Render references if provided separately
            if references_text and references_text.strip():
                pdf.ln(line_height * 2)
                pdf.set_font("SegoeUI", 'B', 12)
                pdf.multi_cell(page_width, line_height, txt="REFERENCIAS", align='C')
                pdf.ln(line_height)

                # Quitar encabezado "REFERENCES/REFERENCIAS" si el texto lo incluye
                ref_lines = references_text.split('\n')
                first_line_clean = clean_text(ref_lines[0]) if ref_lines else ""
                if first_line_clean and first_line_clean.lower() in (
                    'references', 'referencias', 'bibliography', 'bibliografía'
                ):
                    ref_lines = ref_lines[1:]

                for ref_line in ref_lines:
                    ref_line_clean = clean_text(ref_line)
                    if not ref_line_clean:
                        pdf.ln(line_height * 0.3)
                        continue
                    pdf.set_font("SegoeUI", '', font_size)
                    pdf.set_x(margin + 5)
                    pdf.multi_cell(page_width - 5, line_height, txt=ref_line_clean)
                    pdf.ln(line_height * 0.5)

            pdf.output(output_path)
            return True

        except Exception as e:
            print(f"Error creating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def _read_text(file_path: str) -> str:
        """Lee un archivo de texto plano."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _read_pdf(file_path: str) -> str:
        """Lee un archivo PDF y extrae su texto."""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    
    @staticmethod
    def _read_docx(file_path: str) -> Dict[str, Any]:
        """Lee un archivo DOCX y extrae su contenido preservando estructura."""
        doc = Document(file_path)
        paragraphs = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append({
                    'text': para.text,
                    'style': para.style.name if para.style else 'Normal',
                    'alignment': str(para.alignment) if para.alignment else None
                })
        
        # Tambien extraer tablas
        tables = []
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)
        
        return {'paragraphs': paragraphs, 'tables': tables}
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """
        Extrae solo el texto plano de un archivo DOCX.
        
        Args:
            file_path: Ruta al archivo DOCX
            
        Returns:
            Texto extraido del DOCX
        """
        try:
            doc = Document(file_path)
            paragraphs = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            # Tambien extraer texto de tablas
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text)
            
            return '\n\n'.join(paragraphs)
            
        except Exception as e:
            print(f"Error al extraer texto de DOCX: {e}")
            return ""
    
    @staticmethod
    def _read_pptx(file_path: str) -> Dict[str, Any]:
        """Lee un archivo PPTX y extrae su contenido."""
        prs = Presentation(file_path)
        slides = []
        
        for slide in prs.slides:
            slide_content = {
                'title': '',
                'content': []
            }
            
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    if shape.shape_type == 13:  # Placeholder
                        slide_content['title'] = shape.text
                    else:
                        slide_content['content'].append(shape.text)
            
            slides.append(slide_content)
        
        return slides
    
    @staticmethod
    def _read_excel(file_path: str) -> pd.DataFrame:
        """Lee un archivo Excel y retorna un DataFrame."""
        return pd.read_excel(file_path)
    
    @staticmethod
    def _read_json(file_path: str) -> Any:
        """Lee un archivo JSON."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def _read_html(file_path: str) -> str:
        """Lee un archivo HTML y extrae el texto."""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
            return soup.get_text(separator='\n', strip=True)

    @staticmethod
    def translate_docx_in_place(docx_path: str, output_docx_path: str, translator_agent: Any,
                               source_language: str = "es", target_language: str = "en",
                               context: str = "", glossary: Optional[list] = None,
                               translate_references: bool = False,
                               progress_callback=None) -> bool:
        """
        Realiza una traducción estructurada in-place elemento por elemento sobre un DOCX.
        Construye un mapa de claves {id_i: texto_original}, traduce con translate_structured_dict
        en lotes pequeños con control de tasa, y reemplaza cada texto traducido
        directamente en su párrafo u objeto de origen sin alterar la maquetación.
        """
        try:
            from docx import Document
            import re
            import time
            if not os.path.exists(docx_path):
                return False

            doc = Document(docx_path)

            # Recolectar todos los elementos de párrafos y celdas
            raw_elements = []
            for p in doc.paragraphs:
                t = p.text.strip()
                if t:
                    raw_elements.append(('p', p, t))

            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            t = p.text.strip()
                            if t:
                                raw_elements.append(('table', p, t))

            if not raw_elements:
                doc.save(output_docx_path)
                return True

            def is_noise(t):
                return bool(re.search(r'\(page number not for citation purposes\)|XSL-FO RenderX|RenderX|J Med Internet Res \d+.*?p\.\s*\d+|https?://www\.jmir\.org/\d+/\d+/e\d+', t, re.IGNORECASE))

            def is_skip_element(t):
                # Números puros, porcentajes, símbolos, DOIs, URLs, caracteres aislados
                if re.fullmatch(r'[\d\s.,;:/\-+%()\[\]<>=±]+', t):
                    return True
                if re.fullmatch(r'https?://\S+|doi:\S+', t, re.IGNORECASE):
                    return True
                if len(t) <= 1:
                    return True
                return False

            # Limpiar ruido y separar elementos a traducir
            to_translate = []
            in_references = False

            for typ, p_obj, orig_t in raw_elements:
                if is_noise(orig_t):
                    p_obj.text = ""
                    continue

                if re.match(r'^(REFERENCES|REFERENCIAS|BIBLIOGRAPHY|BIBLIOGRAFÍA)\s*:?$', orig_t.strip(), re.IGNORECASE):
                    in_references = True
                    to_translate.append((p_obj, orig_t))
                    continue

                if in_references and not translate_references:
                    # Si no se traducen referencias, conservar entradas bibliográficas intactas
                    if re.match(r'^\[?\d+\]?[\.\s]', orig_t.strip()) or re.search(r'https?://|doi:', orig_t):
                        continue

                if is_skip_element(orig_t):
                    continue

                to_translate.append((p_obj, orig_t))

            if not to_translate:
                doc.save(output_docx_path)
                return True

            # Crear lotes dinámicos basados en límite de caracteres (~2500 chars) o max 20 elementos
            batches = []
            cur_batch = []
            cur_chars = 0
            for item in to_translate:
                t_len = len(item[1])
                if cur_batch and (len(cur_batch) >= 20 or cur_chars + t_len > 2500):
                    batches.append(cur_batch)
                    cur_batch = []
                    cur_chars = 0
                cur_batch.append(item)
                cur_chars += t_len
            if cur_batch:
                batches.append(cur_batch)

            total_batches = len(batches)
            print(f"[Translator] Traduciendo DOCX in-place: {len(to_translate)} elementos en {total_batches} lotes")

            for b_idx, batch in enumerate(batches):
                if progress_callback:
                    progress_callback(b_idx + 1, total_batches)

                text_map = {f"elem_{idx}": item[1] for idx, item in enumerate(batch)}

                # Intentar traducir el lote con reintentos
                translated_map = {}
                for attempt in range(1, 4):
                    try:
                        translated_map = translator_agent.translate_structured_dict(
                            text_dict=text_map,
                            source_language=source_language,
                            target_language=target_language,
                            context=context,
                            glossary=glossary
                        )
                        if translated_map:
                            break
                    except Exception as b_err:
                        print(f"[Translator] Intento {attempt} fallido para lote {b_idx+1}/{total_batches}: {b_err}")
                        time.sleep(3 * attempt)

                # Reinyectar traducciones en sus objetos DOCX originales
                for idx, (p_obj, orig_text) in enumerate(batch):
                    key = f"elem_{idx}"
                    translated_val = translated_map.get(key, orig_text) if translated_map else orig_text
                    if translated_val:
                        if p_obj.runs:
                            p_obj.runs[0].text = str(translated_val)
                            for r in p_obj.runs[1:]:
                                r.text = ""
                        else:
                            p_obj.text = str(translated_val)

                # Pequeña pausa entre llamadas para proteger cuota de API
                if b_idx < total_batches - 1:
                    time.sleep(2)

            doc.save(output_docx_path)
            print(f"[Translator] DOCX traducido exitosamente guardado en: {output_docx_path}")
            return True
        except Exception as e:
            print(f"Error traduciendo DOCX in-place: {e}")
            return False

    @staticmethod
    def optimize_translated_docx(docx_path: str, output_docx_path: str) -> bool:
        """
        Post-procesa el DOCX traducido para optimizar la maquetación y corregir defectos:
        1. Preserva y posiciona correctamente todas las imágenes y figuras (elimina el
           interlineado exacto de 1pt de pdf2docx que las ocultaba y envuelve figuras anchas
           en secciones de 1 columna).
        2. Limpia marcas de agua e hipervínculos de ruido (RenderX, XSL-FO, URLs de JMIR).
        3. Corrige la altura fija de filas (hRule='exact' -> 'atLeast') para que el texto
           en español no se desborde ni se solape con párrafos posteriores.
        4. Formatea tablas científicas con bordes académicos y viñetas limpias (•).
        5. Comprime espaciados excesivos en párrafos vacíos para evitar bloques en blanco.
        """
        try:
            from docx import Document
            from docx.shared import Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsdecls, qn
            import re

            WATERMARK_PATTERN = re.compile(
                r'XSL.?FO|RenderX|\(page number not for citation\)|'
                r'J Med Internet Res \d+.*?p\.\s*\d+|https?://www\.jmir\.org',
                re.IGNORECASE
            )

            doc = Document(docx_path)

            # -------------------------------------------------------------
            # 1. TRATAMIENTO Y POSICIONAMIENTO DE IMÁGENES / FIGURAS
            # -------------------------------------------------------------
            for i, p in enumerate(doc.paragraphs):
                drawing = p._element.find('.//' + qn('w:drawing'))
                if drawing is not None:
                    # Verificar si contiene una imagen real (a:blip)
                    blip = drawing.find('.//' + qn('a:blip'))
                    if blip is not None:
                        # Eliminar interlineado fijo que fuerza a la imagen a dibujarse fuera de la página
                        pPr = p._element.get_or_add_pPr()
                        spacing = pPr.find(qn('w:spacing'))
                        if spacing is not None:
                            pPr.remove(spacing)
                        
                        p.paragraph_format.line_spacing = 1.0
                        p.paragraph_format.space_before = Pt(8)
                        p.paragraph_format.space_after = Pt(8)
                        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

                        # Si la imagen es ancha (> 3.3 pulgadas), garantizar que esté en 1 columna
                        extent = drawing.find('.//' + qn('wp:extent'))
                        if extent is not None:
                            cx = int(extent.get('cx', 0))
                            if cx > 3000000:  # ~3.3 pulgadas en EMUs
                                if i > 0:
                                    prev_p = doc.paragraphs[i - 1]
                                    prev_pPr = prev_p._element.get_or_add_pPr()
                                    sect1 = parse_xml(r'<w:sectPr %s><w:type w:val="continuous"/><w:cols w:num="1"/></w:sectPr>' % nsdecls('w'))
                                    prev_pPr.append(sect1)
                                
                                sect2 = parse_xml(r'<w:sectPr %s><w:type w:val="continuous"/><w:cols w:num="2" w:space="720"/></w:sectPr>' % nsdecls('w'))
                                pPr.append(sect2)

            # -------------------------------------------------------------
            # 2. LIMPIEZA DE MARCAS DE AGUA (HIPERVÍNCULOS Y TEXTOS ESPECÍFICOS)
            # -------------------------------------------------------------
            # Limpiar hipervínculos y runs de watermark en párrafos
            for p in doc.paragraphs:
                for hyperlink in list(p._element.findall('.//' + qn('w:hyperlink'))):
                    h_text = "".join((t.text or "") for t in hyperlink.findall('.//' + qn('w:t')))
                    if WATERMARK_PATTERN.search(h_text):
                        hp = hyperlink.getparent()
                        if hp is not None:
                            hp.remove(hyperlink)
                
                for r in p.runs:
                    if r.text and WATERMARK_PATTERN.search(r.text):
                        r.text = ""

            # Limpiar tablas completas o celdas que solo contengan watermark
            for table in list(doc.tables):
                all_text = "".join(c.text.strip() for row in table.rows for c in row.cells)
                cleaned = WATERMARK_PATTERN.sub("", all_text).strip()
                if not cleaned:
                    parent = table._element.getparent()
                    if parent is not None:
                        parent.remove(table._element)
                    continue

                for row in table.rows:
                    for cell in row.cells:
                        c_text = "".join((t.text or "") for t in cell._tc.findall('.//' + qn('w:t'))).strip()
                        if c_text and not WATERMARK_PATTERN.sub("", c_text).strip():
                            for wt in cell._tc.findall('.//' + qn('w:t')):
                                wt.text = ""
                            for hyperlink in list(cell._tc.findall('.//' + qn('w:hyperlink'))):
                                hp = hyperlink.getparent()
                                if hp is not None:
                                    hp.remove(hyperlink)

            # -------------------------------------------------------------
            # 3. CORRECCIÓN DE ALTURA DE FILAS EN TODAS LAS TABLAS
            # -------------------------------------------------------------
            for table in doc.tables:
                for row in table.rows:
                    trPr = row._tr.get_or_add_trPr()
                    trHeight = trPr.find(qn('w:trHeight'))
                    if trHeight is not None:
                        hRule = trHeight.get(qn('w:hRule'))
                        if hRule == 'exact':
                            trHeight.set(qn('w:hRule'), 'atLeast')

            # -------------------------------------------------------------
            # 4. FORMATEO, COLUMNAS Y CONTENCIÓN EN TABLAS CIENTÍFICAS
            # -------------------------------------------------------------
            # A. Reincorporar párrafos huérfanos que quedaron inmediatamente después de las tablas
            body = doc.element.body
            children = list(body)
            for i, child in enumerate(children):
                if child.tag.endswith("tbl"):
                    if i + 1 < len(children) and children[i + 1].tag.endswith("p"):
                        next_p = children[i + 1]
                        text = "".join(next_p.itertext()).strip()
                        if text and (text.startswith("optimizar") or text.startswith("recomendar") or text.startswith("vicios") or "Toma de decisiones" in text):
                            for t in doc.tables:
                                if t._element == child:
                                    target_cell = None
                                    for row in t.rows:
                                        for cell in row.cells:
                                            if "Optimización" in cell.text or "simulación" in cell.text:
                                                target_cell = cell
                                    if target_cell is None:
                                        target_cell = t.rows[-1].cells[-1]
                                    target_cell.add_paragraph(text)
                                    body.remove(next_p)
                                    break

            # B. Deduplicar notas al pie repetidas (ej. 'aDT: gemelo digital.')
            for p in doc.paragraphs:
                if "aDT: gemelo digital." in p.text:
                    p.text = re.sub(r'(aDT:\s*gemelo digital\.)+', r'\1', p.text)

            # C. Bordes y anchos de columnas en tablas científicas (>=5 filas, >=4 columnas)
            BORDER_XML = (
                '<w:tblBorders %s>'
                '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
                '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
                '<w:insideH w:val="none"/>'
                '<w:insideV w:val="none"/>'
                '<w:left w:val="none"/>'
                '<w:right w:val="none"/>'
                '</w:tblBorders>'
            ) % nsdecls('w')

            HEADER_BORDER_XML = (
                '<w:tcBorders %s><w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/></w:tcBorders>'
            ) % nsdecls('w')

            for table in doc.tables:
                if len(table.rows) >= 5 and len(table.columns) >= 4:
                    tblPr = table._tbl.tblPr
                    existing_borders = tblPr.find(qn('w:tblBorders'))
                    if existing_borders is not None:
                        tblPr.remove(existing_borders)
                    tblPr.append(parse_xml(BORDER_XML))
                    table.autofit = True

                    # Ajustar distribución de columnas (total ~9600 dxa = 6.67 pulgadas)
                    col_widths = [300, 1800, 300, 1050, 1050, 300, 2250, 300, 2250]
                    tblGrid = table._tbl.find(qn('w:tblGrid'))
                    if tblGrid is not None:
                        for c_idx, gridCol in enumerate(tblGrid.findall(qn('w:gridCol'))):
                            if c_idx < len(col_widths):
                                gridCol.set(qn('w:w'), str(col_widths[c_idx]))

                    for r_idx, row in enumerate(table.rows):
                        for c_idx, cell in enumerate(row.cells):
                            tcPr = cell._tc.get_or_add_tcPr()
                            # Eliminar bordes individuales para evitar cortes en medio de la tabla
                            tcBorders = tcPr.find(qn('w:tcBorders'))
                            if tcBorders is not None:
                                tcPr.remove(tcBorders)
                            if r_idx == 0:
                                tcPr.append(parse_xml(HEADER_BORDER_XML))

                            if c_idx < len(col_widths):
                                tcW = tcPr.find(qn('w:tcW'))
                                if tcW is not None:
                                    tcW.set(qn('w:w'), str(col_widths[c_idx]))

                            for para in cell.paragraphs:
                                para.paragraph_format.space_before = Pt(1)
                                para.paragraph_format.space_after = Pt(1)
                                para.paragraph_format.line_spacing = 1.05
                                for run in para.runs:
                                    # Limpiar glifos de viñeta rotos
                                    if run.text:
                                        run.text = re.sub(r'[\u25a1\uf0b7\u25aa\u25fb\u25fc]', '• ', run.text)
                                    if r_idx == 0:
                                        run.font.bold = True
                                        run.font.size = Pt(8.5)
                                    else:
                                        run.font.size = Pt(7.5)


            # -------------------------------------------------------------
            # 5. COMPRESIÓN DE ESPACIADO EN PÁRRAFOS VACÍOS
            # -------------------------------------------------------------
            for p in doc.paragraphs:
                # No alterar párrafos que contienen imágenes
                if p._element.find('.//' + qn('w:drawing')) is not None:
                    continue
                t = p.text.strip()
                if not t:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = Pt(1)
                else:
                    sa = p.paragraph_format.space_after
                    sb = p.paragraph_format.space_before
                    if sa is not None and sa.pt is not None and sa.pt > 6:
                        p.paragraph_format.space_after = Pt(3)
                    if sb is not None and sb.pt is not None and sb.pt > 6:
                        p.paragraph_format.space_before = Pt(2)

            doc.save(output_docx_path)
            print(f"[Optimizer] DOCX optimizado guardado en: {output_docx_path}")
            return True
        except Exception as e:
            print(f"[Optimizer] Error al optimizar DOCX: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def update_docx_with_translation(docx_path: str, output_docx_path: str, translated_text: str) -> bool:
        """Fallback de actualización basada en párrafos."""
        try:
            from docx import Document
            import re
            if not os.path.exists(docx_path):
                return False

            doc = Document(docx_path)
            trans_paras = [p.strip() for p in (translated_text or "").split('\n\n') if p.strip()]
            if not trans_paras:
                doc.save(output_docx_path)
                return True

            docx_elements = [p for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            if p.text.strip():
                                docx_elements.append(p)

            trans_idx = 0
            num_trans = len(trans_paras)

            for elem in docx_elements:
                orig_t = elem.text.strip()
                if re.search(r'\(page number not for citation purposes\)|XSL-FO RenderX|RenderX|J Med Internet Res \d+.*?p\.\s*\d+|https?://www\.jmir\.org/\d+/\d+/e\d+', orig_t, re.IGNORECASE):
                    elem.text = ""
                    continue

                if trans_idx < num_trans:
                    new_text = trans_paras[trans_idx]
                    if elem.runs:
                        elem.runs[0].text = new_text
                        for r in elem.runs[1:]:
                            r.text = ""
                    else:
                        elem.text = new_text
                    trans_idx += 1

            doc.save(output_docx_path)
            return True
        except Exception as e:
            print(f"Error actualizando DOCX: {e}")
            return False

    @staticmethod
    def write_file(file_path: str, content: Any, original_data: Dict[str, Any]) -> bool:
        """
        Escribe contenido traducido a un archivo.
        
        Args:
            file_path: Ruta donde guardar el archivo
            content: Contenido traducido
            original_data: Datos originales del archivo
            
        Returns:
            True si se escribio correctamente
        """
        ext = original_data['extension']
        
        try:
            if ext == '.txt':
                FileHandler._write_text(file_path, content)
            elif ext == '.pdf':
                docx_path = original_data.get('docx_path')
                pdf_created = False
                if docx_path and os.path.exists(docx_path):
                    out_docx = docx_path.replace('.docx', '_traducido.docx')
                    if os.path.exists(out_docx):
                        FileHandler.optimize_translated_docx(out_docx, out_docx)
                        created_pdf = FileHandler.docx_to_pdf(out_docx, os.path.dirname(file_path))
                        if created_pdf and os.path.exists(created_pdf):
                            if os.path.abspath(created_pdf) != os.path.abspath(file_path):
                                import shutil
                                shutil.move(created_pdf, file_path)
                            pdf_created = True
                    else:
                        if FileHandler.update_docx_with_translation(docx_path, out_docx, content):
                            FileHandler.optimize_translated_docx(out_docx, out_docx)
                            created_pdf = FileHandler.docx_to_pdf(out_docx, os.path.dirname(file_path))
                            if created_pdf and os.path.exists(created_pdf):
                                if os.path.abspath(created_pdf) != os.path.abspath(file_path):
                                    import shutil
                                    shutil.move(created_pdf, file_path)
                                pdf_created = True

                if not pdf_created:
                    FileHandler.create_pdf_from_text(content, file_path, title=None)
            elif ext == '.docx':
                docx_path = original_data.get('docx_path') or original_data.get('original_file_path')
                out_docx = docx_path.replace('.docx', '_traducido.docx') if docx_path else None
                if out_docx and os.path.exists(out_docx):
                    import shutil
                    shutil.copy(out_docx, file_path)
                elif docx_path and os.path.exists(docx_path):
                    FileHandler.update_docx_with_translation(docx_path, file_path, content)
                else:
                    FileHandler._write_docx(file_path, content, original_data.get('content', {}))
            elif ext == '.pptx':
                FileHandler._write_pptx(file_path, content, original_data.get('content', []))
            elif ext in ['.xlsx', '.xls']:
                FileHandler._write_excel(file_path, content, original_data.get('content'))
            elif ext == '.json':
                FileHandler._write_json(file_path, content)
            elif ext == '.html':
                FileHandler._write_html(file_path, content)
            else:
                return False
            
            return True
        except Exception as e:
            print(f"Error al escribir archivo {file_path}: {e}")
            return False
    
    @staticmethod
    def _write_text(file_path: str, content: str):
        """Escribe contenido en archivo de texto."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def _write_docx(file_path: str, content: Any, original_content: Dict[str, Any]):
        """Escribe contenido traducido en archivo DOCX."""
        doc = Document()
        
        if isinstance(content, dict) and 'paragraphs' in content:
            paragraphs = content['paragraphs']
        elif isinstance(content, str):
            paragraphs = [{'text': content, 'style': 'Normal'}]
        else:
            paragraphs = [{'text': str(content), 'style': 'Normal'}]
        
        for para_data in paragraphs:
            if isinstance(para_data, dict):
                para = doc.add_paragraph(para_data.get('text', ''))
                if para_data.get('style'):
                    try:
                        para.style = para_data['style']
                    except:
                        pass
            else:
                doc.add_paragraph(str(para_data))
        
        doc.save(file_path)
    
    @staticmethod
    def _write_pptx(file_path: str, content: Any, original_content: list):
        """Escribe contenido traducido en archivo PPTX."""
        prs = Presentation()
        
        if isinstance(content, list):
            for slide_data in content:
                slide_layout = prs.slide_layouts[1]  # Layout con titulo
                slide = prs.slides.add_slide(slide_layout)
                
                # Titulo
                if slide_data.get('title'):
                    title = slide.shapes.title
                    title.text = slide_data['title']
                
                # Contenido
                if slide_data.get('content'):
                    body = slide.placeholders[1]
                    body.text = "\n".join(slide_data['content'])
        
        prs.save(file_path)
    
    @staticmethod
    def _write_excel(file_path: str, content: Any, original_content: pd.DataFrame):
        """Escribe contenido traducido en archivo Excel."""
        if isinstance(content, pd.DataFrame):
            content.to_excel(file_path, index=False)
        else:
            original_content.to_excel(file_path, index=False)
    
    @staticmethod
    def _write_json(file_path: str, content: Any):
        """Escribe contenido en archivo JSON."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _write_html(file_path: str, content: str):
        """Escribe contenido en archivo HTML."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"<html><body><pre>{content}</pre></body></html>")
    
    @staticmethod
    def get_supported_extensions() -> list:
        """Retorna lista de extensiones soportadas."""
        return ['.txt', '.pdf', '.docx', '.pptx', '.xlsx', '.xls', '.json', '.html']
