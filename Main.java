import javax.sound.midi.*;
import java.util.Scanner;
import java.util.Random;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Random random = new Random();
        
        // 1. 季節の入力
        System.out.print("季節を入力してください（例：春）: ");
        String season = scanner.next();

        // 2. 天気の入力
        System.out.print("天気を入力してください（例：晴れ）: ");
        String weather = scanner.next();

        // --- 条件チェックの開始 ---
        // 季節が「春」かつ、天気が「晴れ」の場合のみ実行
        if (season.equals("春") && weather.equals("晴れ")) {
            
            System.out.println("条件クリア：春の晴天モードを開始します。");
            System.out.println("Cdur");
            
            int n = 60;
            int r = random.nextInt(12);
            
            // 計算
            n = (r * 7) + n;
            System.out.println("計算直後の n: " + n);

            // オクターブ調整（68以下にする）
            while (n >= 69) {
                n = n - 12;
            }

            // 音名判定
            String[] noteNames = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
            int noteIndex = n % 12;
            String noteName = noteNames[noteIndex];
            int octave = (n / 12) - 1;

            System.out.println("確定した調: " + noteName + "dur");
            System.out.println(noteName + octave + " の音を出します (n=" + n + ")");

            try {
                Synthesizer synth = MidiSystem.getSynthesizer();
                synth.open();
                MidiChannel[] channels = synth.getChannels();

                channels[0].noteOn(n, 100);
                Thread.sleep(3000);
                channels[0].noteOff(n);
                
                synth.close();
            } catch (Exception e) {
                e.printStackTrace();
            }

        } else {
            // 条件を満たさない場合はメッセージを出して停止
            System.out.println("エラー：指定された条件（春・晴れ）ではないため、プログラムを停止します。");
        }

        scanner.close();
    }
}