import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
# このsettings.pyファイルが src/config/ にあるため、
# .envファイルは2階層上のプロジェクトルートにあることを想定
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
dotenv_path = os.path.join(project_root, '.env')

# デバッグ用に実際のパスを表示
# print(f"Attempting to load .env from: {dotenv_path}")

load_dotenv(dotenv_path=dotenv_path)

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Model Configuration ---
# 初期はOpenAIのベースモデルを使用
DEFAULT_MODEL_NAME = "gpt-3.5-turbo"
# ファインチューニング後に、ファインチューニング済みモデルのIDを設定する
# 例: "ft:gpt-3.5-turbo-0613:your-org:custom-model-name:xxxxxxx"
FINETUNED_MODEL_ID = None

# --- Generation Parameters (Defaults) ---
# これらの値は、記事生成時に個別に上書き可能にする
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000 # ブログ記事なので少し長めに設定
DEFAULT_TOP_P = 1.0
# 必要に応じて他のデフォルトパラメータも追加できます
# DEFAULT_FREQUENCY_PENALTY = 0.0
# DEFAULT_PRESENCE_PENALTY = 0.0

# --- File Paths (Optional, if needed globally) ---
# 例:
# DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
# FINETUNING_DATA_PATH = os.path.join(DATA_DIR, 'finetuning_data', 'training_corpus.jsonl')
# GENERATED_ARTICLES_DIR = os.path.join(DATA_DIR, 'generated_articles')

# --- Logging Configuration (Optional) ---
# LOG_LEVEL = "INFO"

# --- Sanity Check ---
if not OPENAI_API_KEY:
    print("警告: 環境変数 OPENAI_API_KEY が設定されていません。")
    print(f".envファイルのパス: {dotenv_path}")
    print(f"OPENAI_API_KEY の値: {OPENAI_API_KEY}") # デバッグ用
else:
    print("環境変数 OPENAI_API_KEY は正常に読み込まれました。") # 成功時のメッセージを追加

# --- For direct execution test ---
if __name__ == "__main__":
    print("\n--- settings.py 実行テスト ---")
    print(f"OpenAI API Key (最初の5文字): {OPENAI_API_KEY[:5]}..." if OPENAI_API_KEY else "OpenAI API Key: 未設定")
    print(f"Default Model Name: {DEFAULT_MODEL_NAME}")
    print(f"Finetuned Model ID: {FINETUNED_MODEL_ID}")
    print(f"Default Temperature: {DEFAULT_TEMPERATURE}")
    print(f"Default Max Tokens: {DEFAULT_MAX_TOKENS}")
    print(f".env file path used: {dotenv_path}")
    print("--- テスト終了 ---")
