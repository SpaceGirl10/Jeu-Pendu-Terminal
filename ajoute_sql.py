import mysql.connector

def add_player(name, score):
    # Connexion à la base de données
    conn = mysql.connector.connect(
        host='localhost',       # Remplace par l'hôte de ta base
        user='clot',            # Remplace par ton utilisateur
        password='Toro',    # Remplace par ton mot de passe
        database='Tables_in_mysql' # Remplace par le nom de ta base
    )
    cursor = conn.cursor()
    
    # Insertion des données
    sql = "INSERT INTO players (name, score) VALUES (%s, %s)"
    values = (name, score)
    cursor.execute(sql, values)
    conn.commit()
    
    print(f"Joueur {name} ajouté avec un score de {score}.")
    
    # Fermeture de la connexion
    cursor.close()
    conn.close()

# Exemple d'utilisation
if __name__ == "__main__":
    add_player("Frank", 1700)