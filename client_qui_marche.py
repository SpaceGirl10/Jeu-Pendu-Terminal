from socket import socket, AF_INET, SOCK_STREAM
import rsa
import pyaes
from random import randint
import random
import time
import threading
from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.live import Live

class Pendu:
    def __init__(self, fichier_mots="liste_mots.txt", vies=6):
        self.fichier_mots = fichier_mots
        self.vies = vies
        self.vies_max = vies
        self.mot = self.choisir_mot()
        self.mot_lettres = list(self.mot)
        self.L_mot = ["_" for _ in self.mot]
        self.lettres_incorrectes = []
        self.gagne = False
        self.score = 0
        self.message = ""

    def choisir_mot(self):
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
        if lettre in self.L_mot or lettre in self.lettres_incorrectes:
            self.message = "Vous avez déjà tenté cette lettre."
            return
        if lettre in self.mot_lettres:
            for i, l in enumerate(self.mot_lettres):
                if l == lettre:
                    self.L_mot[i] = lettre
            self.score += max(100 - int(temps_reponse * 10), 20)
            self.message = "Bonne lettre !"
        else:
            self.vies -= 1
            self.lettres_incorrectes.append(lettre)
            self.score = max(self.score - 5, 0)
            self.message = f"Mauvaise lettre '{lettre}' !"

    def tester_mot(self, mot_propose, temps_reponse):
        if mot_propose == self.mot:
            self.gagne = True
            self.L_mot = list(self.mot)
            self.score += max(200 - int(temps_reponse * 10), 20)
            self.message = "Mot complet trouvé !"
            return True
        else:
            self.vies -= 1
            self.score = max(self.score - 10, 0)
            self.message = "Mot incorrect !"
            return False

class Client:
    def __init__(self, host="10.69.228.82", port=4100):
        self.host = host
        self.port = port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connecté à {self.host} sur le port {self.port}")

        self.e = int(self.sock.recv(2048).decode('utf-8'))
        print("e reçu")
        self.sock.sendall("bien recu".encode('utf-8'))
        self.n = int(self.sock.recv(2048).decode('utf-8'))
        print("n reçu")
        self.pub = rsa.PublicKey(self.n, self.e)

        nombre = [randint(0, 255) for _ in range(32)]
        self.clef = bytes(nombre)
        print("Clé AES générée")

        clef_code = rsa.encrypt(self.clef, self.pub)
        self.sock.sendall(clef_code)

    def reception(self):
        message_code = self.sock.recv(2048)
        aes = pyaes.AESModeOfOperationCTR(self.clef)
        message = aes.decrypt(message_code).decode('utf-8')
        return message

    def envoi(self, mess):
        aes = pyaes.AESModeOfOperationCTR(self.clef)
        message_code = aes.encrypt(mess.encode('utf-8'))
        self.sock.send(message_code)

    def start(self):
        jeu = Pendu()
        interface = Interface(jeu)
        interface.jouer()
        self.envoi(str(jeu.score))
        self.reception()
        exit()

class Interface:
    def __init__(self, jeu):
        self.console = Console()
        self.jeu = jeu
        self.input_value = None

        # Classement table
        self.classement = Table(box=box.DOUBLE, title="Classement: Vous", style="salmon1")
        self.classement.header_style = "light_goldenrod2"
        self.classement.title_style = "light_goldenrod2"
        self.classement.add_column("Joueur", justify="center", style="light_goldenrod2")
        self.classement.add_column("Score", justify="center", style="light_goldenrod2")

        # Layout original
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="upper"),
            Layout(name="lower")
        )
        self.layout["upper"].split_column(
            Layout(Panel(Text("JEU DU PENDU", justify="center"), style="salmon1", expand=True)),
            Layout(name="mot_a_trouver")
        )
        self.layout["lower"].split_row(
            Layout(name="pendu"),
            Layout(name="right")
        )
        self.layout["right"].split_row(
            Layout(name="lettres"),
            Layout(name="full_right")
        )
        self.layout["full_right"].split_column(
            Layout(self.classement, name="classement"),
            Layout(name="time")
        )

    def update_layout(self, remaining=None):
        # Mot à deviner
        mot_panel = Panel(Text(' '.join(self.jeu.L_mot), justify="center"), title="Mot à trouver", style="salmon1")
        self.layout["mot_a_trouver"].update(mot_panel)
        # Vies
        pendu_panel = Panel(Text(f"Vies: {self.jeu.vies}/{self.jeu.vies_max}", justify="center"), title="Vies", style="salmon1")
        self.layout["pendu"].update(pendu_panel)
        # Lettres incorrectes
        inc = ', '.join(self.jeu.lettres_incorrectes) if self.jeu.lettres_incorrectes else 'Aucune'
        lettres_panel = Panel(Text(inc, justify="center"), title="Lettres incorrectes", style="salmon1")
        self.layout["lettres"].update(lettres_panel)
        # Classement (score)
        self.classement.rows.clear()
        self.classement.add_row("Vous", str(self.jeu.score))
        # Timer
        if remaining is not None:
            timer_text = Text(f"{remaining}s", justify="center", style="bold cyan")
        else:
            timer_text = Text("--:--", justify="center", style="bold cyan")
        self.layout["time"].update(Panel(timer_text, title="Timer", style="sky_blue3"))

    def jouer(self):
        with Live(self.layout, refresh_per_second=10, screen=True):
            while self.jeu.vies > 0 and not self.jeu.gagne:
                debut = time.time()
                # input thread
                self.input_value = None
                def read_input():
                    self.input_value = input("Entrez lettre ou mot: ").lower().strip()
                t = threading.Thread(target=read_input, daemon=True)
                t.start()
                # timer loop
                while time.time() - debut < 15 and self.input_value is None:
                    remaining = 15 - int(time.time() - debut)
                    self.update_layout(remaining)
                    time.sleep(0.1)
                # timeout
                if not self.input_value:
                    self.jeu.vies -= 1
                    self.jeu.message = "Temps écoulé !"
                    continue
                # process input
                fin = time.time()
                entree = self.input_value
                if not entree.isalpha():
                    self.jeu.message = "Entrée invalide"
                elif len(entree) == 1:
                    self.jeu.tester_lettre(entree, fin - debut)
                else:
                    self.jeu.tester_mot(entree, fin - debut)
                # check win
                if self.jeu.L_mot == self.jeu.mot_lettres:
                    self.jeu.gagne = True
                self.update_layout(0)
            # fin de partie
            if self.jeu.gagne:
                self.jeu.message = f"Bravo ! Mot '{self.jeu.mot}' trouvé"
            else:
                self.jeu.message = f"Perdu ! Le mot était '{self.jeu.mot}'"
            self.update_layout()
            time.sleep(3)

if __name__ == "__main__":
    client = Client()
    client.start()
