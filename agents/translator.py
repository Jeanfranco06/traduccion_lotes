import os
import json
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class TranslatorAgent:
    """
    Agente traductor usando LangChain con Google Gemini.
    Toma texto original y genera traducción preservando formato.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash",
                 fallback_model_name: Optional[str] = "gemini-2.0-flash"):
        """
        Inicializa el agente traductor.
        
        Args:
            api_key: API key de Google Gemini (si no se provee, usa variable de entorno)
            model_name: Nombre del modelo a usar
            fallback_model_name: Modelo alternativo si el primario agota cuota/429
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere GOOGLE_API_KEY para usar el agente traductor")
        
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        
        llm_kwargs = {
            "model": model_name,
            "google_api_key": self.api_key,
            "max_tokens": 16384
        }
        if "lite" not in model_name.lower():
            llm_kwargs["temperature"] = 0.2
        self.llm = ChatGoogleGenerativeAI(**llm_kwargs)
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Eres un traductor profesional y experto en el idioma {target_language}. Traduces EXCLUSIVAMENTE del {source_language} al {target_language}.

REGLAS ABSOLUTAS:
1. TRADUCE EL TEXTO COMPLETO al {target_language}. Cada oración, cada frase, cada palabra.
2. NO dejes NADA en {source_language} ni en ningún otro idioma. NUNCA copies texto sin traducir.
3. Traduce con longitud equivalente: NO reescribas, NO resumas, NO omitas frases ni ideas.
4. La traducción debe sonar natural y fluida en {target_language}, adaptando terminología académica y metodológica de forma estándar (ejemplo: 'snowballing' -> 'búsqueda/muestreo en bola de nieve').
5. Mantén TODOS los marcadores [PARRAFO] exactamente en su posición original, en su propia línea, sin fusionar ni dividir párrafos.

GLOSARIO (usa SIEMPRE estas traducciones para la terminología, para mantener consistencia en todo el documento):
{glossary_text}

CONTEXTO DEL DOCUMENTO (ajusta el vocabulario y el registro):
{context_text}

EXCEPCIONES (mantener exactamente como están, sin traducir):
- URLs: https://...
- DOIs: doi:10.xxxx
- Identificadores de cita y Medline: [FREE Full text], [Medline: xxx], [doi: xxx]
- Números de referencia entre corchetes: [1], [1-4], [2,8,14]
- Nombres de bases de datos y pautas científicas: PubMed, CINAHL, Web of Science, Embase, PsycINFO, PRISMA-ScR
- Nombres propios, marcas y apellidos (Dassault Systèmes, Siemens, Medtronic, EndNote, Covidence)

TODO LO DEMÁS DEBE ESTAR COMPLETAMENTE EN {target_language}. Sin excepciones.

Responde SOLO con el texto traducido. Sin explicaciones ni notas."""),
            ("human", "Traduce el siguiente texto del {source_language} al {target_language}:\n\n{text}")
        ])
        
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
        # Cadena alternativa para fallback por cuota
        self.fallback_llm = None
        if fallback_model_name and fallback_model_name != model_name:
            fb_kwargs = {
                "model": fallback_model_name,
                "google_api_key": self.api_key,
                "max_tokens": 16384
            }
            if "lite" not in fallback_model_name.lower():
                fb_kwargs["temperature"] = 0.2
            self.fallback_llm = ChatGoogleGenerativeAI(**fb_kwargs)
            self.fallback_chain = self.prompt_template | self.fallback_llm | StrOutputParser()
    
    @staticmethod
    def _is_quota_exhausted(error: Exception) -> bool:
        """Detecta si el error corresponde a cuota agotada (429 / RESOURCE_EXHAUSTED)."""
        text = str(error)
        return ('429' in text) or ('RESOURCE_EXHAUSTED' in text.upper()) or ('quota' in text.lower())
    
    def _invoke_chain(self, inputs: Dict[str, Any]) -> str:
        """
        Invoca la cadena de traducción intentando el modelo primario y,
        si falla por cuota, el modelo de respaldo.
        """
        try:
            return self.chain.invoke(inputs)
        except Exception as primary_error:
            if self.fallback_llm is not None and self._is_quota_exhausted(primary_error):
                print(f"[Translator] Cuota agotada en {self.model_name}; "
                      f"reintentando con fallback {self.fallback_model_name}")
                try:
                    return self.fallback_chain.invoke(inputs)
                except Exception:
                    raise primary_error
            raise primary_error
    
    def translate_structured_dict(self, text_dict: Dict[str, str], 
                                source_language: str = "es",
                                target_language: str = "en", 
                                context: str = "",
                                glossary: Optional[list] = None) -> Dict[str, str]:
        """
        Traduce un diccionario de elementos {id: texto} preservando las claves JSON exactas.
        Esto garantiza que cada párrafo, celda de tabla y título se reincorpore exactamente
        en su contenedor original.
        """
        if not text_dict:
            return {}

        import json, time, re
        glossary_items = [f"- {g['source']} -> {g['target']}" for g in (glossary or []) if isinstance(g, dict)]
        glossary_str = "\n".join(glossary_items) if glossary_items else "Sin glosario específico."

        prompt_str = (
            f"Eres un traductor científico experto. Traduce todos los valores de este diccionario JSON del {source_language} al {target_language}.\n\n"
            f"REGLAS CRÍTICAS:\n"
            f"1. Conserva EXACTAMENTE las mismas claves JSON.\n"
            f"2. Traduce ÚNICAMENTE los valores al {target_language} con precisión académica y tono formal.\n"
            f"3. Glosario de términos:\n{glossary_str}\n"
            f"4. Si un valor es 'snowballing', tradúcelo como 'búsqueda en bola de nieve' o 'muestreo en bola de nieve'.\n"
            f"5. Conserva intactos números de referencia [1], URLs (https://...), DOIs (doi:10.xxx) y marcas registradas (Siemens, Medtronic, etc.).\n"
            f"6. Responde ÚNICAMENTE con un JSON válido parseable. Sin explicaciones ni bloques markdown ```json.\n\n"
            f"JSON A TRADUCIR:\n"
            + json.dumps(text_dict, ensure_ascii=False, indent=2)
        )

        from langchain_core.prompts import ChatPromptTemplate
        dict_prompt = ChatPromptTemplate.from_messages([("human", "{prompt}")])
        chain = dict_prompt | self.llm | StrOutputParser()

        response = None
        for attempt in range(1, 4):
            try:
                response = chain.invoke({"prompt": prompt_str})
                break
            except Exception as primary_err:
                print(f"[Translator] Intento {attempt} con {self.model_name} falló: {primary_err}")
                if self.fallback_llm is not None and self._is_quota_exhausted(primary_err):
                    print(f"[Translator] Probando modelo de respaldo {self.fallback_model_name}...")
                    try:
                        fallback_chain = dict_prompt | self.fallback_llm | StrOutputParser()
                        response = fallback_chain.invoke({"prompt": prompt_str})
                        break
                    except Exception as fb_err:
                        print(f"[Translator] Intento con respaldo {self.fallback_model_name} falló: {fb_err}")
                
                if attempt < 3:
                    sleep_s = 10 * attempt
                    print(f"[Translator] Esperando {sleep_s}s antes de reintentar...")
                    time.sleep(sleep_s)
                else:
                    return text_dict

        # Parsear JSON de respuesta
        cleaned_resp = str(response or "").strip()
        cleaned_resp = re.sub(r'^```json\s*', '', cleaned_resp)
        cleaned_resp = re.sub(r'^```\s*', '', cleaned_resp)
        cleaned_resp = re.sub(r'\s*```$', '', cleaned_resp)

        translated_map = None
        try:
            translated_map = json.loads(cleaned_resp)
        except Exception:
            json_match = re.search(r'\{.*\}', cleaned_resp, re.DOTALL)
            if json_match:
                try:
                    translated_map = json.loads(json_match.group(0))
                except Exception:
                    pass

        if isinstance(translated_map, dict):
            return {str(k): str(v) for k, v in translated_map.items()}
        return text_dict

    def translate_text(self, text: str, source_language: str = "es", 
                      target_language: str = "en", context: str = "",
                      glossary: Optional[list] = None) -> str:
        """
        Traduce un texto del idioma origen al destino.
        
        Args:
            text: Texto a traducir
            source_language: Código del idioma origen (es, en, fr, etc.)
            target_language: Código del idioma destino (es, en, fr, etc.)
            context: Contexto del documento (dominio, tono, instrucciones)
            glossary: Lista de términos clave para terminología consistente
            
        Returns:
            Texto traducido
        """
        # Mapear codigos a nombres completos para mejor comprension del LLM
        lang_names = {
            'es': 'español/Spanish',
            'en': 'English/inglés',
            'fr': 'francés/French',
            'de': 'alemán/German',
            'it': 'italiano/Italian',
            'pt': 'portugués/Portuguese',
            'zh': 'chino/Chinese',
            'ja': 'japonés/Japanese'
        }
        
        source_name = lang_names.get(source_language, source_language)
        target_name = lang_names.get(target_language, target_language)
        
        # Formatear glosario como lista de equivalencias
        glossary_text = "No hay glosario definido. Usa la terminología estándar del campo."
        if glossary:
            items = []
            for term in glossary:
                if isinstance(term, dict):
                    src = term.get('term') or term.get('source') or term.get('original')
                    tgt = term.get('translation') or term.get('target')
                    if src and tgt:
                        items.append(f"- {src} = {tgt}")
                elif isinstance(term, str) and '=' in term:
                    items.append(f"- {term.strip()}")
            if items:
                glossary_text = "Usa estas equivalencias EXACTAS:\n" + "\n".join(items)
        
        context_text = "No hay contexto adicional. Traduce de manera profesional."
        if context and context.strip():
            context_text = context.strip()
        
        try:
            # Reemplazar saltos de parrafo con el marcador [PARRAFO]
            # Esto evita que el LLM pierda la estructura de párrafos
            marked_text = text.replace('\n\n', '\n[PARRAFO]\n')
            # Normalizar multiples saltos consecutivos
            import re as _re
            marked_text = _re.sub(r'\[PARRAFO\](?:\s*\[PARRAFO\])+', '[PARRAFO]', marked_text)
            
            result = self._invoke_chain({
                "text": marked_text,
                "source_language": source_name,
                "target_language": target_name,
                "glossary_text": glossary_text,
                "context_text": context_text
            })
            
            # Restaurar los saltos de parrafo
            if result:
                # El LLM puede haber variado el formato del marcador
                result = _re.sub(r'\s*\[PARRAFO\]\s*', '\n\n', result)
                result = _re.sub(r'\s*¶\s*', '\n\n', result)
                # Normalizar multiples saltos
                result = _re.sub(r'\n{3,}', '\n\n', result)
                
            return result
        except Exception as e:
            raise Exception(f"Error en traducción: {str(e)}")
    
    def translate_with_format(self, content: Any, source_language: str = "es",
                            target_language: str = "en") -> Any:
        """
        Traduce contenido preservando la estructura del archivo.
        
        Args:
            content: Contenido del archivo (puede ser string, dict, etc.)
            source_language: Código del idioma origen
            target_language: Código del idioma destino
            
        Returns:
            Contenido traducido manteniendo estructura
        """
        if isinstance(content, str):
            return self.translate_text(content, source_language, target_language)
        
        elif isinstance(content, dict):
            # Para archivos DOCX con párrafos y tablas
            if 'paragraphs' in content:
                translated_paragraphs = []
                for para in content['paragraphs']:
                    translated_text = self.translate_text(
                        para['text'], source_language, target_language
                    )
                    translated_paragraphs.append({
                        'text': translated_text,
                        'style': para.get('style', 'Normal'),
                        'alignment': para.get('alignment')
                    })
                
                translated_tables = []
                for table in content.get('tables', []):
                    translated_table = []
                    for row in table:
                        translated_row = [self.translate_text(cell, source_language, target_language) 
                                        for cell in row]
                        translated_table.append(translated_row)
                    translated_tables.append(translated_table)
                
                return {'paragraphs': translated_paragraphs, 'tables': translated_tables}
            
            # Para archivos PPTX
            elif isinstance(content, list) and len(content) > 0 and 'title' in content[0]:
                translated_slides = []
                for slide in content:
                    translated_slide = {
                        'title': self.translate_text(slide.get('title', ''), 
                                                   source_language, target_language),
                        'content': [self.translate_text(item, source_language, target_language)
                                   for item in slide.get('content', [])]
                    }
                    translated_slides.append(translated_slide)
                return translated_slides
            
            # Para archivos JSON
            else:
                return self._translate_dict(content, source_language, target_language)
        
        elif isinstance(content, list):
            # Para listas (como slides de PPTX)
            return [self.translate_with_format(item, source_language, target_language) 
                   for item in content]
        
        else:
            return str(content)
    
    def _translate_dict(self, data: Any, source_language: str, 
                       target_language: str) -> Any:
        """Traduce recursivamente un diccionario."""
        if isinstance(data, dict):
            return {k: self._translate_dict(v, source_language, target_language) 
                   for k, v in data.items()}
        elif isinstance(data, list):
            return [self._translate_dict(item, source_language, target_language) 
                   for item in data]
        elif isinstance(data, str):
            return self.translate_text(data, source_language, target_language)
        else:
            return data
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Retorna diccionario de idiomas soportados."""
        return {
            'es': 'Español',
            'en': 'Inglés',
            'fr': 'Francés',
            'de': 'Alemán',
            'it': 'Italiano',
            'pt': 'Portugués',
            'zh': 'Chino',
            'ja': 'Japonés',
            'ko': 'Coreano',
            'ar': 'Árabe'
        }

    def build_glossary(self, analysis: Dict[str, Any], source_language: str,
                       target_language: str) -> Optional[list]:
        """
        Construye un glosario de términos a partir del análisis del documento.

        Extrae los key_terms del análisis. Si vienen con traducción, los usa;
        si no, los deja como términos a fijar con la pauta "mantener consistencia".

        Args:
            analysis: Resultado del análisis del extractor
            source_language: Código del idioma origen
            target_language: Código del idioma destino

        Returns:
            Lista de términos para el glosario, o None
        """
        if not analysis:
            return None
        key_terms = analysis.get('key_terms') or []
        if not key_terms:
            return None

        glossary = []
        for term in key_terms:
            if isinstance(term, dict):
                # Si ya trae traducción, usarla tal cual
                if term.get('translation') or term.get('target'):
                    glossary.append({
                        'term': term.get('term') or term.get('source') or term.get('original'),
                        'translation': term.get('translation') or term.get('target')
                    })
                else:
                    src = term.get('term') or term.get('source') or term.get('original')
                    if src:
                        glossary.append({'term': src, 'translation': None})
            elif isinstance(term, str) and term.strip():
                glossary.append({'term': term.strip(), 'translation': None})

        return glossary if glossary else None

    def estimate_source_chars(self, text: str) -> int:
        """
        Estima el número de caracteres significativos del texto origen
        (contenido original sin marcadores ni ruido).
        """
        import re as _re
        # Quitar marcadores y saltos
        t = _re.sub(r'\[PARRAFO\]', ' ', text)
        t = _re.sub(r'\s+', ' ', t)
        return len(t.strip())

    @staticmethod
    def looks_untranslated(text: str, source_language: str,
                           target_language: str) -> bool:
        """
        Detecta si un texto probablemente NO fue traducido o conserva segmentos
        del idioma origen. Usa heurísticas léxicas ligeras según los pares de
        idioma más comunes, sin depender de una API.

        Args:
            text: Texto a evaluar (debería estar en target_language)
            source_language: Código del idioma origen
            target_language: Código del idioma destino

        Returns:
            True si hay indicios de que el texto no está completamente
            en el idioma destino.
        """
        if not text or not text.strip():
            return True

        sample = text.strip()[:4000]
        words = [w for w in sample.split() if w.strip()]

        # Definir conjuntos de palabras funcionales muy frecuentes por idioma
        # (palabras cortas y comunes que casi siempre aparecerían si el texto
        # quedara sin traducir en ese idioma).
        FUNCTION_WORDS = {
            'es': {'el', 'la', 'los', 'las', 'de', 'del', 'en', 'que', 'para', 'por',
                   'con', 'una', 'un', 'como', 'su', 'sus', 'se', 'pero', 'más', 'mas',
                   'este', 'esta', 'es', 'son', 'entre', 'también', 'tambien', 'sobre'},
            'en': {'the', 'and', 'of', 'to', 'in', 'is', 'are', 'with', 'that', 'for',
                   'on', 'as', 'by', 'this', 'these', 'from', 'or', 'an', 'at', 'be',
                   'it', 'not', 'but', 'their', 'which', 'was', 'were', 'has', 'have'},
            'fr': {'le', 'la', 'les', 'de', 'du', 'des', 'en', 'et', 'que', 'pour',
                   'avec', 'une', 'un', 'comme', 'son', 'ses', 'mais', 'plus', 'cette',
                   'ce', 'ces', 'est', 'sont', 'entre', 'aussi', 'sur'},
            'de': {'der', 'die', 'das', 'den', 'dem', 'des', 'und', 'von', 'mit', 'für',
                   'für', 'ist', 'sind', 'nicht', 'wie', 'auch', 'auf', 'über', 'über',
                   'nach', 'bei', 'es', 'ein', 'eine'},
            'pt': {'o', 'a', 'os', 'as', 'de', 'do', 'da', 'em', 'que', 'para', 'por',
                   'com', 'uma', 'um', 'como', 'seu', 'sua', 'mas', 'mais', 'este',
                   'esta', 'é', 'e', 'são', 'sobre', 'entre'},
            'it': {'il', 'lo', 'la', 'gli', 'le', 'di', 'del', 'della', 'in', 'che',
                   'per', 'con', 'una', 'un', 'come', 'suo', 'sua', 'ma', 'più', 'piu',
                   'questo', 'questa', 'è', 'sono', 'tra', 'fra', 'anche'},
            'zh': None,
            'ja': None,
        }

        src_words = FUNCTION_WORDS.get(source_language)
        tgt_words = FUNCTION_WORDS.get(target_language)

        # Para idiomas sin heurística léxica (zh, ja), no podemos detectar bien:
        # asumimos que NUNCA "parece sin traducir" por heurística (se evita
        # falsos positivos). La validación real queda en el revisor LLM.
        if src_words is None or len(words) == 0:
            return False

        # Contar cuántas palabras del idioma origen (funcionales) aparecen en text.
        # Pegar palabras: contar apariciones de cada palabra funcional del origen.
        def _count_function_words(word_set):
            hits = 0
            for w in word_set:
                count = 0
                idx = 0
                while True:
                    idx = lower_sample.find(' ' + w + ' ', idx)
                    if idx == -1:
                        break
                    idx += 1
                    count += 1
                if lower_sample.startswith(w + ' '):
                    count += 1
                if lower_sample.endswith(' ' + w):
                    count += 1
                hits += count
            return hits

        lower_sample = sample.lower()
        orig_hits = _count_function_words(src_words)
        tgt_hits = _count_function_words(tgt_words) if tgt_words else 0

        # El texto está traducido si DOMINAN las palabras funcionales del destino.
        # Cuando destino no tiene heurística (zh/ja), exigir umbral alto de origen.
        if tgt_words is None:
            if orig_hits >= 5:
                return True
            return False

        # Falso positivo si solo hay unas pocas palabras de origen entre un
        # texto claramente dominado por el idioma destino (p. ej. "of", "for",
        # "and" residuales en nombres propios o citas).
        if orig_hits < 5:
            return False

        # Señal clara de texto sin traducir: las palabras del origen superan
        # a las del destino → el texto quedó mayoritariamente en el origen.
        return orig_hits > tgt_hits

