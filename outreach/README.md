# Oliveti Ritrovati — Sistema Outreach B2B

Macchina commerciale per mappare e contattare ristoranti, enoteche, hotel, agriturismi e negozi gourmet.

## Setup (una volta sola)

```bash
cd outreach
uv pip install -r requirements.txt
uv run playwright install chromium
```

## Flusso

```
1. scraper.py       → contacts.csv    (Google Maps → lista target)
2. enrich_emails.py → contacts.csv    (aggiunge email dai siti web)
3. dashboard.py     → statistiche CRM
4. send_emails.py   → invia email     (Gmail SMTP)
   dashboard.py --export-wa → wa_messages.txt  (messaggi WA pronti)
```

## Step 1: Scraping

```bash
# Scrapa tutte le categorie predefinite (ristoranti, enoteche, hotel, agriturismi...)
uv run python scraper.py

# Solo una categoria specifica
uv run python scraper.py --query "enoteca" --area "Matera"

# Limitato a 20 risultati per categoria (test rapido)
uv run python scraper.py --limit 20
```

Output: `contacts.csv`

## Step 2: Arricchimento email

```bash
# Cerca l'email sul sito web di ogni contatto
uv run python enrich_emails.py

# Solo i primi 20 (test)
uv run python enrich_emails.py --limit 20
```

## Step 3: Dashboard

```bash
uv run python dashboard.py                          # statistiche generali
uv run python dashboard.py --tipo ristorante        # filtra per tipo
uv run python dashboard.py --stato email_inviata    # chi ha già ricevuto l'email
uv run python dashboard.py --export-wa              # genera wa_messages.txt
```

## Step 4: Invio email

Configura le credenziali Gmail (App Password, non la password normale):
```bash
# Google Account → Sicurezza → Verifica in 2 passaggi → Password per le app
export GMAIL_USER="olivetiritrovatimatera@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

```bash
uv run python send_emails.py --preview        # SEMPRE prima per vedere cosa verrà inviato
uv run python send_emails.py --limit 5        # invia a 5 (test reale)
uv run python send_emails.py                  # invia a tutti i nuovi con email
```

## Gestione stati (contacts.csv)

| stato | significato |
|-------|-------------|
| `nuovo` | non ancora contattato |
| `email_inviata` | email inviata, nessuna risposta ancora |
| `wa_inviato` | messaggio WhatsApp inviato |
| `risposto` | ha risposto — aggiornare a mano con note |
| `non_interessato` | ha declinato — non contattare più |

Aggiorna `stato` e `note` direttamente nel CSV (apri con Numbers/Excel).

## Templates

Personalizza i template in `templates/`:
- `email_ristorante.txt` — per ristoranti, osterie, agriturismi
- `email_enoteca.txt` — per enoteche, wine bar, hotel
- `whatsapp_ristorante.txt` — messaggio WA breve per ristoranti
- `whatsapp_hotel_bb.txt` — messaggio WA per hotel e B&B

Variabili disponibili: `{nome_ristorante}`, `{nome_enoteca}`, `{nome_contatto}`
