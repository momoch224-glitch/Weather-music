package JavaPython;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Scanner;

public class WeatherApp {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("都道府県名を英語で入力してください (例: Tokyo, Osaka): ");
        String city = scanner.nextLine();

        try {
            // Pythonスクリプトを呼び出すコマンドを構築する
            // "python" の部分は環境に合わせて "python3" などに変える必要があるかもしれない
           ProcessBuilder pb = new ProcessBuilder("python", "JavaPython/weather.py", city);
            Process process = pb.start();

            // Pythonからの出力を読み取る
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"));
            String line;
            while ((line = reader.readLine()) != null) {
                // ここではJSONがそのまま文字列として返ってくる
                System.out.println("取得結果: " + line);
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                System.err.println("Pythonの実行中にエラーが発生しました。");
            }

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            scanner.close();
        }
    }
}