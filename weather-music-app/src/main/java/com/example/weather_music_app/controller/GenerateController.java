package com.example.weather_music_app.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.io.*;
import java.nio.file.*;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CompletableFuture;

@RestController
public class GenerateController {

    private final ObjectMapper mapper = new ObjectMapper();

    // タスクの状況を一時保存するメモ帳（受付番号 -> 状況）
    private final Map<String, String> taskStatus = new ConcurrentHashMap<>();

    // APIキーを環境変数から読み込む
    @Value("${WEATHER_API_KEY}")
    private String apiKey;

    // フロントエンドから「緯度・経度」で天気を要求された時の通信口
    @GetMapping("/api/weather")
    public ResponseEntity<?> getWeather(@RequestParam double lat, @RequestParam double lon) {
        try {
            String url = "https://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + apiKey + "&lang=ja&units=metric";
            RestTemplate restTemplate = new RestTemplate();
            String result = restTemplate.getForObject(url, String.class);
            
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("message", "天気データの取得に失敗しました", "detail", e.getMessage()));
        }
    }

    // 音楽生成の要求を受け付ける通信口
    @PostMapping("/generate")
    public ResponseEntity<?> generate(@RequestBody Map<String,Object> body) {
        String location = body.get("location") != null ? body.get("location").toString() : "";
        if (location.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("message","場所を入力してください"));
        }

        // 1. ランダムな「受付番号（Task ID）」を発行
        String taskId = UUID.randomUUID().toString();
        
        // 2. メモ帳に「処理中(PROCESSING)」として登録
        taskStatus.put(taskId, "PROCESSING");

        // 3. 裏作業（非同期処理）を開始する
        CompletableFuture.runAsync(() -> {
            try {
                ProcessBuilder pb = new ProcessBuilder("/bin/bash", "run_generation.sh", location);
                pb.directory(new File(".")); 
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
                    taskStatus.put(taskId, "ERROR");
                    return;
                }

                Path chords = Paths.get("chords.json");
                if (!Files.exists(chords)) {
                    taskStatus.put(taskId, "ERROR");
                    return;
                }
                String json = Files.readString(chords);
                Map<?,?> jsonMap = mapper.readValue(json, Map.class);
                if (!jsonMap.containsKey("season")) {
                    taskStatus.put(taskId, "ERROR");
                    return;
                }

                // 全ての処理とファイルの確認が成功したら「完了(COMPLETED)」にする
                taskStatus.put(taskId, "COMPLETED");

            } catch (Exception e) {
                e.printStackTrace();
                taskStatus.put(taskId, "ERROR");
            }
        });

        // 4. ブラウザには「受付番号」だけを即座に返して通信を終わらせる
        return ResponseEntity.ok(Map.of("message", "生成を開始しました", "taskId", taskId));
    }

    // フロントエンドが定期的に「できましたか？」と聞きに来る通信口
    @GetMapping("/api/status")
    public ResponseEntity<?> checkStatus(@RequestParam String taskId) {
        // メモ帳を見て状況を返す（見つからなければ NOT_FOUND）
        String status = taskStatus.getOrDefault(taskId, "NOT_FOUND");
        return ResponseEntity.ok(Map.of("status", status));
    }
}