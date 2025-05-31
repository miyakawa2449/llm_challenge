import json
import os
import re
from openai import OpenAI
from tqdm import tqdm # 進捗表示用

# APIキーとモデル設定
# 実際のプロジェクトでは src.config.settings から読み込むことを推奨します。
# 例:
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from src.config import settings
# OPENAI_API_KEY = settings.OPENAI_API_KEY
# DEFAULT_MODEL_NAME = settings.DEFAULT_MODEL_NAME

# このスクリプト単体で実行するための仮設定 (環境変数から読み込み)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DEFAULT_MODEL_NAME = os.environ.get("DEFAULT_MODEL_NAME", "gpt-3.5-turbo") # gpt-4oなども指定可能

def clean_text_python_pre_ai(text_content: str, title_for_prompt: str) -> str:
    """
    AI処理前にPythonで実行する基本的なテキストクリーニング。
    - 特定の不要セクションの削除
    - @miyakawa2449 のスペース処理
    """
    # ルール2: @miyakawa2449 の表記の前後にある半角スペースを消す
    text_content = re.sub(r"\s*@miyakawa2449\s*", "@miyakawa2449", text_content)

    # ルール3の一部: 明確な不要セクションの削除 (正規表現ベース)
    # 関連記事セクション (次の主要な見出し、または記事の終わりまで)
    text_content = re.sub(r"^(関連記事|関連する記事|■関連記事)\s*\n(.|\n)*?(?=\n\n(?:#|\*{2,}.*\*{2,}|\w)|$)", "", text_content, flags=re.MULTILINE | re.IGNORECASE)
    # 引用元
    text_content = re.sub(r"^引用元:.*$", "", text_content, flags=re.MULTILINE | re.IGNORECASE)
    # 海外での Twitter の反応セクション
    text_content = re.sub(r"^(海外での\s*Twitter\s*の反応|海外の反応)\s*\n(.|\n)*?(?=\n\n(?:#|\*{2,}.*\*{2,}|\w)|$)", "", text_content, flags=re.MULTILINE | re.IGNORECASE)
    # Amazonリンクや商品紹介と思われる行
    text_content = re.sub(r"^Amazon\s*\|.*$", "", text_content, flags=re.MULTILINE | re.IGNORECASE)
    text_content = re.sub(r"^.*(通販\s*\|\s*Amazon|Amazon\s*で見る)$", "", text_content, flags=re.MULTILINE | re.IGNORECASE)
    text_content = re.sub(r"^\s*<a href=.*amazon\.co\.jp.*<\/a>\s*$", "", text_content, flags=re.MULTILINE | re.IGNORECASE) # HTMLのAmazonリンク
    # YouTubeリンクと思われる行
    text_content = re.sub(r"^.*YouTube$", "", text_content, flags=re.MULTILINE | re.IGNORECASE)
    # 公式サイトへのリンク行
    text_content = re.sub(r"^映画「.*?」公式サイト.*公開$", "", text_content, flags=re.MULTILINE | re.IGNORECASE)
    # 目次のようなリスト
    text_content = re.sub(r"^(目次|この記事の目次)\s*\n(-|\*|\d\.).*\n((?:-|\*|\d\.).*\n)*", "", text_content, flags=re.MULTILINE | re.IGNORECASE)


    # 連続する空行を1行にまとめる
    text_content = re.sub(r"\n\s*\n", "\n\n", text_content)
    return text_content.strip()

def refine_and_restructure_with_ai(client: OpenAI, title: str, text_content: str) -> str:
    """
    OpenAI APIを使用して記事を編集し、6部構成に再編する。
    """
    system_message_content = f"""あなたはプロの映画ブログ編集者です。提供された映画レビューのテキストを以下の指示に従って編集し、指定された6部構成に再編してください。

**編集指示:**
1.  **冗長性の排除:** テキスト全体を読みやすく、自然な流れにしてください。特に映画のタイトル「{title}」の過度な繰り返しや、その他冗長な表現を減らしてください。
2.  **文体維持:** 元の記事の文体、トーン、筆者の個人的な視点や口調は最大限維持してください。
3.  **不要情報の削除:** 記事の本筋と関係の薄い情報（例: 外部リンク、商品紹介、読者への直接的な呼びかけが過度な部分、他の記事への誘導、SNSの埋め込みや言及など）は削除してください。ただし、映画の評価に直接関わる引用（例：批評家の言葉）は残しても構いません。

**再構成指示:**
編集後のテキストを、以下の6つのセクションに沿って再編成してください。各セクション見出しは `# セクション名` の形式で記述してください。

1.  `# 導入`
2.  `# 予告編とあらすじ`
3.  `# 出演者・スタッフ情報`
4.  `# 感想レビュー`
5.  `# メインキャスト紹介`
6.  `# まとめ`

**重要な注意点:**
*   各セクションには、**元のテキストに含まれる情報のみ**を使用してください。
*   不足している情報を**新たに追加したり、内容を創作したりしないでください**。
*   元のテキストに特定のセクションに該当する情報がほとんどない場合は、そのセクションの内容を簡潔にするか、「このセクションに該当する情報は元のテキストにありませんでした。」のように記述してください。無理に情報を引き延ばさないでください。
*   最終出力は、上記6部構成のマークダウン形式のみとしてください。余計な前置きや後書きは不要です。
"""

    user_message_content = f"""以下の映画レビューテキストを編集し、6部構成に再構成してください。

元のタイトル（参考情報、出力に含めない）: {title}
元のテキスト:
{text_content}

編集・再構成された記事:
"""
    try:
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message_content},
                {"role": "user", "content": user_message_content}
            ],
            temperature=0.3, # 指示への忠実性を高めるため低めに設定
            max_tokens=5000, # 出力長に余裕を持たせる
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during OpenAI API call for title '{title}': {e}")
        return f"エラー: AIによる処理に失敗しました。詳細: {e}\n\n元のテキスト:\n{text_content}"


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    input_file_path = os.path.join(project_root, "output.jsonl")
    output_dir = os.path.join(project_root, "data", "finetuning_data")
    output_file_path = os.path.join(output_dir, "output_refined_by_ai.jsonl")

    if not OPENAI_API_KEY:
        print("エラー: OpenAI APIキーが設定されていません。環境変数 OPENAI_API_KEY を設定してください。")
        return

    client = OpenAI(api_key=OPENAI_API_KEY)
    os.makedirs(output_dir, exist_ok=True)

    processed_articles = []
    all_articles_data = []

    with open(input_file_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            try:
                all_articles_data.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                print(f"警告: JSONデコードエラーのため、行をスキップ（読み込み時）: {line.strip()[:100]}...")


    # API呼び出し回数を制限したい場合は、以下のコメントアウトを解除して調整
    # articles_to_process_ai = all_articles_data[:3] # 例: 最初の3件だけAI処理
    articles_to_process_ai = all_articles_data # 全件AI処理

    for article_data in tqdm(articles_to_process_ai, desc="Processing articles with AI"):
        try:
            original_id = article_data.get("id")
            original_title = article_data.get("title", "")
            original_text = article_data.get("text", "")
            original_category = article_data.get("category")
            original_post_date = article_data.get("post_date")

            # ルール1: title から「映画」という文字を取り除く
            # 「」や【】なども除去してAIに渡しやすくする
            processed_title = original_title.replace("映画", "").strip()
            title_for_prompt = re.sub(r"[「」【】]", "", processed_title)


            # Pythonによる前処理 (ルール2とルール3の一部)
            text_after_python_clean = clean_text_python_pre_ai(original_text, title_for_prompt)

            # AIによる編集と再構成 (ルール3の残り、ルール4、ルール5)
            refined_text_ai = refine_and_restructure_with_ai(client, title_for_prompt, text_after_python_clean)

            processed_articles.append({
                "id": original_id,
                "title": processed_title,
                "text": refined_text_ai, # AIによって再構成されたテキスト
                "category": original_category,
                "post_date": original_post_date
            })

        except Exception as e:
            tqdm.write(f"警告: 記事ID {original_id} の処理中に予期せぬエラーが発生しました: {e}")
            # エラーが発生した場合でも、元の情報を保持してリストに追加する（オプション）
            processed_articles.append({
                "id": original_id,
                "title": processed_title, # Pythonで処理済みのタイトル
                "text": f"エラー発生。元のテキスト:\n{text_after_python_clean}", # Pythonで処理済みのテキスト
                "category": original_category,
                "post_date": original_post_date,
                "error": str(e)
            })


    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for article in processed_articles:
            outfile.write(json.dumps(article, ensure_ascii=False) + "\n")

    print(f"\n処理が完了しました。整形済みデータは {output_file_path} に保存されました。")
    print(f"処理された記事数: {len(processed_articles)}")

if __name__ == "__main__":
    # 環境変数 OPENAI_API_KEY と DEFAULT_MODEL_NAME を設定してください
    # 例: export OPENAI_API_KEY="your_api_key_here"
    #     export DEFAULT_MODEL_NAME="gpt-4o" (または "gpt-3.5-turbo" など)
    main()