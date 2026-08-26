import java.io.*;
import java.util.*;

public class Main {

    public static void main(String[] args) {

        try {

            System.setOut(new PrintStream(System.out, true, "UTF-8"));
            System.setErr(new PrintStream(System.err, true, "UTF-8"));

            Scanner scanner = new Scanner(System.in);

            System.out.print("都市名を入力してください: ");
            String city = scanner.nextLine();

            System.out.print("i (-10～10) を入力してください: ");
            int i = scanner.nextInt();

            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    "-Xutf8",
                    "JavaPython/weather.py",
                    city
            );

            pb.redirectErrorStream(true);

            Process process = pb.start();

            BufferedReader reader =
                    new BufferedReader(
                            new InputStreamReader(
                                    process.getInputStream(),
                                    "UTF-8"
                            )
                    );

            String json = reader.readLine();
            json = json.replace(": ", ":");
            System.out.println(
                "DEBUG JSON = " + json
            );

            process.waitFor();

            if (json == null) {

                System.out.println(
                        "weather.py から結果を取得できません"
                );

                return;
            }

            String season =
                    clean(extract(json, "season"));

            String condition =
                    clean(extract(json, "condition"));

            String weather;

            switch (condition) {

                case "Clear":
                    weather = "晴れ";
                    break;

                case "Clouds":
                    weather = "曇り";
                    break;

                case "Rain":
                    weather = "雨";
                    break;

                default:
                    weather = "不明";
            }

            int baseNote =
                    switch (season) {

                        case "春" -> 60;
                        case "夏" -> 67;
                        case "秋" -> 64;
                        case "冬" -> 62;

                        default -> 60;
                    };

            String type =
                    weather.equals("晴れ")
                            ? "dur"
                            : "moll";

            int root =
                    weather.equals("晴れ")
                            ? baseNote
                            : baseNote + 9;

            int finalNote =
                    (root + i + 120) % 12;

            String[] noteNames = {
                    "C",
                    "C#",
                    "D",
                    "D#",
                    "E",
                    "F",
                    "F#",
                    "G",
                    "G#",
                    "A",
                    "A#",
                    "B"
            };

            String key1 =
                    noteNames[root % 12];

            String key2 =
                    noteNames[finalNote];

            System.out.println(
                    "季節 = " + season
            );

            System.out.println(
                    "天気 = " + weather
            );

            System.out.println(
                    "生成キー① = "
                            + key1
                            + " "
                            + type
            );

            System.out.println(
                    "生成キー② = "
                            + key2
                            + " "
                            + type
            );

            String[] patternA;

            switch (season) {

                case "春":

                    patternA = new String[]{
                            "I",
                            "V",
                            "VIm",
                            "IIIm"
                    };

                    break;

                case "夏":

                    patternA = new String[]{
                            "I",
                            "V",
                            "VIm",
                            "IV"
                    };

                    break;

                case "秋":

                    patternA = new String[]{
                            "IV",
                            "III",
                            "VI",
                            "V"
                    };

                    break;

                default:

                    patternA = new String[]{
                            "VIm",
                            "IV",
                            "V",
                            "I"
                    };
            }

            String[] patternB;

            switch (weather) {

                case "晴れ":

                    patternB = new String[]{
                            "IV",
                            "V",
                            "IIIm",
                            "VIm"
                    };

                    break;

                case "曇り":

                    patternB = new String[]{
                            "I",
                            "IV",
                            "V",
                            "V"
                    };

                    break;

                default:

                    patternB = new String[]{
                            "IV",
                            "I",
                            "IIm",
                            "VIm"
                    };
            }

            String[] chordsA =
                    convertRomanToKey(
                            key1,
                            patternA
                    );

            String[] chordsB =
                    convertRomanToKey(
                            key1,
                            patternB
                    );

            writeJson(
                    key1,
                    chordsA,
                    chordsB
            );

            System.out.println(
                    "chords.json 作成完了"
            );

            ProcessBuilder python =
                    new ProcessBuilder(
                            "venv38\\Scripts\\python.exe",
                        "Main.py"
                    );

            python.inheritIO();

            Process p =
                    python.start();

            p.waitFor();

            System.out.println(
                    "Main.py 実行完了"
            );

        }

        catch (Exception e) {

            e.printStackTrace();
        }
    }

    static String[] convertRomanToKey(
            String key,
            String[] roman
    ) {

        Map<String, String[]> map =
                new HashMap<>();

        map.put(
                "C",
                new String[]{
                        "C",
                        "Dm",
                        "Em",
                        "F",
                        "G",
                        "Am",
                        "Bdim"
                }
        );

        map.put(
                "G",
                new String[]{
                        "G",
                        "Am",
                        "Bm",
                        "C",
                        "D",
                        "Em",
                        "F#dim"
                }
        );

        map.put(
                "D",
                new String[]{
                        "D",
                        "Em",
                        "F#m",
                        "G",
                        "A",
                        "Bm",
                        "C#dim"
                }
        );

        map.put(
                "A",
                new String[]{
                        "A",
                        "Bm",
                        "C#m",
                        "D",
                        "E",
                        "F#m",
                        "G#dim"
                }
        );

        map.put(
                "F",
                new String[]{
                        "F",
                        "Gm",
                        "Am",
                        "A#",
                        "C",
                        "Dm",
                        "Edim"
                }
        );

        String[] scale =
                map.getOrDefault(
                        key,
                        map.get("C")
                );

        String[] result =
                new String[roman.length];

        for (int i = 0; i < roman.length; i++) {

            switch (roman[i]) {

                case "I":
                    result[i] = scale[0];
                    break;

                case "IIm":
                    result[i] = scale[1];
                    break;

                case "IIIm":
                    result[i] = scale[2];
                    break;

                case "IV":
                    result[i] = scale[3];
                    break;

                case "V":
                    result[i] = scale[4];
                    break;

                case "VIm":
                    result[i] = scale[5];
                    break;

                default:
                    result[i] = scale[0];
            }
        }

        return result;
    }

    static void writeJson(
            String key,
            String[] a,
            String[] b
    ) throws Exception {

        PrintWriter pw =
                new PrintWriter(
                        new FileWriter(
                                "chords.json"
                        )
                );

        pw.println("{");
        pw.println("  \"bpm\": 90,");
        pw.println("  \"key\": \"" + key + "\",");
        pw.println("  \"patterns\": [");

        pw.println("    {");
        pw.println("      \"name\": \"A\",");
        pw.println("      \"chords\": " +
                Arrays.toString(a)
                        .replace(" ", "")
                        .replace("[", "[\"")
                        .replace("]", "\"]")
                        .replace(",", "\",\""));
        pw.println("    },");

        pw.println("    {");
        pw.println("      \"name\": \"B\",");
        pw.println("      \"chords\": " +
                Arrays.toString(b)
                        .replace(" ", "")
                        .replace("[", "[\"")
                        .replace("]", "\"]")
                        .replace(",", "\",\""));
        pw.println("    }");

        pw.println("  ]");
        pw.println("}");

        pw.close();
    }

    static String extract(
            String json,
            String key
    ) {

        String pattern =
                "\"" + key + "\":";

        int start =
                json.indexOf(pattern);

        if (start == -1)
            return "";

        start += pattern.length();

        if (json.charAt(start) == '"') {

            start++;

            int end =
                    json.indexOf(
                            "\"",
                            start
                    );

            return json.substring(
                    start,
                    end
            );
        }

        return "";
    }

    static String clean(
            String s
    ) {

        return s == null
                ? ""
                : s.replace("\"", "")
                .trim();
    }
}