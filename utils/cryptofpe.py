import tink
import tink_fpe
import json
from tink import cleartext_keyset_handle, JsonKeysetReader
from tink_fpe import FpeParams, UnknownCharacterStrategy
import os

class Crypto:

    def __init__(self):
        
        # Enregistrement de Tink FPE avec le runtime Tink
        tink_fpe.register()

        self.params = FpeParams(strategy=UnknownCharacterStrategy.SKIP)

   
    def create_keyset(self):
        """Création de la keyset."""
        # Enregistrer Tink FPE avec le runtime Tink
        tink_fpe.register()

        # Spécifier le modèle de clé à utiliser. Dans cet exemple, nous voulons une clé FF3-1 de 256 bits
        # qui peut gérer les caractères alphanumériques
        key_template = tink_fpe.fpe_key_templates.FPE_FF31_256_ALPHANUMERIC

        # Créer un keyset
        keyset_handle = tink.new_keyset_handle(key_template)
        
        keyset_json = {}

        # Ecriture du keyset dans un fichier et le sauvegarder
        with open("tmp.json", 'wt') as keyset_file:
            try:
                cleartext_keyset_handle.write(
                    tink.JsonKeysetWriter(keyset_file), keyset_handle)
            except tink.TinkError as e:
                print(f"Erreur : {e}")

        with open("tmp.json", 'r') as f:
            keyset_json = json.load(f)
        
        # Suppression du fichier temporaire
        os.remove("tmp.json")

        return keyset_json
    

    def encrypt_data(self, data, keyset_key):
        """Chiffre les données avec FPE."""
        try:
            # Chiffrement des données
            tink_fpe.register()
            keyset_handle = cleartext_keyset_handle.read(tink.JsonKeysetReader(json.dumps(keyset_key)))
            fpe = keyset_handle.primitive(tink_fpe.Fpe)
            data_bytes = data.encode('utf-8')
            crypted_data = fpe.encrypt(data_bytes, self.params)
            return crypted_data
        except tink.TinkError as e:
            print(f"Erreur lors du chiffrement des données : {e}")
            return None
    
    def decrypt_data(self, encrypted_data, keyset_key):
        """Déchiffre les données avec FPE."""
        print(encrypted_data, type(encrypted_data), "encrypted_data")
        try:
            tink_fpe.register()
            keyset_handle = cleartext_keyset_handle.read(tink.JsonKeysetReader(json.dumps(keyset_key)))
            fpe = keyset_handle.primitive(tink_fpe.Fpe)
            encrypted_data = encrypted_data.encode('utf-8')
            # Déchiffrer les données
            decrypted_data = fpe.decrypt(encrypted_data, self.params)
            # Convertir les données déchiffrées en chaîne si nécessaire
            if isinstance(decrypted_data, bytes):
                decrypted_data = decrypted_data.decode('utf-8')
            return decrypted_data 

        except tink.TinkError as e:
            print(f"Erreur lors du déchiffrement des données : {e}")
            return None

