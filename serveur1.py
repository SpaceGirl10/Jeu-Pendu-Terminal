from socket import socket, AF_INET, SOCK_STREAM
import rsa
import pyaes
import threading

class Server:
    def __init__(self, host="10.69.225.142", port=4100):
        self.host = host
        self.port = port
        self.clef_publique, self.clef_privee = rsa.newkeys(2048)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"Serveur en écoute sur {self.host}:{self.port}")

    def reception(self, client, clef):
        message_code = client.recv(2048)
        aes = pyaes.AESModeOfOperationCTR(clef)
        message = aes.decrypt(message_code).decode('utf-8')
        return message

    def envoi(self, mess, client, clef):
        aes = pyaes.AESModeOfOperationCTR(clef)
        message_code = aes.encrypt(mess.encode('utf-8'))
        client.send(message_code)

    def handle_client(self, client, address):
        print(f"Connecté à {address[0]}:{address[1]}")
        e = self.clef_publique.e
        n = self.clef_publique.n
        client.sendall(str(e).encode('utf-8'))
        print("e envoyé")
        client.sendall(str(n).encode('utf-8'))
        print("n envoyé")
        cle_code = client.recv(2048)
        clef = rsa.decrypt(cle_code, self.clef_privee)
        print("Clé AES reçue et déchiffrée")
        
        while True:
            try:
                mess = self.reception(client, clef)
                print(mess)
            except:
                print(f"Client {address[0]}:{address[1]} déconnecté")
                break
        client.close()

    def start(self):
        while True:
            client, address = self.sock.accept()
            thread = threading.Thread(target=self.handle_client, args=(client, address))
            thread.start()

if __name__ == "__main__":
    server = Server()
    server.start()