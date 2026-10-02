"""
Invia email B2B da contacts.csv usando Gmail SMTP.

Uso:
    uv run python send_emails.py --preview         # mostra cosa verrebbe inviato, non invia
    uv run python send_emails.py --limit 5         # invia le prime 5 (test)
    uv run python send_emails.py                   # invia a tutti i "nuovo" con email

Config (una volta sola):
    export GMAIL_USER="olivetiritrovatimatera@gmail.com"
    export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"   # Google App Password (non la password normale)

Per generare App Password:
    Google Account → Sicurezza → Verifica in 2 passaggi → Password per le app
"""

import argparse
import csv
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from string import Template

CSV_PATH = Path(__file__).parent / "contacts.csv"
TEMPLATES_DIR = Path(__file__).parent / "templates"

GMAIL_USER = os.environ.get("GMAIL_USER", "olivetiritrovatimatera@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

# Mappa tipo contatto → template email
TIPO_TEMPLATE = {
    "ristorante": "email_ristorante.txt",
    "osteria": "email_ristorante.txt",
    "trattoria": "email_ristorante.txt",
    "enoteca": "email_enoteca.txt",
    "wine bar": "email_enoteca.txt",
    "agriturismo": "email_ristorante.txt",
    "hotel": "email_enoteca.txt",
    "b&b": "email_enoteca.txt",
}
DEFAULT_TEMPLATE = "email_ristorante.txt"


def load_template(tipo: str) -> tuple[str, str]:
    """Ritorna (subject, body) del template giusto per il tipo."""
    tipo_lower = tipo.lower()
    tpl_file = DEFAULT_TEMPLATE
    for k, v in TIPO_TEMPLATE.items():
        if k in tipo_lower:
            tpl_file = v
            break
    path = TEMPLATES_DIR / tpl_file
    content = path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    subject = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("OGGETTO:"):
            subject = line.replace("OGGETTO:", "").strip()
            body_start = i + 2  # salta riga vuota e ---
            break
    body = "\n".join(lines[body_start:]).strip()
    return subject, body


def fill_template(text: str, row: dict) -> str:
    return (text
            .replace("{nome_ristorante}", row["nome"])
            .replace("{nome_enoteca}", row["nome"])
            .replace("{nome_hotel}", row["nome"])
            .replace("{nome_contatto}", "Gentilissimi")  # default generico
            )


def send_email(smtp: smtplib.SMTP_SSL, to: str, subject: str, body: str, preview: bool):
    if preview:
        print(f"\n--- PREVIEW → {to} ---")
        print(f"OGGETTO: {subject}")
        print(body[:300] + "...")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject
    # Testo plain (rispettoso delle caselle, non finisce in spam)
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        smtp.sendmail(GMAIL_USER, to, msg.as_string())
        return True
    except Exception as e:
        print(f"    ✗ Errore invio a {to}: {e}")
        return False


def update_status(rows: list[dict], nome: str, email: str, new_status: str):
    for r in rows:
        if r["nome"] == nome and r["email"] == email:
            r["stato"] = new_status
            break


def save_csv(rows: list[dict]):
    if not rows:
        return
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Mostra senza inviare")
    parser.add_argument("--limit", type=int, default=0, help="Max email da inviare (0 = tutte)")
    parser.add_argument("--delay", type=float, default=3.0, help="Secondi tra un invio e l'altro")
    args = parser.parse_args()

    if not CSV_PATH.exists():
        print("contacts.csv non trovato.")
        return

    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    targets = [r for r in rows if r.get("email") and r.get("stato") == "nuovo"]
    if args.limit:
        targets = targets[:args.limit]

    if not targets:
        print("Nessun contatto da contattare (stato=nuovo + email presente).")
        return

    print(f"{'PREVIEW' if args.preview else 'INVIO'} email a {len(targets)} contatti...")

    if not args.preview and not GMAIL_APP_PASSWORD:
        print("⚠ GMAIL_APP_PASSWORD non impostato. Esporta la variabile d'ambiente e riprova.")
        return

    smtp = None
    if not args.preview:
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)

    sent = 0
    for row in targets:
        subject_tpl, body_tpl = load_template(row.get("tipo", ""))
        subject = fill_template(subject_tpl, row)
        body = fill_template(body_tpl, row)

        ok = send_email(smtp, row["email"], subject, body, args.preview)
        if ok and not args.preview:
            update_status(rows, row["nome"], row["email"], "email_inviata")
            sent += 1
            print(f"  ✓ [{sent}] {row['nome'][:40]} → {row['email']}")
            time.sleep(args.delay)

    if smtp:
        smtp.quit()

    if not args.preview:
        save_csv(rows)
        print(f"\n✅ {sent} email inviate. Stato aggiornato in contacts.csv")


if __name__ == "__main__":
    main()
