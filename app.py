from flask import Flask, request, render_template, send_file
from google.cloud import texttospeech
import os
from dotenv import load_dotenv

app = Flask(__name__)

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

# Ana sayfa (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Konu seçim sayfası (topic-selection.html)
@app.route('/topic-selection')
def topic_selection():
    return render_template('topic-selection.html')

# Hikaye sayfası (story.html)
@app.route('/story')
def story():
    return render_template('story.html')

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
            speaking_rate=1.0
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
