package com.example.weather_music_app;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

//@RestController
//@CrossOrigin(origins = "*")
public class MusicController {

    @PostMapping("/generate")
    public String generateMusic(@RequestBody Map<String, Object> weatherData) {
        
        System.out.println("--- 音楽生成リクエストを受信しました ---");
        System.out.println("受信した気象データ: " + weatherData);

        String rhythmStyle = "medium";
        if (weatherData.containsKey("wind_speed")) {
            double windSpeed = Double.parseDouble(weatherData.get("wind_speed").toString());
            if (windSpeed >= 10.0) {
                rhythmStyle = "high";
            } else if (windSpeed <= 3.0) {
                rhythmStyle = "low";
            }
        }
        System.out.println("決定したリズム: " + rhythmStyle);

        String json = "{\n" +
                "  \"bpm\": 90,\n" +
                "  \"key\": \"C\",\n" +
                "  \"rhythm_style\": \"" + rhythmStyle + "\",\n" +
                "  \"patterns\": [\n" +
                "    {\"name\": \"A\", \"chords\": [\"C\", \"G\", \"Am\", \"Em\"]},\n" +
                "    {\"name\": \"B\", \"chords\": [\"F\", \"G\", \"Em\", \"Am\"]},\n" +
                "    {\"name\": \"C\", \"chords\": [\"F\", \"C\", \"Dm\", \"Am\"]},\n" +
                "    {\"name\": \"D\", \"chords\": [\"C\", \"G\", \"Am\", \"F\"]},\n" +
                "    {\"name\": \"E\", \"chords\": [\"F\", \"G\", \"Em\", \"Am\"]}\n" +
                "  ]\n" +
                "}";

        // "chords.json" をそのまま作成
        try (FileWriter file = new FileWriter("chords.json")) {
            file.write(json);
            System.out.println("chords.json を作成しました");
        } catch (IOException e) {
            e.printStackTrace();
            return "エラー: JSONファイルの作成に失敗しました";
        }

        // "Main.py" をそのまま実行
        try {
            ProcessBuilder pb = new ProcessBuilder("python", "Main.py");
            pb.inheritIO();
            Process process = pb.start();
            int exitCode = process.waitFor();
            System.out.println("Python 終了コード = " + exitCode);
        } catch (Exception e) {
            e.printStackTrace();
            return "エラー: Pythonの実行に失敗しました";
        }

        // "final.mid" をそのまま確認
        File finalMidi = new File("final.mid");
        if (finalMidi.exists()) {
            return "大成功！ final.mid が生成されました！";
        } else {
            return "エラー: Pythonは動きましたが、final.mid が見つかりません";
        }
    }
}