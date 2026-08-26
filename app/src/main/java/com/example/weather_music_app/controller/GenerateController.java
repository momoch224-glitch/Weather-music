package com.example.weather_music_app.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.*;
import java.nio.file.*;
import java.util.Map;

@RestController
public class GenerateController {

    private final ObjectMapper mapper = new ObjectMapper();

    @PostMapping("/generate")
    public ResponseEntity<?> generate(@RequestBody Map<String,Object> body) {
        String location = body.get("location") != null ? body.get("location").toString() : "";
        if (location.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("message","場所を入力してください"));
        }

        try {
            // ローカルテスト時は "." を使うと分かりやすい。Dockerでは "/app" に変更してください。
            ProcessBuilder pb = new ProcessBuilder("/bin/bash", "run_generation.sh", location);
            pb.directory(new File(".")); // ローカル実行時はプロジェクトルートを想定
            // pb.directory(new File("/app")); // Docker化したらこちらに切替
            pb.redirectErrorStream(true);
            Process p = pb.start();

            try (BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()))) {
                String line;
                while ((line = br.readLine()) != null) {
                    System.out.println("[run_generation] " + line);
                }
            }

            int code = p.waitFor();
            if (code != 0) {
                return ResponseEntity.status(500).body(Map.of("message", "生成スクリプトが失敗しました", "code", code));
            }

            // chords.json をプロジェクトルートに作る想定（Dockerなら /app/chords.json）
            Path chords = Paths.get("chords.json");
            if (!Files.exists(chords)) {
                return ResponseEntity.status(500).body(Map.of("message", "chords.json が見つかりません"));
            }
            String json = Files.readString(chords);
            Map<?,?> jsonMap = mapper.readValue(json, Map.class);
            if (!jsonMap.containsKey("season")) {
                return ResponseEntity.status(500).body(Map.of("message", "chords.json に 'season' がありません"));
            }

            return ResponseEntity.ok(Map.of("message", "生成完了", "season", jsonMap.get("season")));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("message", "内部エラー", "detail", e.getMessage()));
        }
    }
}
