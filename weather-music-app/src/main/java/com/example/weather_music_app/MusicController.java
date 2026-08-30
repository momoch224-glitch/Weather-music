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

        // ...(中略: 19行目〜49行目はそのまま)...

        // ★探すファイル名を "Final_arranged.mid" に変更！
        File finalMidi = new File("Final_arranged.mid");
        if (finalMidi.exists()) {
            return "大成功！ Final_arranged.mid が生成されました！";
        } else {
            return "エラー: Pythonは動きましたが、Final_arranged.mid が見つかりません";
        }
    }
}