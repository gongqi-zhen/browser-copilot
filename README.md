## browser-copilot

### 概要
このプロジェクトはブラウザで動作するエージェントです。
ブラウザを使用中にこのエージェントを呼び出すことでタスクを引き継ぐことができます。
タスクを引き継ぐことで他のタスクに集中することができます。

### インストール方法
1. このリポジトリをクローンします。
```bash
git clone 
cd browser-copilot
```
2. 仮想環境に入り、必要なパッケージをインストールします。
```bash
python3 -m venv env

source venv/bin/activate # macOS, Linuxの場合
.\venv\Scripts\activate # WindowsのPowerShell

pip install -r requirements.txt
```
3. playwrightをインストールする(未インストールの場合)
```bash
playwright install
```
5. .envファイルを作成する。
.envファイルを作成して、.env.exampleをコピーしてください。
.env.exampleを参考にして、APIキーを設定してください。
必要になるAPIキーはGroqのAPIキーとGeminiのAPIキーです。


### 使い方
1.エージェントを起動して下さい。
```bash
python main.py
```
2.browser-copilotを呼び出す。
「ハローベータ」と呼び出すことでbrowser-copilotがアクティブ状態になります。

3.タスクを入力する。
引き継ぐ or 新規タスクを音声で入力して下さい。

3.タスクの確認と認証をする。
AIが設計したタスクが音声で読み上げられるので、「You have control」と音声で入力し、タスクが実行されます。
（AIはまだ完璧ではないため、AIがタスクを実行している時も、ブラウザから目を離すことはしないでください。）

4.タスクの完了を確認する。
タスクが完了したらリザルトが音声で読み上げられます。

### ライセンス
このプロジェクトはMITライセンスの下でライセンスされています。
詳細については、LICENSEファイルを参照してください。