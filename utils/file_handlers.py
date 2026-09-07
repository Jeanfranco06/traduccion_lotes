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
        Post-procesa el DOCX traducido para mejorar el layout:
        1. Elimina tablas donde TODO el texto es watermark/vacío.
        2. Limpia celdas que solo contienen watermark (texto e imágenes).
        3. Limpia párrafos standalone de watermark en el cuerpo.
        4. Convierte sectPr intermedios a 'continuous' para eliminar saltos forzados.
        5. Comprime espaciado de párrafos vacíos/excesivo (cuerpo y celdas).
        6. Aplica bordes profesionales a tablas científicas (>=5 filas y >=4 cols).
        """
        try:
            from docx import Document
            from docx.shared import Pt
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsdecls, qn
            from lxml import etree
            import re

            WATERMARK_PATTERN = re.compile(
                r'XSL.?FO|RenderX|\(page number not for citation\)|'
                r'J Med Internet Res \d+.*?p\.\s*\d+|https?://www\.jmir\.org|'
                r'JOURNAL OF MEDICAL INTERNET RESEARCH',
                re.IGNORECASE
            )

            # Patrón para encabezados de journal que aparecen repetidos como separadores de sección
            JOURNAL_HEADER_PATTERN = re.compile(
                r'^(JOURNAL OF MEDICAL INTERNET RESEARCH|Ringeval\s+(?:et al|y col))',
                re.IGNORECASE
            )

            def _compress_para(p):
                """Comprime espaciado de un párrafo vacío o con exceso de espacio."""
                t = p.text.strip()
                if not t:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = Pt(1)
                else:
                    sa = p.paragraph_format.space_after
                    sb = p.paragraph_format.space_before
                    if sa is not None and sa.pt is not None and sa.pt > 8:
                        p.paragraph_format.space_after = Pt(3)
                    if sb is not None and sb.pt is not None and sb.pt > 8:
                        p.paragraph_format.space_before = Pt(2)

            def _is_drawing_watermark(p_elem):
                """Párrafo con w:drawing pero sin texto — logo de imagen RenderX."""
                if p_elem.find('.//' + qn('w:drawing')) is None:
                    return False
                text_content = "".join(
                    (r.text or "") for r in p_elem.findall('.//' + qn('w:t'))
                ).strip()
                return not text_content

            def _clear_watermark_para(p):
                """Vacía texto, hyperlinks y drawings de un párrafo watermark."""
                # Vaciar todos los w:t del párrafo (incluyendo dentro de w:hyperlink)
                for wt in p._element.findall('.//' + qn('w:t')):
                    wt.text = ""
                # Remover drawings
                for drawing in p._element.findall('.//' + qn('w:drawing')):
                    dp = drawing.getparent()
                    if dp is not None:
                        dp.remove(drawing)
                # Remover hyperlinks completos
                for hyperlink in p._element.findall('.//' + qn('w:hyperlink')):
                    hp = hyperlink.getparent()
                    if hp is not None:
                        hp.remove(hyperlink)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)

            def _get_para_full_text(p_elem):
                """Extrae todo el texto de un párrafo incluyendo hyperlinks."""
                return "".join(
                    (t.text or "") for t in p_elem.findall('.//' + qn('w:t'))
                ).strip()

            def _is_watermark_cell(cell):
                """Celda cuyo único texto es watermark (ningún otro contenido)."""
                # Usar extracción de texto completa incluyendo hyperlinks
                text = "".join(
                    (t.text or "") for t in cell._tc.findall('.//' + qn('w:t'))
                ).strip()
                if not text:
                    return True
                non_wm = WATERMARK_PATTERN.sub("", text).strip()
                return not non_wm

            doc = Document(docx_path)

            # 0. Eliminar w:drawing que contienen texto watermark en DrawingML (a:t tags)
            #    Esto cubre el logo SVG/EMF de RenderX embebido en drawings
            A_T = '{http://schemas.openxmlformats.org/drawingml/2006/main}t'
            drawings_to_remove = []
            for drawing in doc.element.body.findall('.//' + qn('w:drawing')):
                drawing_texts = "".join(
                    (t.text or "") for t in drawing.findall('.//' + A_T)
                ).strip()
                if drawing_texts and WATERMARK_PATTERN.search(drawing_texts):
                    drawings_to_remove.append(drawing)
            for drawing in drawings_to_remove:
                parent = drawing.getparent()
                if parent is not None:
                    parent.remove(drawing)
            print(f"[Optimizer] Removed {len(drawings_to_remove)} watermark drawings")

            # 1. Eliminar tablas donde TODO el contenido es watermark / vacío

            tables_to_delete = []
            for table in doc.tables:
                all_cells_text = "".join(c.text.strip() for row in table.rows for c in row.cells)
                cleaned = WATERMARK_PATTERN.sub("", all_cells_text).strip()
                if not cleaned:
                    tables_to_delete.append(table)
            for t in tables_to_delete:
                parent = t._element.getparent()
                if parent is not None:
                    parent.remove(t._element)

            # 2. Limpiar celdas individuales que solo contienen watermark
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if _is_watermark_cell(cell):
                            for p in cell.paragraphs:
                                _clear_watermark_para(p)

            # 3. Limpiar párrafos de watermark en el cuerpo principal (incluye hyperlinks)
            for p in doc.paragraphs:
                full_text = _get_para_full_text(p._element)
                if WATERMARK_PATTERN.search(full_text) or _is_drawing_watermark(p._element):
                    _clear_watermark_para(p)


            # 4. Convertir sectPr intermedios (dentro de pPr) a tipo 'continuous'
            #    para eliminar saltos de página forzados entre secciones de pdf2docx
            body = doc.element.body
            for pPr in body.findall('.//' + qn('w:pPr')):
                sectPr = pPr.find(qn('w:sectPr'))
                if sectPr is not None:
                    # Eliminar el type existente si lo hay
                    existing_type = sectPr.find(qn('w:type'))
                    if existing_type is not None:
                        sectPr.remove(existing_type)
                    # Añadir type=continuous
                    type_elem = parse_xml(
                        '<w:type %s w:val="continuous"/>' % nsdecls('w')
                    )
                    sectPr.insert(0, type_elem)

            # 5. Comprimir espaciado de párrafos vacíos/excesivo (cuerpo + todas las celdas)
            all_paras = list(doc.paragraphs)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        all_paras.extend(cell.paragraphs)
            for p in all_paras:
                _compress_para(p)

            # 6. Bordes profesionales en tablas científicas (>=5 filas, >=4 columnas)
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

            for table in doc.tables:
                if len(table.rows) >= 5 and len(table.columns) >= 4:
                    tblPr = table._tbl.tblPr
                    existing_borders = tblPr.find(qn('w:tblBorders'))
                    if existing_borders is not None:
                        tblPr.remove(existing_borders)
                    tblPr.append(parse_xml(BORDER_XML))
                    table.autofit = False

                    for r_idx, row in enumerate(table.rows):
                        for cell in row.cells:
                            for para in cell.paragraphs:
                                para.paragraph_format.space_before = Pt(1)
                                para.paragraph_format.space_after = Pt(1)
                                for run in para.runs:
                                    if r_idx == 0:
                                        run.font.bold = True
                                        run.font.size = Pt(8.5)
                                    else:
                                        run.font.size = Pt(7.8)

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
