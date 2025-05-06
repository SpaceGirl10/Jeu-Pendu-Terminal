from socket import socket, AF_INET, SOCK_STREAM
import rsa
import pyaes
import threading

class Server:
    def __init__(self, host="10.69.228.82", port=4100):
        # Initialisation des attributs du serveur
        self.host = host
        self.port = port
        # Génération d'une paire de clés RSA (clé publique et privée)
        self.clef_publique, self.clef_privee = rsa.newkeys(2048)
        # Création et configuration du socket serveur
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"Serveur en écoute sur {self.host}:{self.port}")

    def reception(self, client, clef):
        # Réception d'un message chiffré via AES depuis le client
        message_code = client.recv(2048)
        aes = pyaes.AESModeOfOperationCTR(clef)
        # Déchiffrement du message
        message = aes.decrypt(message_code).decode('utf-8')
        return message

    def envoi(self, mess, client, clef):
        # Chiffrement du message avec AES
        aes = pyaes.AESModeOfOperationCTR(clef)
        message_code = aes.encrypt(mess.encode('utf-8'))
        # Envoi du message chiffré au client
        client.send(message_code)

    def handle_client(self, client, address):
        # Gestion d'un client connecté
        print(f"Connecté à {address[0]}:{address[1]}")
        # Envoi de l'exposant e de la clé publique RSA
        e = self.clef_publique.e
        n = self.clef_publique.n
        client.sendall(str(e).encode('utf-8'))
        print("e envoyé")
        # Réception d'un accusé de réception ou message intermédiaire
        reception = client.recv(2048)
        print(reception.decode('utf-8'))
        # Envoi du modulo n de la clé publique RSA
        client.sendall(str(n).encode('utf-8'))
        print("n envoyé")
        # Réception de la clé AES chiffrée avec RSA et déchiffrement
        cle_code = client.recv(2048)
        clef = rsa.decrypt(cle_code, self.clef_privee)
        print("Clé AES reçue et déchiffrée")
        
        # Boucle de communication sécurisée avec le client
        while True:
            try:
                # Réception et affichage du score chiffré
                score = self.reception(client, clef)
                print(score)
                # Envoi d’un accusé de réception chiffré
                self.envoi("bien recu".encode('utf-8'))
            except:
                # Déconnexion du client en cas d'erreur
                print(f"Client {address[0]}:{address[1]} déconnecté")
                break
        client.close()

    def start(self):
        # Démarrage du serveur : attente et gestion de nouveaux clients
        while True:
            client, address = self.sock.accept()
            # Création d’un thread pour chaque client
            thread = threading.Thread(target=self.handle_client, args=(client, address))
            thread.start()

if __name__ == "__main__":
    # Point d'entrée du programme : lancement du serveur
    server = Server()
    server.start()
