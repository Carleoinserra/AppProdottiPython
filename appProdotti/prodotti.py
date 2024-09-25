import numpy as np
import pandas as pd
from flask import Flask, render_template, request, make_response
import mysql.connector
from matplotlib import pyplot as plt
from stripe._http_client import requests
from translate import Translator
import io
from flask import Flask, request, redirect, url_for, session

class prodotto:
    def __init__(self, nome, marca, prezzo, url,pezzi,  prodottiV):
        self.nome = nome
        self.marca = marca
        self.prezzo = prezzo
        self.url = url
        self.pezzi = pezzi
        self.prodottiV = prodottiV

class prodottiV:
    def __init__(self, nome, marca, prezzo, url):
        self.nome = nome
        self.marca = marca
        self.prezzo = prezzo
        self.url = url


    def setPezzi(self, pezziV):
        self.pezziV = pezziV


    def getPezzi(self):
        return self.pezziV

# Variabili username e password predefinite
USERNAME = "admin"
PASSWORD = "password"



app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Usato per firmare la sessione

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="PyDb"
)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica le credenziali dell'utente
        if username == USERNAME and password == PASSWORD:
            session['user'] = username  # Memorizza l'utente nella sessione
            return redirect(url_for('gestore'))  # Reindirizza all'area protetta
        else:
            return "Credenziali non valide"

    return render_template("login.html")




# Rotta accessibile solo dopo l'autenticazione
@app.route('/gestore')
def gestore():
    if 'user' in session:
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM prodotti")

        myresult = mycursor.fetchall()
        listaD = []
        for i in myresult:
            listaD.append(i[2])

        listaS = list(dict.fromkeys(listaD))
        print(listaS)
        import csv

        # Nome del file CSV
        file_csv = 'prodotti.csv'

        # Scrivi i dati nel file CSV
        with open(file_csv, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Scrivi l'intestazione (opzionale)
            writer.writerow(['ID', 'Nome', 'Marca', 'Prezzo', 'URL', 'Pezzi'])  # Modifica in base alle tue colonne

            # Scrivi i dati
            writer.writerows(myresult)

        print(f"File {file_csv} creato con successo!")
        query = "SELECT * FROM prodotti"

        # Carica i dati della query in un DataFrame di Pandas
        df = pd.read_sql(query, mydb)

        # Visualizza il DataFrame


        query = "SELECT id, nome, marca, pezzi, prodottiV  FROM prodotti"
        mycursor.execute(query)
        myresult1 = mycursor.fetchall()
        # Ottenere i nomi delle colonne
        column_names = [desc[0] for desc in mycursor.description]

        # Creare un DataFrame Pandas con i nomi delle colonne
        df = pd.DataFrame(myresult1, columns=column_names)

        # Calcolare la colonna "Somma" (es. somma dei pezzi in magazzino e venduti)
        sommaP = df['pezzi'].sum()
        sommaV = df['prodottiV'].sum()

        mediaP = df['pezzi'].mean()
        # Nuova riga da aggiungere
        new_row = {
            'id': np.nan,  # Imposta su NaN o su un valore predefinito
            'nome': np.nan,  # Imposta su NaN o su un valore predefinito
            'marca': "Somma",  # Imposta su NaN o su un valore predefinito
            'pezzi': sommaP,  # Valore specificato
            'prodottiV': sommaV  # Valore specificato
        }

        ## Creare un DataFrame dalla nuova riga
        new_row_df = pd.DataFrame([new_row])

        # Aggiungere la nuova riga usando pd.concat
        df = pd.concat([df, new_row_df], ignore_index=True)
        # Convertire il DataFrame in una lista di liste (ogni riga è una lista)
        lista_prodotti = df.values.tolist()

        # Calcolare il prodotto più venduto
        index_max = df['prodottiV'].idxmax()  # Ottieni l'indice del valore massimo

        # Calcolare l'indice del prodotto più venduto, escludendo l'ultima riga
        index_max = df['prodottiV'][:-1].idxmax()  # Prende solo le righe fino all'ultima
        prodotto_piu_venduto = df.loc[index_max]
        prodottoMax = prodotto_piu_venduto['nome']
        print(prodottoMax)
        # Calcolare il prodotto più venduto

        index_min = df['prodottiV'][:-1].idxmin()
        prodotto_meno_venduto = df.loc[index_min]
        prodottoMin = prodotto_meno_venduto['nome']

        print(prodottoMin)

        return render_template("gestore.html", lista=lista_prodotti, listaS=listaS, prodottoMax = prodottoMax, prodottoMin = prodottoMin)

    else:
      return redirect(url_for('login'))

@app.route('/process', methods=['POST', 'GET'])
def process():
    if request.method == 'POST':
        nome = request.form['nome']
        marca = request.form['marca']
        prezzo = request.form['prezzo']
        url = request.form['url']
        pezzi = request.form['pezzi']
        prodottiV = 0

        mycursor = mydb.cursor()
        sql = ("INSERT INTO prodotti (nome, marca, prezzo, url,pezzi,  prodottiV) VALUES (%s, %s,%s, %s, %s, %s)")
        val = (nome, marca, prezzo, url, pezzi, prodottiV)
        mycursor.execute(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")

        p1 = prodotto(nome, marca, prezzo, url, pezzi, prodottiV)


    return render_template("insert.html", prod = p1)


@app.route("/remove", methods=['POST', 'GET'])
def remove():
    if request.method == 'POST':
        id = int(request.form['prod'])
        mycursor = mydb.cursor()
        sql = ("DELETE FROM prodotti WHERE id = %s")
        val = (id,)
        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "record removed.")


        return("prodotto rimosso")

@app.route("/search", methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        marca = request.form['marca']
        mycursor = mydb.cursor()
        sql = "SELECT * FROM prodotti WHERE marca = (%s)"
        val = (marca,)
        mycursor.execute(sql, val)

        myresult = mycursor.fetchall()






        return render_template("stampaMarche.html", lista = myresult)
def truncate_text(text, max_length=500):
    if len(text) > max_length:
        return text[:max_length] + '...'
    return text
lista = []

@app.route("/")
def store():
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM prodotti")

    myresult = mycursor.fetchall()

    totCarrello = 0
    for i in lista:
        totCarrello += int(i.prezzo) * int(i.getPezzi())



    url = "https://www.themealdb.com/api/json/v1/1/random.php"
    response = requests.get(url)

    if response.status_code == 200:
        # Crea un'istanza del traduttore

        data = response.json()
        print(data['meals'][0])
        txt = data['meals'][0]['strInstructions']
        # Crea un'istanza del traduttore
        translator = Translator(to_lang="it")

        txtRidotto = truncate_text(txt, 400)

        print(txtRidotto)
        # Traduci il testo
        translation = translator.translate(txtRidotto)



        return render_template('store.html', data=data['meals'][0],lista = myresult, ricetta = translation, carrello = lista, totale = totCarrello )
    else:
        return f"Errore {response.status_code}"



@app.route("/updatePezzi", methods=['POST', 'GET'])
def updatePezzi():
    if request.method == 'POST':
        id = int(request.form['prodID'])
        pezzi = request.form['Npezzi']
        mycursor = mydb.cursor()
        sql =  "UPDATE prodotti SET pezzi = pezzi + %s  WHERE id = %s"
        val = (pezzi, id)
        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "record update.")


        return("Prodottoaggiornato")


@app.route("/buy", methods=['POST', 'GET'])
def buy():
    if request.method == 'POST':


     for i, p1 in enumerate(lista):


            mycursor = mydb.cursor()
            sql = "UPDATE prodotti SET pezzi = pezzi - %s  WHERE nome = %s"
            val = (p1.getPezzi(), p1.nome)
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "record update.")

            mycursor = mydb.cursor()
            sql = "UPDATE prodotti SET prodottiV = prodottiV + %s  WHERE nome = %s"
            val = (p1.getPezzi(), p1.nome)
            mycursor.execute(sql, val)
            mydb.commit()

            print(mycursor.rowcount, "record update.")

            '''
            mycursor = mydb.cursor()

            mycursor.execute("SELECT * FROM prodotti")

            myresult = mycursor.fetchall()
            idS = (listaId[i])
            for j in myresult:

                if (j[0]) == idS:
                    p1 = prodottiV(j[1], j[2], j[3], j[4], num)
                    print("ciao")
                    listaPr.append(p1)
'''

    somma = 0
    for i in lista:
        somma += int(i.prezzo) * int(i.getPezzi())












    return render_template("recap.html", lista = lista, somma = somma)
@app.route('/combined_chart.png')
def plot_png():
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM prodotti")

    prodotti = mycursor.fetchall()

    # Estrai le etichette (colonna [1]) e vendite (colonna [7]) dalle tuple
    etichette = [row[1] for row in prodotti]  # Supponiamo che row[1] sia il nome del prodotto
    vendite = [row[6] for row in prodotti]  # Sup

    # Crea una figura con due subplot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))  # 1 riga, 2 colonne

    # --- Grafico a barre ---
    ax1.bar(etichette, vendite, color='skyblue')
    ax1.set_title('Vendite per Prodotto (Grafico a Barre)')
    ax1.set_ylabel('Vendite')

    # --- Grafico a torta ---
    ax2.pie(vendite, labels=etichette, autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff', '#99ff99'])
    ax2.axis('equal')  # Per mantenere la torta circolare
    ax2.set_title('Distribuzione Vendite (Grafico a Torta)')

    # Salva la figura in memoria come PNG
    output = io.BytesIO()
    fig.savefig(output, format='png')
    plt.close(fig)
    output.seek(0)

    return make_response(output.getvalue(), 200, {'Content-Type': 'image/png'})



@app.route("/add", methods=['POST', 'GET'])
def add():
    id = request.form.get('prodId')
    num = request.form.get('prodA')

    mycursor = mydb.cursor()

    sql = ("SELECT * FROM prodotti WHERE id = %s")

    val = (id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()

    for p1 in myresult:
     p2 = prodottiV(p1[1], p1[2], p1[3], p1[4])
     p2.setPezzi(num)
     lista.append(p2)


    return(store())

@app.route("/rimuovi", methods=['POST', 'GET'])
def rimuovi():
    if request.method == 'POST':
        nome = request.form['nome']

        for p1 in lista:
            if (p1.nome == nome):
                lista.remove(p1)

    return(store())

if __name__ == '__main__':

   app.run(debug = True)
