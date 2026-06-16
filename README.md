# Gestore Spese — Deploy su Render

## Struttura del progetto
```
gestore-spese/
├── app.py              ← server Flask (backend)
├── requirements.txt    ← dipendenze Python
├── render.yaml         ← configurazione Render
└── static/
    └── index.html      ← la tua app (adattata per il cloud)
```

## Come fare il deploy su Render (gratis, ~10 minuti)

### 1. Crea un account GitHub
Vai su https://github.com e registrati (gratis).

### 2. Crea un nuovo repository
- Clicca "New repository"
- Nome: `gestore-spese`
- Lascia tutto il resto di default → "Create repository"

### 3. Carica i file
Trascina tutti i file di questa cartella nel repository GitHub appena creato
(oppure usa il tasto "uploading an existing file").
Ricordati di caricare anche la cartella `static/` con `index.html` dentro.

### 4. Crea un account Render
Vai su https://render.com e registrati con il tuo account GitHub.

### 5. Crea il servizio web
- Dashboard Render → "New" → "Web Service"
- Collega il repository `gestore-spese`
- Render rileverà automaticamente `render.yaml`
- Clicca "Create Web Service"

### 6. Attendi il deploy (~2-3 minuti)
Render mostrerà i log di build. Quando vedi "==> Your service is live",
l'app è online all'indirizzo mostrato (es. `https://gestore-spese.onrender.com`).

### 7. Apri dal telefono
Vai all'URL sul telefono tuo e di tua moglie. I dati sono condivisi in tempo reale.

---

## Note importanti

**Piano gratuito Render:** il servizio "va in sleep" dopo 15 minuti di inattività.
La prima apertura del giorno impiega ~30 secondi per "svegliarsi". È normale.
Se vuoi evitarlo, usa il piano "Starter" a $7/mese.

**I dati:** sono salvati in un database SQLite sul disco di Render.
Con il piano gratuito il disco persiste tra i deploy (configurato in `render.yaml`).

**Sicurezza:** l'app è pubblica (chiunque abbia l'URL può vederla).
Se vuoi protezione con password, chiedimi e aggiungo un login semplice.
