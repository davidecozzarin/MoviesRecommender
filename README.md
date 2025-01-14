Nel file requirements.txt sono elencate le dipendenze necessarie per il progetto, per installarle tutte basta lanciare:
pip install -r requirements.txt

Per lanciare il progetto lanciare da terminale:
streamlit run app.py

Usare Prefissi Standard:

feat: Per nuove funzionalità o aggiunte al codice.
    Esempio: feat: add user authentication with MongoDB
fix: Per risolvere bug.
    Esempio: fix: correct issue with movie selection list not updating
docs: Per modifiche alla documentazione.
    Esempio: docs: update README with setup instructions
refactor: Per modifiche che non aggiungono funzionalità ma migliorano il codice.
    Esempio: refactor: optimize database query for movie recommendations
style: Per cambiamenti estetici (ad esempio spaziature, nomi variabili).
    Esempio: style: fix indentation in app.py
test: Per aggiungere o correggere test.
    Esempio: test: add unit tests for authentication module


Il flusso corretto per lavorare con le pull request:
Lavora in un branch separato:

Quando inizi a lavorare su una nuova funzionalità o modifica, crea un nuovo branch:

git checkout -b nome-del-branch

Ad esempio:
git checkout -b feature-nuova-funzionalita

Dopo aver modificato i file:

git add .
git commit -m "Descrizione del commit"


Pusha il branch al repository remoto:
Spingi il tuo branch sul repository remoto:

git push origin nome-del-branch


Crea una pull request:

Dopo aver pushato, vai su GitHub.
GitHub ti suggerirà automaticamente di creare una pull request per il branch appena pushato.
Clicca su Compare & pull request.
Scrivi una descrizione chiara della modifica e invia la pull request.
Esegui i controlli sulla pull request:

Gli altri membri del team possono rivedere le modifiche, lasciare commenti e approvare la pull request.
I test CI configurati nella pipeline verranno eseguiti automaticamente sulla pull request.
Merge nel branch main:

Una volta approvata la pull request e passati i test, puoi fare il merge sul branch main direttamente da GitHub.
Se hai i permessi di amministratore, puoi eseguire il merge. Altrimenti, lo farà il reviewer.