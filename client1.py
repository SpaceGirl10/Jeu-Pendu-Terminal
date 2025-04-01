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
from rich.padding import Padding
from rich.table import Table
from rich import box
from rich.live import Live
from rich.progress import Progress

class Pendu:
    def __init__(self, fichier_mots="liste_mots.txt", vies=6):
        self.fichier_mots = fichier_mots
        self.vies = vies
        self.mot = self.choisir_mot()
        self.mot_lettres = list(self.mot)
        self.L_mot = ["_" for _ in self.mot]
        self.gagne = False
        self.score = 0
        
    
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
    
    def jouer(self):
        while self.vies > 0:
            print(f"L'avancement du mot : {''.join(self.L_mot)} - Vies restantes : {self.vies} - Score : {self.score}")
            debut = time.time()
            entree = input("Entrez une lettre ou un mot : ").lower().strip()
            fin = time.time()

            if not entree.isalpha():
                print("Entrée invalide, veuillez entrer uniquement des lettres.")
                continue

            temps_reponse = fin - debut
            if temps_reponse > 15:
                print("Temps écoulé ! Vous avez dépassé la limite de 15 secondes.")
                self.vies -= 1
                continue

            if len(entree) == 1:
                self.tester_lettre(entree, temps_reponse)
            else:
                if self.tester_mot(entree, temps_reponse):
                    break
        
        if self.gagne:
            print(f"Bravo ! Vous avez trouvé le mot '{self.mot}' avec {self.vies} vies restantes ! Score final : {self.score}")
            
        else:
            print(f"Dommage... Le mot était '{self.mot}'. Score final : {self.score}")
            
    
    def tester_lettre(self, lettre, temps_reponse):
        if lettre in self.L_mot:
            print("Vous avez déjà trouvé cette lettre.")
            return
        
        if lettre in self.mot_lettres:
            for i, l in enumerate(self.mot_lettres):
                if l == lettre:
                    self.L_mot[i] = lettre
            self.score += max(100 - int(temps_reponse * 10), 20)
            print("Bonne lettre !")
        else:
            print("Mauvaise lettre, vous perdez une vie !")
            self.vies -= 1
            if self.score != 0 and self.score > 5: self.score -= 5
    
    def tester_mot(self, mot_propose, temps_reponse):
        if mot_propose == self.mot:
            self.gagne = True
            self.score += max(200 - int(temps_reponse * 10), 20)
            return True
        else:
            print("Ce n'est pas le bon mot, vous perdez une vie !")
            self.vies -= 1
            if self.score != 0 and self.score > 10: self.score -= 10
            return False

class Client:
    def __init__(self, host="10.69.224.231", port=4100):
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
        while True:
            instance_jeu = Pendu()
            instance_jeu.jouer()
            score = instance_jeu.score
            self.envoi(str(score))
            self.reception()
            exit()

class Interface:

    def __init__(self):
            self.console = Console()
            self.layout = Layout()
            self.titre = Text("JEU DU PENDU", justify="center")
            self.classement = Table(box=box.DOUBLE, title="Classement", style="salmon1")
            self.classement.header_style = "light_goldenrod2"
            self.classement.title_style = "light_goldenrod2"
            self.classement.add_column("Joueur", justify="right", style="light_goldenrod2", min_width=20)
            self.classement.add_column("Score", justify="right", style="light_goldenrod2", min_width=20)
            
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
            
            self.layout["lower"].size = None
            self.layout["lower"].ratio = 3
            self.layout["classement"].size = None
            self.layout["classement"].ratio = 15

    def update_classement(self, joueurs_scores):
        self.classement.rows.clear()
        for joueur, score in joueurs_scores.items():
            self.classement.add_row(joueur, str(score))
    
    def countdown_timer(self, seconds):
        with Live(self.layout, refresh_per_second=1):
            for remaining in range(seconds, -1, -1):
                timer_text = Text(f"Temps restant : {remaining}s", justify="center", style="medium_turquoise")
                self.layout["time"].update(Panel(timer_text, style="salmon1"))
                time.sleep(1)
    
    def display_interface(self):
        self.console.print(self.layout)

    

if __name__ == "__main__":
    client = Client()
    client.start()
    interface = Interface()
    interface.display_interface()
    
