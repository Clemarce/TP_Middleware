import requests
import json
import uuid

# Configuration du serveur oneM2M
CSE_URL = "http://localhost:8080/cse-in"  # Mise à jour pour refléter le bon chemin

def generate_headers(content_type, origin="Cmyself"):
    return {
        'X-M2M-Origin': origin,  # Identifiant de l'AE ou utilisateur admin
        'Content-Type': content_type,  # Type pour la création
        'X-M2M-RI': str(uuid.uuid4()),  # Identifiant unique généré dynamiquement
        'X-M2M-RVI': '3'  # Version de publication conforme au serveur
    }

# Création d'AE
def register_ae(parent_url, ae_name):
    payload = {
        "m2m:ae": {
            "rn": ae_name,
            "api": "NnotebookAE",  # Application ID
            "rr": True,  # Indique que l'AE souhaite recevoir des requêtes
            "srv": ["3"]  # Versions supportées
        }
    }
    try:
        response = requests.post(parent_url, headers=generate_headers('application/json;ty=2'), data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print(f"AE '{ae_name}' enregistré avec succès.")
        elif response.status_code == 400:
            print(f"Requête incorrecte pour l'AE '{ae_name}': {response.text}")
        elif response.status_code == 500:
            print(f"Erreur interne du serveur lors de l'enregistrement de l'AE '{ae_name}': {response.text}")
        else:
            print(f"Erreur lors de l'enregistrement de l'AE '{ae_name}': {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Exception lors de l'enregistrement de l'AE '{ae_name}': {e}")

# Création de container
def create_container(container_name, parent_url, origin="Cmyself"):
    payload = {
        "m2m:cnt": {
            "rn": container_name,
            "mni": 100              #Limite le container à ce nombre d'instances. Dépenser ce nombre supprime l'instance la plus ancienne.
        }
    }
    try:
        response = requests.post(parent_url, headers=generate_headers('application/json;ty=3', origin=origin), data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print(f"Conteneur '{container_name}' créé avec succès.")
        elif response.status_code == 400:
            print(f"Requête incorrecte pour le conteneur '{container_name}': {response.text}")
        elif response.status_code == 500:
            print(f"Erreur interne du serveur lors de la création du conteneur '{container_name}': {response.text}")
        else:
            print(f"Erreur lors de la création du conteneur '{container_name}': {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Exception lors de la création du conteneur '{container_name}': {e}")


# Création d'une souscription
def create_subscription(container_url, notification_url, subscription_name="Subscription", origin="Cmyself"):
    payload = {
        "m2m:sub": {
            "rn": subscription_name,
            "nu": [notification_url],  # URL vers laquelle envoyer les notifications
            "nct": 1,  # Type de notification (1: notification sur modification)
            "enc": {
                "net": [1, 3]  # Types d'événements: creation et update
            }
        }
    }
    
    try:
        # Envoie la requête de création de la souscription
        response = requests.post(container_url, headers=generate_headers('application/json;ty=23', origin=origin), data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print(f"Souscription '{subscription_name}' créée avec succès.")
        elif response.status_code == 400:
            print(f"Requête incorrecte pour la souscription '{subscription_name}': {response.text}")
        elif response.status_code == 500:
            print(f"Erreur interne du serveur lors de la création de la souscription '{subscription_name}': {response.text}")
        else:
            print(f"Erreur lors de la création de la souscription '{subscription_name}': {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Exception lors de la création de la souscription '{subscription_name}': {e}")

# MAIN
def main():

    # Créer l'AE
    ae_name = "Notebook-Application"
    register_ae(CSE_URL, ae_name)

    # Créer des conteneurs
    containers = ["Switch", "LED"]
    for container in containers:
        create_container(container, f"{CSE_URL}/{ae_name}", origin="Cmyself")

    container_url = f"{CSE_URL}/{ae_name}/Switch"  # URL du container
    notification_url = "http://localhost:8090/measure"  #URL de notre service java
    create_subscription(container_url, notification_url)


if __name__ == "__main__":
    main()