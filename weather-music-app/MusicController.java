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