# 🌱 EcoTale

**EcoTale**, çocuklara çevre bilinci kazandırmayı amaçlayan interaktif ve eğitici bir hikaye anlatım uygulamasıdır. Kullanıcıdan alınan yaş ve isim bilgilerine göre çevre temalı hikayeler üretilir. Bu hikaye, bir animasyon karakter eşliğinde **Gemini API** kullanılarak oluşturulur ve **Text-to-Speech (TTS)** teknolojisiyle sesli olarak anlatılır.

## 🧪 Kullanılan Teknolojiler

- **HTML** – Uygulama arayüzü
- **CSS** – Tasarım ve stil
- **JavaScript** – Uygulama mantığı, API entegrasyonları ve animasyon
- **Python/Flask** - Backend, API entegrasyonu
- **Gemini API** – Yaşa ve konuya göre hikaye üretimi
- **Google Cloud TTS (Text-to-Speech)** – Hikayeyi sesli hale getirme
- **Three.js** - Interaktif 3D animasyonlar

## 🚀 Kurulum ve Çalıştırma

1. Gereksinimleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Ortam değişkenlerini ayarlayın:
   - GOOGLE_APPLICATION_CREDENTIALS=Google Cloud TTS için hizmet hesabı dosya yolu
   - GEMINI_API_KEY=Google Gemini API anahtarınız
   - SECRET_KEY=Flask session güvenlik anahtarı

3. Uygulamayı çalıştırın:
   ```
   python app.py
   ```

## 🔌 Gemini API Entegrasyonu

Gemini API entegrasyonu şu adımları içerir:

1. **API Anahtarı Yapılandırması**: .env dosyasında GEMINI_API_KEY değişkeni ayarlanır
2. **prompt Optimizasyonu**: Çocuklara uygun, eğitici ve ilgi çekici hikayeler oluşturmak için özel olarak tasarlanmış promptlar
3. **Hikaye Üretimi**: Seçilen sürdürülebilirlik konusuna göre hikaye oluşturulur
4. **Seslendirme**: Üretilen hikaye Google TTS ile seslendirilir

## 📆 Geliştirme Süreci

| Gün        | Yapılanlar                                                                 |
|------------|-----------------------------------------------------------------------------|
| **Cuma**   | Jam başlangıcı                                                              |
| **Cumartesi** | Proje fikrinin belirlenmesi, görev dağılımı yapıldı                        |
| **Pazar**  | UI araştırmaları ve tasarımın tamamlanması, TTS teknolojisi üzerine araştırmalar |
| **Pazartesi** | Gemini API entegrasyonu ve test çalışmaları                               |
| **Salı**   | Proje anlatım videosu çekimi, sunum ve teslim                               |

## 🔁 Uygulama Akışı

1. **Kullanıcı Girişi**
   - Yaş ve isim bilgisi alınır.
2. **Konu Seçimi**
   - Kullanıcı çevre temalı konulardan birini seçer.
3. **Hikaye Oluşumu ve Anlatımı**
   - Girilen bilgilere göre **Gemini API** ile hikaye oluşturulur.
   - Bir animasyon karakter eşliğinde **TTS** ile hikaye sesli olarak dinletilir.

## 🎯 Hedef Kitle

- 5–12 yaş arası çocuklar
- Çevre bilinci kazandırmak isteyen aileler ve öğretmenler

## 🎥 Demo Videosu

> Demo bağlantısı salı günü eklenecek.

## 👥 Takım Üyeleri

- Kezban Şevval İnci – Proje Yönetici
- Ahmet Koca – Developer
- Barış Berişbek – Developer
- Hatice Yalçın – Developer
- Büşra Deveci – Tasarımcı


---

**Not:** Bu proje, belirli bir sürede sınırlı kaynaklarla geliştirilmiş bir **hackathon projesidir**. Gelecekte genişletilmeye açıktır.
