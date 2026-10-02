"""
Dashboard CRM minimale — statistiche e lista contatti da contacts.csv.

Uso:
    uv run python dashboard.py              # panoramica
    uv run python dashboard.py --tipo enoteca
    uv run python dashboard.py --stato risposto
    uv run python dashboard.py --export-wa  # genera messaggi WA pronti da copiare
"""

import argparse
import csv
from collections import Counter
from pathlib import Path

CSV_PATH = Path(__file__).parent / "contacts.csv"
TEMPLATES_DIR = Path(__file__).parent / "templates"


def load() -> list[dict]:
    if not CSV_PATH.exists():
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def print_stats(rows: list[dict]):
    total = len(rows)
    stati = Counter(r["stato"] for r in rows)
    tipi = Counter(r["tipo"].split(",")[0].strip().lower() for r in rows)
    with_email = sum(1 for r in rows if r.get("email"))
    with_phone = sum(1 for r in rows if r.get("telefono"))

    print(f"\n{'='*50}")
    print(f"  OLIVETI RITROVATI — CRM Outreach")
    print(f"{'='*50}")
    print(f"  Totale contatti:   {total}")
    print(f"  Con email:         {with_email}")
    print(f"  Con telefono:      {with_phone}")
    print(f"\n  Stato:")
    for stato, n in sorted(stati.items(), key=lambda x: -x[1]):
        bar = "█" * min(n, 30)
        print(f"    {stato:<20} {n:>4}  {bar}")
    print(f"\n  Top 10 tipi:")
    for tipo, n in tipi.most_common(10):
        print(f"    {tipo:<25} {n:>4}")
    print(f"{'='*50}\n")


def print_list(rows: list[dict], filtro_tipo: str = "", filtro_stato: str = ""):
    filtered = rows
    if filtro_tipo:
        filtered = [r for r in filtered if filtro_tipo.lower() in r.get("tipo", "").lower()]
    if filtro_stato:
        filtered = [r for r in filtered if r.get("stato", "") == filtro_stato]

    print(f"\n{len(filtered)} contatti:\n")
    for r in filtered:
        email = r.get("email") or "—"
        tel = r.get("telefono") or "—"
        print(f"  {r['nome'][:35]:<35} {r['tipo'][:20]:<20} {r['stato']:<15} {email[:30]:<30} {tel}")


def export_wa(rows: list[dict]):
    """Genera file WA con messaggi pronti per i contatti con telefono, stato=nuovo."""
    targets = [r for r in rows if r.get("telefono") and r.get("stato") == "nuovo"]
    if not targets:
        print("Nessun contatto con telefono e stato=nuovo.")
        return

    wa_file = Path(__file__).parent / "wa_messages.txt"
    tpl_ristorante = (TEMPLATES_DIR / "whatsapp_ristorante.txt").read_text(encoding="utf-8").strip()
    tpl_hotel = (TEMPLATES_DIR / "whatsapp_hotel_bb.txt").read_text(encoding="utf-8").strip()

    with open(wa_file, "w", encoding="utf-8") as f:
        for r in targets:
            tipo = r.get("tipo", "").lower()
            tpl = tpl_hotel if any(x in tipo for x in ["hotel", "b&b", "albergo"]) else tpl_ristorante
            tel = r["telefono"].replace(" ", "").replace("-", "")
            if not tel.startswith("+"):
                tel = "+39" + tel.lstrip("0")
            f.write(f"=== {r['nome']} | {tel} ===\n")
            f.write(tpl + "\n\n")
            f.write(f"Link WA: https://wa.me/{tel.lstrip('+')}?text={__import__('urllib.parse', fromlist=['quote']).quote(tpl)}\n")
            f.write("\n" + "-"*60 + "\n\n")

    print(f"✅ {len(targets)} messaggi WA → {wa_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", default="", help="Filtra per tipo (es. ristorante)")
    parser.add_argument("--stato", default="", help="Filtra per stato (es. risposto)")
    parser.add_argument("--export-wa", action="store_true", help="Genera wa_messages.txt")
    args = parser.parse_args()

    rows = load()
    if not rows:
        print("contacts.csv vuoto o non trovato. Esegui scraper.py prima.")
        return

    print_stats(rows)

    if args.tipo or args.stato:
        print_list(rows, args.tipo, args.stato)
    elif args.export_wa:
        export_wa(rows)


if __name__ == "__main__":
    main()
