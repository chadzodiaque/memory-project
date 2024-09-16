import tink
import tink_fpe
import json
from tink import cleartext_keyset_handle, JsonKeysetReader
from tink_fpe import FpeParams, UnknownCharacterStrategy

class Crypto:

    def __init__(self):
        
        # Enregistrement de Tink FPE avec le runtime Tink
        tink_fpe.register()
        

        keyset_json = json.dumps({
            "primaryKeyId": 1382079328,
            "key": [
                {
                    "keyData": {
                        "typeUrl": "type.googleapis.com/ssb.crypto.tink.FpeFfxKey",
                        "value": "EhD4978shQNRpBNaBjbF4KO4GkIQAho+QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVphYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ejAxMjM0NTY3ODk=",
                        "keyMaterialType": "SYMMETRIC"
                    },
                    "status": "ENABLED",
                    "keyId": 1382079328,
                    "outputPrefixType": "RAW"
                }
            ]
        })

        
        # Création de la keyset
        self.keyset_handle = cleartext_keyset_handle.read(tink.JsonKeysetReader(keyset_json))
        
        # Récupération de la primitive FPE
        self.fpe = self.keyset_handle.primitive(tink_fpe.Fpe)
        
        # Paramètres FPE : ici, on choisit d'ignorer les caractères inconnus
        self.params = FpeParams(strategy=UnknownCharacterStrategy.SKIP)

    def encrypt_data(self, data):
        """Chiffre les données avec FPE."""
        try:
            # Chiffrement des données
            data_bytes = data.encode('utf-8')
            crypted_data = self.fpe.encrypt(data_bytes, self.params)
            return crypted_data
        except tink.TinkError as e:
            print(f"Erreur lors du chiffrement des données : {e}")
            return None
    
    def decrypt_data(self, encrypted_data):
        """Déchiffre les données avec FPE."""
        #print(encrypted_data, type(encrypted_data), "encrypted_data")
        try:
            encrypted_data = encrypted_data.encode('utf-8')
            # Déchiffrer les données
            decrypted_data = self.fpe.decrypt(encrypted_data, self.params)
            # Convertir les données déchiffrées en chaîne si nécessaire
            if isinstance(decrypted_data, bytes):
                decrypted_data = decrypted_data.decode('utf-8')

            return decrypted_data
            
        except tink.TinkError as e:
            print(f"Erreur lors du déchiffrement des données : {e}")
            return None

