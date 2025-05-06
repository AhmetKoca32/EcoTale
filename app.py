from flask import Flask, request, render_template, send_file, jsonify, session
from google.cloud import texttospeech
import os
from dotenv import load_dotenv
from gemini_service import generate_story

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")

# .env dosyasını yükleyin
load_dotenv()

# Google Cloud servis hesabı dosyası
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_credentials:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials
else:
    print("Hata: GOOGLE_APPLICATION_CREDENTIALS çevresel değişkeni eksik!")

# Google TTS istemcisi
tts_client = texttospeech.TextToSpeechClient()


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
        return {"error": "Hikaye metni eksik!"}, 400

    audio_content = synthesize_speech(story_text)

    if not audio_content:
        return {"error": "Ses oluşturulamadı!"}, 500

    # Sabit dosya adı
    filename = "output.mp3"
    filepath = os.path.join("static", "assets", "audio", filename)

    # Eski dosyayı silip, yeni dosyayı üzerine kaydet
    with open(filepath, "wb") as out:
        out.write(audio_content)

    return {"audio_url": f"/static/assets/audio/{filename}"}


# TTS Fonksiyonu
def synthesize_speech(text):
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="tr-TR",
            name="tr-TR-Chirp3-HD-Sadaltager",  # Ses ismi burada doğruluğunu kontrol et
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            effects_profile_id=["small-bluetooth-speaker-class-device"],
            speaking_rate=0.90
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        if response.audio_content:
            return response.audio_content
        else:
            print("Ses içeriği boş döndü.")
            return None
    except Exception as e:
        print(f"Ses sentezleme hatası: {e}")
        return None  # Hata durumunda None döndür


if __name__ == '__main__':
    app.run(debug=True)