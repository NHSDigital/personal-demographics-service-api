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
        
    public static String phoneNumber() {
        // returns e.g. 0800 695 0181
        return faker.phoneNumber().phoneNumber();
    }

    public static String givenName() {
        // returns e.g. "John"
        return faker.name().firstName();
    }

    public static String cityName() {
        return faker.address().city();
    }

}
