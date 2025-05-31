import os
import json
from datetime import datetime

from src.generator.article_generator import ArticleGenerator
from src.prompts.prompt_manager import PromptManager # 仮のPromptManager
from src.config import settings # FINETUNED_MODEL_ID を直接使う場合

def load_user_blog_style_example(file_path: str, num_chars: int = 1000) -> str:
    """
    指定されたJSON Linesファイルから最初の記事のテキストを読み込み、
    指定文字数分の文体例として返す。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line:
                data = json.loads(first_line)
                # textがNoneでないことを確認
                text_content = data.get("text", "")
                return text_content[:num_chars] if text_content else ""
            return ""
    except FileNotFoundError:
        print(f"エラー: 文体例ファイルが見つかりません: {file_path}")
        return ""
    except json.JSONDecodeError:
        print(f"エラー: 文体例ファイルのJSONデコードに失敗しました: {file_path}")
        return ""
    except Exception as e:
        print(f"エラー: 文体例ファイルの読み込み中に予期せぬエラーが発生しました: {e}")
        return ""

def save_generated_article(article_content: str, movie_title: str, output_dir: str) -> None:
    """
    生成された記事を指定されたディレクトリに保存する。
    ファイル名は映画タイトルとタイムスタンプから生成する。
    """
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"作成されたディレクトリ: {output_dir}")
        except OSError as e:
            print(f"エラー: 出力ディレクトリの作成に失敗しました: {output_dir} ({e})")
            return

    # ファイル名に使えない文字を置換・削除
    safe_movie_title = "".join(c if c.isalnum() or c in " .-_" else "_" for c in movie_title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{safe_movie_title}_{timestamp}.txt"
    file_path = os.path.join(output_dir, file_name)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(article_content)
        print(f"生成された記事を保存しました: {file_path}")
    except Exception as e:
        print(f"エラー: 記事の保存中にエラーが発生しました: {file_path} ({e})")


def main():
    print("映画レビュー記事生成システムを開始します...")

    # --- 設定 ---
    # settings.pyからAPIキーが読み込まれているか確認 (settings.py内のprint文で確認)
    if not settings.OPENAI_API_KEY:
        print("致命的エラー: OpenAI APIキーが設定されていません。プログラムを終了します。")
        exit()

    # 文体例として使用する過去のブログ記事データ (output.jsonl)
    # main.py は src/ にあるので、プロジェクトルートの output.jsonl を指すには '../output.jsonl'
    # または、より堅牢なパス指定方法として settings.py に定義することも検討
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    user_blog_data_path = os.path.join(project_root, "output.jsonl")
    user_style_example = load_user_blog_style_example(user_blog_data_path, num_chars=1500) # 少し長めに

    if not user_style_example:
        print("警告: ユーザーの文体例を読み込めませんでした。デフォルトの文体で生成が試みられます。")
        # user_style_example = "ここにデフォルトの文体例を記述するか、プロンプトを調整してください。" # フォールバック

    # 生成したい映画のタイトル
    target_movie_title = "君の名は。"
    # target_movie_title = " ヴァチカンのエクソシスト(2023年公開)" # 他の映画で試す場合

    # 使用するモデルを決定
    # FINETUNED_MODEL_ID が settings.py に定義されていて、かつ値が設定されていればそれを使用し、
    # コメントアウトされているなどで未定義、または値が空の場合は DEFAULT_MODEL_NAME を使用
    model_to_use = settings.DEFAULT_MODEL_NAME # デフォルトを設定
    if hasattr(settings, 'FINETUNED_MODEL_ID') and settings.FINETUNED_MODEL_ID:
        # FINETUNED_MODEL_ID が存在し、空文字列やNoneでないことを確認
        model_to_use = settings.FINETUNED_MODEL_ID
        print(f"情報: ファインチューニング済みモデルを使用します: {model_to_use}")
    else:
        print(f"情報: デフォルトモデルを使用します: {model_to_use}")

    # 生成パラメータ (オプション)
    # これらを指定しない場合、settings.pyのデフォルト値やOpenAIAdapterのデフォルトが使われる
    custom_generation_params = {
        "temperature": 0.5,       # 少し創造性を高める
        "max_tokens": 2500,       # ブログ記事なので長めに
        "frequency_penalty": 0.5, # 繰り返しを抑える
        "presence_penalty": 0,  # 新しいトピックを促す
        "model": model_to_use # 動的に決定されたモデルIDを使用
        # "top_p": 0.9
    }

    # 出力ディレクトリ (プロジェクトルート/data/generated_articles)
    output_directory = os.path.join(project_root, "data", "generated_articles")

    # --- 記事生成の実行 ---
    print(f"\n映画「{target_movie_title}」のレビューを生成します...")
    print(f"使用モデル: {custom_generation_params.get('model', settings.DEFAULT_MODEL_NAME)}")
    print(f"Temperature: {custom_generation_params.get('temperature', settings.DEFAULT_TEMPERATURE)}")
    print(f"Max Tokens: {custom_generation_params.get('max_tokens', settings.DEFAULT_MAX_TOKENS)}")


    article_gen = ArticleGenerator() # デフォルトのクライアントとプロンプトマネージャーを使用

    generated_review = article_gen.generate_movie_review(
        movie_title=target_movie_title,
        user_blog_style_example=user_style_example,
        tone_and_style_details="あなたのブログ読者が親しみを感じ、映画の魅力が伝わるように、熱意を込めて書いてください。",
        other_notes="映画の核心的なネタバレは避けつつ、期待感を高めるような記述を心がけてください。",
        generation_params=custom_generation_params
    )

    # --- 結果の表示と保存 ---
    if generated_review and not generated_review.startswith("エラー:"):
        print("\n--- 生成されたレビュー ---")
        print(generated_review)
        print("------------------------")
        save_generated_article(generated_review, target_movie_title, output_directory)
    else:
        print("\nレビューの生成に失敗しました。")
        if generated_review:
            print(f"エラー詳細: {generated_review}")

    print("\n映画レビュー記事生成システムを終了します。")

if __name__ == "__main__":
    main()
