package helpers;

import java.util.Locale;

import com.github.javafaker.Faker;

public class FakerWrapper {
    static Faker faker = new Faker(new Locale("en-GB"));
        
    public static String streetAddress() {
        // return e.g. 7158 Manual Knoll
        return faker.address().streetAddress(); 
    }
     
    public static String postCode() {
        // return e.g. Y96 6ND
        // we use our own method, since the faker method can build invalid post codes
        String regexString = 
            "([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|"
            + "(([AZa-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z]))))[0-9][A-Za-z]{2})";
        return faker.regexify(regexString).toUpperCase();
    }

    public static String phoneNumber() {
        // return e.g. 0800 695 0181
        return faker.phoneNumber().phoneNumber();
    }

}
