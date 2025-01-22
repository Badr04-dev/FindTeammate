from datetime import datetime, timedelta
from data_model import *


#################### PLAYERS ##############################

# Fonction de test pour get_player_by_username
def test_get_player_by_username():
    username = "lazyfrog764"
    player = get_player_by_username(username)
    if player == -1:
        print("Test Failed !")
    else:
        print("Informations du joueur:")
        print(player)

def test_show_player_account():
    player_id = 1  # Remplacer 1 par l'ID du joueur que vous souhaitez afficher
    player_info = show_player_account(player_id)
    if(player_info != -1):
        print(player_info)
    else :
        print("Test Failed !")

# Fonction de test pour update_player_account
def test_update_player_account():
    username = "Badro"
    result = update_player_account(8,"John", "Doe", "test.jpg", username, 25, "john@example.com", "123456789", "password123", "Defenseur Central")
    if result != -1:
        print(get_player_by_username(username))
        print("Test Passed !")
    else:
        print("Test Failed !")

#################### AVAILABILITY ##############################
def test_is_availability_expired():
    player_id = 1
    add_to_waiting_list(player_id,"2023-04-13T11:30","2024-04-26T11:30")
    if is_availability_expired(player_id):
        print("La disponibilité du joueur est expirée.")
    else:
        print("La disponibilité du joueur est encore valide.")
    delete_from_waiting_list(player_id)


#################### WAITING LIST ##############################

# Fonction de test pour show_waiting_list
def test_show_waiting_list():
    print("Liste d'attente des joueurs:")
    print(show_waiting_list())

# Fonction de test pour user_in_waiting_list
def test_user_in_waiting_list():
    player_id = 2
    if user_in_waiting_list(player_id):
        print("Test Passed !")
    else:
        print("Test Failed !")

# Fonction de test pour add_to_waiting_list
def test_add_and_show_waiting_list():
    player_id = 2  # Remplacez par l'ID du joueur à ajouter
    start = datetime.now().strftime('%Y-%m-%d %H:%M')
    end = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M')
    result = add_to_waiting_list(player_id, start, end)
    if result == 1:
        print("Test Passed !")
        print(show_waiting_list())
    elif result == -1:
        print(show_waiting_list())
        print("Test Failed !")
    else:
        print("Échec de l'ajout du joueur à la liste d'attente.")

# Fonction de test pour delete_from_waiting_list
def test_delete_from_waiting_list():
    player_id = 1
    result = delete_from_waiting_list(player_id)
    if result == 1:
        print("Test Passed !")
    elif result == -1:
        print("Test Failed !")
    else:
        print("Échec de la suppression du joueur de la liste d'attente.")


####################### JOIN REQUEST ####################################


# Fonction de test pour request_exists
def test_request_exists():
    requestor_username = "lazyfrog764"
    requestee_username = "bluelion224"
    if request_exists(requestor_username, requestee_username):
        print("Une demande d'invitation existe entre les deux joueurs.")
    else:
        print("Aucune demande d'invitation entre les deux joueurs.")

# Fonction de test pour get_join_requests_to
def test_get_join_requests_to():
    username = "blackcat166"
    print(f"Demandes d'invitation adressées à '{username}':")
    print(get_join_requests_to(username))

# Fonction de test pour join_request
def test_join_request():
    requestor_username = "lazyfrog764"
    requestee_username = "yellowbear758"
    result = join_request(requestor_username, requestee_username)
    if result == -1:
        print("Échec : requestee n'existe pas.")
    elif result == -2:
        print("Échec : requestor n'existe pas.")
    elif result == -3:
        print("Échec : Une demande d'invitation de requestor à requestee est déjà enregistrée.")
    elif result == -4:
        print("Échec : requestor et requestee sont déjà en équipe.")
    else:
        print("La demande d'invitation a été enregistrée avec succès.")
        print(f"Clé ID associée à la demande d'invitation : {result}")

# Fonction de test pour delete_join_request
def test_delete_join_request():
    requestor_username = "lazyfrog764"
    requestee_username = "yellowbear758"
    result = delete_join_request(requestor_username, requestee_username)
    if result == -1:
        print("Échec : requestor ou requestee n'existe pas.")
    else:
        print("La demande d'invitation a été supprimée avec succès.")

# Fonction de test pour accept_join_request
def test_accept_join_request():
    requestor_username = "lazyfrog764"
    requestee_username = "bluelion224"
    result = accept_join_request(requestor_username, requestee_username)
    if result == -1:
        print("Échec : Aucune demande d'invitation entre requestor et requestee.")
    else:
        print("La demande d'invitation a été acceptée avec succès.")

# Fonction de test pour refuse_join_request
def test_refuse_join_request():
    requestor_username = "lazyfrog764"  # Remplacez par le nom d'utilisateur du demandeur
    requestee_username = "bluelion224"  # Remplacez par le nom d'utilisateur de l'invité
    result = refuse_join_request(requestor_username, requestee_username)
    if result == -1:
        print("Échec : Aucune demande d'invitation entre requestor et requestee.")
    else:
        print("La demande d'invitation a été refusée avec succès.")

# Exécution des fonctions de test
if __name__ == "__main__":
    #test_get_player_by_username() # TEST PASSED
    #test_show_player_account() # TEST PASSED
    #test_update_player_account() # TEST PASSED
    #test_is_availability_expired()  #TEST PASSED
    #test_show_waiting_list()  # TEST PASSED
    #test_user_in_waiting_list()  # TEST PASSED
    #test_add_and_show_waiting_list()  # TEST PASSED
    #test_delete_from_waiting_list()  # TEST PASSED
    #test_request_exists()  # TEST PASSED
    #test_get_join_requests_to()  # TEST PASSED
    #test_join_request()  # TEST PASSED
    #test_delete_join_request()  # TEST PASSED
    #test_accept_join_request()  # TEST PASSED
    #test_refuse_join_request()  # TEST PASSED
    print("All Test Passed !")
