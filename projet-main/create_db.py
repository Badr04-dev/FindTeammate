import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
import data_model


JSONFILENAME = 'players.json'
DBFILENAME = 'players.sqlite'



# Utility function
def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()

def load(fname=JSONFILENAME, db_name=DBFILENAME):
    db_run('DROP TABLE IF EXISTS player')
    db_run('DROP TABLE IF EXISTS waiting_list')
    db_run('DROP TABLE IF EXISTS join_requests')
    db_run('DROP TABLE IF EXISTS joined_team')

    db_run('''CREATE TABLE player (
         id INTEGER PRIMARY KEY AUTOINCREMENT, 
         firstname TEXT, 
         lastname TEXT, 
         picture TEXT, 
         username TEXT, 
         age INT, 
         email TEXT, 
         phone TEXT, 
         password TEXT, 
         description TEXT)''')

    db_run('''CREATE TABLE waiting_list (
         id INTEGER PRIMARY KEY AUTOINCREMENT, 
         player_id INT, 
         start TEXT, 
         end TEXT, 
         FOREIGN KEY (player_id) REFERENCES player(id))''')

    db_run('''CREATE TABLE join_requests (
         id INTEGER PRIMARY KEY AUTOINCREMENT, 
         requestor_id INT, 
         requestee_id INT, 
         message TEXT, 
         FOREIGN KEY (requestor_id) REFERENCES player(id), 
         FOREIGN KEY (requestee_id) REFERENCES player(id))''')
    db_run('''CREATE TABLE joined_team (
         id INTEGER PRIMARY KEY AUTOINCREMENT, 
         player1_id INT, 
         player2_id INT, 
         FOREIGN KEY (player1_id) REFERENCES player(id), 
         FOREIGN KEY (player2_id) REFERENCES player(id))''')

    with open('players.json', 'r') as file:
        data = json.load(file)
        for item in data:
            # Créer le joueur
            player_id = create_new_player(item['firstname'], item['lastname'], item['picture'], item['username'], item['age'], item['email'], item['phone'], generate_password_hash(item['password']), item['description'])

    print("Données chargées avec succès dans la base de données !")


def player_exists(username):
    result = data_model.db_fetch('SELECT COUNT(*) as count FROM player WHERE username = ?', (username,))
    return result['count'] > 0


def create_new_player(firstname, lastname, picture, username, age, email, phone, password, description):
    if(player_exists(username)):
        return -1
    player_id = data_model.db_insert('INSERT INTO player (firstname, lastname, picture, username, age, email, phone, password, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                     (firstname, lastname, picture, username, age, email, phone, generate_password_hash(password), description))
    return player_id




#################################################

if __name__=='__main__':
    load()
    #create_test_user()




