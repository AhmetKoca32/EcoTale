from flask import Flask, request, render_template, jsonify, session
import os
import logging
from google.cloud import texttospeech
from dotenv import load_dotenv
from gemini_service import generate_story

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")

# Loglama ayarı
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# .env dosyasını yükleyin
load_dotenv()

# Google Cloud servis hesabı dosyası
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_credentials:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials
    logger.info(f"Google credentials loaded from: {google_credentials}")
else:
    logger.error("Hata: GOOGLE_APPLICATION_CREDENTIALS çevresel değişkeni eksik!")

# Ses dosyalarının kaydedileceği klasörü kontrol et ve oluştur
audio_directory = os.path.join("static", "assets", "audio")
if not os.path.exists(audio_directory):
    os.makedirs(audio_directory)
    logger.info(f"Created audio directory: {audio_directory}")

# Google TTS istemcisi
try:
    tts_client = texttospeech.TextToSpeechClient()
    logger.info("TTS client initialized successfully")
except Exception as e:
    logger.error(f"TTS client initialization error: {e}")
    tts_client = None


@app.route('/')
def splash():
    return render_template('splash.html')

# Ana sayfa (index.html)
@app.route('/start')
def index():
    return render_template('index.html')

# Konu seçim sayfası (topic-selection.html)
@app.route('/topic-selection')
def topic_selection():
    return render_template('topic-selection.html')

# Hikaye sayfası (story.html)
@app.route('/story')
def story():
    # Pass any stored story to the template if available
    story_text = session.get('story_text', '')
    
    # Hikaye oluşturulduysa, hemen ses dosyasını oluştur
    if story_text and story_text != "Hikaye oluşturulamadı. Lütfen daha sonra tekrar deneyin.":
        try:
            audio_content = synthesize_speech(story_text)
            if audio_content:
                filename = "output.mp3"
                filepath = os.path.join("static", "assets", "audio", filename)
                with open(filepath, "wb") as out:
                    out.write(audio_content)
                logger.info("Audio created during story page load")
        except Exception as e:
            logger.error(f"Error pre-generating audio: {e}")
    
    return render_template('story.html', story_text=story_text)

# Gemini API ile hikaye oluştur
@app.route('/generate-story', methods=['POST'])
def create_story():
    data = request.get_json()
    topic_id = data.get('topic_id')
    
    # Topic ID to topic name mapping
    topics = {
        '1': 'Yoksulluğa Son',
        '2': 'Açlığa Son',
        '3': 'Sağlık ve Kaliteli Yaşam',
        '4': 'Nitelikli Eğitim',
        '5': 'Toplumsal Cinsiyet Eşitliği',
        '6': 'Temiz Su ve Sanitasyon',
        '7': 'Erişilebilir ve Temiz Enerji',
        '8': 'İnsana Yakışır İş ve Ekonomik Büyüme',
        '9': 'Sanayi, Yenilikçilik ve Altyapı',
        '10': 'Eşitsizliklerin Azaltılması',
        '11': 'Sürdürülebilir Şehirler ve Topluluklar',
        '12': 'Sorumlu Üretim ve Tüketim',
        '13': 'İklim Eylemi',
        '14': 'Sudaki Yaşam',
        '15': 'Karasal Yaşam',
        '16': 'Barış, Adalet ve Güçlü Kurumlar',
        '17': 'Amaçlar için Ortaklıklar'
    }
    
    topic = topics.get(str(topic_id), 'Sürdürülebilirlik')
    logger.info(f"Generating story for topic: {topic}")
    
    # Generate story using Gemini API
    story_text = generate_story(topic)
    
    # Store the story in session for later use
    session['story_text'] = story_text
    
    return jsonify({
        'success': True,
        'story': story_text
    })

# Hikaye al ve sesi oluştur (speak)
@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    story_text = data.get("text", "")
    
    if not story_text:
        logger.error("Speak API called with empty text")
        return {"error": "Hikaye metni eksik!"}, 400
    
    if not tts_client:
        logger.error("TTS client is not initialized")
        return {"error": "TTS istemcisi başlatılamadı!"}, 500

    try:
        logger.info(f"Synthesizing speech for text of length: {len(story_text)}")
        
        # Ses dosyasının mevcut olup olmadığını kontrol et
        filename = "output.mp3"
        filepath = os.path.join("static", "assets", "audio", filename)
        
        if os.path.exists(filepath):
            logger.info("Using existing audio file")
            return {"audio_url": f"/static/assets/audio/{filename}"}
        
        # Ses dosyası yoksa oluştur
        audio_content = synthesize_speech(story_text)

        if not audio_content:
            logger.error("Audio content is empty after synthesis")
            return {"error": "Ses oluşturulamadı!"}, 500

        logger.info(f"Saving audio to: {filepath}")
        # Eski dosyayı silip, yeni dosyayı üzerine kaydet
        with open(filepath, "wb") as out:
            out.write(audio_content)

        logger.info("Audio file saved successfully")
        return {"audio_url": f"/static/assets/audio/{filename}"}
    except Exception as e:
        logger.error(f"Error in speak route: {e}")
        return {"error": f"Ses oluşturma sırasında hata: {str(e)}"}, 500


# TTS Fonksiyonu
def synthesize_speech(text):
    try:
        logger.info("Starting speech synthesis")
        
        # Çok uzun metinleri parçalama (Google TTS API sınırlaması)
        max_length = 4500  # Google TTS karakter sınırı yaklaşık 5000
        
        if len(text) > max_length:
            logger.info(f"Text too long ({len(text)} chars), splitting into chunks")
            chunks = []
            sentences = text.split('.')
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 <= max_length:
                    current_chunk += sentence + '.'
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + '.'
            
            if current_chunk:
                chunks.append(current_chunk)
                
            logger.info(f"Split into {len(chunks)} chunks")
            
            # Her bölümü ayrı ayrı sentezle ve sonuçları birleştir
            audio_contents = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Synthesizing chunk {i+1}/{len(chunks)}")
                audio_content = synthesize_chunk(chunk)
                if audio_content:
                    audio_contents.append(audio_content)
                else:
                    logger.error(f"Failed to synthesize chunk {i+1}")
                    
            # MP3 formatını destekleyen basit birleştirme
            if audio_contents:
                return b''.join(audio_contents)
            return None
        else:
            # Tek parça olarak sentezle
            return synthesize_chunk(text)
            
    except Exception as e:
        logger.error(f"Ses sentezleme hatası: {e}")
        return None  # Hata durumunda None döndür


def synthesize_chunk(text):
    """Tek bir metin parçasını sese çevirir"""
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Mevcut Türkçe sesleri bulmak için, kullanılabilir sesleri kontrol et
        # Kullanılabilir sesler değişebileceğinden alternatif sesler deneyelim
        try:
            voice = texttospeech.VoiceSelectionParams(
                language_code="tr-TR",
                name="tr-TR-Standard-A",  # Standart kadın sesi
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.90
            )
            
            response = tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            if response.audio_content:
                return response.audio_content
                
        except Exception as e1:
            logger.warning(f"First voice attempt failed: {e1}, trying alternative voice")
            # Alternatif ses dene
            try:
                voice = texttospeech.VoiceSelectionParams(
                    language_code="tr-TR",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
                )
                
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=0.90
                )
                
                response = tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
                
                if response.audio_content:
                    return response.audio_content
            except Exception as e2:
                logger.error(f"Alternative voice failed too: {e2}")
                return None
                
        logger.error("Ses içeriği boş döndü.")
        return None
        
    except Exception as e:
        logger.error(f"Chunk synthesis error: {e}")
        return None


if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True)
