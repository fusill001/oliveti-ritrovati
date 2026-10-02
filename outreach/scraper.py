"""
Scraper Google Maps per target B2B Oliveti Ritrovati.
Cerca ristoranti, enoteche, agriturismi, hotel, negozi gourmet a Matera e dintorni.

Uso:
    uv run python scraper.py
    uv run python scraper.py --query "agriturismo" --area "Matera"
    uv run python scraper.py --limit 200

Output: contacts.csv (aggiunto ai contatti esistenti, no duplicati)

Dipendenze: playwright (uv run playwright install chromium la prima volta)
"""

import argparse
import csv
import re
import time
import json
import os
from pathlib import Path
from urllib.parse import quote

OUTPUT_CSV = Path(__file__).parent / "contacts.csv"

FIELDNAMES = [
    "nome", "tipo", "indirizzo", "citta", "telefono", "sito_web",
    "email", "rating", "num_recensioni", "google_maps_url",
    "stato",          # nuovo | email_inviata | wa_inviato | risposto | non_interessato
    "note",
    "data_aggiunta",
]

SEARCHES = [
    ("ristorante", "Matera"),
    ("osteria", "Matera"),
    ("trattoria", "Matera"),
    ("enoteca", "Matera"),
    ("wine bar", "Matera"),
    ("agriturismo", "Matera"),
    ("agriturismo", "Provincia di Matera"),
    ("hotel", "Matera"),
    ("b&b", "Matera"),
    ("gastronomia", "Matera"),
    ("negozio alimentari gourmet", "Matera"),
    ("supermercato", "Matera"),
    ("ristorante", "Metaponto"),
    ("ristorante", "Pisticci"),
    ("ristorante", "Bernalda"),
    ("ristorante", "Policoro"),
]


def load_existing(path: Path) -> set:
    """Ritorna set di (nome, telefono) già in contacts.csv."""
    existing = set()
    if not path.exists():
        return existing
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            existing.add((row["nome"].strip().lower(), row["telefono"].strip()))
    return existing


def append_contacts(path: Path, contacts: list[dict]):
    is_new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        if is_new:
            w.writeheader()
        w.writerows(contacts)


def scrape_query(page, query: str, area: str, existing: set, limit: int) -> list[dict]:
    """Scrapa Google Maps per una singola query+area."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeout

    url = f"https://www.google.com/maps/search/{quote(query + ' ' + area)}"
    print(f"  → {query} | {area}")
    page.goto(url, wait_until="networkidle", timeout=30_000)
    time.sleep(2)

    results = []
    seen_in_run = set()

    # Scorri la sidebar per caricare più risultati
    sidebar_sel = '[role="feed"]'
    try:
        page.wait_for_selector(sidebar_sel, timeout=8_000)
    except PlaywrightTimeout:
        print("    ⚠ sidebar non trovata, salto")
        return []

    for _ in range(20):
        page.eval_on_selector(sidebar_sel, "el => el.scrollBy(0, 800)")
        time.sleep(1.2)
        items = page.query_selector_all('a[href*="/maps/place/"]')
        if len(items) >= limit:
            break

    items = page.query_selector_all('a[href*="/maps/place/"]')

    for item in items[:limit]:
        try:
            href = item.get_attribute("href") or ""
            name_el = item.query_selector("div.fontHeadlineSmall, .qBF1Pd")
            if not name_el:
                continue
            name = name_el.inner_text().strip()
            if not name:
                continue

            # rating e recensioni
            rating_el = item.query_selector("span.MW4etd")
            rating = rating_el.inner_text().strip() if rating_el else ""
            reviews_el = item.query_selector("span.UY7F9")
            reviews = reviews_el.inner_text().strip().strip("()").replace(".", "") if reviews_el else ""

            # tipo / categoria
            cat_el = item.query_selector(".W4Efsd:nth-child(2) > .W4Efsd span:first-child")
            tipo = cat_el.inner_text().strip() if cat_el else query

            key = (name.lower(), "")
            if key in existing or key in seen_in_run:
                continue
            seen_in_run.add(key)

            from datetime import date
            results.append({
                "nome": name,
                "tipo": tipo or query,
                "indirizzo": "",
                "citta": area,
                "telefono": "",
                "sito_web": "",
                "email": "",
                "rating": rating,
                "num_recensioni": reviews,
                "google_maps_url": href,
                "stato": "nuovo",
                "note": "",
                "data_aggiunta": date.today().isoformat(),
            })
        except Exception:
            continue

    print(f"    ✓ {len(results)} nuovi risultati")
    return results


def enrich_details(page, contact: dict) -> dict:
    """
    Apre la pagina Google Maps del posto e recupera telefono + sito web.
    Chiamato su contatti con telefono vuoto.
    """
    from playwright.sync_api import TimeoutError as PlaywrightTimeout

    if not contact.get("google_maps_url"):
        return contact
    try:
        page.goto(contact["google_maps_url"], wait_until="networkidle", timeout=25_000)
        time.sleep(1.5)

        # Telefono
        tel_el = page.query_selector('button[data-item-id*="phone"] .Io6YTe')
        if not tel_el:
            tel_el = page.query_selector('a[href^="tel:"]')
        if tel_el:
            contact["telefono"] = tel_el.inner_text().strip()

        # Sito web
        web_el = page.query_selector('a[data-item-id="authority"] .Io6YTe')
        if not web_el:
            web_el = page.query_selector('a[href^="http"]:not([href*="google"])')
        if web_el:
            contact["sito_web"] = web_el.get_attribute("href") or web_el.inner_text().strip()

        # Indirizzo
        addr_el = page.query_selector('button[data-item-id*="address"] .Io6YTe')
        if addr_el:
            contact["indirizzo"] = addr_el.inner_text().strip()

    except (PlaywrightTimeout, Exception):
        pass
    return contact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Query singola (sovrascrive SEARCHES predefinite)")
    parser.add_argument("--area", default="Matera")
    parser.add_argument("--limit", type=int, default=50, help="Max risultati per query")
    parser.add_argument("--enrich", action="store_true", default=True,
                        help="Apri ogni risultato per recuperare telefono/sito (più lento)")
    parser.add_argument("--no-enrich", dest="enrich", action="store_false")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    existing = load_existing(OUTPUT_CSV)
    searches = [(args.query, args.area)] if args.query else SEARCHES
    all_new = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            locale="it-IT",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = ctx.new_page()

        # Accetta cookie Google se appare
        page.goto("https://www.google.com/maps", wait_until="networkidle", timeout=20_000)
        try:
            page.click('button:has-text("Accetta tutto")', timeout=4_000)
        except Exception:
            pass

        for query, area in searches:
            new_contacts = scrape_query(page, query, area, existing, args.limit)

            if args.enrich and new_contacts:
                print(f"    Arricchimento dettagli ({len(new_contacts)} posti)...")
                for i, c in enumerate(new_contacts):
                    new_contacts[i] = enrich_details(page, c)
                    time.sleep(0.8)

            all_new.extend(new_contacts)
            # Aggiorna existing per evitare duplicati tra query diverse
            for c in new_contacts:
                existing.add((c["nome"].lower(), c["telefono"]))

        browser.close()

    if all_new:
        append_contacts(OUTPUT_CSV, all_new)
        print(f"\n✅ {len(all_new)} nuovi contatti aggiunti → {OUTPUT_CSV}")
    else:
        print("\nNessun nuovo contatto trovato.")


if __name__ == "__main__":
    main()
