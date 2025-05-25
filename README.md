# Belge Tarama Uygulaması (Document Scanner)

Bu proje, kullanıcının bir fotoğrafını yükleyip, belgeyi otomatik olarak tespit ederek perspektif düzeltmesi yapabilen ve sonrasında iyileştirme işlemleri uygulayan bir masaüstü belge tarama uygulamasıdır. Kullanıcı ayrıca işlenen belgeyi PDF olarak kaydedebilir.

---

## Özellikler

- Fotoğraf yükleme desteği (JPEG, PNG, BMP formatları)
- Belge köşelerini otomatik olarak tespit etme
- Köşeleri manuel olarak düzenleyebilme
- Perspektif düzeltmesi ile belgeyi A4 oranına uygun hale getirme
- Görüntü iyileştirme: kontrast artırma, gürültü azaltma, keskinleştirme
- İşlenen belgeyi PDF dosyası olarak kaydetme
- Kullanıcı dostu grafik arayüz (Tkinter ile)

---

## Gereksinimler

- Python 3.7 ve üzeri
- OpenCV (`cv2`)  
- NumPy  
- Pillow (`PIL`)  
- FPDF  
- Tkinter (Python standart kütüphanesi ile gelir)

Kurulum için:

```bash
pip install opencv-python numpy pillow fpdf
```

---

## Kullanım

1. Programı çalıştırın:

```bash
python document_scanner.py
```

2. **Fotoğraf Yükle** butonuna tıklayarak belge fotoğrafınızı seçin.  
3. Uygulama belge köşelerini otomatik tespit eder, isterseniz köşeleri manuel olarak düzenleyebilirsiniz.  
4. **Belgeyi İşle** butonuna tıklayarak belgeyi perspektif düzeltmesi ve iyileştirme işlemlerinden geçirin.  
5. İşlenmiş belgeyi görmek için arayüzde görüntülenecektir.  
6. **PDF Olarak Kaydet** butonuna tıklayarak belgeyi PDF formatında kaydedin.

---

## Proje Yapısı

- `document_scanner.py` — Ana uygulama dosyası

---

## İyileştirme ve Geliştirme Fikirleri

- Çok sayfalı PDF oluşturma desteği  
- Kamera entegrasyonu ile canlı belge tarama  
- OCR ile metin tanıma ve düzenleme  
- Daha gelişmiş görüntü iyileştirme algoritmaları  
- Mobil uygulama versiyonu  

---


## İletişim

Herhangi bir sorun, öneri veya katkı için bana ulaşabilirsiniz.


