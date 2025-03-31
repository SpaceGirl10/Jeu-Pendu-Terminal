import random
import time

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

if __name__ == "__main__":
    jeu = Pendu()
    jeu.jouer()
exit()