import google.generativeai as genai
import os
import re
import logging
import time
from dotenv import load_dotenv

# Loglama ayarı
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API anahtarını kontrol et
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Gemini API yapılandırması
try:
    genai.configure(api_key=api_key)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")
    raise

# Gemini modeli için daha güvenilir yapılandırma
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

# Model oluştur
try:
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        safety_settings=safety_settings
    )
    logger.info("Gemini model initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Gemini model: {e}")
    raise

def detect_repetition(paragraphs):
    """
    Hikaye içindeki tekrar eden bölümleri tespit eder.
    
    Args:
        paragraphs (list): Hikaye paragrafları listesi
    
    Returns:
        list: Tekrar içermeyen paragraf listesi
    """
    if len(paragraphs) <= 1:
        return paragraphs
    
    # Ortak kelimeler listesi - Türkçe bağlaçlar ve yaygın kelimeler
    common_words = {'ve', 'ile', 'bir', 'bu', 'da', 'de', 'için', 'ama', 'fakat', 
                   'çünkü', 'eğer', 'gibi', 'kadar', 'sonra', 'önce', 'ki', 'diye'}
    
    cleaned_paragraphs = []
    story_segments = []
    
    for paragraph in paragraphs:
        # Paragrafı kelimelerine ayır
        words = paragraph.lower().split()
        # Ortak kelimeleri çıkar
        significant_words = [w for w in words if w not in common_words and len(w) > 2]
        # Anlamlı kelimeleri birleştir
        if significant_words:
            story_segments.append((paragraph, ' '.join(significant_words)))
    
    # Hikayeyi segmentlere ayır
    seen_segments = set()
    for paragraph, segment in story_segments:
        # Eğer bu segment çok benzer bir segmente sahipse, atla
        if any(similarity(segment, seen) > 0.7 for seen in seen_segments):
            logger.info(f"Detected repeated paragraph: {paragraph[:30]}...")
            continue
        
        cleaned_paragraphs.append(paragraph)
        seen_segments.add(segment)
    
    return cleaned_paragraphs

def similarity(text1, text2):
    """İki metin arasındaki benzerliği ölçer (basit yaklaşım)"""
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0.0
    
    common_words = words1.intersection(words2)
    return len(common_words) / max(len(words1), len(words2))

def detect_story_restart(text):
    """
    Hikayenin yeniden başlamasını tespit eder ve düzeltir
    
    Args:
        text (str): Hikaye metni
        
    Returns:
        str: Düzeltilmiş hikaye metni
    """
    # Hikaye başlangıcı için yaygın kalıplar
    start_patterns = [
        r'bir zamanlar',
        r'bir varmış bir yokmuş',
        r'bir gün',
        r'uzak bir ülkede',
        r'merhaba',
        r'başlık:',
        r'hikaye:',
        r'[\*\-\_]{3,}'  # Bölüm ayırıcılar (***) gibi
    ]
    
    pattern = '|'.join(start_patterns)
    matches = list(re.finditer(pattern, text.lower()))
    
    # İlk başlangıç noktasını atla, sonrakileri kontrol et
    if len(matches) > 1:
        # İlk eşleşmeden sonra bir yeniden başlangıç varsa
        first_match = matches[0]
        for match in matches[1:]:
            # Eğer yeni bir başlangıç, metnin ortasındaysa
            if match.start() > len(text) * 0.2:
                logger.warning(f"Detected story restart at position {match.start()}")
                return text[:match.start()]
    
    return text

def clean_story_text(text):
    """
    Hikaye metnini temizleyerek tekrar eden kısımları kaldırır.
    
    Args:
        text (str): Gemini API'den gelen ham hikaye metni
    
    Returns:
        str: Temizlenmiş ve düzenlenmiş hikaye metni
    """
    logger.info(f"Cleaning story text of length: {len(text)}")
    
    # Hikayenin yeniden başlamasını kontrol et
    text = detect_story_restart(text)
    
    # Boş satırları temizle
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Başlık ve açıklama türünde metin varsa kaldır
    text = re.sub(r'^(Başlık:|Hikaye:|Story:|Title:).*\n+', '', text, flags=re.IGNORECASE)
    
    # Metni paragraflara böl
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    logger.info(f"Split into {len(paragraphs)} paragraphs")
    
    # Hikayeyi ikiye bölüp tekrarlayan kısım var mı kontrol et
    if len(paragraphs) > 6:
        middle = len(paragraphs) // 2
        first_half = ' '.join(paragraphs[:middle])
        second_half = ' '.join(paragraphs[middle:])
        
        similarity_score = similarity(first_half, second_half)
        logger.info(f"Story half similarity score: {similarity_score}")
        
        if similarity_score > 0.5:
            logger.warning("Detected significant repetition between story halves")
            # Sadece ilk yarıyı kullan
            paragraphs = paragraphs[:middle]
    
    # Tekrarlanan paragrafları tespit et ve kaldır
    cleaned_paragraphs = detect_repetition(paragraphs)
    logger.info(f"After cleaning: {len(cleaned_paragraphs)} paragraphs")
    
    # Temizlenmiş paragrafları tekrar birleştir
    cleaned_text = '\n\n'.join(cleaned_paragraphs)
    
    # Hikaye tutarlılığını kontrol et
    if len(cleaned_paragraphs) < 3:
        logger.error("Story too short after cleaning, returning error message")
        return "Hikaye oluşturulurken bir sorun oluştu. Lütfen tekrar deneyin."
    
    return cleaned_text

def generate_story(topic, age_range="4-10"):
    """
    Generate a sustainability story based on the selected topic
    
    Args:
        topic (str): The sustainability topic to create a story about
        age_range (str): Target age range for the story (default: "4-10")
        
    Returns:
        str: The generated story text
    """
    logger.info(f"Generating story about topic: {topic}")
    
    # Daha güçlü prompt tasarımı
    prompt = f"""
    4-10 yaş aralığındaki çocuklar için "{topic}" konusunda sürdürülebilirlik temalı bir hikaye yaz.
    
    Hikaye şu özelliklere sahip olmalıdır:
    - Çocukların anlayabileceği dilde, basit ve kısa paragraflarla yazılmalı
    - Ana karakterler çocuklar, hayvanlar veya fantastik yaratıklar olabilir
    - Net bir başlangıç, gelişme ve sonuç bölümü olmalı
    - Sürdürülebilirlik ve çevre sorumluluğu konusunda öğretici olmalı
    - Olumlu ve umut verici bir tona sahip olmalı
    - Basit bir çağrı veya öğüt ile sona ermeli
    - 300-500 kelime uzunluğunda olmalı
    - Tamamen Türkçe yazılmalı
    
    Önemli: Lütfen sadece hikaye metnini yaz. Başlık, açıklama veya yorum ekleme.
    Her paragraf arasında bir boşluk bırak. Hikayede tekrar olmamalı ve hikayeyi ortada yeniden başlatma.
    """
    
    try:
        max_retries = 2
        retry_delay = 1  # Hatadan sonra bekleme süresi (saniye)
        
        for attempt in range(max_retries + 1):
            logger.info(f"Generating story attempt {attempt + 1}/{max_retries + 1}")
            
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=1024,
                        stop_sequences=["Hikaye:", "Story:", "Title:", "Başlık:"],
                    )
                )
                
                # Ham hikaye metni
                if not response or not response.text:
                    logger.error("Empty response from Gemini API")
                    if attempt < max_retries:
                        time.sleep(retry_delay)
                        continue
                    return "Hikaye oluşturulamadı. Lütfen daha sonra tekrar deneyin."
                
                raw_story = response.text
                
                # Metni temizle ve düzenle
                cleaned_story = clean_story_text(raw_story)
                
                # Eğer hikaye temizlendikten sonra hala kullanılamıyorsa ve daha fazla deneme hakkımız varsa
                if "Hikaye oluşturulurken bir sorun oluştu" in cleaned_story and attempt < max_retries:
                    logger.warning("Cleaned story was too short or invalid, retrying...")
                    time.sleep(retry_delay)
                    continue
                
                return cleaned_story
                
            except Exception as api_error:
                logger.error(f"API error on attempt {attempt + 1}: {api_error}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
                return "Hikaye oluşturulamadı. Lütfen daha sonra tekrar deneyin."
            
    except Exception as e:
        logger.error(f"Error generating story with Gemini API: {e}")
        return "Hikaye oluşturulamadı. Lütfen daha sonra tekrar deneyin." 