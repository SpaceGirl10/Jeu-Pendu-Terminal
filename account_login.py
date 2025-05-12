from rich.prompt import Prompt
from rich.console import Console
from ajoute_sql_tous import *
from hashlib import sha256

console = Console()

# Stockage simple en mémoire (pour tester)
users = {}

def create_account():
    console.print("\n[bold green]Création d'un compte[/bold green]")
    username = Prompt.ask("Choisis un nom d'utilisateur")
    if username in liste_players():
        console.print("[red]Ce nom existe déjà. Essaie un autre.[/red]")
        return
    password = Prompt.ask("Choisis un mot de passe", password=True)
    hachage_c = sha256(password.encode('utf-8'))
    users[username] = hachage_c.hexdigest()
    conn = connect_db()
    cursor = conn.cursor()
    """Ajoute le name et le hachage dans la BDD"""
    sql = "INSERT INTO players (name, hash) VALUES (%s, %s);"

    cursor.execute(sql, (username, hachage_c.hexdigest()))
    conn.commit()
    print(users)
    return username, hachage_c.hexdigest()



def login():
    console.print("\n[bold cyan]Connexion[/bold cyan]")
    username = Prompt.ask("Nom d'utilisateur")
    if username not in liste_players():
        console.print("[red]Utilisateur inconnu.[/red]")
        return
    password = Prompt.ask("Mot de passe", password=True)
    hachage_l = sha256(password.encode('utf-8'))
    if recup_hash(username) == hachage_l.hexdigest():
        console.print(f"[green]Bienvenue {username} ![/green]")
        return True
    else:
        console.print("[red]Mot de passe incorrect.[/red]")

def main():
    while True:
        action = Prompt.ask("\n[bold]Veux-tu [green]créer[/green] un compte ou [cyan]te connecter[/cyan] ?[/bold]", choices=["new", "log", "quit"])
        if action == "new":
            create_account()
        elif action == "log":
            if login():  # si login() retourne True
                console.print("[bold green]Connexion réussie ![/bold green]")
                break       # on sort de la boucle
        elif action == "quit":
            console.print("[bold yellow]À bientôt ![/bold yellow]")
            break
    #login effectué
    

if __name__ == "__main__":
    main()

