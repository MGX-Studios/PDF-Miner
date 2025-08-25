#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
import threading
import subprocess
from queue import Queue, Empty
from pathlib import Path


# Optional color support
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
except Exception:  # fallback to no-colors
    class _No:
        RESET_ALL = ""
    class _NoFore:
        CYAN = BLUE = GREEN = MAGENTA = YELLOW = RED = WHITE = ""
    Fore = _NoFore()
    class _NoStyle:
        BRIGHT = NORMAL = ""
    Style = _NoStyle()


APP_NAME = "PDF Minner"

# Cache for banner rendering (avoids re-rendering on each frame)
_BANNER_CACHE: str | None = None


def clear_screen() -> None:
    # Clear + move cursor home + set black background and magenta text
    sys.stdout.write("\x1b[2J\x1b[H\x1b[40m\x1b[35m")
    sys.stdout.flush()


def banner() -> str:
    global _BANNER_CACHE
    if _BANNER_CACHE is not None:
        return _BANNER_CACHE

    # Prefer pyfiglet for ASCII art, gracefully fallback
    try:
        from pyfiglet import Figlet  # type: ignore
        cols, _ = term_size()
        f = Figlet(font="slant", width=max(60, cols))
        title = f.renderText(APP_NAME)
    except Exception:
        title = r"""
   ____  ______ _____     __  __ _       _                
  |  _ \|  ____|  __ \   |  \/  (_)     | |               
  | |_) | |__  | |  | |  | \  / |_ _ __ | | _____ _ __    
  |  _ <|  __| | |  | |  | |\/| | | '_ \| |/ / _ \ '__|   
  | |_) | |____| |__| |  | |  | | | | | |   <  __/ |      
  |____/|______|_____/   |_|  |_|_|_| |_|_|\_\___|_|      
"""

    tagline = "PDF → Markdown (Screenplay-aware)"
    box_top = f"{Fore.MAGENTA}{Style.BRIGHT}┌{'─'*50}┐{Style.NORMAL}"
    box_mid = (
        f"{Fore.MAGENTA}{Style.BRIGHT}│{Style.NORMAL}   "
        f"{Fore.MAGENTA}{APP_NAME}{Style.NORMAL} — Basit ve Hızlı"
        f"{' '*(50-26)}{Fore.MAGENTA}{Style.BRIGHT}│{Style.NORMAL}"
    )
    box_bot = f"{Fore.MAGENTA}{Style.BRIGHT}└{'─'*50}┘{Style.NORMAL}"
    _BANNER_CACHE = f"{Fore.MAGENTA}{title}{tagline}\n\n{box_top}\n{box_mid}\n{box_bot}{Style.NORMAL}"
    return _BANNER_CACHE


def hide_cursor():
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\x1b[?25h" + Style.RESET_ALL)
    sys.stdout.flush()


def term_size():
    try:
        import shutil
        sz = shutil.get_terminal_size(fallback=(80, 24))
        return sz.columns, sz.lines
    except Exception:
        return 80, 24


def splash_rain_lightning(duration: float = 2.5) -> None:
    import random
    # Optional: Windows key detection for early exit
    try:
        import msvcrt  # type: ignore
        has_kb = True
    except Exception:
        msvcrt = None  # type: ignore
        has_kb = False
    cols, rows = term_size()
    rows = max(10, rows - 2)
    drops = []  # list of (x, y)
    density = max(1, cols // 8)
    last_flash = 0.0
    flash = False
    start = time.time()
    hide_cursor()
    try:
        while time.time() - start < duration:
            # Early exit on key (Windows)
            if has_kb and msvcrt.kbhit():  # type: ignore
                try:
                    msvcrt.getch()  # consume
                except Exception:
                    pass
                break
            clear_screen()
            # spawn new drops
            for _ in range(density):
                x = random.randint(0, cols - 1)
                drops.append([x, 0])
            # advance drops
            for d in drops:
                d[1] += 1
            drops[:] = [d for d in drops if d[1] < rows]

            # occasional lightning flash
            if time.time() - last_flash > random.uniform(0.6, 1.4):
                flash = True
                last_flash = time.time()
            else:
                flash = False

            # draw
            buf = []
            if flash:
                buf.append(f"{Fore.MAGENTA}{Style.BRIGHT}")
            else:
                buf.append(f"{Fore.MAGENTA}{Style.NORMAL}")
            # header line
            buf.append(banner())
            buf.append("\n")
            # rain field
            field = [[" "] * cols for _ in range(rows)]
            for x, y in drops:
                ch = "|" if not flash else "|"
                if 0 <= y < rows and 0 <= x < cols:
                    field[y][x] = ch
            # overlay centered prompt
            msg = "Devam etmek için bir tuşa basın"
            if len(msg) < cols:
                y = rows // 2
                sx = max(0, (cols - len(msg)) // 2)
                for i, ch in enumerate(msg):
                    if 0 <= sx + i < cols:
                        field[y][sx + i] = ch
            for r in field:
                line = "".join(r)
                buf.append(line)
            sys.stdout.write("\n".join(buf)[:8000])
            sys.stdout.flush()
            time.sleep(0.08)
    finally:
        show_cursor()
    # If not Windows, pause for Enter to honor the prompt
    if not has_kb:
        try:
            input("Devam etmek için bir tuşa basın...")
        except Exception:
            pass


def menu(selected_file: Path | None, output_dir: Path | None, remove_wm: bool) -> str:
    sf = str(selected_file) if selected_file else "(seçilmedi)"
    od = str(output_dir) if output_dir else "(seçilmedi)"
    wm = f"Açık" if remove_wm else "Kapalı"
    return (
        f"\n{Fore.YELLOW}Menü{Style.RESET_ALL}\n"
        f"  1) PDF dosyası seç   : {Fore.GREEN}{sf}{Style.RESET_ALL}\n"
        f"  2) Çıktı klasörü seç : {Fore.GREEN}{od}{Style.RESET_ALL}\n"
        f"  3) Filigranı temizle : {Fore.CYAN}{wm}{Style.RESET_ALL}\n"
        f"  4) Dönüştürmeyi başlat\n"
        f"  5) Hakkında\n"
        f"  6) Çıkış\n\n"
        f"Seçiminiz (1-6): "
    )


def choose_pdf_gui() -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        # filetypes only PDFs
        file_path = filedialog.askopenfilename(
            title="PDF seç",
            filetypes=[("PDF files", "*.pdf")],
        )
        root.destroy()
        return Path(file_path) if file_path else None
    except Exception as e:
        print(f"GUI açılamadı: {e}")
        return None


def choose_dir_gui() -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        dir_path = filedialog.askdirectory(title="Çıktı klasörü seç")
        root.destroy()
        return Path(dir_path) if dir_path else None
    except Exception as e:
        print(f"GUI açılamadı: {e}")
        return None


# -------- PDF Extraction Backends --------

def extract_pdf_text(path: Path, progress: Queue | None = None) -> str:
    # Try pdfminer.six
    try:
        from pdfminer.high_level import extract_text  # type: ignore
        if progress:
            progress.put(("status", "pdfminer ile çıkarılıyor"))
        return extract_text(str(path))
    except Exception:
        pass

    # Try pypdf with per-page progress
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        n = len(reader.pages)
        texts: list[str] = []
        for i, page in enumerate(reader.pages, start=1):
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            texts.append(txt)
            if progress:
                progress.put(("progress", int(i * 100 / max(1, n))))
        return "\n\f\n".join(texts)
    except Exception:
        pass

    # Try system pdftotext
    exe = _which("pdftotext")
    if exe:
        if progress:
            progress.put(("status", "pdftotext ile çıkarılıyor"))
        try:
            cp = subprocess.run([exe, "-layout", str(path), "-"], capture_output=True, check=True)
            return cp.stdout.decode("utf-8", errors="ignore")
        except Exception as e:
            raise RuntimeError(f"pdftotext başarısız: {e}")

    raise RuntimeError(
        "PDF metni çıkarılamadı. 'pdfminer.six' veya 'pypdf' kurun ya da PATH'te 'pdftotext' bulundurun."
    )


def _which(cmd: str) -> str | None:
    from shutil import which
    return which(cmd)


# -------- Screenplay Markdown Formatter --------

import re

SCENE_RE = re.compile(r"^(INT\.|EXT\.|INT/EXT\.|I/E\.)[\w\W]*")
TRANSITION_RE = re.compile(r"^[A-Z][A-Z \-]+TO:\s*$")


def format_screenplay_md(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            out.append("")
            i += 1
            continue
        if SCENE_RE.match(s):
            out.append(f"## {s}")
            i += 1
            continue
        if TRANSITION_RE.match(s):
            out.append(f"> _{s}_")
            i += 1
            continue
        if _is_character_line(s):
            out.append(f"**{s}**")
            i += 1
            while i < len(lines):
                nxt = lines[i].rstrip()
                ns = nxt.strip()
                if not ns:
                    out.append("")
                    i += 1
                    break
                if SCENE_RE.match(ns) or _is_character_line(ns) or TRANSITION_RE.match(ns):
                    break
                if ns.startswith("(") and ns.endswith(")") and len(ns) < 80:
                    out.append(f"_{ns}_")
                else:
                    out.append(nxt)
                i += 1
            continue
        out.append(line)
        i += 1
    cleaned: list[str] = []
    blank_run = 0
    for l in out:
        if l.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                cleaned.append("")
        else:
            blank_run = 0
            cleaned.append(l)
    return "\n".join(cleaned) + ("\n" if cleaned and cleaned[-1] != "" else "")


def _is_character_line(s: str) -> bool:
    if not (2 <= len(s) <= 30):
        return False
    if not s.isupper():
        return False
    tmp = s.replace(" ", "").replace("-", "").replace("'", "")
    return tmp.isalpha()


def detect_screenplay(text: str) -> bool:
    lines = [l.rstrip() for l in text.splitlines()]
    scene_hits = 0
    char_hits = 0
    for l in lines[:1000]:
        s = l.strip()
        if not s:
            continue
        if s.startswith(("INT.", "EXT.", "INT/EXT.", "I/E.")):
            scene_hits += 1
        if 2 <= len(s) <= 30 and s.isupper() and s.replace(" ", "").isalpha():
            char_hits += 1
    return scene_hits >= 1 or char_hits >= 3


# -------- Watermark detection/removal --------

def _split_pages(text: str) -> list[str]:
    # Many backends insert form feed between pages
    if "\f" in text:
        return text.split("\f")
    # Fallback: single page
    return [text]


def _normalize_line(s: str) -> str:
    return " ".join(s.strip().split())


def detect_watermark_candidates(pages: list[str]) -> set[str]:
    import collections
    n = len(pages)
    if n <= 1:
        return set()
    counts = collections.Counter()
    for p in pages:
        # consider unique short lines per page to reduce bias
        seen = set()
        for raw in p.splitlines():
            s = _normalize_line(raw)
            if not s:
                continue
            if len(s) > 60 or len(s) < 2:
                continue
            if s.isdigit():
                continue
            # ignore typical headings
            if s.lower() in {"confidential", "draft"} or s.endswith(":"):
                pass
            seen.add(s)
        for s in seen:
            counts[s] += 1
    # threshold: appears on >= 60% of pages and at least 3 pages
    thresh = max(3, int(0.6 * n))
    candidates = {s for s, c in counts.items() if c >= thresh}
    return candidates


def remove_watermarks_from_text(text: str) -> tuple[str, list[str]]:
    pages = _split_pages(text)
    cands = detect_watermark_candidates(pages)
    if not cands:
        return text, []
    cleaned_pages: list[str] = []
    for p in pages:
        out_lines = []
        for raw in p.splitlines():
            s = _normalize_line(raw)
            if s in cands:
                continue
            out_lines.append(raw)
        cleaned_pages.append("\n".join(out_lines))
    return "\n".join(cleaned_pages), sorted(cands)


# -------- Worker Thread + Spinner --------

def detect_watermark_candidates_with_counts(pages: list[str]) -> list[tuple[str, int]]:
    import collections
    n = len(pages)
    counts = collections.Counter()
    for p in pages:
        seen = set()
        for raw in p.splitlines():
            s = _normalize_line(raw)
            if not s or len(s) > 60 or len(s) < 2 or s.isdigit():
                continue
            seen.add(s)
        for s in seen:
            counts[s] += 1
    items = [(s, c) for s, c in counts.items()]
    items.sort(key=lambda t: (-t[1], t[0]))
    return items


def remove_watermarks_by_selection(text: str, phrases: list[str]) -> str:
    if not phrases:
        return text
    norms = [ _normalize_line(p) for p in phrases if p.strip() ]
    pages = _split_pages(text)
    cleaned_pages: list[str] = []
    for p in pages:
        out_lines = []
        for raw in p.splitlines():
            s = _normalize_line(raw)
            remove = False
            for n in norms:
                if not n:
                    continue
                if s == n:
                    remove = True
                    break
                if len(n) >= 3 and n in s and len(s) <= 120:
                    remove = True
                    break
            if not remove:
                out_lines.append(raw)
        cleaned_pages.append("\n".join(out_lines))
    return "\n".join(cleaned_pages)


def extract_only_worker(pdf_path: Path, q: Queue) -> None:
    try:
        q.put(("status", "PDF okunuyor"))
        txt = extract_pdf_text(pdf_path, progress=q)
        q.put(("text", txt))
    except Exception as e:
        q.put(("error", str(e)))


def convert_worker(pdf_path: Path, out_dir: Path, q: Queue, *, remove_wm: bool) -> None:
    try:
        q.put(("status", "PDF okunuyor"))
        txt = extract_pdf_text(pdf_path, progress=q)
        if remove_wm:
            q.put(("status", "Filigran temizleniyor"))
            txt, removed = remove_watermarks_from_text(txt)
        q.put(("status", "Biçimleniyor"))
        md = format_screenplay_md(txt) if detect_screenplay(txt) else txt
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (pdf_path.stem + ".md")
        out_path.write_text(md, encoding="utf-8")
        q.put(("done", str(out_path)))
    except Exception as e:
        q.put(("error", str(e)))


SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def run_with_spinner(thread: threading.Thread, q: Queue) -> tuple[bool, str | None]:
    idx = 0
    percent = None
    status = "Hazır"
    while thread.is_alive():
        # Drain messages
        try:
            while True:
                kind, payload = q.get_nowait()
                if kind == "progress":
                    percent = int(payload)
                elif kind == "status":
                    status = str(payload)
                elif kind == "error":
                    print()
                    return False, str(payload)
                elif kind == "done":
                    print()
                    return True, str(payload)
                elif kind == "text":
                    print()
                    return True, str(payload)
        except Empty:
            pass
        spin = SPINNER_FRAMES[idx % len(SPINNER_FRAMES)]
        idx += 1
        if percent is not None:
            line = f" {Fore.MAGENTA}{spin}{Style.RESET_ALL} {status} — %{percent:3d}"
        else:
            line = f" {Fore.MAGENTA}{spin}{Style.RESET_ALL} {status}"
        print("\r" + line + " " * 20, end="", flush=True)
        time.sleep(0.08)

    # Final drain
    try:
        while True:
            kind, payload = q.get_nowait()
            if kind == "error":
                print()
                return False, str(payload)
            elif kind == "done":
                print()
                return True, str(payload)
            elif kind == "text":
                print()
                return True, str(payload)
            elif kind == "progress":
                pass
            elif kind == "status":
                status = str(payload)
    except Empty:
        pass
    print()
    return False, "Bilinmeyen durum"


# -------- Main loop --------

def main() -> int:
    selected_file: Path | None = None
    output_dir: Path | None = None
    remove_wm = True

    # Splash animation once at startup
    splash_rain_lightning(2.8)

    while True:
        clear_screen()
        print(banner())
        choice = input(menu(selected_file, output_dir, remove_wm)).strip()

        if choice == "1":
            f = choose_pdf_gui()
            if f and f.suffix.lower() == ".pdf" and f.exists():
                selected_file = f
            else:
                print(f"{Fore.RED}Geçerli bir PDF seçilmedi.{Style.RESET_ALL}")
                input("Devam için Enter...")

        elif choice == "2":
            d = choose_dir_gui()
            if d:
                output_dir = d
            else:
                print(f"{Fore.RED}Klasör seçilmedi.{Style.RESET_ALL}")
                input("Devam için Enter...")

        elif choice == "3":
            remove_wm = not remove_wm

        elif choice == "4":
            if not selected_file:
                print(f"{Fore.RED}Önce bir PDF dosyası seçin.{Style.RESET_ALL}")
                input("Devam için Enter...")
                continue
            if not output_dir:
                # Varsayılan: kaynağın yanına
                output_dir = selected_file.parent

            # 1) Extract text with spinner
            print(f"\n{Fore.YELLOW}PDF okunuyor...{Style.RESET_ALL}")
            q: Queue = Queue()
            t = threading.Thread(target=extract_only_worker, args=(selected_file, q), daemon=True)
            t.start()
            ok, payload = run_with_spinner(t, q)
            if not ok or not payload:
                print(f"{Fore.RED}Hata:{Style.RESET_ALL} {payload}")
                input("Devam için Enter...")
                continue

            text = payload

            # 2) Watermark interactive selection (optional)
            if remove_wm:
                pages = _split_pages(text)
                ranked = detect_watermark_candidates_with_counts(pages)
                # Propose top candidate first
                selected_phrases: list[str] = []
                if ranked:
                    best, cnt = ranked[0]
                    ans = input(f"\nOlası filigran: '{best}' (yaklaşık {cnt} sayfa). Temizlensin mi? [E/h]: ").strip().lower()
                    if ans in ("e", "evet", "y", "yes", ""):  # default yes
                        selected_phrases = [best]
                    else:
                        print("\nDiğer adaylar:")
                        # show up to 20
                        show = ranked[:20]
                        for i, (s, c) in enumerate(show, start=1):
                            print(f"  {i:2d}) {s}  [{c}]")
                        raw = input("Temizlenecek numaraları girin (örn: 1,3) veya özel metin girin (boş geç: hiçbiri): ").strip()
                        if raw:
                            if any(ch.isdigit() for ch in raw):
                                picks: list[str] = []
                                for part in raw.split(','):
                                    part = part.strip()
                                    if not part:
                                        continue
                                    if part.isdigit():
                                        idx = int(part)
                                        if 1 <= idx <= len(show):
                                            picks.append(show[idx-1][0])
                                selected_phrases = picks
                            else:
                                # treat entire input as custom phrases separated by ;
                                selected_phrases = [p.strip() for p in raw.split(';') if p.strip()]

                if selected_phrases:
                    print(f"\nFiligran temizleniyor: {', '.join(selected_phrases)}")
                    text = remove_watermarks_by_selection(text, selected_phrases)

            # 3) Format and write
            print(f"\n{Fore.YELLOW}Biçimleniyor ve yazılıyor...{Style.RESET_ALL}")
            md = format_screenplay_md(text) if detect_screenplay(text) else text
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / (selected_file.stem + ".md")
            out_path.write_text(md, encoding="utf-8")
            print(f"{Fore.GREEN}Bitti:{Style.RESET_ALL} {out_path}")
            input("Devam için Enter...")

        elif choice == "5":
            clear_screen()
            print(banner())
            print(
                "Basit ama işini iyi yapan bir PDF → Markdown dönüştürücü.\n"
                "• Senaryo (screenplay) metinlerinde sahne/karakter/geçişleri akıllıca biçimler.\n"
                "• Tekrarlayan kısa satırları tespit ederek filigranları temizlemeye yardımcı olur.\n\n"
                "Mütevazı hedefimiz: PDF metinlerini daha okunur ve işlenir hale getirmek.\n"
                "Özellikle yapay zekâ eğitimlerinde, ajan/LLM eğitim hatlarında veya veri işleme\n"
                "akışlarında, hızlıca temiz metne ulaşmak ve basit bir Markdown çıktısıyla\n"
                "ön işleme maliyetini azaltmak için tasarlandı."
            )
            print("\nOpsiyonel bağımlılıklar: pdfminer.six, pypdf, colorama, pyfiglet, Poppler(pdftotext)")
            print("Filigran temizleme: sayfalar arası tekrar eden kısa satırları tespit edip kaldırmayı dener.")
            input("Geri dönmek için Enter...")

        elif choice == "6":
            print(f"{Fore.CYAN}Güle güle!{Style.RESET_ALL}")
            return 0

        else:
            print(f"{Fore.RED}Geçersiz seçim.{Style.RESET_ALL}")
            time.sleep(0.8)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nİptal edildi.")
        raise SystemExit(130)
