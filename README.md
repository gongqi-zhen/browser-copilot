# Browser-Copilot
![image](https://github.com/user-attachments/assets/60926e58-2a27-472a-8dae-5b9825d8b37f)

ブラウザ操作を自動化するAIアシスタント

## 📋 概要

Browser-Copilotは、ブラウザ上で動作するAIエージェントです。ブラウザ使用中にこのエージェントを音声で呼び出すことで、タスクを引き継ぎ自動化できます。これにより、ユーザーは他の重要なタスクに集中することが可能になります。

## 🚀 インストール方法

### 前提条件
- Python 3.x
- Git

### 手順
1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/foxn2000/browser-copilot.git
   cd browser-copilot
   ```

2. **仮想環境のセットアップと依存パッケージのインストール**
   ```bash
   # 仮想環境の作成
   python3 -m venv env

   # 仮想環境の有効化
   # macOS/Linuxの場合
   source env/bin/activate
   # Windowsの場合
   .\env\Scripts\activate

   # 依存パッケージのインストール
   pip install -r requirements.txt
   ```

3. **Playwrightのインストール**（未インストールの場合）
   ```bash
   playwright install
   ```

4. **環境設定ファイルの作成**
   - `.env.example`ファイルをコピーして`.env`ファイルを作成
   - 必要なAPIキー（GroqとGemini）を`.env`ファイルに設定

## 💻 使い方

1. **エージェントの起動**
   ```bash
   python main.py
   ```

2. **Browser-Copilotの呼び出し**
   - 「ハローベータ」と音声で呼びかけることでエージェントがアクティブになります

3. **タスクの指示**
   - 引き継ぎたいタスクまたは新規タスクを音声で入力します

4. **タスクの確認と認証**
   - AIが設計したタスクが音声で読み上げられます
   - 「You have control」と音声で応答するとタスクが実行されます
   - ⚠️ **注意**: AIの動作中もブラウザから目を離さないでください

5. **タスク完了の確認**
   - タスク完了後、結果が音声で読み上げられます

## ⚖️ ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細については[LICENSE](./LICENSE)ファイルを参照してください。
