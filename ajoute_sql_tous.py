import mysql.connector
import account_login
from account_login import *


def connect_db():
    """Établit une connexion à la base de données MySQL."""
    return mysql.connector.connect(
        host='localhost',
        user='clot',
        password='clot',
        database='project'
    )

def maj_player(username, new_score):
    
    """Met à jour le score d'un joueur dans la base de données."""
    conn = connect_db()
    cursor = conn.cursor()

    # Met à jour le score de l'utilisateur dans la table 'players'
    sql = "UPDATE players SET score = %s WHERE name = %s"
    cursor.execute(sql, (new_score, username))
    conn.commit()

    # Vérification que la mise à jour a eu lieu
    if cursor.rowcount > 0:
        print(f"Le score de {username} a été mis à jour à {new_score} !")
    else:
        print(f"Erreur : l'utilisateur {username} n'a pas pu être trouvé ou mis à jour.")

    cursor.close()
    conn.close()


def add_player(name, hash, score=None):
    """Ajoute un joueur avec son score dans la table players."""
    conn = connect_db()
    cursor = conn.cursor()

    try:
        sql_1 = "SELECT name FROM players WHERE name = %s"
        cursor.execute(sql_1, (name,))
        nom_players = cursor.fetchall()

        if len(nom_players) == 0:
            sql_2 = "INSERT INTO players (name, score, hash) VALUES (%s, %s, %s)"
            values = (name, score, hash)
            cursor.execute(sql_2, values)
            conn.commit()
            print(f"Joueur {name} ajouté avec un score de {score}.")
            result = 0
        else:
            result = 1
    finally:
        cursor.close()
        conn.close()

    return result

def liste_players():
    """Récupère la liste de tous les players sous forme d'une liste simple."""
    conn = connect_db()
    cursor = conn.cursor()
    sql = "SELECT name from players"
    cursor.execute(sql)
    liste_name = cursor.fetchall()
    # Extraire les noms de chaque tuple pour avoir une liste de strings
    players_names = [name[0] for name in liste_name]
    cursor.close()
    conn.close()
    return players_names

def recup_hash(username):
    """Récupère le hash associé à un nom d'utilisateur"""
    conn = connect_db()
    cursor = conn.cursor()
    sql = "SELECT hash FROM players WHERE name = %s"
    cursor.execute(sql, (username,))  # note la virgule pour passer un tuple
    result = cursor.fetchone()  # on récupère un seul résultat
    cursor.close()
    conn.close()
    if result:
        return result[0]  # le hash
    else:
        return None  # utilisateur non trouvé

def reset_players(name=None):
    """Réinitialise la table :
    - Supprime un joueur spécifique si un nom est donné.
    - Supprime tous les joueurs si aucun nom n'est donné.
    """
    conn = connect_db()
    cursor = conn.cursor()

    if name:
        sql = "DELETE FROM players WHERE name = %s"
        cursor.execute(sql, (name,))
        print(f"Joueur {name} supprimé.")
    else:
        sql = "DELETE FROM players"
        cursor.execute(sql)
        print("Tous les joueurs ont été supprimés.")

    conn.commit()
    cursor.close()
    conn.close()


print(recup_hash("gyom"))


# Exemple d'utilisation
if __name__ == "__main__":
    reset_players()