import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class Main2 {

    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);

        System.out.println("Select rhythm style:");
        System.out.println("low");
        System.out.println("medium");
        System.out.println("high");
        System.out.print("> ");

        String rhythmStyle =
                scanner.nextLine()
                        .trim()
                        .toLowerCase();

        if (!rhythmStyle.equals("low")
                && !rhythmStyle.equals("medium")
                && !rhythmStyle.equals("high")) {

            System.out.println("Invalid input");
            return;
        }

        String json =
                "{\n" +
                "  \"bpm\": 90,\n" +
                "  \"key\": \"C\",\n" +
                "  \"rhythm_style\": \"" + rhythmStyle + "\",\n" +
                "  \"patterns\": [\n" +

                "    {\n" +
                "      \"name\": \"A\",\n" +
                "      \"chords\": [\"C\", \"G\", \"Am\", \"Em\"]\n" +
                "    },\n" +

                "    {\n" +
                "      \"name\": \"B\",\n" +
                "      \"chords\": [\"F\", \"G\", \"Em\", \"Am\"]\n" +
                "    },\n" +

                "    {\n" +
                "      \"name\": \"C\",\n" +
                "      \"chords\": [\"F\", \"C\", \"Dm\", \"Am\"]\n" +
                "    },\n" +

                "    {\n" +
                "      \"name\": \"D\",\n" +
                "      \"chords\": [\"C\", \"G\", \"Am\", \"F\"]\n" +
                "    },\n" +

                "    {\n" +
                "      \"name\": \"E\",\n" +
                "      \"chords\": [\"F\", \"G\", \"Em\", \"Am\"]\n" +
                "    }\n" +

                "  ]\n" +
                "}";

        try (FileWriter file = new FileWriter("chords.json")) {

            file.write(json);

            System.out.println("chords.json created");

        } catch (IOException e) {

            e.printStackTrace();
            return;
        }

        try {

            ProcessBuilder pb =
                    new ProcessBuilder(
                            "python",
                            "Main.py"
                    );

            pb.inheritIO();

            Process process = pb.start();

            int exitCode = process.waitFor();

            System.out.println(
                    "Python exit code = " + exitCode
            );

        } catch (Exception e) {

            e.printStackTrace();
            return;
        }

        File finalMidi =
                new File("final.mid");

        if (finalMidi.exists()) {

            System.out.println(
                    "final.mid created"
            );

        } else {

            System.out.println(
                    "final.mid not found"
            );
        }

        System.out.println("Java finished");
    }
}