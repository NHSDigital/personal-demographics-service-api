package helpers;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.interfaces.RSAPrivateKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.time.Instant;
import java.util.Base64;
import java.util.Map;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTCreator;
import com.auth0.jwt.algorithms.Algorithm;

import org.json.JSONObject;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;


public class Utils {

    public static String getLoginFormAction(String htmlDoc) {
        /*
         * This method is relied on by the oauth2 authentication flow,
         * where users are given a web form to fill in. We parse the html
         * to retrieve the value of the form action, i.e. the url we post
         * our form details to.
         */
        Document doc = Jsoup.parse(htmlDoc);
        Element loginForm = doc.getElementById("kc-form-login");
        String action = loginForm.attr("action");
        return action;
    }

    public static String generateJWT(Map<String, String> inputs) throws NoSuchAlgorithmException, InvalidKeySpecException, IOException {

        String PRIVATE_HEADER = "-----BEGIN RSA PRIVATE KEY-----";
        String PRIVATE_FOOTER = "-----END RSA PRIVATE KEY-----";

        /*
         * This method is relied on by the application restricted 
         * authentication flow, where we need to make a request that
         * sends an encoded JWT in order to get a bearer token.
         */
        String signingKey = inputs.get("signingKey");
        String keyID = inputs.get("keyID");
        String apiKey = inputs.get("apiKey");
        String authURL = inputs.get("authURL");

        // Bouncy Castle provides so much magic when it comes to handling the key encoding...
        // (don't ask me for details...)
        java.security.Security.addProvider(
            new org.bouncycastle.jce.provider.BouncyCastleProvider()
        );

        Path path = Paths.get(signingKey);
        byte[] bytes = Files.readAllBytes(path);
        String signingKeyString = new String(bytes);
    
        signingKeyString = signingKeyString.replace(PRIVATE_HEADER, "");
        signingKeyString = signingKeyString.replace(PRIVATE_FOOTER, "");
        signingKeyString = signingKeyString.replace(" ", "");
        signingKeyString = signingKeyString.replaceAll(System.lineSeparator(), "");

        // getMimeDecoder can work around issues between different systems...
        // using getDecoder worked locally but failed on ADO...
        // https://stackoverflow.com/questions/55068969/how-to-correctly-encode-and-decode-a-string-in-base64
        byte[] privateKeyBytes = Base64.getMimeDecoder().decode(signingKeyString);        
        
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        RSAPrivateKey privateKey = (RSAPrivateKey) keyFactory.generatePrivate(new PKCS8EncodedKeySpec(privateKeyBytes));

        // Create the JWT token
        Algorithm algorithm = Algorithm.RSA512(null, privateKey);
        
        // Create a JSON object for the headers
        JSONObject headers = new JSONObject()
            .put("alg","HS512")
            .put("kid",keyID);
        
        JWTCreator.Builder jwtBuilder = JWT.create()
            .withHeader(headers.toString());

        jwtBuilder    
            .withClaim("sub", apiKey)
            .withClaim("iss", apiKey)
            .withClaim("jti", java.util.UUID.randomUUID().toString())
            .withClaim("aud", authURL)
            .withClaim("exp", Instant.now().plusSeconds(300).getEpochSecond());
                    
        String token = jwtBuilder.sign(algorithm);
        return token;
    }
    
}