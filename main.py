import time
import wave
import numpy as np
import pyaudio
import pyttsx3
import speech_recognition as sr
from src.API_functions import client_groq, extract_tag, gemini_agent, gemini_chat

listener = sr.Recognizer()

level_zero_system_prompt = r"""
あなたは、ユーザーの入力から目的を正確に把握し、そのリクエストを達成するために必要な情報やブラウザ操作タスクを整理・生成するAIエージェントです。ユーザーが求める情報や実行すべきタスクを十分に考慮し、適切な順序と具体的な操作手順を提案してください。

**【基本役割】**
- ユーザーのリクエスト内容を丁寧に整理し、目的を明確にする
- 目的達成に必要な情報や具体的なブラウザ操作を特定する
- ユーザーが求めていないことは絶対にしない。ユーザーのリクエストに応じた操作のみを提案する
- ここではあくまでユーザーの入力を整理するだけにとどめる
- 思考過程と最終的な操作タスクを明確に区分して出力する

**【出力ルール】**

1. **思考過程**  
   - ユーザーのリクエストをどのように理解したか、どんな目的があるかを簡潔に説明してください。  
   - 必要な情報、参照すべきリンク、実行すべき操作の検討事項など、背景や判断理由を述べます。  
   - ここではまだ具体的なタスクの定義は行いません。

2. **タスク定義**  
   - ユーザーの目的を達成するため、ブラウザ上で実行すべき具体的な操作を順序立てて示します。  
   - 操作は「検索」、「リンクのクリック」、「フォーム入力」など、実際のブラウザ操作を明示してください。  
   - **必ず全ての操作は一組の\<task> ～ </task>タグ内にまとめること。**  
   - 複数の\<task>タグを使用せず、すべてのタスクは1つのタグ内に記述してください。

3. **注意点**  
   - ユーザーのリクエストに直接関係する操作のみをタスクとして記述すること。  
   - 思考過程やその他の解説は\<task>タグの外に記述してください。  
   - タスクは実際にブラウザで実行可能な具体的な操作であること。

---

**【サンプル】**

ユーザーのリクエスト：「最新のニュースを調べたい」

ユーザーは最新のニュース情報を得たいと考えているため、まずは信頼できるニュースサイトや検索エンジンで「最新ニュース」というキーワードを検索する必要があると判断しました。上位に表示される信頼性の高いニュースサイトにアクセスすることで、目的が達成されると考えられます。
 
<task>Googleで「最新ニュース」を検索し、最初に表示されたニュースサイトのリンクをクリックして、その内容をユーザーに伝える。</task>
これで実行します。
"""

level_one_system_prompt = r"""
あなたは、既に生成されたタスクに対してユーザーからの新たな要求や変更点を反映し、タスクを改善・再構築するAIエージェントです。ユーザーの新たな要望を正確に把握し、ブラウザ上で実行可能な具体的操作を提示してください。

**【基本役割】**
- 既存タスクの内容を把握し、ユーザーから提示された追加要求や変更点を正確に理解する。
- ユーザーの新たな要望を反映し、必要な改善・修正を検討する。
- 変更が不要な場合は、既存タスクをそのまま出力する。(どんなことがあろうとも<task>～</task>タグの中にタスクを入れて出力すること。)
- ユーザーが求めていないことは絶対にしない。ユーザーのリクエストに応じた操作のみを提案する
- ここではあくまでユーザーの入力を整理するだけにとどめる

**【出力ルール】**

1. **思考過程**  
   - ユーザーの追加要求や変更点をどのように解釈し、どの部分の改善が必要かを簡潔に説明してください。  
   - ここでは、ユーザーの意図や背景、検討すべき操作の流れなどを記述しますが、具体的なタスク定義は含めません。

2. **タスク定義**  
   - ユーザーの新たな要求を反映した上で、ブラウザ上で実行する具体的な操作を記述してください。  
   - 操作例としては、「Googleで‘○○’を検索する」「2番目に表示されたリンクをクリックする」「フォームに情報を入力して送信する」など、実際にブラウザ上で行える手順を示します。  
   - **必ず最終的なタスク全体は1組の\<task>～</task>タグで囲んでください。**  
   - 複数の\<task>タグを使用せず、すべての操作は一つのタグ内にまとめること。

3. **注意点**  
   - ユーザーの新たな要求を正確に反映し、必要な操作改善のみをタスクとして記述してください。  
   - 思考過程や補足説明は自由に記述して構いませんが、必ず最終的なタスク部分は\<task>～</task>タグ内に含めること。

---

**【サンプル】**

ユーザーの追加要求：「前回のタスクで『ニュースサイトをチェック』という操作に加えて、最新の天気情報も調べたい」

ユーザーは既存の「ニュースサイトをチェック」タスクに、最新の天気情報の取得を追加したいと要求しています。  
そのため、まずはニュースサイトの操作を実行し、その後、天気情報を提供する信頼性の高いサイトで天気情報を検索する必要があると考えます。

<task>まずGoogleで「最新ニュース」を検索し、最初に表示された信頼性の高いニュースサイトのリンクをクリックする。その後、Googleで「今日の天気」を検索し、表示された天気情報サイトをクリックして、その内容をユーザーに伝える。</task>
"""

level_two_system_prompt = r"""
あなたは、ブラウザ操作などの各タスクを完了した後の「結果や成果」を簡潔に報告するAIエージェントです。  
1. 実行した操作や取得した情報の要点を要約し、最終的な成果や結論を短くわかりやすく示してください。  
2. 結果が数値や具体的なデータの場合は、箇条書きやシンプルな表現で提示してください。  
3. 必要に応じて得られた知見の背景や考察を簡潔に補足してもかまいません。  
4. 文章は理解しやすいようにまとめ、専門用語を使う場合は一言説明を付け加えてください。
"""

# -------------------------
# 音声合成と録音パラメータの設定
# -------------------------
def speak(text):
    """
    pyttsx3を使用してテキストを音声合成します。
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# 音量がこれ未満なら「小さい」とみなす閾値
SILENCE_THRESHOLD = 500

# ユーザーが話し始めた後、連続沈黙がこの秒数続いたら録音を終了
SILENCE_DURATION = 1.0

def record_audio(output_filename, threshold=SILENCE_THRESHOLD, timeout=10, silence_duration=SILENCE_DURATION):
    """
    録音を開始し、以下の条件で終了:
      1) 開始から 10秒 以内に一度も閾値を超えなかった => frames=None で終了 (ユーザーが話さない)
      2) いったん閾値を超えた (user_spoke=True) 後は、約 1秒 連続で閾値を下回ったら録音終了

    Return:
      (frames, user_spoke)
        frames      => 実際に録音した音声データのリスト (バイナリ)
                       10秒話さなければ None
        user_spoke  => True: ユーザーが話した / False: 話さずに終了
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("録音を開始しました。話してください (最大10秒待機)。")

    frames = []
    user_spoke = False
    start_time = time.time()

    # 連続サイレンスの判定用
    silent_chunks = 0
    required_silent_chunks = int((RATE / CHUNK) * silence_duration)

    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        amplitude = np.abs(np.frombuffer(data, dtype=np.int16)).max()

        # 10秒以内に話さなければ終了 => frames=None
        elapsed_time = time.time() - start_time
        if not user_spoke and (elapsed_time >= timeout):
            print("10秒以内に発話が検出されませんでした。録音を停止します。")
            frames = None
            break

        # 一度でも閾値を超えたらフラグを立てる
        if amplitude > threshold:
            user_spoke = True
            silent_chunks = 0  # リセット

        if user_spoke:
            # ユーザーが話した後、音量が閾値を下回っていたら silent_chunks++
            if amplitude < threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0

            # 1秒分の連続沈黙があれば終了
            if silent_chunks >= required_silent_chunks:
                print(f"{silence_duration}秒の連続沈黙を検知。録音を終了します。")
                break

    stream.stop_stream()
    stream.close()
    p.terminate()

    # ユーザーが話さなかった場合 => frames=None のまま
    if frames is not None:
        # WAV ファイルへ保存
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"録音データを {output_filename} に保存しました。")

    return frames, user_spoke


chat_history = []
level = 0

def main_task_loop():
    global chat_history, level
    audio_filename = "user_input.wav"

    while True:
        # 1. ユーザーの音声を録音 (10秒待って話さなければ終了)
        frames, user_spoke = record_audio(audio_filename, threshold=SILENCE_THRESHOLD, timeout=10)

        # ユーザーがまったく話さなかった
        if frames is None:
            print("ユーザーの発話がなかったので終了します。")
            break

        # 2. 音声ファイルができたので Groq Whisper API で文字起こし
        with open(audio_filename, "rb") as file:
            transcription = client_groq.audio.transcriptions.create(
                file=(audio_filename, file.read()),
                model="whisper-large-v3-turbo",
                prompt="",
                response_format="json",
                language="ja",
                temperature=0.0
            )
        user_text = transcription.text.strip()
        print("【音声認識結果】", user_text)

        if not user_text:
            print("音声認識結果が空です。会話を終了します。")
            break

        # 3. Chat Completion API へ
        if level == 0:
            chat_history.append({"role": "user", "content": user_text})
            response = gemini_chat(chat_history, level_zero_system_prompt)
            extracted_tasks = extract_tag(response, "text", "task")
            if extracted_tasks:
                task = extracted_tasks[0]
            else:
                print("タスクが抽出されませんでした。前回のタスクを維持します。")
            chat_history.append({"role": "assistant", "content": response})
            print("AI: " + response)
            level += 1

        elif level == 1:
            if user_text == "You have control":
                speak("I have control.")
                level += 1
            else:
                chat_history.append({"role": "user", "content": user_text})
                response = gemini_chat(chat_history, level_one_system_prompt)
                extracted_tasks = extract_tag(response, "text", "task")
                if extracted_tasks:
                    task = extracted_tasks[0]
                else:
                    print("タスクが抽出されませんでした。前回のタスクを維持します。")
                chat_history.append({"role": "assistant", "content": response})
                print("AI: " + response)

        if level == 2:
            print("AI: 実行しました。")
            results = gemini_agent(task)
            response = gemini_chat([{"role": "user", "content": str(results)}], level_two_system_prompt)
            print("AI: " + str(response))

        # 4. 応答を TTS で読み上げる
        print("読み上げ開始…")
        speak(response)
        print("読み上げ終了。")
        # => 再度ループして録音開始 (ユーザーが黙れば終了、話せば継続)

    print("プログラムを終了します。")

def main():
    while True:
        voice_text = ""
        while voice_text != "ハローベータ":
            with sr.Microphone() as source:
                print("Listening...")
                voice = listener.listen(source)
                try:
                    voice_text = listener.recognize_google(voice, language="ja-JP")
                except sr.UnknownValueError:
                    print("音声が認識できませんでした。もう一度お試しください。")
                    continue
                print(voice_text)
        speak("認識しました。ご用件をお願いします。")
        main_task_loop()

if __name__ == "__main__":
    main()
