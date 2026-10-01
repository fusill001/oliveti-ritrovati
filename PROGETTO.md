# PROGETTO BIBBIA — OLIVETI RITROVATI

> File di riferimento permanente. Leggi questo prima di toccare qualsiasi cosa.

---

## BRAND

**Nome corretto:** OLIVETI RITROVATI (plurale, sempre così — mai "OLIVETO RITROVATO")  
**Forma breve:** OLIVETI RITROVATI  
**Tagline:** L'olio ritrovato di Matera  
**Sito live:** https://oliveti-ritrovati.vercel.app  
**Instagram:** @percorsiritrovatimatera  
**Email:** olivetiritrovatimatera@gmail.com  
**WhatsApp ordini:** +39 339 379 2491 → `https://wa.me/393393792491`

---

## IL PROGETTO

Società Cooperativa OLIVETI RITROVATI — costola della Comunità Slow Food OLIVETI RITROVATI DEL MATERANO.

**Fondatore:** Prof. Francesco Linzalone — agronomo, ex professore, ex fiduciario Slow Food Matera, ex coordinatore regionale guide Osterie d'Italia ed Extravergini. Famiglia con frantoio storico in Via Casalnuovo (Sassi di Matera) dal 1959.

**Missione:** salvare ~3000 olivi centenari abbandonati nella campagna materana. Comodato d'uso con i proprietari, cura colturale, produzione dell'OLIO RITROVATO.

**Varietà:** Tarantina (amara, polifferolica, matura a metà novembre) + Ghiannara/Gnannara (delicata, precoce, matura ottobre).

**Metodo:** 0 fertilizzanti chimici, 0 fitofarmaci, potatura a Vaso Policonico, trinciatura residui, molitura entro 8 ore dalla raccolta.

**Premio:** Marzo 2023 → OLIO LUCANO D'ECCELLENZA (manifestazione OLIVARUM, Regione Basilicata).

**Anno 2026:** Prima produzione olio monovarietale TARANTINA — prima volta nella storia che Matera produce un olio varietale certificato.

---

## PRODOTTO & PREZZI

- **Bottiglia 500ml:** €10
- Produzione 2022: 250L in bottiglie (≈500 bottiglie), 350L in lattine
- Entrate stimate: ~€6.000
- Quantità limitata ogni anno

---

## STACK TECNICO

```
Tipo:           Static HTML — NESSUN framework
Deploy:         Vercel (outputDirectory: "public")
File principale: public/index.html
Animazioni:     GSAP 3.12.5 + ScrollTrigger (cdnjs CDN)
Font:           Cinzel (titoli) + EB Garamond (corpo) — Google Fonts
Deploy cmd:     cd workspaces/oliveti-ritrovati && vercel --prod
```

### vercel.json
```json
{ "outputDirectory": "public", "rewrites": [{"source": "/(.*)", "destination": "/index.html"}] }
```

---

## LINEA GRAFICA

### Palette colori (valori reali nel CSS)

```css
--nero:    #232323   /* sfondo principale — scelto dal cliente */
--oro:     #C4A84A   /* accent primario — bottoni, cerchi, dettagli */
--tufo:    #9A9590   /* testo secondario, caption */
--bianco:  #d9d9d9   /* testo principale — scelto dal cliente */
--bianco2: #f0ece4   /* testo alternativo su sfondo chiaro */

/* Alias HT (non modificare) */
--brown:      #232323
--primary:    #C4A84A
--dark-brown: #232323
```

**Logica d'uso:**
- Sfondo → `--nero` su tutte le sezioni (angle, unwrap, inside_sides, footer)
- Testo corrente → `--bianco`
- Caption/label → `--tufo`
- CTA/pulsanti/accent → `--oro` su sfondo `--nero`, testo `--nero` su sfondo `--oro`
- Sezione traditions → sfondo `--oro`, testo `--nero`

### Tipografia

```
Salmond        — display, titoli h1/h2/h3, logo wordmark
               weights: 500 (medium), 700 (bold)
               file: fonts/Salmond-Bold.woff2, fonts/Salmond-Medium.woff2

GraphikX       — corpo testo, UI, navigazione
               weight: 500 (medium)
               file: fonts/GraphikX-Medium.otf

fallback stack: Salmond → 'Georgia', serif
                GraphikX → 'Inter', sans-serif
```

**Logica d'uso:**
- Tutti i `.h1 .h2 .h3 .like_h1 .h2_middle .footer_txt` → Salmond
- Tutto il resto (`.base_txt`, nav, bottoni, caption) → GraphikX
- Logo wordmark: "OLIVETI / RITROVATI" Salmond 700, 13px, tracking 2.5px, uppercase
- Tagline logo: "MATERA · BASILICATA" Salmond 500, 6.5px, tracking 3px, colore `--oro`

### Logo

**NON creare loghi — usare sempre e solo il file SVG ufficiale caricato dal cliente.**

```
File ufficiale: public/images/ring-mark.svg
Sorgente:       /Users/emanuelebruno/Desktop/Desktop/SynologyDrive/OLIVETI RITROVATI/loghi/coop oliveti ritrovati.svg
Fill attuale:   #C4A84A (modificato da #B89A3E con sed)
```

Nel sito il logo è composto da:
- `<img src="images/ring-mark.svg">` — il mark SVG ufficiale
- Due div `.h2` con testo "OLIVETI" / "RITROVATI" in Salmond
- Una riga tagline "MATERA · BASILICATA" in Salmond oro

---

## REFERENCE DESIGN: Hungry Tiger

File locale: `/Users/emanuelebruno/Downloads/sito-scaricato/www.eathungrytiger.com/index.html`

Pattern CSS chiave da replicare IDENTICI (solo colori/font adattati):
- `.jar_motion` — bottiglia centrata e fissa, 100vw x 100dvh
- `.background_hero` — background fisso per parallax su scroll
- `.like_h1` — titolo hero 5-7em, Cinzel 900, line-height .9, uppercase, tracking tight
- `.h-link` — nav pill, border-radius 100em, background oro, padding px
- `.traditions` — sezione sfondo oro (#B89A3E per noi), testo scuro
- `.breakdown_grid` — griglia 4 colonne borderate per dettagli prodotto
- `grain_texture` — overlay grana film, mix-blend-mode:overlay, opacity .04
- `.wrapper_hero` — position:relative z-index:1 per scrollare sopra la bottiglia

---

## FOTO DISPONIBILI (public/images/)

| File | Contenuto |
|------|-----------|
| `bottiglia.png` | Bottiglia matte nera su sfondo nero — usa mix-blend-mode:lighten |
| `hero-oliveto.jpg` | Panoramica oliveto con Matera sullo sfondo |
| `masseria.jpg` | Masseria con arco in tufo |
| `ulivi.jpg` | Close-up radici ulivi centenari |
| `prof-linzalone.jpg` | **RITRATTO Prof. Linzalone** (occhiali rotondi, camicia, sfondo olivi — perfetto per sezione "Chi siamo") |
| `oliveto-panorama.jpg` | Panoramica oliveti con Matera in lontananza |
| `oliveti-centenari.jpg` | Campo verde con ulivi centenari solitari |
| `tour-oliveto.jpg` | Gruppo in visita guidata negli oliveti (Prof. che indica albero) |
| `masseria-interno.jpg` | Interno masseria in tufo, volta a botte — Prof. che racconta |
| `cappella-rupestre.jpg` | Cappella rupestre con affresco e arco |
| `frantoio-antico.jpg` | Interno frantoio rupestre con volta in tufo |

---

## VIDEO DRONE

Percorso: `/Users/emanuelebruno/Desktop/Desktop/SynologyDrive/PERCORSI RITROVATI/video drone/`
- DJI_0228.MP4, DJI_0201.MP4, DJI_0020.MP4, DJI_0195.MP4, DJI_0293.MP4

⚠️ File > 50MB: NON caricare su Vercel direttamente. Opzioni:
1. Comprimere con ffmpeg a < 50MB e caricare
2. YouTube unlisted + embed
3. Cloudflare Stream

---

## STRUTTURA SITO (sezioni in ordine)

1. **Header** — logo mark + wordmark + nav pills (Lo Shop, La Storia, Contatti)
2. **Hero/Bottiglia** — jar_motion, bottiglia centrata fissa, titolo hero "L'OLIO / RITROVATO / DI MATERA"
3. **Intro fullbleed** — foto panoramica oliveto, testo su sfondo
4. **Storia del Territorio** — testo narrativo, immagine masseria
5. **Tradizione & Metodo** — sezione oro (traditions), 4 step numerati
6. **Il Prodotto** — breakdown_grid, prezzo €10, CTA WhatsApp
7. **Il Professore** — ritratto Prof. Linzalone + bio breve
8. **Premi** — badge OLIVARUM 2023 + Slow Food
9. **Galleria** — grid foto Marco Vitale
10. **Abbinamenti** — cards con suggerimenti culinari
11. **Acquista** — sezione urgency, bottiglia limitata, CTA WhatsApp grande
12. **Footer** — Instagram + email + copyright

---

## DOCUMENTI SORGENTE

- Curriculum: `/Users/emanuelebruno/Desktop/Desktop/SynologyDrive/OLIVETI RITROVATI/CURRICULUM OLIVETI RITROVATI.docx`
- Storia prof: `/Users/emanuelebruno/Downloads/sito_prof/LA STORIA.docx`
- Varietà olio: `/Users/emanuelebruno/Downloads/sito_prof/OLIVETI RITROVATI.docx`
- Matera città dell'olio: `/Users/emanuelebruno/Downloads/sito_prof/Matera città dell'olio.docx`

---

## LOGHI UFFICIALI

- SVG: `/Users/emanuelebruno/Desktop/Desktop/SynologyDrive/OLIVETI RITROVATI/loghi/coop oliveti ritrovati.svg`
- File mark: `brand/logo/olive_tree_mark_CANVA_recolorable.svg` (6 ring paths, viewBox 0 0 1254 1254)
