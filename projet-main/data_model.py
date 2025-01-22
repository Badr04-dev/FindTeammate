import sqlite3
import math
from datetime import datetime
from werkzeug.security import generate_password_hash


DBFILENAME = 'players.sqlite'

########################### FONCTIONS UTILITAIRE
def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        # to allow access to columns by name in res
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        # convert to a python dictionary for convenience
        if all:
            res = cur.fetchall()
            if res:
                res = [dict(e) for e in res]
            else:
                res = []
        else:
            res = cur.fetchone()
            if res:
                res = dict(res)
    return res

def db_insert(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid


def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()


def db_update(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.rowcount


########################### PLAYER
def get_player_by_username(username):
    player = db_fetch('SELECT * FROM player WHERE username = ?', (username,))
    if player:
        return player  # Retourner le joueur s'il existe
    else:
        return -1  # Retourner -1 si le nom d'utilisateur n'existe pas

def show_player_account(player_id):
    query = '''SELECT id, firstname, lastname, picture, age, email, phone, description, username
               FROM player 
               WHERE id = ?'''
    player_info = db_fetch(query, (player_id,))
    if player_info:
        return player_info
    else:
        return -1

def update_player_account(id,firstname, lastname, picture, username, age, email, phone, password, description):
    query = '''
    UPDATE player 
    SET firstname = ?, lastname = ?, picture = ?, age = ?, email = ?, phone = ?, password = ?, description = ?, username = ?
    WHERE id=?
    '''
    args = (firstname, lastname, picture, age, email, phone, generate_password_hash(password), description, username,id)
    return db_update(query, args)


########################### WAITING LIST
def show_waiting_list():
    # Récupération de tous les joueurs de la liste d'attente
    query = """
        SELECT player.*, start, end
        FROM waiting_list
        JOIN player ON waiting_list.player_id = player.id
    """
    waiting_players = db_fetch(query, all=True)

    # Liste pour stocker les nouveaux joueurs dans la liste d'attente
    new_waiting_players = []

    # Vérification de chaque joueur dans la liste d'attente
    for player in waiting_players:
        end_datetime = datetime.datetime.strptime(player['end'], "%Y-%m-%dT%H:%M")
        current_datetime = datetime.datetime.now()

        # Si la date de fin est passée, on supprime le joueur de la liste d'attente
        if end_datetime <= current_datetime:
            delete_from_waiting_list(player['id'])
        else:
            # Si la date de fin n'est pas passée, on ajoute le joueur à la nouvelle liste d'attente
            new_waiting_players.append(player)

    # Retour de la nouvelle liste de joueurs dans la liste d'attente
    return new_waiting_players




def user_in_waiting_list(player_id):
    result = db_fetch('SELECT count(*) FROM waiting_list WHERE player_id = ?', (int(player_id),))
    if result and result['count(*)'] > 0:
        return True
    else:
        return False

def add_to_waiting_list(player_id, start, end):
    if user_in_waiting_list(int(player_id)):
        return -1
    else:
        db_insert('INSERT INTO waiting_list (player_id, start, end) VALUES (?, ?, ?)', (int(player_id), start, end))
        return 1

def delete_from_waiting_list(player_id):
    if not user_in_waiting_list(player_id):
        return -1
    else:
        db_run('DELETE FROM waiting_list WHERE player_id = ?', (player_id,))
        return 1


########################### JOIN REQUEST
def request_exists(requestor_username, requestee_username):
    # Vérifier si une demande d'invitation existe entre requestor et requestee
    requestor = get_player_by_username(requestor_username)
    requestee = get_player_by_username(requestee_username)

    if requestor == -1 or requestee == -1:
        return False  # L'un des utilisateurs n'existe pas, donc la demande n'existe pas

    existing_requests = db_fetch('SELECT * FROM join_requests WHERE requestor_id = ? AND requestee_id = ?',
                                 (requestor['id'], requestee['id']))
    return bool(existing_requests)

def get_join_requests_to(username):
    player_id = get_player_by_username(username)['id']

    query = """
    SELECT requestor.*, requestee.username AS requestee_username, join_requests.message
    FROM join_requests
    JOIN player AS requestor ON join_requests.requestor_id = requestor.id
    JOIN player AS requestee ON join_requests.requestee_id = requestee.id
    WHERE join_requests.requestee_id = ?;
    """

    join_requests = db_fetch(query, (player_id,), all=True)

    if not join_requests:
        return []

    return join_requests


def join_request(requestor_username, requestee_username, message):
    # Vérifier si requestor et requestee sont des utilisateurs enregistrés
    requestor = get_player_by_username(requestor_username)
    requestee = get_player_by_username(requestee_username)

    if requestee == -1:
        return -1  # requestee n'existe pas
    elif requestor == -1:
        return -2  # requestor n'existe pas

    # Vérifier s'il y a déjà une demande d'invitation de requestor à requestee enregistrée
    if request_exists(requestor_username, requestee_username):
        return -3

        # Vérifier si requestor et requestee sont déjà en équipe
    if are_teammates(requestor,requestee):
        return -4

        # Enregistrer la demande d'invitation dans la table join_requests
    return db_insert('INSERT INTO join_requests (requestor_id, requestee_id, message) VALUES (?, ?, ?)',
                     (requestor['id'], requestee['id'], message))


def delete_join_request(requestor_username, requestee_username):
    # Vérifier si requestor et requestee sont des utilisateurs enregistrés
    requestor = get_player_by_username(requestor_username)
    requestee = get_player_by_username(requestee_username)

    if requestor == -1 or requestee == -1:
        return -1

        # Supprimer toutes les demandes d'invitation de requestor à requestee
    db_run('DELETE FROM join_requests WHERE requestor_id = ? AND requestee_id = ?',
           (requestor['id'], requestee['id']))
    return True


########################### AVAILABILITY
def convert_text_to_datetime(player):
    player_end_date = db_fetch('SELECT end FROM waiting_list WHERE player_id = ?', (int(player['id']),), True)
    if player_end_date:
        player_end_date = datetime.strptime(player_end_date['end'], '%Y-%m-%dT%H:%M')
        return player_end_date

    return None

import datetime

def is_availability_expired(player_id, db_name=DBFILENAME):
    current_date = datetime.date.today()

    query = "SELECT end FROM waiting_list WHERE player_id = ?"

    result = None
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(query, (player_id,))
        result = cur.fetchone()
    if result:
        end_date = datetime.datetime.strptime(result[0], "%Y-%m-%dT%H:%M").date()
        return current_date > end_date
    else:
        return False


########################### JOINED TEAM
def are_teammates(requestor, requestee):
    # Vérifier si requestor et requestee sont déjà en équipe
    result = db_fetch('SELECT * FROM joined_team WHERE (player1_id = ? AND player2_id = ?) OR (player1_id = ? AND player2_id = ?)',
                      (requestor['id'], requestee['id'], requestee['id'], requestor['id']))
    return bool(result)

def get_joined_teammates(username):
    player = get_player_by_username(username)
    if player == -1:
        return []  # Le joueur n'existe pas

    player_id = player['id']

    # Requête pour récupérer les coéquipiers rejoins du joueur
    query = """
        SELECT player.*
        FROM player
        JOIN joined_team ON (player.id = joined_team.player1_id OR player.id = joined_team.player2_id)
        WHERE player.id != ? AND (joined_team.player1_id = ? OR joined_team.player2_id = ?)
    """

    teammates = db_fetch(query, (player_id, player_id, player_id), all=True)

    return teammates

def accept_join_request(requestor_username, requestee_username):
    requestor=get_player_by_username(requestor_username)
    requestee=get_player_by_username(requestee_username)

    if(request_exists(requestor_username,requestee_username) != True):
        return -2
    # Supprimer la demande d'invitation de requestor à requestee
    if delete_join_request(requestor_username, requestee_username) != True:
        return -1  # Aucune demande d'invitation entre requestor et requestee

    # Vérifier si requestor et requestee sont déjà en équipe
    if are_teammates(requestor , requestee):
        return -1  # requestor et requestee sont déjà en équipe

    if delete_from_waiting_list(requestee['id'])!=1:
        return -1

    # Ajouter une entrée pour requestor et requestee dans la table joined_team
    db_insert('INSERT INTO joined_team (player1_id, player2_id) VALUES (?, ?)',
              (requestor['id'], requestee['id']))

    return True

def refuse_join_request(requestor_username, requestee_username):
    if(request_exists(requestor_username,requestee_username) != True):
        return -2
    # Supprimer la demande d'invitation de requestor à requestee
    if delete_join_request(requestor_username, requestee_username) != True:
        return -1  # Aucune demande d'invitation entre requestor et requestee
    return True

def delete_player_from_team(requestor_username, requestee_username):
    # Récupérer les joueurs correspondant aux noms d'utilisateur
    player1 = get_player_by_username(requestor_username)
    player2 = get_player_by_username(requestee_username)

    # Si l'un des joueurs n'existe pas, ne rien faire
    if not player1 or not player2:
        return False

    if(is_availability_expired(player2['id'])):
        db_run('DELETE FROM joined_team WHERE (player1_id = ? AND player2_id = ?) OR (player1_id = ? AND player2_id = ?)',
               (player1['id'], player2['id'], player2['id'], player1['id']))
        return True

    return False


