import javax.sound.midi.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Scanner;
import java.util.Random;
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        // 1. 入力セクション
        System.out.print("都道府県名を英語で入力してください (例: Tokyo, Osaka): ");
        String city = scanner.nextLine();
        System.out.print("展開パラメータ i を入力 (-10 ～ 10): ");
        int i = scanner.nextInt();

        // 2. Pythonから天気データを取得
        String jsonResult = "";
        try {
            // Pythonスクリプトを呼び出し
            ProcessBuilder pb = new ProcessBuilder("python", "JavaPython/weather.py", city);
            Process process = pb.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"));
            jsonResult = reader.readLine(); 
            
            // デバッグ用：Pythonからの生の出力を表示
            System.out.println("\nDEBUG: Pythonからの生データ -> " + jsonResult);
            
            process.waitFor();
        } catch (Exception e) {
            System.err.println("Pythonの呼び出しに失敗しました。パスやapikey.txtを確認してください。");
            e.printStackTrace();
            return;
        }

        if (jsonResult == null || jsonResult.isEmpty()) {
            System.err.println("エラー：Pythonからデータを受け取れませんでした。");
            return;
        }

        // 3. JSON文字列からデータを抽出（強化版パース）
        String season = extractJsonValue(jsonResult, "season");
        String condition = extractJsonValue(jsonResult, "condition");
        
        // Pythonの天気を音楽用の「晴れ・雨・曇り」に変換
        String weather = switch (condition) {
            case "Clear" -> "晴れ";
            case "Rain", "Drizzle", "Thunderstorm" -> "雨";
            default -> "曇り"; 
        };

        System.out.println("--- 取得データ ---");
        System.out.println("季節: " + season + " / 天気: " + weather + " (" + condition + ")");
        System.out.println("------------------\n");

        // 4. 音楽生成の準備
        int n = switch (season) {
            case "春" -> 60; // C4
            case "夏" -> 67; // G4
            case "秋" -> 62; // D4
            case "冬" -> 57; // A3
            default -> 60;   // 取得失敗時はC4
        };

        Random random = new Random();
        int r = random.nextInt(12);
        int n_root = (r * 7) + n;
        while (n_root >= 69) { n_root -= 12; }

        int beat = (int)((60.0 / 72.0) * 1000); // ♩=72

        try {
            Synthesizer synth = MidiSystem.getSynthesizer();
            synth.open();
            MidiChannel channel = synth.getChannels()[0];
            channel.controlChange(7, 127); // 音量最大

            if (weather.equals("曇り")) {
                playCadence(channel, n_root, "dur", beat, i);
                Thread.sleep(beat); // durとmollの間の休符
                playCadence(channel, n_root + 9, "moll", beat, i);
            } else {
                String type = weather.equals("晴れ") ? "dur" : "moll";
                // 雨（moll）の場合は平行短調にする
                int rootFinal = weather.equals("晴れ") ? n_root : n_root + 9;
                playCadence(channel, rootFinal, type, beat, i);
            }

            // 最後の和音の余韻を待ってから終了
            Thread.sleep(1500); 
            synth.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        scanner.close();
    }

    /**
     * JSON文字列から特定のキーの値を取り出す強化版メソッド
     */
    private static String extractJsonValue(String json, String key) {
        try {
            String searchKey = "\"" + key + "\"";
            int keyIndex = json.indexOf(searchKey);
            if (keyIndex == -1) return "データなし";

            int colonIndex = json.indexOf(":", keyIndex + searchKey.length());
            int startQuote = json.indexOf("\"", colonIndex);
            int endQuote = json.indexOf("\"", startQuote + 1);

            return json.substring(startQuote + 1, endQuote);
        } catch (Exception e) {
            return "解析エラー";
        }
    }

    /**
     * 和音進行（I-IV-V-I）を演奏するメソッド
     */
    private static void playCadence(MidiChannel channel, int root, String type, int duration, int i) throws InterruptedException {
        String[] noteNames = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
        boolean isDur = type.equals("dur");
        
        int third = isDur ? 4 : 3;
        int sixth = isDur ? 9 : 8; // mollのときは短6度(8)にする

        System.out.println("【演奏開始: " + noteNames[root % 12] + type + " (i=" + i + ")】");

        int[][] baseChords = {
            {root, root + third, root + 7},    // I
            {root, root + 5, root + sixth},    // IV (第2展開形のベース)
            {root - 1, root + 2, root + 7},    // V  (第1展開形のベース)
            {root, root + third, root + 7}     // I
        };

        for (int[] chord : baseChords) {
            // 前の音を止める（重なり防止）
            channel.allNotesOff();
            
            // パラメータ i に基づいて転回形を計算
            int[] inverted = applyInversion(chord, i);
            
            // 演奏
            for (int note : inverted) channel.noteOn(note, 90);
            
            // ♩=72の長さ分待機
            Thread.sleep(duration);
        }
        // 最後に音を止める
        channel.allNotesOff();
    }

    /**
     * 転回ロジック: i 回数分、一番低い音を上げる（または高い音を下げる）
     */
    private static int[] applyInversion(int[] chord, int i) {
        int[] result = chord.clone();
        if (i > 0) {
            for (int step = 0; step < i; step++) {
                Arrays.sort(result);
                result[0] += 12;
            }
        } else if (i < 0) {
            for (int step = 0; step > i; step--) {
                Arrays.sort(result);
                result[result.length - 1] -= 12;
            }
        }
        Arrays.sort(result);
        return result;
    }
}