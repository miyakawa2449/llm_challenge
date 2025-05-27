import csv
import json
import re
from bs4 import BeautifulSoup, Comment # Comment をインポートに追加

# --- 追加ここから ---
# アフィリエイト関連のHTML要素を特定するためのセレクタリスト
AFFILIATE_HTML_SELECTORS = [
    {"name": "div", "attrs": {"class": "hatena-asin-detail"}},
    # 他にもHTML構造で特定できるアフィリエイトコンテナがあればここに追加
    # 例: {"name": "div", "attrs": {"class": "freezed"}} # サンプルデータより
]

# テキスト抽出後、これらのパターンを含む「段落」を除去するための正規表現リスト
TEXT_AFFILIATE_PATTERNS_FOR_PARAGRAPH_REMOVAL = [
    re.compile(r"https?://(?:www\.)?amazon\.(?:[a-z\.]{2,6})/[^\s\"'<]+", re.IGNORECASE),
    re.compile(r"\[asin:[^\]]+:detail\]", re.IGNORECASE),
]

# 除去対象のショートコードの正規表現パターンリスト
SHORTCODE_PATTERNS_TO_REMOVE = [
    re.compile(r"\[caption.*?\[/caption\]", re.DOTALL | re.IGNORECASE), # [caption]...[/caption] 全体
    re.compile(r"\[/?\w+.*?\]"),  # [shortcode attr="value"] や [/shortcode] 形式の一般的なもの
]
# --- 追加ここまで ---

def clean_content(html_content): # 関数名を元のまま使用
    """
    HTMLコンテンツからHTMLタグ、コメント、指定されたショートコード、
    アフィリエイト関連の要素や段落を除去し、テキストを整形する。
    段落間は二重改行で区切る。
    """
    if not html_content or not isinstance(html_content, str):
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. HTMLコメントを除去 (例: <!--more-->)
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # 2. HTML構造ベースのアフィリエイト要素を除去
    for selector in AFFILIATE_HTML_SELECTORS:
        for element in soup.find_all(selector["name"], selector.get("attrs", {})):
            element.decompose() # 要素ごと削除

    # 3. <br> タグを改行文字に置換 (テキスト抽出前に)
    for br_tag in soup.find_all('br'):
        br_tag.replace_with('\n')

    # 4. テキスト抽出 (ブロック要素間の区切りとして改行を意識)
    raw_text = soup.get_text(separator='\n', strip=True)

    # 5. テキストレベルでのショートコード除去
    for pattern in SHORTCODE_PATTERNS_TO_REMOVE:
        raw_text = pattern.sub('', raw_text)
    
    # --- ここに追加 ---
    # 5.1. 特定のTwitterアカウント表記の改行を除去
    # raw_text = raw_text.replace("\n@miyakawa2449\n", "@miyakawa2449")
    # もし、@miyakawa2449 の前後にスペースが1つだけあるパターンも考慮するなら、以下のように複数回replaceするか正規表現を使います。
    # 例: raw_text = raw_text.replace(" \n@miyakawa2449\n ", " @miyakawa2449 ") 
    # より汎用的にするなら正規表現: 
    raw_text = re.sub(r'\s*\n@miyakawa2449\n\s*', ' @miyakawa2449 ', raw_text).strip()
    # ただし、今回はご指定の完全一致パターンで対応します。
    # --- 追加ここまで ---

    # 6. 段落の分割と整形
    #    連続する改行(3つ以上)を2つにまとめる
    processed_text = re.sub(r'\n{3,}', '\n\n', raw_text)
    # 空白のみの行が連続するようなパターンも二重改行に近づける
    processed_text = re.sub(r'(\n\s*){2,}', '\n\n', processed_text).strip()

    paragraphs_candidates = processed_text.split('\n\n')
    
    final_cleaned_paragraphs = []
    for para_text_candidate in paragraphs_candidates:
        current_para_text = para_text_candidate.strip()

        if not current_para_text: # 空の段落候補はスキップ
            continue

        # 7. アフィリエイトパターンを含む段落は除去
        is_affiliate_para = False
        for aff_pattern in TEXT_AFFILIATE_PATTERNS_FOR_PARAGRAPH_REMOVAL:
            if aff_pattern.search(current_para_text):
                is_affiliate_para = True
                break
        if is_affiliate_para:
            continue

        # 8. 段落内の整形:
        #    - 段落内の改行は維持
        #    - 各行の先頭・末尾の空白除去
        #    - 各行内の連続する空白を単一スペースに
        lines_in_current_para = current_para_text.split('\n')
        cleaned_lines_for_para = []
        for line in lines_in_current_para:
            cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
            if cleaned_line: # 空でなければ追加
                cleaned_lines_for_para.append(cleaned_line)
        
        if cleaned_lines_for_para: # 整形後に内容が残っていれば段落として採用
            final_cleaned_paragraphs.append("\n".join(cleaned_lines_for_para))

    # 9. 最終的に空でなくなった段落を二重改行で結合
    result = "\n\n".join(final_cleaned_paragraphs)
    
    return result.strip() # 全体の先頭末尾の空白も除去

def convert_csv_to_jsonl(input_csv_filepath, output_jsonl_filepath):
    """
    CSVファイルを読み込み、指定された形式でJSONLファイルに変換する。
    """
    processed_count = 0
    try:
        with open(input_csv_filepath, 'r', encoding='utf-8', newline='') as csvfile, \
             open(output_jsonl_filepath, 'w', encoding='utf-8') as jsonlfile:

            reader = csv.DictReader(csvfile)

            # CSVヘッダーの存在確認
            if not reader.fieldnames:
                print(f"エラー: CSVファイル '{input_csv_filepath}' が空か、ヘッダー行がありません。")
                return

            # 必要な列が存在するか確認
            required_cols = ["ID", "post_title", "post_content", "post_date", "category"]
            missing_cols = [col for col in required_cols if col not in reader.fieldnames]
            if missing_cols:
                print(f"エラー: CSVファイル '{input_csv_filepath}' に必要な列がありません: {', '.join(missing_cols)}")
                return

            for row in reader:
                try:
                    post_id = row.get("ID", "").strip()
                    post_title = row.get("post_title", "").strip()
                    post_content_raw = row.get("post_content", "")
                    post_date = row.get("post_date", "").strip()
                    category = row.get("category", "").strip()

                    # post_contentのクリーニング
                    cleaned_text = clean_content(post_content_raw)

                    # JSONLオブジェクトの作成
                    # キーの順番: id, title, text, category, post_date
                    json_record = {
                        "id": post_id,
                        "title": post_title,
                        "text": cleaned_text,
                        "category": category,
                        "post_date": post_date
                    }

                    # JSONLファイルに書き込み
                    jsonlfile.write(json.dumps(json_record, ensure_ascii=False) + '\n')
                    processed_count += 1

                except Exception as e:
                    print(f"行の処理中にエラーが発生しました (ID: {row.get('ID', 'N/A')}): {e}")
                    # エラーが発生した行をスキップして処理を続ける場合は以下をコメント解除
                    # continue

            print(f"処理が完了しました。{processed_count}件のレコードが '{output_jsonl_filepath}' に出力されました。")

    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{input_csv_filepath}' が見つかりません。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == '__main__':
    # 入力CSVファイル名と出力JSONLファイル名を指定
    # このファイル名は実際の環境に合わせて変更してください
    input_file = 'downloaded_data.csv'
    output_file = 'output.jsonl'

    print(f"'{input_file}' を処理して '{output_file}' に出力します...")
    convert_csv_to_jsonl(input_file, output_file)

    # --- 使用例 ---
    # スクリプトと同じディレクトリに 'downlooaded_data.csv' があると仮定します。
    #
    # 例: downloaded_data.csv の内容
    # ID,post_title,post_content,post_date,category,other_column
    # 1,"最初の記事","<p>これは<b>最初の</b>記事です。  改行1\n\n改行2</p>[my_shortcode] <p>追加テキスト</p>","2023-01-01","技術","abc"
    # 2,"２番目の記事","<div>記事の本文。</div>  [another_code attr='test'] \n\n さらにテキスト。","2023-01-02","趣味","def"
    #
    # 例: output.jsonl の期待される内容 (1行1JSON)
    # {"id": "1", "title": "最初の記事", "text": "これは 最初の 記事です。 改行1\n改行2 追加テキスト", "category": "技術", "post_date": "2023-01-01"}
    # {"id": "2", "title": "２番目の記事", "text": "記事の本文。 さらにテキスト。", "category": "趣味", "post_date": "2023-01-02"}
