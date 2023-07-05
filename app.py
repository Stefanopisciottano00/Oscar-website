from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
import pandas as pd
from io import BytesIO
from colorama import Fore

# Specifica le informazioni di connessione al tuo database MongoDB
# Sostituisci <mongodb-uri> con l'URI effettivo del tuo database
client = MongoClient('mongodb://localhost:27017')

# Seleziona il database desiderato
db = client['Oscar']

# Seleziona la collezione
collection = db['Film']

app = Flask(__name__)


def preprocess_films():

    # NEL DATABASE INIZIALE 65 FILM AVEVANO SOLO DUE CIFRE COME ANNO

    films = collection.find({'Year': {'$gt': 1, '$lt': 99}})
    count = 1

    for film in films:
        year = film['Year']

        if year == 21:
            year = '20' + str(year)  # Aggiungi "20" all'inizio
            year = int(year)
            print (film)


        else:
            year = '19' + str(year)  # Aggiungi "20" all'inizio
            year = int(year)

        # Aggiorna il documento del film nel database con il nuovo valore dell'attributo "Year"
        collection.update_one({'_id': film['_id']}, {'$set': {'Year': year}})

        count += 1  # Incrementa la variabile di conteggio

#FUNZIONE PER EFFETTUARE LE QUERY
def query_mongodb(testo):
    if testo is None:
        return []

    x = testo.split()

    if x[0] == 'Film':
        nome_film = ' '.join(x[2:])

        query = {x[0]: nome_film}
        result = collection.find(query)
        films = []

        for doc in result:
            film_info = ', '.join([f"{key}: {value}" for key, value in doc.items()])
            films.append(film_info)
        return films

    elif x[0] == 'Year' or x[0] == 'Award' or x[0] == 'Nomination':

        if (x[1] == '>') :
            year = int(x[2])
            query = {x[0]: {'$gt': year}}
            result = collection.find(query)
            films = []

            for doc in result:
                film_info = ', '.join([f"{key}: {value}" for key, value in doc.items()])
                films.append(film_info)

            return '\n'.join(films)

        elif(x[1] == '<') :
            year = int(x[2])
            query = {x[0]: {'$lt': year}}
            result = collection.find(query)
            films = []

            for doc in result:
                film_info = ', '.join([f"{key}: {value}" for key, value in doc.items()])
                films.append(film_info)

            return '\n'.join(films)

        else:
            year = int(x[2])
            query = {x[0] : year}
            result = collection.find(query)
            films = []

            for doc in result:
                film_info = ', '.join([f"{key}: {value}" for key, value in doc.items()])
                films.append(film_info)

            return '\n'.join(films)


def aggiungi_film():
    # Ottenere i dati dal form
    titolo = request.form.get('aggiungi_titolo')
    anno = request.form.get('aggiungi_anno')
    awards = request.form.get('aggiungi_awards')
    nomination = request.form.get('aggiungi_nomination')

    if not (titolo and anno and awards and nomination):
        return render_template('operazioni.html')

    anno = int(anno)
    awards = int(awards)
    nomination = int(nomination)

    if (anno < 1000 or anno > 9999):
        print("ciao")
        return render_template('operazioni.html', errorMessage="L'anno deve essere compreso tra 1000 e 9999.")

    return render_template('operazioni.html')
    # Dopo aver aggiunto il film al database, reindirizza l'utente a una pagina di conferma
    #return redirect(url_for('conferma_aggiunta_film'))

def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    return df

#PAGINA PRINCIPALE
@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'submitButton' in request.form:

            input_text = request.form.get('inputText')
            if not input_text:
                return render_template('index.html')

            result = query_mongodb(input_text)

            # Assegnare il risultato all'attributo 'value' dell'input text
            return render_template('index.html', outputText=result)

    return render_template('index.html')


#PAGINA DATABASE
@app.route('/database.html')
def loaddataset():
    csv_file_path = r'C:\Users\pisci\Desktop\bd\FLASK-MONGO\templates\oscar.csv'
    csv_data = read_csv_file(csv_file_path)
    return render_template('database.html', csv_data=csv_data)

@app.route('/richiesta_operazioni.html', methods=['GET', 'POST'])
def load_richiesta_operazioni():

    input = request.form.get('input_richiesta')

    if input==None :
        return render_template('richiesta_operazioni.html')

    if (input == "Aggiungere" or input == "aggiungere"):
        return redirect(url_for('load_aggiunta'))


    elif(input == "Eliminare" or input == "eliminare"):
        return redirect(url_for('load_cancellazione'))

    elif (input == "Modificare" or input == "modificare"):
        return redirect(url_for('load_modifica'))
    else:
        return render_template('richiesta_operazioni.html')


@app.route('/operazioni_aggiunta.html', methods=['GET', 'POST'])
def load_aggiunta():
        # Ottenere i dati dal form
        titolo = request.form.get('aggiungi_titolo')
        anno = request.form.get('aggiungi_anno')
        awards = request.form.get('aggiungi_awards')
        nomination = request.form.get('aggiungi_nomination')

        print(titolo)

        if not (titolo and anno and awards and nomination):
            return render_template('operazioni_aggiunta.html')

        anno = int(anno)
        awards = int(awards)
        nomination = int(nomination)

        if (anno < 1000 or anno > 9999):
            print("ciao")
            return render_template('operazioni_aggiunta.html', errorMessage="Errore, l'anno deve essere di quattro cifre")

        film = {
            'Film': titolo,
            'Year': anno,
            'Award': awards,
            'Nomination': nomination
        }

        result = collection.insert_one(film)

        # Verifica se l'inserimento è stato eseguito correttamente
        if result.acknowledged:
            return render_template('operazioni_aggiunta.html', errorMessage="Il film è stato aggiunto alla collezione!")
        else:
            return render_template('operazioni_aggiunta.html', errorMessage="Il film NON è stato aggiunto alla collezione!")



@app.route('/operazioni_cancellazione.html', methods=['GET', 'POST'])
def load_cancellazione():
    # Ottenere i dati dal form
    titolo = request.form.get('elimina_titolo')

    print(titolo)
    if not (titolo):
        return render_template('operazioni_cancellazione.html')
    else:
        print(titolo)

    # Criterio di ricerca per l'eliminazione
    criterio = {'Film': titolo}

    # Eliminazione del documento dalla collezione
    result = collection.delete_one(criterio)

    # Verifica se l'eliminazione è stata eseguita correttamente
    if result.deleted_count > 0:
        return render_template('operazioni_cancellazione.html', errorMessageDelete="Il film è stato eliminato alla collezione!")
    else:
        return render_template('operazioni_cancellazione.html', errorMessageDelete="Il film non è stato eliminato dalla collezione!")


@app.route('/operazioni_modifica.html', methods=['GET', 'POST'])
def load_modifica():
    # Ottenere i dati dal form
    titolo = request.form.get('titolo_modifica')

    campo_da_modificare = request.form.get('campo_modifica')

    nuovo_valore = request.form.get('nuovo_valore_modifica')

    if campo_da_modificare == 'Film':

        query = {campo_da_modificare: titolo}

        aggiornamento = {'$set': {'Film': nuovo_valore}}

        print(aggiornamento)

        risultato = collection.update_one(query, aggiornamento)

        if risultato.modified_count > 0:
            return render_template('operazioni_modifica.html', modMessage = "modifica avvenuta con successo")

        else:
            return render_template('operazioni_modifica.html', modMessage = "errore, modifica non avvenuta")


    elif campo_da_modificare == 'Year' :

        nuovo_valore = int(nuovo_valore)

        if ( (nuovo_valore > 999) and (nuovo_valore < 10000) ):

            query = {'Film': titolo}
            aggiornamento = {'$set': {'Year': nuovo_valore}}

            risultato = collection.update_one(query, aggiornamento)

            if risultato.modified_count > 0:
                return render_template('operazioni_modifica.html', modMessage = "modifica avvenuta con successo")
            else:
                return render_template('operazioni_modifica.html', modMessage = "errore, modifica non avvenuta")

        else:
            return render_template('operazioni_modifica.html', modMessage="errore, l'anno deve essere di quattro cifre")


    elif campo_da_modificare == 'Award':

        nuovo_valore = int(nuovo_valore)

        if (nuovo_valore < 100):

            query = {'Film': titolo}
            aggiornamento = {'$set': {'Award': nuovo_valore}}

            risultato = collection.update_one(query, aggiornamento)

            if risultato.modified_count > 0:
                return render_template('operazioni_modifica.html', modMessage="modifica avvenuta con successo")
            else:
                return render_template('operazioni_modifica.html', modMessage="errore, modifica non avvenuta")

        else:
            return render_template('operazioni_modifica.html', modMessage="errore, il numero di award deve essere minore di 100")



    elif campo_da_modificare == 'Nomination':

        nuovo_valore = int(nuovo_valore)

        if (nuovo_valore < 100):

            query = {'Film': titolo}
            aggiornamento = {'$set': {'Nomination': nuovo_valore}}

            risultato = collection.update_one(query, aggiornamento)

            if risultato.modified_count > 0:
                return render_template('operazioni_modifica.html', modMessage="modifica avvenuta con successo")
            else:
                return render_template('operazioni_modifica.html', modMessage="errore, modifica non avvenuta")

        else:
            return render_template('operazioni_modifica.html', modMessage="errore, il numero di award deve essere minore di 100")

    return render_template('operazioni_modifica.html')


#PAGINA STATISTICHE
@app.route('/statistiche.html')
def loadstats():

    pipeline = [{'$group': {'_id': '$Award', 'count': {'$sum': 1}}}, {'$sort': {'_id': 1}}]

    result = collection.aggregate(pipeline)

    # Prepara i dati per il grafico
    labels = []
    values = []
    for item in result:
        labels.append(item['_id'])
        values.append(item['count'])

    labels = [str(label) for label in labels]

    # Passa i dati al template HTML e visualizza la pagina del grafico
    return render_template('statistiche.html', labels=labels, values=values)


@app.route('/statistiche2.html')
def loadstats2():

    pipeline = [{'$group': {'_id': '$Nomination', 'count': {'$sum': 1}}}, {'$sort': {'_id': 1}}]

    result = collection.aggregate(pipeline)

    # Prepara i dati per il grafico
    labels = []
    values = []
    for item in result:
        labels.append(item['_id'])
        values.append(item['count'])

    labels = [str(label) for label in labels]

    # Passa i dati al template HTML e visualizza la pagina del grafico
    return render_template('statistiche2.html', labels=labels, values=values)

@app.route('/statistiche3.html')
def loadstats3():

    pipeline = [{'$group': {'_id': '$Year', 'count': {'$sum': 1}}}, {'$sort': {'_id': 1}}]

    result = collection.aggregate(pipeline)

    # Prepara i dati per il grafico
    labels = []
    values = []
    for item in result:
        labels.append(item['_id'])
        values.append(item['count'])

    labels = [str(label) for label in labels]

    # Passa i dati al template HTML e visualizza la pagina del grafico
    return render_template('statistiche3.html', labels=labels, values=values)


#Qui dovrebbe essere fatto il preprocessing
if __name__ == '__main__':
    preprocess_films()  # Esegui il preprocessing dei film
    app.run()
