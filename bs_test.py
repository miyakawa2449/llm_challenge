from bs4 import BeautifulSoup

print("--- BeautifulSoup 最小限テスト開始 ---")

# テストケース1: 単純な日本語文字列
test_string_1 = "これはテスト文字列です。"
print(f"\nテスト文字列1: {repr(test_string_1)}")
soup1 = BeautifulSoup(test_string_1, 'html.parser')
strings1 = list(soup1.stripped_strings)
print(f"  html.parser - stripped_strings: {strings1}")
print(f"  html.parser - ' '.join(strings1): '{' '.join(strings1)}'")

# テストケース2: 簡単なHTMLを含む文字列
test_string_2 = "<h3>見出し</h3><p>これは段落です。<b>太字</b>も使えます。</p>"
print(f"\nテスト文字列2: {repr(test_string_2)}")
soup2 = BeautifulSoup(test_string_2, 'html.parser')
strings2 = list(soup2.stripped_strings)
print(f"  html.parser - stripped_strings: {strings2}")
print(f"  html.parser - ' '.join(strings2): '{' '.join(strings2)}'")

print("--- BeautifulSoup 最小限テスト終了 ---")