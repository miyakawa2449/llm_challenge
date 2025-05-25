import re
import json

# アフィリエイトリンクやASINを検出するための正規表現パターンのリスト
# これらが含まれる段落は全体が削除されます。
AFFILIATE_PATTERNS = [
    # AmazonのURL (http, https, wwwありなし、各種TLDに対応)
    re.compile(r"https?://(?:www\.)?amazon\.(?:[a-z\.]{2,6})/[^\s\"'<]+", re.IGNORECASE),
    # はてなASIN詳細の形式
    re.compile(r"\[asin:[^\]]+:detail\]", re.IGNORECASE),
    # <a> タグで囲まれたAmazonリンクの存在をチェック (href属性のみ確認)
    re.compile(r"<a\s[^>]*href=[\"']https?://(?:www\.)?amazon\.(?:[a-z\.]{2,6})/[^\s\"']+[\"']", re.IGNORECASE)
]

# 除去対象のショートコードの正規表現パターンのリスト
# これらはショートコード自体が削除されますが、段落は残ります。
SHORTCODE_PATTERNS = [
    re.compile(r"\[caption\].*?\[/caption\]", re.DOTALL | re.IGNORECASE)
    # 他のショートコードのパターンがあれば、ここに追加できます。例:
    # re.compile(r"\[gallery\s.*?\]", re.IGNORECASE)
]

def contains_affiliate_or_product_link(paragraph_text):
    """
    段落内にアフィリエイト関連のパターンが含まれているかどうかを判定します。
    """
    for pattern in AFFILIATE_PATTERNS:
        if pattern.search(paragraph_text):
            return True
    return False

def remove_shortcodes_from_text(text_content):
    """
    テキストから指定されたショートコードを除去します。
    """
    processed_text = text_content
    for pattern in SHORTCODE_PATTERNS:
        processed_text = pattern.sub("", processed_text)
    return processed_text

def process_text_content(original_text_content):
    """
    与えられたテキストコンテンツに対して、指定された全ての処理を適用します。
    """
    if not original_text_content or not isinstance(original_text_content, str):
        return "" # もし入力がNoneまたは文字列でない場合は空文字を返す

    # 1. 改行コードを '\n' に統一
    text = original_text_content.replace("\r\n", "\n")

    # 2. テキストを行に分割
    lines = text.split('\n')

    # 3. 段落に再構成 (空行または空白のみの行が段落の区切り)
    #    この時点では、各段落は元の行のリストとして保持
    raw_paragraphs_lines = []
    current_paragraph_single_lines = []
    for line_content in lines:
        if line_content.strip() == "": # 空行または空白のみの行
            if current_paragraph_single_lines: # それまでに集めた行があれば、一つの段落として確定
                raw_paragraphs_lines.append("\n".join(current_paragraph_single_lines))
                current_paragraph_single_lines = []
        else:
            current_paragraph_single_lines.append(line_content) # 内容のある行を追加
    
    if current_paragraph_single_lines: # ループ後に残っている行があれば、最後の段落として追加
        raw_paragraphs_lines.append("\n".join(current_paragraph_single_lines))

    # 4. 各段落を処理
    final_paragraphs_to_join = []
    for paragraph_block in raw_paragraphs_lines:
        # a. アフィリエイト/商品紹介が含まれるかチェック
        if contains_affiliate_or_product_link(paragraph_block):
            continue # 含まれていれば、この段落はスキップ（除去）

        # b. ショートコードを除去
        paragraph_without_shortcodes = remove_shortcodes_from_text(paragraph_block)

        # c. 段落内の整形: 各行の先頭・末尾の空白を除去し、
        #    整形後に空になった行は詰める（段落内の不要な空行を除去）
        #    段落内の意図的な改行は維持される。
        paragraph_lines_cleaned = []
        for line_in_para in paragraph_without_shortcodes.split('\n'):
            stripped_line = line_in_para.strip()
            if stripped_line: # stripした結果、内容が残る行のみ採用
                paragraph_lines_cleaned.append(stripped_line)
        
        if paragraph_lines_cleaned: # 整形後に内容が残っている段落のみ追加
            final_paragraphs_to_join.append("\n".join(paragraph_lines_cleaned))

    # 5. 処理済みの段落を二重改行 ('\n\n') で結合
    return "\n\n".join(final_paragraphs_to_join)

# --- 以下は、JSONLファイルを処理するためのメインロジックの例です ---
# この部分は、実際のファイルパスやJSON内のテキストフィールド名に合わせて調整が必要です。

# input_file_path = "output.jsonl"
# output_file_path = "output_processed.jsonl"
# text_field_name = "text" # JSONオブジェクト内のテキストデータが含まれるフィールド名

# try:
#     with open(input_file_path, 'r', encoding='utf-8') as infile, \
#          open(output_file_path, 'w', encoding='utf-8') as outfile:
#         for line_number, json_line in enumerate(infile, 1):
#             try:
#                 data_object = json.loads(json_line)
#                 if text_field_name in data_object and isinstance(data_object[text_field_name], str):
#                     # メインのテキスト処理関数を呼び出し
#                     processed_content = process_text_content(data_object[text_field_name])
#                     data_object[text_field_name] = processed_content
#                 else:
#                     # テキストフィールドが存在しないか、文字列でない場合は警告を出すなど検討
#                     print(f"Warning: Line {line_number}: Field '{text_field_name}' not found or not a string. Original data kept.")
                
#                 # 処理後のJSONオブジェクトを新しいファイルに書き出し
#                 outfile.write(json.dumps(data_object, ensure_ascii=False) + '\n')
#             except json.JSONDecodeError:
#                 print(f"Error: Line {line_number}: Malformed JSON. Skipping line: {json_line.strip()}")
#             except Exception as e:
#                 print(f"Error: Line {line_number}: An unexpected error occurred: {e}")
#     print(f"Processing complete. Output written to {output_file_path}")

# except FileNotFoundError:
#     print(f"Error: Input file '{input_file_path}' not found.")
# except Exception as e:
#     print(f"An unexpected error occurred during file operations: {e}")
