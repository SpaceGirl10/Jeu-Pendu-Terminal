from socket import socket, AF_INET, SOCK_STREAM
import rsa
import pyaes
from random import randint
import random
import time
from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.live import Live

# Classe représentant la logique du jeu du pendu
class Pendu:
    def __init__(self, fichier_mots="liste_mots.txt", vies=6):
        # Initialisation des variables du jeu
        self.fichier_mots = fichier_mots
        self.vies = vies
        self.vies_max = vies
        self.mot = self.choisir_mot()
        self.mot_lettres = list(self.mot)
        self.L_mot = ["_" for _ in self.mot]  # Mot à afficher avec des lettres manquantes
        self.gagne = False
        self.score = 0
        self.lettres_trouvees = []
        self.lettres_incorrectes = []
        self.message = ""

    def choisir_mot(self):
        # Choix aléatoire d'un mot dans le fichier
        try:
            with open(self.fichier_mots, 'r', encoding='utf-8') as fichier:
                mots = fichier.read().split()
            if not mots:
                raise ValueError("Le fichier de mots est vide.")
            return random.choice(mots)
        except FileNotFoundError:
            print("Erreur : fichier de mots introuvable.")
            exit()
        except ValueError as e:
            print(f"Erreur : {e}")
            exit()

    def tester_lettre(self, lettre, temps_reponse):
        # Teste si une lettre est dans le mot
        if lettre in self.L_mot:
            self.message = "Vous avez déjà trouvé cette lettre."
            return

        if lettre in self.mot_lettres:
            for i, l in enumerate(self.mot_lettres):
                if l == lettre:
                    self.L_mot[i] = lettre
            self.score += max(100 - int(temps_reponse * 10), 20)  # Score dépendant du temps de réponse
            self.message = "Bonne lettre !"
        else:
            self.lettres_incorrectes.append(lettre)
            self.message = "Mauvaise lettre, vous perdez une vie !"
            self.vies -= 1
            if self.score > 5:
                self.score -= 5

    def tester_mot(self, mot_propose, temps_reponse):
        # Teste si un mot complet est correct
        if mot_propose == self.mot:
            self.gagne = True
            self.L_mot = list(self.mot)
            self.score += max(200 - int(temps_reponse * 10), 20)
            return True
        else:
            self.vies -= 1
            self.message = "Ce n'est pas le bon mot, vous perdez une vie !"
            if self.score > 10:
                self.score -= 10
            return False

# Classe Client gérant la connexion et la communication sécurisée avec le serveur
class Client:
    def __init__(self, host="10.69.228.82", port=4100):
        self.host = host
        self.port = port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connecté à {self.host} sur le port {self.port}")

        # Réception de la clé publique RSA du serveur
        self.e = int(self.sock.recv(2048).decode('utf-8'))
        print("e reçu")
        self.sock.sendall("bien recu".encode('utf-8'))
        self.n = int(self.sock.recv(2048).decode('utf-8'))
        print("n reçu")
        self.pub = rsa.PublicKey(self.n, self.e)

        # Génération aléatoire d’une clé AES 256 bits
        nombre = [randint(0, 255) for _ in range(32)]
        self.clef = bytes(nombre)
        print("Clé AES générée")

        # Chiffrement RSA de la clé AES et envoi au serveur
        clef_code = rsa.encrypt(self.clef, self.pub)
        self.sock.sendall(clef_code)

    def reception(self):
        # Réception et déchiffrement AES d’un message du serveur
        message_code = self.sock.recv(2048)
        aes = pyaes.AESModeOfOperationCTR(self.clef)
        message = aes.decrypt(message_code).decode('utf-8')
        return message

    def envoi(self, mess):
        # Chiffrement AES d’un message et envoi au serveur
        aes = pyaes.AESModeOfOperationCTR(self.clef)
        message_code = aes.encrypt(mess.encode('utf-8'))
        self.sock.send(message_code)

    def start(self):
        # Lancement du jeu et envoi du score au serveur
        jeu = Pendu()
        interface = Interface(jeu)
        interface.jouer()
        self.envoi(str(jeu.score))
        self.reception()
        exit()

# Classe pour l’interface utilisateur avec Rich
class Interface:
    def __init__(self, jeu):
        self.console = Console()
        self.jeu = jeu

        # Création de la mise en page principale
        self.layout = Layout()
        self.titre = Text("JEU DU PENDU", justify="center", style="light_goldenrod2")

        # Tableau de classement (à compléter avec des données réelles)
        self.classement = Table(box=box.DOUBLE, title="Classement", style="light_goldenrod2")
        self.classement.header_style = "bold sky_blue3"
        self.classement.title_style = "bold sky_blue3"
        self.classement.add_column("Joueur", justify="right", style="light_goldenrod2", min_width=20)
        self.classement.add_column("Score", justify="right", style="light_goldenrod2", min_width=20)

        # Organisation de l'affichage en sections
        self.layout.split_column(
            Layout(name="upper"),
            Layout(name="lower")
        )

        self.layout["lower"].split_row(
            Layout(name="pendu"),
            Layout(name="right")
        )

        self.layout["upper"].split_column(
            Layout(Panel(self.titre, style="salmon1", expand=True)),
            Layout(name="mot_a_trouver")
        )

        self.layout["right"].split_row(
            Layout(name="lettres"),
            Layout(name="full_right")
        )
        self.layout["full_right"].split_column(
            Layout(self.classement, name="classement"),
            Layout(name="time")
        )

    def jouer(self):
        # Boucle principale du jeu avec rafraîchissement dynamique de l’interface
        with Live(self.layout, refresh_per_second=4, screen=True):
            while self.jeu.vies > 0 and not self.jeu.gagne:
                self.update_interface()
                debut = time.time()
                entree = input("\nEntrez une lettre ou un mot : ").lower().strip()
                fin = time.time()

                if not entree.isalpha():
                    self.jeu.message = "Entrée invalide, uniquement des lettres."
                    continue

                temps_reponse = fin - debut
                if temps_reponse > 15:
                    self.jeu.message = "Temps écoulé ! Vous perdez une vie."
                    self.jeu.vies -= 1
                    continue

                if len(entree) == 1:
                    self.jeu.tester_lettre(entree, temps_reponse)
                else:
                    if self.jeu.tester_mot(entree, temps_reponse):
                        break

                if self.jeu.L_mot == self.jeu.mot_lettres:
                    self.jeu.gagne = True

            self.update_interface(final=True)
            time.sleep(7)

    def update_interface(self, final=False):
        # Mise à jour de l'affichage dynamique en fonction de l'état du jeu
        self.layout["mot_a_trouver"].update(Panel(Text(f"Mot : {' '.join(self.jeu.L_mot)}", style="light_goldenrod2", justify="center"), style="sky_blue3"))
        self.layout["pendu"].update(Panel(f"Vies restantes : {self.jeu.vies} / {self.jeu.vies_max}\nScore : {self.jeu.score}\n{self.jeu.message}", style="sky_blue3"))
        self.layout["time"].update(Panel(Text("Répondez vite ! (15s max)", justify="center"), style="salmon1"))
        
        lettres_incorrectes_str = ' '.join(self.jeu.lettres_incorrectes)
        self.layout["lettres"].update(Panel(f"Lettres incorrectes : {lettres_incorrectes_str}", style="salmon1"))

        if final:
            if self.jeu.gagne:
                msg = f"Bravo ! Vous avez trouvé le mot '{self.jeu.mot}' avec {self.jeu.vies} vies restantes !"
            else:
                msg = f"Dommage... Le mot était '{self.jeu.mot}'."
            self.layout["mot_a_trouver"].update(Panel(Text(msg, style="bold green"), style="salmon1"))

if __name__ == "__main__":
    # Lancement du client et du jeu
    client = Client()
    client.start()
