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

        // 2. 条件チェック（春 かつ 晴れ・雨・曇りのいずれか）
        if (season.equals("春") && (weather.equals("晴れ") || weather.equals("雨") || weather.equals("曇り"))) {
            
            System.out.println("Cdur");
            
            int n = 60;
            int r = random.nextInt(12);
            
            // 基本の計算（晴れの音を基準に算出）
            int n_dur = (r * 7) + n;
            while (n_dur >= 69) { n_dur -= 12; }

            // 音名リスト
            String[] noteNames = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

            try {
                Synthesizer synth = MidiSystem.getSynthesizer();
                synth.open();
                MidiChannel[] channels = synth.getChannels();

                if (weather.equals("曇り")) {
                    // --- 曇りの処理：晴れ(dur)と雨(moll)を両方出す ---
                    System.out.println("曇りを検知：平行調の関係にあるdurとmollを連続で鳴らします。");

                    // 1音目：晴れ(dur)の音
                    int indexDur = n_dur % 12;
                    System.out.println("確定した調1: " + noteNames[indexDur] + "dur");
                    channels[0].noteOn(n_dur, 100);
                    Thread.sleep(1500); // 少し短めに鳴らす
                    channels[0].noteOff(n_dur);

                    // 2音目：雨(moll/平行調)の音
                    int n_moll = n_dur + 9;
                    while (n_moll >= 69) { n_moll -= 12; }
                    int indexMoll = n_moll % 12;
                    System.out.println("確定した調2: " + noteNames[indexMoll] + "moll");
                    channels[0].noteOn(n_moll, 100);
                    Thread.sleep(1500);
                    channels[0].noteOff(n_moll);

                } else {
                    // --- 晴れ または 雨 の単発処理 ---
                    int final_n = n_dur;
                    String scaleType = "dur";

                    if (weather.equals("雨")) {
                        final_n = n_dur + 9;
                        while (final_n >= 69) { final_n -= 12; }
                        scaleType = "moll";
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

        } else {
            System.out.println("エラー：指定された条件（春の晴れ、雨、または曇り）ではないため、停止します。");
        }

        scanner.close();
    }
}