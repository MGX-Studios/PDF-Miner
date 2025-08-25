# PDF Minner

A small, practical PDF → Markdown converter. It extracts text from a PDF, can optionally remove repeating watermark lines, lightly formats screenplay‑like text, and saves the result as `.md`. Nothing fancy—just a handy tool for everyday use.

## Features
- Sensible extraction: tries `pdfminer.six`, then `pypdf`, then system `pdftotext`.
- Screenplay hints: scene headings, CHARACTER lines, and transitions formatted to simple Markdown.
- Watermark cleanup: detects short repeating lines across pages and lets you remove them.
- Simple UI: pick files and folders with system dialogs; watch a minimal progress spinner.
- Single file: run the script directly; no big setup.

## Quick Start
- Requires Python 3.10+
- Optional extras (recommended):
  ```
  pip install pdfminer.six pypdf colorama pyfiglet
  ```
- Run:
  ```
  python pdf_minner.py
  ```

Output will be saved next to the source PDF (or your chosen folder) as `name.pdf → name.md`.

## Notes
- Optional tools improve results but aren’t mandatory. If extraction fails, install one of `pdfminer.six`, `pypdf`, or make sure Poppler’s `pdftotext` is on your PATH.
- `colorama` adds color; `pyfiglet` adds a small ASCII title; both are optional.
- GUI pickers use `tkinter` (usually included with Python). If a dialog fails to open, check your environment.
- Encrypted PDFs often cannot be processed.

## License
MIT. See `LICENSE`.

---

## Türkçe

Küçük ve pratik bir PDF → Markdown dönüştürücü. PDF’ten metni çıkarır, isterseniz sayfalar arası tekrar eden filigran satırlarını temizlemeye yardımcı olur, senaryo benzeri metinleri hafifçe Markdown’a biçimler ve sonucu `.md` olarak kaydeder. Gösterişsiz, günlük kullanım için el altında bir araç.

### Özellikler
- Mantıklı çıkarım: önce `pdfminer.six`, sonra `pypdf`, ardından sistem `pdftotext` denenir.
- Senaryo ipuçları: sahne başlıkları, KARAKTER satırları ve geçişler basit Markdown’a dönüştürülür.
- Filigran temizleme: sayfalar arası tekrar eden kısa satırları tespit edip kaldırmanıza yardımcı olur.
- Sade arayüz: sistem pencereleriyle dosya/klasör seçin; minimal ilerleme göstergesini izleyin.
- Tek dosya: doğrudan çalıştır, büyük kurulum yok.

### Hızlı Başlangıç
- Python 3.10+ gerekir.
- (Önerilen) Opsiyonel paketler:
  ```
  pip install pdfminer.six pypdf colorama pyfiglet
  ```
- Çalıştırma:
  ```
  python pdf_minner.py
  ```

Çıktı, kaynak PDF’in yanında (veya seçtiğiniz klasörde) `ad.pdf → ad.md` olarak kaydedilir.

### Notlar
- Çıkarım başarısızsa `pdfminer.six`, `pypdf` kurmayı veya Poppler’ın `pdftotext` aracını PATH’e eklemeyi deneyin.
- `colorama` renk katar; `pyfiglet` küçük bir ASCII başlık ekler; ikisi de opsiyoneldir.
- `tkinter` genelde Python ile gelir; diyalog açılmıyorsa ortamı kontrol edin.
- Şifreli PDF’ler çoğunlukla işlenemez.

### Lisans
MIT. Ayrıntılar için `LICENSE`.
