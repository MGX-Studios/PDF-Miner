# PDF‑Miner ✨

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-444)](#)
[![License](https://img.shields.io/badge/License-MIT-00b16a)](LICENSE)

Basit, hızlı ve şık bir PDF → Metin/Markdown dönüştürücü. Seçtiğiniz PDF’ten metni çıkarır, isterse filigranları temizler, senaryo (screenplay) metinlerini akıllı şekilde Markdown’a biçimler ve sonucu `.md` olarak kaydeder.

Uygulama etkileşimli bir menü ile gelir; PDF ve çıktı klasörünü görsel seçim pencereleriyle (tkinter) belirleyebilir, dönüşüm ilerlemesini animasyonlu göstergelerle takip edebilirsiniz.

— “PDF Minner” arayüzü bu depoda “PDF‑Miner” adıyla yer alır.

## Özellikler
- Akıllı çıkarım: pdfminer.six → pypdf → sistem `pdftotext` sıralı deneme.
- Senaryo farkındalığı: `INT./EXT.` sahne başlıkları, KARAKTER satırları ve geçişler otomatik biçimlenir.
- Filigran temizleme: Sayfalar arası tekrar eden kısa satırları tespit edip kaldırır (isteğe bağlı ve etkileşimli).
- Görsel seçim: PDF ve çıktı klasörünü sistem seçicisiyle belirleme (tkinter).
- İlerleme ve durum: Terminalde animasyonlu ilerleme göstergesi ve başlangıç ekranı.
- Tek dosya: Kurulumu kolay, doğrudan çalıştırılabilir Python betiği.

## Hızlı Başlangıç
1) Python 3.10+ yüklü olduğundan emin olun.

2) (Önerilen) İsteğe bağlı bağımlılıkları kurun:
```
pip install pdfminer.six pypdf colorama pyfiglet
```

3) Uygulamayı çalıştırın:
```
python pdf_minner.py
```

4) Menüden şu adımları izleyin:
- “PDF dosyası seç” ile dönüştürülecek PDF’i seçin.
- “Çıktı klasörü seç” ile hedef klasörü belirleyin (boş bırakılırsa PDF’in bulunduğu klasör kullanılır).
- “Filigranı temizle” tercihini açıp kapatın.
- “Dönüştürmeyi başlat” ile `.md` çıktısını oluşturun.

Çıktı dosyası, seçtiğiniz klasöre `ornek.pdf → ornek.md` şeklinde kaydedilir.

## Senaryo (Screenplay) Biçimlendirme
Metin senaryo yapısına benziyorsa otomatik olarak Markdown’a dönüştürülür:
- `INT./EXT./INT/EXT./I/E.` ile başlayan satırlar → `## SAHNE BAŞLIĞI`
- TAMAMEN BÜYÜK HARF karakter satırları → `**KARAKTER**`
- Parantez içi kısa açıklamalar → `_italic_`
- `... TO:` şeklindeki geçişler → alıntı bloğu içinde italik

Biçimlendirme sezgiseldir; klasik PDF metinleri değişmeden basitçe `.md` olarak yazılır.

## Bağımlılıklar
- Zorunlu: Python 3.10+
- Opsiyonel (çıkarım kalitesi/performans için önerilir):
  - `pdfminer.six`
  - `pypdf`
  - `colorama` (renkli terminal çıktısı)
  - `pyfiglet` (ASCII art başlık)
  - Poppler `pdftotext` (sistem aracısı; PATH’te bulunursa kullanılır)

Not: `tkinter` çoğu Python dağıtımında yerleşik gelir; sisteminizde bulunmuyorsa işletim sisteminize uygun paketle kurmanız gerekebilir.

## İpuçları ve Sorun Giderme
- “PDF metni çıkarılamadı” uyarısı alırsanız; sırayla `pdfminer.six`, `pypdf` ve sistem `pdftotext` denemeleri başarısız olmuştur. İlgili paketi kurmayı veya Poppler’ı yükleyip `pdftotext`’i PATH’e eklemeyi deneyin.
- Renkli çıktı görünmüyorsa `colorama` kurulu olmayabilir. Renkler olmadan da çalışır.
- GUI dosya/klasör seçim penceresi açılmıyorsa, ortamda `tkinter` eksik olabilir.
- Şifreli/korumalı PDF’ler genellikle çıkarılamaz; mümkünse açık bir kopya kullanın.

## Geliştirme
- Kod tek dosyada: `pdf_minner.py`
- Stiller ve animasyonlar terminal tabanlıdır; görsel arayüz bağımlılıklarını minimumda tutar.
- Katkılar, hata bildirimleri ve öneriler için Issues/PR’lar açabilirsiniz.

## Lisans
Bu proje MIT lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

— İyi dönüşümler! 📄➡️📘
