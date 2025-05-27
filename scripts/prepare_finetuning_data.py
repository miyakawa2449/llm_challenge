import json
import os

def convert_to_finetuning_format(input_file_path: str, output_file_path: str):
    """
    元のブログ記事データ (JSON Lines) をOpenAIファインチューニング用の
    チャット形式 (JSON Lines) に変換する。

    Args:
        input_file_path (str): 元のデータファイルへのパス (例: "output.jsonl")。
        output_file_path (str): 変換後のデータファイルへのパス (例: "data/finetuning_data/training_corpus.jsonl")。
    """
    processed_count = 0
    skipped_count = 0

    # 出力ディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"作成されたディレクトリ: {output_dir}")

    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
             open(output_file_path, 'w', encoding='utf-8') as outfile:

            for line in infile:
                try:
                    original_data = json.loads(line.strip())
                    movie_title = original_data.get("title")
                    blog_text = original_data.get("text")

                    if not movie_title or not blog_text:
                        print(f"警告: titleまたはtextが不足しているため、エントリをスキップします: {original_data.get('id', 'ID不明')}")
                        skipped_count += 1
                        continue

                    # ファインチューニング用のメッセージリストを作成
                    messages = [
                        {
                            "role": "system",
                            "content": "あなたは、筆者の個人的な視点と文体を強く反映した映画レビューを書くアシスタントです。"
                        },
                        {
                            "role": "user",
                            # プロンプトは目的に応じて調整可能
                            "content": f"映画「{movie_title}」についてのブログ記事を、私のスタイルで執筆してください。"
                        },
                        {
                            "role": "assistant",
                            "content": blog_text.strip() # 前後の空白を除去
                        }
                    ]

                    # JSON Lines形式で出力ファイルに書き込む
                    outfile.write(json.dumps({"messages": messages}, ensure_ascii=False) + "\n")
                    processed_count += 1

                except json.JSONDecodeError:
                    print(f"警告: JSONデコードエラーのため、行をスキップします: {line.strip()[:100]}...")
                    skipped_count += 1
                except Exception as e:
                    print(f"警告: 予期せぬエラーのため、エントリ処理中にエラーが発生しました: {e}")
                    skipped_count += 1

        print(f"\n変換処理が完了しました。")
        print(f"処理されたエントリ数: {processed_count}")
        print(f"スキップされたエントリ数: {skipped_count}")
        print(f"出力ファイル: {output_file_path}")

    except FileNotFoundError:
        print(f"エラー: 入力ファイルが見つかりません: {input_file_path}")
    except Exception as e:
        print(f"エラー: ファイル処理中に予期せぬエラーが発生しました: {e}")


if __name__ == "__main__":
    # プロジェクトルートを基準にパスを設定
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 入力ファイル (プロジェクトルートにある output.jsonl)
    input_jsonl = os.path.join(project_root, "output.jsonl")
    
    # 出力ファイル (プロジェクトルート/data/finetuning_data/training_corpus.jsonl)
    # Spec.md で定義したパスに合わせる
    output_finetuning_jsonl = os.path.join(project_root, "data", "finetuning_data", "training_corpus.jsonl")

    print(f"入力ファイル: {input_jsonl}")
    print(f"出力ファイル: {output_finetuning_jsonl}")

    convert_to_finetuning_format(input_jsonl, output_finetuning_jsonl)
