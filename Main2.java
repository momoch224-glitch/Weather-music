import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class Main2 {

    public static void main(String[] args) {

        String json =
                "{\n" +
                "  \"bpm\": 90,\n" +
                "  \"key\": \"C\",\n" +
                "  \"patterns\": [\n" +
                "    {\n" +
                "      \"name\": \"A\",\n" +
                "      \"chords\": [\"C\", \"G\", \"Am\", \"Em\"]\n" +
                "    },\n" +
                "    {\n" +
                "      \"name\": \"B\",\n" +
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

            ProcessBuilder pb = new ProcessBuilder(
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

        File finalMidi = new File("final.mid");

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