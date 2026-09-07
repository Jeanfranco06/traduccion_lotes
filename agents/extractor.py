import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json


class ExtractorAgent:
    """
    Agente extractor/normalizador de pre-procesamiento.
    Analiza el documento, remueve caracteres no deseados, detecta idioma y dominio.
    Prepara instrucciones de contexto para el agente traductor.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.5-flash",
                 fallback_model_name: Optional[str] = None):
        """
        Inicializa el agente extractor.
        
        Args:
            api_key: API key de Google Gemini
            model_name: Nombre del modelo a usar
            fallback_model_name: Modelo alternativo si el primario agota cuota
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere GOOGLE_API_KEY para usar el agente extractor")
        
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        llm_kwargs = {"model": model_name, "google_api_key": self.api_key, "max_tokens": 2048}
        if "lite" not in model_name.lower():
            llm_kwargs["temperature"] = 0.2
        self.llm = ChatGoogleGenerativeAI(**llm_kwargs)
        self.fallback_llm = None
        if fallback_model_name and fallback_model_name != model_name:
            fb_kwargs = {"model": fallback_model_name, "google_api_key": self.api_key, "max_tokens": 2048}
            if "lite" not in fallback_model_name.lower():
                fb_kwargs["temperature"] = 0.2
            self.fallback_llm = ChatGoogleGenerativeAI(**fb_kwargs)
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto analista de documentos con especialización en pre-procesamiento de textos para traducción.

Tu tarea es analizar el texto extraído y proporcionar:
1. Idioma detectado del texto
2. Dominio/categoría del texto
3. Limpieza del texto (normalización)
4. Instrucciones de contexto para la traducción

Formato de respuesta JSON:
{
    "detected_language": "código del idioma (es, en, fr, etc.)",
    "domain": "técnico|médico|legal|literario|general|científico|negocios|tecnología",
    "tone": "formal|informal|académico|profesional|coloquial",
    "cleaned_text": "texto limpiado y normalizado",
    "context_instructions": "instrucciones específicas para el traductor basadas en el dominio y tono detectados",
    "key_terms": ["término1", "término2"],
    "warnings": ["advertencia1 si aplica"]
}

Criterios de análisis:
- Detecta el idioma principal con precisión
- Identifica el dominio por vocabulario especializado
- Limpia caracteres especiales, espacios múltiples, saltos de línea innecesarios
- Identifica términos clave que no deben traducirse o que requieren atención especial
- Genera instrucciones contextualizadas para el traductor"""),
            ("human", """Texto extraído del archivo:
{text}

Por favor, analiza y normaliza este texto para prepararlo para la traducción.""")
        ])
        
        self.chain = self.analysis_prompt | self.llm | StrOutputParser()
        self.fallback_chain = None
        if self.fallback_llm is not None:
            self.fallback_chain = self.analysis_prompt | self.fallback_llm | StrOutputParser()
    
    def _invoke_chain(self, inputs: Dict[str, Any]) -> str:
        """Invoca con fallback por cuota agotada."""
        try:
            return self.chain.invoke(inputs)
        except Exception as primary_error:
            text = str(primary_error)
            if self.fallback_chain is not None and ('429' in text or 'RESOURCE_EXHAUSTED' in text.upper()):
                print(f"[Extractor] Cuota agotada en {self.model_name}; usando fallback {self.fallback_model_name}")
                try:
                    return self.fallback_chain.invoke(inputs)
                except Exception:
                    raise primary_error
            raise primary_error

    def analyze_and_normalize(self, text: str) -> Dict[str, Any]:
        """
        Analiza y normaliza el texto extraido.
        
        Args:
            text: Texto extraido del archivo
            
        Returns:
            Diccionario con analisis y texto normalizado
        """
        try:
            # Limpiar texto primero
            cleaned_text = self.clean_extracted_text(text)
            
            # No limitar el texto - el traductor ya hace chunking
            
            response = self._invoke_chain({"text": cleaned_text})
            
            # Intentar parsear la respuesta como JSON
            try:
                analysis = json.loads(response)
                # Asegurar que cleaned_text este presente
                if 'cleaned_text' not in analysis:
                    analysis['cleaned_text'] = cleaned_text
                return analysis
            except json.JSONDecodeError:
                # Si no es JSON valido, crear estructura basica
                return {
                    "detected_language": "auto",
                    "domain": "general",
                    "tone": "formal",
                    "cleaned_text": cleaned_text,
                    "context_instructions": "Traduce de manera precisa y natural",
                    "key_terms": [],
                    "warnings": [],
                    "raw_response": response
                }
                
        except Exception as e:
            return {
                "detected_language": "auto",
                "domain": "general",
                "tone": "formal",
                "cleaned_text": self.clean_extracted_text(text),
                "context_instructions": "Traduce de manera precisa y natural",
                "key_terms": [],
                "warnings": [f"Error en analisis: {str(e)}"],
                "error": str(e)
            }
    
    def clean_extracted_text(self, text: str) -> str:
        """
        Limpia el texto extraido de caracteres no deseados.
        
        Args:
            text: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        import re
        
        if not text:
            return ""
        
        # Eliminar patrones /gidXXXXX
        text = re.sub(r'/gid\d+', '', text)
        
        # Eliminar marcadores de pagina (Página X, Page X) y notas de citación de maquetación PDF
        text = re.sub(r'\(page number not for citation purposes\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'XSL\s*•\s*FO\s*RenderX', '', text, flags=re.IGNORECASE)
        text = re.sub(r'RenderX', '', text, flags=re.IGNORECASE)
        text = re.sub(r'JOURNAL OF MEDICAL INTERNET RESEARCH\s+Ringeval et al', '', text, flags=re.IGNORECASE)
        text = re.sub(r'https?://www\.jmir\.org/\d+/\d+/e\d+\s+J Med Internet Res\s+\d+.*?p\.\s*\d+', '', text, flags=re.IGNORECASE)
        
        # Eliminar números de página aislados en líneas propias (ej. líneas con solo un número)
        text = re.sub(r'\n\s*\d{1,4}\s*\n', '\n', text)
        
        # Eliminar parentesis vacios o con espacios
        text = re.sub(r'\(\s*\)', '', text)
        text = re.sub(r'\[\s*\]', '', text)
        
        # Eliminar guiones de cambio de linea (cuando una palabra se corta con -)
        # Solo si el guion está al final de línea y la siguiente línea continúa la palabra
        text = re.sub(r'-\s*\n\s*([a-záéíóúñüàèìòù])', r'\1', text)
        
        # Unir líneas que continúan el párrafo (no terminan en punto, !, ?)
        lines = text.split('\n')
        merged_lines = []
        buffer = ""
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if buffer:
                    merged_lines.append(buffer)
                    buffer = ""
                merged_lines.append('')
                continue
            
            if buffer:
                # Si la línea siguiente es otra frase y la actual no termina en punto final,
                # unirlas (es continuación del mismo párrafo)
                if stripped[0].islower() and not buffer.rstrip().endswith(('.', '!', '?', ':', ';')):
                    buffer = buffer.rstrip() + ' ' + stripped
                else:
                    merged_lines.append(buffer)
                    buffer = stripped
            else:
                buffer = stripped
        
        if buffer:
            merged_lines.append(buffer)
        
        text = '\n'.join(merged_lines)
        # Preservar saltos de párrafo (\n\n), pero colapsar excesivos
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Eliminar caracteres no imprimibles
        text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
        
        return text.strip()
    
    def extract_text_from_content(self, content: Any) -> str:
        """
        Extrae texto plano de diferentes estructuras de contenido.
        
        Args:
            content: Contenido del archivo (puede ser string, dict, etc.)
            
        Returns:
            Texto plano extraído
        """
        if isinstance(content, str):
            return content
        
        elif isinstance(content, dict):
            # Para archivos DOCX con párrafos
            if 'paragraphs' in content:
                paragraphs = [p['text'] for p in content['paragraphs'] if p.get('text')]
                return "\n\n".join(paragraphs)
            
            # Para archivos con tablas
            elif 'tables' in content:
                text_parts = []
                for table in content.get('tables', []):
                    for row in table:
                        text_parts.append(" | ".join(row))
                return "\n".join(text_parts)
        
        elif isinstance(content, list):
            # Para archivos PPTX con slides
            if len(content) > 0 and isinstance(content[0], dict) and 'title' in content[0]:
                text_parts = []
                for slide in content:
                    if slide.get('title'):
                        text_parts.append(slide['title'])
                    text_parts.extend(slide.get('content', []))
                return "\n\n".join(text_parts)
            
            # Para listas simples
            else:
                return "\n".join([str(item) for item in content])
        
        return str(content)
    
    def prepare_translation_context(self, analysis: Dict[str, Any], 
                                   source_lang: str, target_lang: str) -> str:
        """
        Prepara el contexto de traducción basado en el análisis.
        
        Args:
            analysis: Resultado del análisis
            source_lang: Idioma origen
            target_lang: Idioma destino
            
        Returns:
            Contexto formateado para el traductor
        """
        domain = analysis.get('domain', 'general')
        tone = analysis.get('tone', 'formal')
        key_terms = analysis.get('key_terms', [])
        
        context = f"""
Contexto de traducción:
- Dominio: {domain}
- Tono: {tone}
- Idioma origen: {source_lang}
- Idioma destino: {target_lang}
"""
        
        if key_terms:
            context += f"\nTérminos clave a considerar: {', '.join(key_terms)}"
        
        if analysis.get('context_instructions'):
            context += f"\nInstrucciones especiales: {analysis['context_instructions']}"
        
        return context
    
    def get_supported_domains(self) -> Dict[str, str]:
        """Retorna diccionario de dominios soportados."""
        return {
            'general': 'General',
            'técnico': 'Técnico',
            'médico': 'Médico',
            'legal': 'Legal',
            'literario': 'Literario',
            'científico': 'Científico',
            'negocios': 'Negocios',
            'tecnología': 'Tecnología'
        }
