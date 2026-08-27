import java.io.*;
import java.util.*;

public class Main {

    public static void main(String[] args) {

        try {

            System.setOut(new PrintStream(System.out, true, "UTF-8"));
            System.setErr(new PrintStream(System.err, true, "UTF-8"));

            // 修正1: キーボード入力を廃止し、引数から都市名を取得（デフォルトはTokyo）
            String city = (args.length > 0 && !args[0].isEmpty()) ? args[0] : "Tokyo";

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
            if (json != null) {
                json = json.replace(": ", ":");
                System.out.println("DEBUG JSON = " + json);
            }

            process.waitFor();

            if (json == null) {
                System.out.println("weather.py から結果を取得できません");
                return;
            }

            String season = clean(extract(json, "season"));
            String condition = clean(extract(json, "condition"));
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

            String[] majorKeys = {
                    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
            };

            String[] minorKeys = {
                    "Am", "A#m", "Bm", "Cm", "C#m", "Dm", "D#m", "Em", "Fm", "F#m", "Gm", "G#m"
            };

            Random random = new Random();
            String key1;
            String type;

            if (weather.equals("晴れ")) {
                key1 = majorKeys[random.nextInt(majorKeys.length)];
                type = "dur";
            } else if (weather.equals("雨")) {
                key1 = minorKeys[random.nextInt(minorKeys.length)];
                type = "moll";
            } else {
                boolean major = random.nextBoolean();
                if (major) {
                    key1 = majorKeys[random.nextInt(majorKeys.length)];
                    type = "dur";
                } else {
                    key1 = minorKeys[random.nextInt(minorKeys.length)];
                    type = "moll";
                }
            }

            System.out.println("季節 = " + season);
            System.out.println("天気 = " + weather);
            String key2 = "";

            if (weather.equals("晴れ")) {
                if (random.nextBoolean()) {
                    key2 = getDominant(key1);
                } else {
                    key2 = getSubDominant(key1);
                }
            } else if (weather.equals("雨")) {
                if (random.nextBoolean()) {
                    key2 = getDominant(key1);
                } else {
                    key2 = getSubDominant(key1);
                }
            } else {
                key2 = getParallel(key1);
            }

            System.out.println("生成キー① = " + key1 + " " + type);
            System.out.println("生成キー② = " + key2);

            String[] patternA;
            switch (season) {
                case "春": patternA = new String[]{"I", "V", "VIm", "IIIm"}; break;
                case "夏": patternA = new String[]{"I", "V", "VIm", "IV"}; break;
                case "秋": patternA = new String[]{"IV", "III", "VI", "V"}; break;
                default:   patternA = new String[]{"VIm", "IV", "V", "I"};
            }

            String[] patternB;
            switch (weather) {
                case "晴れ": patternB = new String[]{"IV", "V", "IIIm", "VIm"}; break;
                case "曇り": patternB = new String[]{"I", "IV", "V", "V"}; break;
                default:   patternB = new String[]{"IV", "I", "IIm", "VIm"};
            }

            String[] patternC;
            switch (weather) {
                case "晴れ": patternC = new String[]{"IV", "V", "IIIm", "VIm"}; break;
                case "曇り": patternC = new String[]{"IV", "IIIm", "VIm", "I"}; break;
                default:   patternC = new String[]{"VIm", "IV", "I", "V"};
            }

            String[] patternD;
            switch (weather) {
                case "晴れ": patternD = new String[]{"IIm", "V", "I", "VIm"}; break;
                case "曇り": patternD = new String[]{"IIm", "IIIm", "IV", "V"}; break;
                default:   patternD = new String[]{"IV", "V", "VIm", "IIIm"};
            }

            String[] patternE;
            switch (season) {
                case "春": patternE = new String[]{"IV", "V", "I", "I"}; break;
                case "夏": patternE = new String[]{"IV", "V", "VIm", "I"}; break;
                case "秋": patternE = new String[]{"IV", "IIIm", "IIm", "I"}; break;
                default:   patternE = new String[]{"VIm", "IV", "V", "I"};
            }

            String convertKey = key1;
            if (convertKey.endsWith("m")) {
                convertKey = convertKey.substring(0, convertKey.length() - 1);
            }
            String convertKey2 = key2;
            if (convertKey2.endsWith("m")) {
                convertKey2 = convertKey2.substring(0, convertKey2.length() - 1);
            }

            String[] chordsD;
            String[] chordsE;

            if (key2.endsWith("m")) {
                chordsD = convertRomanToMinorKey(convertKey2, patternD);
                chordsE = convertRomanToMinorKey(convertKey2, patternE);
            } else {
                chordsD = convertRomanToKey(convertKey2, patternD);
                chordsE = convertRomanToKey(convertKey2, patternE);
            }

            String[] chordsA = convertRomanToKey(convertKey, patternA);
            String[] chordsB = convertRomanToKey(convertKey, patternB);
            String[] chordsC;

            if (type.equals("moll")) {
                chordsC = convertMinorPatternC(convertKey);
            } else {
                chordsC = convertRomanToKey(convertKey, patternC);
            }

            System.out.println("season debug = [" + season + "]");

            // BPM計算
            int bpm = calculateBPM();

            // 修正2: 最後に「bpm」を追加して9個の引数を渡す！
            writeJson(
                season,
                key1,
                key2,
                chordsA,
                chordsB,
                chordsC,
                chordsD,
                chordsE,
                bpm    
                );

            System.out.println("chords.json 作成完了");

            // 修正3: WindowsパスではなくLinux共通の "python" を呼び出す
            ProcessBuilder python = new ProcessBuilder("python", "Main.py");
            python.inheritIO();
            Process p = python.start();
            p.waitFor();

            System.out.println("Main.py 実行完了");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    static String getDominant(String key) {
        String[] major = {"C","G","D","A","E","B","F#","C#","G#","D#","A#","F"};
        String[] minor = {"Am","Em","Bm","F#m","C#m","G#m","D#m","A#m","Fm","Cm","Gm","Dm"};

        if (key.endsWith("m")) {
            for (int i = 0; i < minor.length; i++) {
                if (minor[i].equals(key)) return minor[(i + 1) % minor.length];
            }
        } else {
            for (int i = 0; i < major.length; i++) {
                if (major[i].equals(key)) return major[(i + 1) % major.length];
            }
        }
        return key;
    }

    static String getSubDominant(String key) {
        String[] major = {"C","G","D","A","E","B","F#","C#","G#","D#","A#","F"};
        String[] minor = {"Am","Em","Bm","F#m","C#m","G#m","D#m","A#m","Fm","Cm","Gm","Dm"};

        if (key.endsWith("m")) {
            for (int i = 0; i < minor.length; i++) {
                if (minor[i].equals(key)) return minor[(i - 1 + minor.length) % minor.length];
            }
        } else {
            for (int i = 0; i < major.length; i++) {
                if (major[i].equals(key)) return major[(i - 1 + major.length) % major.length];
            }
        }
        return key;
    }

    static String getParallel(String key) {
        switch (key) {
            case "C": return "Am";
            case "Am": return "C";
            case "G": return "Em";
            case "Em": return "G";
            case "D": return "Bm";
            case "Bm": return "D";
            case "A": return "F#m";
            case "F#m": return "A";
            case "E": return "C#m";
            case "C#m": return "E";
            case "B": return "G#m";
            case "G#m": return "B";
            case "F": return "Dm";
            case "Dm": return "F";
            case "C#": return "A#m";
            case "A#m": return "C#";
            case "D#": return "Cm";
            case "Cm": return "D#";
            case "F#": return "D#m";
            case "D#m": return "F#";
            case "G#": return "Fm";
            case "Fm": return "G#";
            case "A#": return "Gm";
            case "Gm": return "A#";
            default: return key;
        }
    }

    static String baseChord(String chord) {
        return chord.replace("dim", "").replace("m", "");
    }

    static String buildChord(String chord, String suffix) {
        chord = baseChord(chord);
        if (suffix.equals("m")) return chord + "m";
        if (suffix.equals("7")) return chord + "7";
        if (suffix.equals("m7")) return chord + "m7";
        if (suffix.equals("M7")) return chord + "M7";
        return chord;
    }

    static String[] convertRomanToKey(String key, String[] roman) {
        Map<String, String[]> map = new HashMap<>();
        Map<String, Integer> romanMap = new HashMap<>();

        romanMap.put("I", 0);
        romanMap.put("II", 1);
        romanMap.put("III", 2);
        romanMap.put("IV", 3);
        romanMap.put("V", 4);
        romanMap.put("VI", 5);
        romanMap.put("VII", 6);

        map.put("C", new String[]{"C", "Dm", "Em", "F", "G", "Am", "Bdim"});
        map.put("G", new String[]{"G", "Am", "Bm", "C", "D", "Em", "F#dim"});
        map.put("D", new String[]{"D", "Em", "F#m", "G", "A", "Bm", "C#dim"});
        map.put("A", new String[]{"A", "Bm", "C#m", "D", "E", "F#m", "G#dim"});
        map.put("E", new String[]{"E", "F#m", "G#m", "A", "B", "C#m", "D#dim"});
        map.put("B", new String[]{"B", "C#m", "D#m", "E", "F#", "G#m", "A#dim"});
        map.put("F#", new String[]{"F#", "G#m", "A#m", "B", "C#", "D#m", "Fdim"});
        map.put("C#", new String[]{"C#", "D#m", "Fm", "F#", "G#", "A#m", "Cdim"});
        map.put("G#", new String[]{"G#", "A#m", "Cm", "C#", "D#", "Fm", "Gdim"});
        map.put("F", new String[]{"F", "Gm", "Am", "A#", "C", "Dm", "Edim"});
        map.put("D#", new String[]{"D#", "Fm", "Gm", "G#", "A#", "Cm", "Ddim"});
        map.put("A#", new String[]{"A#", "Cm", "Dm", "D#", "F", "Gm", "Adim"});

        String[] scale = map.getOrDefault(key, map.get("C"));
        String[] result = new String[roman.length];

        for (int i = 0; i < roman.length; i++) {
            String symbol = roman[i];
            String romanPart = "";

            for (String r : romanMap.keySet()) {
                if (symbol.startsWith(r)) {
                    if (r.length() > romanPart.length()) {
                        romanPart = r;
                    }
                }
            }

            String suffix = symbol.substring(romanPart.length());
            int index = romanMap.get(romanPart);
            String chord = scale[index];

            if (suffix.equals("m")) {
                chord = baseChord(chord) + "m";
            } else if (suffix.equals("7")) {
                chord = baseChord(chord) + "7";
            } else if (suffix.equals("m7")) {
                chord = baseChord(chord) + "m7";
            } else if (suffix.equals("M7")) {
                chord = baseChord(chord) + "M7";
            }

            result[i] = chord;
        }

        return result;
    }

    static String[] convertRomanToMinorKey(String key, String[] roman) {
        Map<String, String[]> map = new HashMap<>();

        map.put("A", new String[]{"Am", "Bdim", "C", "Dm", "Em", "F", "G"});
        map.put("A#", new String[]{"A#m", "Cdim", "C#", "D#m", "Fm", "F#", "G#"});
        map.put("B", new String[]{"Bm", "C#dim", "D", "Em", "F#m", "G", "A"});
        map.put("C", new String[]{"Cm", "Ddim", "D#", "Fm", "Gm", "G#", "A#"});
        map.put("C#", new String[]{"C#m", "D#dim", "E", "F#m", "G#m", "A", "B"});
        map.put("D", new String[]{"Dm", "Edim", "F", "Gm", "Am", "A#", "C"});
        map.put("D#", new String[]{"D#m", "Fdim", "F#", "G#m", "A#m", "B", "C#"});
        map.put("E", new String[]{"Em", "F#dim", "G", "Am", "Bm", "C", "D"});
        map.put("F", new String[]{"Fm", "Gdim", "G#", "A#m", "Cm", "C#", "D#"});
        map.put("F#", new String[]{"F#m", "G#dim", "A", "Bm", "C#m", "D", "E"});
        map.put("G", new String[]{"Gm", "Adim", "A#", "Cm", "Dm", "D#", "F"});
        map.put("G#", new String[]{"G#m", "A#dim", "B", "C#m", "D#m", "E", "F#"});

        Map<String, Integer> romanMap = new HashMap<>();
        romanMap.put("I", 0);
        romanMap.put("II", 1);
        romanMap.put("III", 2);
        romanMap.put("IV", 3);
        romanMap.put("V", 4);
        romanMap.put("VI", 5);
        romanMap.put("VII", 6);

        String[] scale = map.getOrDefault(key, map.get("A"));
        String[] result = new String[roman.length];

        for (int i = 0; i < roman.length; i++) {
            String symbol = roman[i];
            String romanPart = "";

            for (String r : romanMap.keySet()) {
                if (symbol.startsWith(r)) {
                    if (r.length() > romanPart.length()) {
                        romanPart = r;
                    }
                }
            }

            String suffix = symbol.substring(romanPart.length());
            int index = romanMap.get(romanPart);
            String chord = scale[index];

            if (suffix.equals("m")) {
                chord = baseChord(chord) + "m";
            } else if (suffix.equals("7")) {
                chord = baseChord(chord) + "7";
            } else if (suffix.equals("m7")) {
                chord = baseChord(chord) + "m7";
            } else if (suffix.equals("M7")) {
                chord = baseChord(chord) + "M7";
            }

            result[i] = chord;
        }

        return result;
    }

    static String[] convertMinorPatternC(String key) {
        Map<String, String[]> map = new HashMap<>();

        map.put("A",  new String[]{"Dm7","G7","CM7","Am7"});
        map.put("A#", new String[]{"D#m7","G#7","C#M7","A#m7"});
        map.put("B",  new String[]{"Em7","A7","DM7","Bm7"});
        map.put("C",  new String[]{"Fm7","A#7","D#M7","Cm7"});
        map.put("C#", new String[]{"F#m7","B7","EM7","C#m7"});
        map.put("D",  new String[]{"Gm7","C7","FM7","Dm7"});
        map.put("D#", new String[]{"G#m7","C#7","F#M7","D#m7"});
        map.put("E",  new String[]{"Am7","D7","GM7","Em7"});
        map.put("F",  new String[]{"A#m7","D#7","G#M7","Fm7"});
        map.put("F#", new String[]{"Bm7","E7","AM7","F#m7"});
        map.put("G",  new String[]{"Cm7","F7","A#M7","Gm7"});
        map.put("G#", new String[]{"C#m7","F#7","BM7","G#m7"});

        return map.getOrDefault(key, map.get("A"));
    }

    static void writeJson(
        String season,
        String key1,
        String key2,
        String[] a,
        String[] b,
        String[] c,
        String[] d,
        String[] e,
        int bpm
    ) throws Exception {

        PrintWriter pw = new PrintWriter(new FileWriter("chords.json"));

        pw.println("{");
        pw.println("  \"bpm\": " + bpm + ",");
        pw.println("  \"season\": \"" + season + "\",");
        pw.println("  \"key1\": \"" + key1 + "\",");
        pw.println("  \"key2\": \"" + key2 + "\",");
        pw.println("  \"patterns\": [");

        // A
        pw.println("    {");
        pw.println("      \"name\": \"A\",");
        pw.println("      \"chords\": " + Arrays.toString(a).replace(" ", "").replace("[", "[\"").replace("]", "\"]").replace(",", "\",\""));
        pw.println("    },");

        // B
        pw.println("    {");
        pw.println("      \"name\": \"B\",");
        pw.println("      \"chords\": " + Arrays.toString(b).replace(" ", "").replace("[", "[\"").replace("]", "\"]").replace(",", "\",\""));
        pw.println("    },");

        // C
        pw.println("    {");
        pw.println("      \"name\": \"C\",");
        pw.println("      \"chords\": " + Arrays.toString(c).replace(" ", "").replace("[", "[\"").replace("]", "\"]").replace(",", "\",\""));
        pw.println("    },");

        // D
        pw.println("    {");
        pw.println("      \"name\": \"D\",");
        pw.println("      \"chords\": " + Arrays.toString(d).replace(" ", "").replace("[", "[\"").replace("]", "\"]").replace(",", "\",\""));
        pw.println("    },");

        // E
        pw.println("    {");
        pw.println("      \"name\": \"E\",");
        pw.println("      \"chords\": " + Arrays.toString(e).replace(" ", "").replace("[", "[\"").replace("]", "\"]").replace(",", "\",\""));
        pw.println("    }");

        pw.println("  ]");
        pw.println("}");

        pw.close();
    }

    static String extract(String json, String key) {
        String pattern = "\"" + key + "\":";
        int start = json.indexOf(pattern);
        if (start == -1) return "";
        start += pattern.length();
        if (json.charAt(start) == '"') {
            start++;
            int end = json.indexOf("\"", start);
            return json.substring(start, end);
        }
        return "";
    }

    static String clean(String s) {
        return s == null ? "" : s.replace("\"", "").trim();
    }

    static int calculateBPM() {
        try {
            String csvPath = "JavaPython/wind_notes.csv";
            BufferedReader reader = new BufferedReader(new FileReader(csvPath));
            String line;
            double humiditySum = 0;
            double changeRateSum = 0;
            int count = 0;

            reader.readLine(); // ヘッダー行スキップ

            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length > 8) {
                    try {
                        double humidity = Double.parseDouble(parts[4]);
                        double changeRate = Double.parseDouble(parts[8]);
                        humiditySum += humidity;
                        changeRateSum += changeRate;
                        count++;
                    } catch (NumberFormatException e) {
                        // スキップ
                    }
                }
            }
            reader.close();

            if (count == 0) {
                System.out.println("警告: wind_notes.csv に有効なデータがありません");
                return 90;
            }

            double humidityAvg = humiditySum / count;
            double changeRateAvg = changeRateSum / count;

            System.out.println("[BPM計算]");
            System.out.println("  平均湿度: " + String.format("%.2f", humidityAvg) + "%");
            System.out.println("  平均風速変化量: " + String.format("%.2f", changeRateAvg));

            double bpmDouble = 120 - (humidityAvg / 100.0) * 30 + (changeRateAvg / 10.0) * 20;
            int bpm = (int) Math.round(bpmDouble);
            
            // 範囲制限 (60-140)
            bpm = Math.max(60, Math.min(140, bpm));
            
            System.out.println("  計算BPM: " + bpm);
            return bpm;

        } catch (Exception e) {
            System.out.println("BPM計算エラー: " + e.getMessage());
            e.printStackTrace();
            return 90;
        }
    }
}