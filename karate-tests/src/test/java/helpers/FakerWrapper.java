package helpers;

import java.util.Locale;

import com.github.javafaker.Faker;

public class FakerWrapper {
    /*
     * Basic wrapper around the Faker object that gives us access to useful
     * data generation methods for our tests, and implements our own methods
     * when the Faker methods needed improvement.
     */
    static Faker faker = new Faker(new Locale("en-GB"));
        
    public static String streetAddress() {
        // returns e.g. 7158 Manual Knoll
        return faker.address().streetAddress(); 
    }
     
    public static String postalCode() {
        /* 
         * returns e.g. Y96 6ND
         * we use our own method, since the faker method can build invalid postal 
         * codes (this regex can also generate invalid postal codes, but it might
         * be an improvement)
         */ 
        String regexString = 
            "((([A-Z][0-9]{1,2})|(([A-Z][A-HJ-Y][0-9]{1,2})|"
            + "(([AZ][0-9][A-Z])|([A-Z][A-HJ-Y][0-9]?[A-Z]))))[0-9][A-Z]{2})";
        return faker.regexify(regexString);
    }

    public static String phoneNumber() {
        // returns e.g. 0800 695 0181
        return faker.phoneNumber().phoneNumber();
    }

}
