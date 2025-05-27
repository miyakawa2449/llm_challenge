import os
import sys
import json
from openai import OpenAI
from typing import List, Dict, Any
import time # time モジュールをインポート

# --- sys.path の調整 ---
project_root_for_sys_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root_for_sys_path not in sys.path:
    sys.path.insert(0, project_root_for_sys_path)
# --- ここまで追加 ---

from src.config import settings # settings.py からAPIキーを読み込む

def check_text_with_moderation_api(client: OpenAI, text_to_check: str) -> Dict[str, Any]:
    """
    指定されたテキストをOpenAI Moderation APIでチェックする。
    """
    try:
        response = client.moderations.create(input=text_to_check)
        # response.results[0] に結果が含まれる
        return response.results[0]
    except Exception as e:
        print(f"Moderation API呼び出し中にエラーが発生しました: {e}")
        return None

def analyze_articles_for_policy_violations(input_file_path: str, output_file_path: str):
    """
    入力ファイルの記事を読み込み、Moderation APIでポリシー違反の可能性をチェックし、
    問題のありそうな記事を結果ファイルに出力する。
    """
    if not settings.OPENAI_API_KEY:
        print("エラー: OpenAI APIキーが settings.py に設定されていません。")
        return

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    problematic_articles: List[Dict[str, Any]] = []
    processed_count = 0
    api_error_count = 0

    print(f"入力ファイル: {input_file_path}")
    print(f"出力ファイル: {output_file_path}")

    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            for line_number, line in enumerate(infile, 1):
                try:
                    article_data = json.loads(line.strip())
                    article_id = article_data.get("id", f"line_{line_number}")
                    article_title = article_data.get("title", "タイトル不明")
                    article_text = article_data.get("text")

                    if not article_text:
                        print(f"警告: ID {article_id} の記事にtextフィールドがありません。スキップします。")
                        continue

                    print(f"処理中: ID {article_id} - {article_title[:30]}...")
                    moderation_result = check_text_with_moderation_api(client, article_text)
                    processed_count += 1

                    # --- ここから追加 ---
                    # API呼び出し後に短いウェイトを入れる (例: 0.5秒)
                    # レート制限エラーメッセージに "Please try again in X ms" とあるので、
                    # それを参考に調整する。
                    # text-moderation-007 の Rate limits (Free tier) は 150,000 TPM なので、
                    # 1記事あたりの平均トークン数にもよるが、少し余裕を持たせる。
                    time.sleep(0.5) # 0.5秒待機 (この値は調整が必要な場合があります)
                    # --- ここまで追加 ---

                    if moderation_result:
                        # 特に sexual と sexual/minors カテゴリをチェック
                        flagged_sexual = moderation_result.categories.sexual
                        score_sexual = moderation_result.category_scores.sexual
                        flagged_sexual_minors = moderation_result.categories.sexual_minors
                        score_sexual_minors = moderation_result.category_scores.sexual_minors

                        # いずれかのフラグがTrue、またはスコアが一定以上の場合に記録 (閾値は調整可能)
                        # OpenAIのドキュメントでは、フラグがTrueのものを主に確認することを推奨
                        if flagged_sexual or flagged_sexual_minors:
                            problematic_articles.append({
                                "id": article_id,
                                "title": article_title,
                                "flagged_sexual": flagged_sexual,
                                "score_sexual": float(f"{score_sexual:.4f}"), # 小数点以下4桁に丸める
                                "flagged_sexual_minors": flagged_sexual_minors,
                                "score_sexual_minors": float(f"{score_sexual_minors:.4f}"),
                                "all_categories": {cat: flagged for cat, flagged in moderation_result.categories.__dict__.items()},
                                "all_scores": {cat: float(f"{score:.4f}") for cat, score in moderation_result.category_scores.__dict__.items()}
                            })
                            print(f"  -> 警告: ID {article_id} にポリシー違反の可能性あり (sexual: {flagged_sexual}, sexual/minors: {flagged_sexual_minors})")
                    else:
                        api_error_count +=1

                except json.JSONDecodeError:
                    print(f"警告: 行 {line_number} のJSONデコードエラー。スキップします: {line.strip()[:100]}...")
                except Exception as e:
                    print(f"警告: 行 {line_number} の処理中に予期せぬエラー: {e}")
    
        # 結果をJSONファイルに出力
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"作成されたディレクトリ: {output_dir}")

        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(problematic_articles, outfile, ensure_ascii=False, indent=2)

        print(f"\n処理完了。")
        print(f"処理済み記事数: {processed_count}")
        print(f"APIエラー発生記事数: {api_error_count}")
        print(f"ポリシー違反の可能性のある記事数: {len(problematic_articles)}")
        print(f"詳細は {output_file_path} を確認してください。")

    except FileNotFoundError:
        print(f"エラー: 入力ファイルが見つかりません: {input_file_path}")
    except Exception as e:
        print(f"エラー: ファイル処理中に予期せぬエラーが発生しました: {e}")


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    input_jsonl = os.path.join(project_root, "output.jsonl")
    # 結果出力ファイル (プロジェクトルート/data/moderation_results/problematic_articles.json)
    output_json = os.path.join(project_root, "data", "moderation_results", "problematic_articles.json")

    print("OpenAI Moderation API を使用してコンテンツポリシーチェックを開始します。")
    print("注意: この処理にはOpenAI APIの利用料が発生する可能性があります（少量ですが）。")
    
    # proceed = input("処理を開始しますか？ (yes/no): ")
    # if proceed.lower() == 'yes':
    #    analyze_articles_for_policy_violations(input_jsonl, output_json)
    # else:
    #    print("処理を中止しました。")
    
    # 今回は自動実行
    analyze_articles_for_policy_violations(input_jsonl, output_json)
    
    print("\nスクリプトを終了します。")