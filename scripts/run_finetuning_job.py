import os
import sys # sysをインポート
import time
from openai import OpenAI

# --- sys.path の調整 ---
# このスクリプト (scripts/run_finetuning_job.py) の親の親 (プロジェクトルート) を sys.path に追加
project_root_for_sys_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root_for_sys_path not in sys.path:
    sys.path.insert(0, project_root_for_sys_path)
# --- ここまで追加 ---

from src.config import settings # settings.py から設定をインポート

def run_openai_finetuning():
    """
    OpenAI APIを使用してファインチューニングジョブを実行する。
    1. トレーニングファイルをアップロード
    2. ファインチューニングジョブを作成
    3. ジョブのステータスを監視 (簡易的)
    """
    if not settings.OPENAI_API_KEY:
        print("エラー: OpenAI APIキーが settings.py に設定されていません。")
        return

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # --- 1. トレーニングファイルの準備 ---
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    training_file_path = os.path.join(project_root, "data", "finetuning_data", "training_corpus.jsonl")

    if not os.path.exists(training_file_path):
        print(f"エラー: トレーニングファイルが見つかりません: {training_file_path}")
        print("scripts/prepare_finetuning_data.py を実行してファイルを生成してください。")
        return

    print(f"トレーニングファイル: {training_file_path}")

    # --- 2. トレーニングファイルのアップロード ---
    uploaded_file = None
    try:
        print("トレーニングファイルをOpenAIにアップロードしています...")
        with open(training_file_path, "rb") as f:
            uploaded_file = client.files.create(file=f, purpose="fine-tune")
        print(f"ファイルがアップロードされました。File ID: {uploaded_file.id}")
    except Exception as e:
        print(f"エラー: ファイルのアップロード中にエラーが発生しました: {e}")
        return

    # --- 3. ファインチューニングジョブの作成 ---
    # ベースモデルはOpenAIのドキュメントで最新の推奨を確認してください。
    # 例: "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106"
    # 2024年5月時点では "gpt-3.5-turbo-0125" が推奨されることが多いです。
    base_model = "gpt-3.5-turbo-0125"
    # suffix はファインチューニング済みモデル名に付与されるカスタム文字列 (オプション)
    # 例: "movieblog-v1"
    custom_suffix = "movieblog" # 必要に応じて変更してください

    finetuning_job = None
    try:
        print(f"\nファインチューニングジョブを作成しています...")
        print(f"  トレーニングファイルID: {uploaded_file.id}")
        print(f"  ベースモデル: {base_model}")
        print(f"  サフィックス: {custom_suffix}")

        finetuning_job = client.fine_tuning.jobs.create(
            training_file=uploaded_file.id,
            model=base_model,
            suffix=custom_suffix,
            # hyperparameters={"n_epochs": 3} # 必要に応じてエポック数などを指定
        )
        print(f"ファインチューニングジョブが作成されました。Job ID: {finetuning_job.id}")
        print(f"ステータス: {finetuning_job.status}")
        print("ジョブの完了には時間がかかることがあります。OpenAIダッシュボードでも確認できます。")

    except Exception as e:
        print(f"エラー: ファインチューニングジョブの作成中にエラーが発生しました: {e}")
        if finetuning_job:
            print(f"作成されたジョブID (エラー発生時): {finetuning_job.id}")
        return

    # --- 4. ジョブのステータス監視 (簡易版) ---
    if finetuning_job:
        print("\nジョブのステータスを監視中 (Ctrl+Cで中断)...")
        try:
            while True:
                job_status = client.fine_tuning.jobs.retrieve(finetuning_job.id)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Job ID: {job_status.id}, Status: {job_status.status}, Fine-tuned Model: {job_status.fine_tuned_model}")

                if job_status.status == "succeeded":
                    print("\nファインチューニングが成功しました！")
                    print(f"ファインチューニング済みモデルID: {job_status.fine_tuned_model}")
                    print(f"このモデルIDを settings.py の FINETUNED_MODEL_ID に設定してください。")
                    break
                elif job_status.status in ["failed", "cancelled"]:
                    print(f"\nファインチューニングが {job_status.status} しました。")
                    print("エラー詳細:")
                    if job_status.error:
                         print(f"  Code: {job_status.error.code}")
                         print(f"  Message: {job_status.error.message}")
                         print(f"  Param: {job_status.error.param}")
                    # イベントログも確認すると良い
                    events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_status.id, limit=5)
                    print("最新のイベント:")
                    for event in reversed(events.data): # 新しい順に表示
                        print(f"  - {event.created_at} [{event.level}]: {event.message}")
                    break
                
                # APIへの過度なリクエストを避けるため、適切な間隔でポーリング
                time.sleep(60)  # 60秒ごとにステータスを確認
        except KeyboardInterrupt:
            print("\nステータス監視を中断しました。")
            print(f"ジョブID: {finetuning_job.id} の状況はOpenAIダッシュボードで確認してください。")
        except Exception as e:
            print(f"エラー: ジョブステータスの取得中にエラーが発生しました: {e}")

if __name__ == "__main__":
    print("OpenAI ファインチューニングジョブ実行スクリプトを開始します。")
    print("注意: この処理にはOpenAI APIの利用料が発生します。")
    
    # ユーザーに実行確認を求める
    # proceed = input("ファインチューニングジョブを開始しますか？ (yes/no): ")
    # if proceed.lower() != 'yes':
    #     print("処理を中止しました。")
    # else:
    #     run_openai_finetuning()
    
    # 今回は自動実行するが、実際の運用では上記のような確認を入れると安全
    run_openai_finetuning()

    print("\nスクリプトを終了します。")
