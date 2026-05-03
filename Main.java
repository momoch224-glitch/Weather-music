import javax.sound.midi.*;
import java.util.Scanner;
import java.util.Random;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Random random = new Random();
        
        // 1. 入力
        System.out.print("季節を入力してください（春・夏・秋・冬）: ");
        String season = scanner.next();

        System.out.print("天気を入力してください（晴れ・雨・曇り）: ");
        String weather = scanner.next();

        // 2. 季節による初期値 n と基準の調の設定
        int n;
        String baseScale;

        if (season.equals("春")) {
            n = 60; baseScale = "Cdur";
        } else if (season.equals("夏")) {
            n = 67; baseScale = "Gdur";
        } else if (season.equals("秋")) {
            n = 62; baseScale = "Ddur";
        } else if (season.equals("冬")) {
            n = 57; baseScale = "Adur";
        } else {
            System.out.println("エラー：未知の季節です。停止します。");
            scanner.close();
            return;
        }

        // 3. 天気の判定（晴れ・雨・曇り以外は停止）
        if (!(weather.equals("晴れ") || weather.equals("雨") || weather.equals("曇り"))) {
            System.out.println("エラー：指定外の天気です。停止します。");
            scanner.close();
            return;
        }

        // 共通処理の開始
        System.out.println("基準設定: " + baseScale);
        
        // 0-11のランダム値を基に調を変える（属調の積み重ね）
        int r = random.nextInt(12);
        int n_dur = (r * 7) + n;
        while (n_dur >= 69) { n_dur -= 12; }

        // 音名リスト
        String[] noteNames = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

        try {
            Synthesizer synth = MidiSystem.getSynthesizer();
            synth.open();
            MidiChannel[] channels = synth.getChannels();

            if (weather.equals("曇り")) {
                // --- 曇り：晴れ(dur)と雨(moll/平行調)を両方出力 ---
                System.out.println("曇りモード：平行調を連続演奏します。");

                // 1音目: dur
                int indexDur = n_dur % 12;
                System.out.println("確定した調1: " + noteNames[indexDur] + "dur");
                channels[0].noteOn(n_dur, 100);
                Thread.sleep(1500);
                channels[0].noteOff(n_dur);

                // 2音目: moll (n + 9)
                int n_moll = n_dur + 9;
                while (n_moll >= 69) { n_moll -= 12; }
                int indexMoll = n_moll % 12;
                System.out.println("確定した調2: " + noteNames[indexMoll] + "moll");
                channels[0].noteOn(n_moll, 100);
                Thread.sleep(1500);
                channels[0].noteOff(n_moll);

            } else {
                // --- 晴れ または 雨 ---
                int final_n = n_dur;
                String scaleType = "dur";

                if (weather.equals("雨")) {
                    final_n = n_dur + 9;
                    while (final_n >= 69) { final_n -= 12; }
                    scaleType = "moll";
                    System.out.println("雨モード：平行調（マイナー）に変換しました。");
                }

                int finalIndex = final_n % 12;
                System.out.println("確定した調: " + noteNames[finalIndex] + scaleType);
                channels[0].noteOn(final_n, 100);
                Thread.sleep(3000);
                channels[0].noteOff(final_n);
            }
            
            synth.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

        scanner.close();
    }
}