package com.insa.tp.RoomCO2MS;

import org.springframework.boot.SpringApplication;


import java.util.UUID;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.sql.*;

@SpringBootApplication
@RestController
@RequestMapping("/measure")
public class RoomCo2MsApplication {
	
	private static final HttpClient httpClient = HttpClient.newHttpClient();

    public static void main(String[] args) {
        SpringApplication.run(RoomCo2MsApplication.class, args);
    }
    
    // Callback function pour répondre aux notifications
    @PostMapping
    public ResponseEntity<String> handleNotification(
            @RequestBody String notificationBody, // Capture le contenu brut de la notification
            @RequestHeader HttpHeaders headers    // Capture les en-têtes HTTP
    ) {

    	// Parse la notification pour en extraire le contenu
    	try {
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode rootNode = objectMapper.readTree(notificationBody);

            JsonNode message = rootNode.get("m2m:sgn");
            
            // Détecte la demande d'authorisation de notifier
            if(message.has("vrq") && message.get("vrq").asBoolean()) {
            	System.out.println("=== Subscription verified ===");
            	System.out.println(message);
            }
            // Ou parse le contenu du message si c'est une ressource
            else {
            	
            	int switchState = message.get("nev").get("rep").get("m2m:cin").get("con").asInt(); 
            	System.out.println("=== New switch state ===");
            	System.out.println(switchState);
            	
            	
            	// Envoi de la donnée à la LED	            		
        		String payload = "{\"m2m:cin\":{\"rn\":\"" + generate64BitUUID() + "\",\"con\":\"" + switchState + "\"}}";
        		System.out.println("DEBUG: Payload constructed: " + payload);

        		String parentUrl = "http://localhost:8080/cse-in/Notebook-Application/LED";
        		System.out.println("DEBUG: Parent URL: " + parentUrl);

        		try {
        		    HttpRequest request = generateHeaders("application/json;ty=4", "Cmyself")
        		            .uri(URI.create(parentUrl))
        		            .POST(HttpRequest.BodyPublishers.ofString(payload))
        		            .build();

        		    System.out.println("INFO: Sending HTTP request to: " + parentUrl);
        		    HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        		    System.out.println("RESPONSE: " + response);

        		} catch (Exception e) {
        		    System.err.println("ERROR: Exception during room creation: " + e.getMessage());
        		}        	
            			
            }
            	
           
        } catch (Exception e) {
            // Gérer les erreurs de parsing JSON
            System.err.println("Erreur lors du traitement de la notification : " + e.getMessage());
            return new ResponseEntity<>("Erreur de traitement", HttpStatus.BAD_REQUEST);
        }
        

        // Retourne une réponse HTTP 2000 = "OK" 
        HttpHeaders responseHeaders = new HttpHeaders();
        responseHeaders.add("X-M2M-RSC", "2000"); // Indique le succès (2000 est le code M2M pour "OK")
        responseHeaders.add("X-M2M-RI", headers.getFirst("X-M2M-RI")); // Reprend l'ID de requête

        return new ResponseEntity<>("Notification received", responseHeaders, HttpStatus.OK);
    }
    

    // Fonction pour générer un ID de container random et éviter les collisions de nommage  
    private static long generate64BitUUID() {
        UUID uuid = UUID.randomUUID();
        return uuid.getMostSignificantBits(); // Utiliser les 64 bits les plus significatifs
    }
    
    // Fonction de génération d'headers
    private static HttpRequest.Builder generateHeaders(String contentType, String originator) {
        return HttpRequest.newBuilder()
                .header("X-M2M-Origin", originator)
                .header("Content-Type", contentType)
                .header("X-M2M-RI", generateRequestId())
                .header("X-M2M-RVI", "3");
    }
    
    private static String generateRequestId() {
        return UUID.randomUUID().toString();
    }
}
