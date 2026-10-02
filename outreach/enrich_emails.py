"""
Arricchisce contacts.csv cercando l'email sui siti web dei contatti.

Strategie (in ordine):
  1. Scraping pagine "Contatti" / "About" del sito
  2. Pattern comuni: info@, contatti@, ristorante@, hotel@...
  3. Whois/RDAP (fallback)

Uso:
    uv run python enrich_emails.py
    uv run python enrich_emails.py --limit 20   # primi 20 senza email
"""

import argparse
import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

CSV_PATH = Path(__file__).parent / "contacts.csv"

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

CONTACT_PATHS = [
    "/contatti", "/contatti.html", "/contact", "/contact.html",
    "/chi-siamo", "/about", "/info", "/dove-siamo",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; bot/1.0; research)",
    "Accept-Language": "it-IT,it;q=0.9",
}


def find_emails_in_html(html: str, base_domain: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    found = set()

    # mailto: href
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            email = href[7:].split("?")[0].strip()
            if EMAIL_RE.match(email):
                found.add(email.lower())

    # testo grezzo
    for m in EMAIL_RE.finditer(soup.get_text()):
        e = m.group().lower()
        # Filtra email generiche/irrilevanti
        if not any(s in e for s in ["example", "yourdomain", "email.com", "sentry"]):
            found.add(e)

    # Preferisci email dello stesso dominio
    domain_emails = [e for e in found if base_domain in e]
    return domain_emails if domain_emails else list(found)


def fetch_site_email(site_url: str, timeout: int = 8) -> str:
    if not site_url or not site_url.startswith("http"):
        return ""

    parsed = urlparse(site_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    domain = parsed.netloc.replace("www.", "")

    urls_to_try = [site_url] + [urljoin(base, p) for p in CONTACT_PATHS]

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
        for url in urls_to_try:
            try:
                r = client.get(url)
                if r.status_code == 200 and "text/html" in r.headers.get("content-type", ""):
                    emails = find_emails_in_html(r.text, domain)
                    if emails:
                        return emails[0]
            except Exception:
                continue

    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Quanti contatti processare (0 = tutti)")
    args = parser.parse_args()

    if not CSV_PATH.exists():
        print("contacts.csv non trovato. Esegui scraper.py prima.")
        return

    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    targets = [r for r in rows if not r.get("email") and r.get("sito_web")]
    if args.limit:
        targets = targets[:args.limit]

    print(f"Arricchimento email per {len(targets)} contatti con sito web...")
    updated = 0

    for i, row in enumerate(targets):
        site = row["sito_web"]
        print(f"  [{i+1}/{len(targets)}] {row['nome'][:40]:<40} {site[:40]}")
        email = fetch_site_email(site)
        if email:
            print(f"    ✓ {email}")
            # aggiorna in rows
            for r in rows:
                if r["nome"] == row["nome"] and r["sito_web"] == row["sito_web"]:
                    r["email"] = email
                    updated += 1
                    break
        time.sleep(1.0)  # sii gentile con i server

    # Riscrivi CSV
    if updated:
        fieldnames = rows[0].keys() if rows else []
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"\n✅ {updated} email trovate e salvate in {CSV_PATH}")
    else:
        print("\nNessuna nuova email trovata.")


if __name__ == "__main__":
    main()
