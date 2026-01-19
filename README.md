# Movie Tracking Application

Ovaj projekt razvijen je u sklopu kolegija **Teorija baza podataka**.  
Radi se o mobilnoj Android aplikaciji koja korisnicima omogućuje:
- pregled filmova  
- označavanje filmova kao pogledanih  
- lajkanje filmova  
- praćenje i upravljanje prijateljima  

Aplikacija koristi **klijent–server arhitekturu**:
- **Frontend**: Android aplikacija (Kotlin, Android Studio)
- **Backend**: REST API (Python, Flask)

---

## Arhitektura sustava

- Android aplikacija komunicira s backendom putem **REST API-ja**
- Backend obrađuje zahtjeve, upravlja poslovnom logikom i pristupa bazama podataka
- Podaci se razmjenjuju u **JSON** formatu

---

## Backend – Flask REST API

### Korištene tehnologije
- Python 3
- Flask
- REST API
- JSON

---

### Preduvjeti
- **Python 3.9+**
- **pip**
- Preporučeno: virtualno okruženje (`venv`)

---

### Pokretanje backend servera

#### 1. Pozicioniranje u backend direktorij
```bash
cd backend
```

#### 2. Kreiranje virtualnog okruženja
```bash
python -m venv venv
```

#### 3. Aktivacija virtualnog okruženja Windows
```bash
venv\Scripts\activate
```

##### Linux / macOS
```bash
source venv/bin/activate
```
#### 4. Instalacija ovisnosti
```bash
pip install -r requirements.txt
```

#### 5. Pokretanje servera
```bash
python app.py
```
#### 6. Pokretanje servera
```bash
http://127.0.0.1:5000/
```


