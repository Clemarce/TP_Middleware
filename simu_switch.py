import requests
import json
import uuid
import time

# Configuration du serveur oneM2M
CSE_URL = "http://localhost:8080/cse-in"  # Mise à jour pour refléter le bon chemin
AE_NAME = "Notebook-Application" # Nom de l'AE

def generate_headers(content_type, origin="Cmyself"):
    return {
        'X-M2M-Origin': origin,  # Identifiant de l'AE ou utilisateur admin
        'Content-Type': content_type,  # Type pour la création
        'X-M2M-RI': str(uuid.uuid4()),  # Identifiant unique généré dynamiquement
        'X-M2M-RVI': '3'  # Version de publication conforme au serveur
    }


# Création d'une instance de container (contenant des données)
def create_content_instance(container_url, content, origin="Cmyself"):
    
    
    payload = {
        "m2m:cin": {
            "rn": str(uuid.uuid4()),
            "con": content
        }
    }

    try:
        response = requests.post(container_url, headers=generate_headers('application/json;ty=4', origin=origin), data=json.dumps(payload))

        if response.status_code in [200, 201]:
            print("Instance de contenu créée avec succès.")
        elif response.status_code == 400:
            print(f"Requête incorrecte pour l'instance de contenu: {response.text}")
        elif response.status_code == 500:
            print(f"Erreur interne du serveur lors de la création de l'instance de contenu: {response.text}")
        else:
            print(f"Erreur lors de la création de l'instance de contenu: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Exception lors de la création de l'instance de contenu: {e}")



# MAIN
def main():

    container_url = f"{CSE_URL}/{AE_NAME}/Switch"
    data = "1"

    #Boucle d'envoi de données
    i = 0
    while(i<4):
        # Ajouter des données dans un conteneur
        create_content_instance(container_url, data)
        if(data == "1"):
            data ="0"
        elif(data == "0"):
            data = "1"

        i += 1
        time.sleep(5)
    


if __name__ == "__main__":
    main()