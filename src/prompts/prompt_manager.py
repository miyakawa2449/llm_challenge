import os
from typing import Dict, Any

class PromptManager:
    """
    プロンプトテンプレートの読み込みと、動的な値の埋め込みを行うクラス。
    """
    def __init__(self, template_dir: str = None):
        """
        PromptManagerのコンストラクタ。

        Args:
            template_dir (str, optional): プロンプトテンプレートが格納されているディレクトリのパス。
                                         Noneの場合、このファイルからの相対パスで 'templates' を使用。
        """
        if template_dir is None:
            # このファイルの場所を基準に 'templates' ディレクトリを指定
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.template_dir = os.path.join(base_dir, 'templates')
        else:
            self.template_dir = template_dir

        if not os.path.isdir(self.template_dir):
            # 開発初期段階ではディレクトリが存在しない可能性もあるため、警告に留める
            print(f"警告: プロンプトテンプレートディレクトリが見つかりません: {self.template_dir}")


    def load_template(self, template_name: str) -> str:
        """
        指定された名前のプロンプトテンプレートを読み込む。

        Args:
            template_name (str): テンプレートファイル名 (例: "movie_review_template.txt")。

        Returns:
            str: 読み込まれたテンプレート文字列。ファイルが見つからない場合は空文字列。
        """
        template_path = os.path.join(self.template_dir, template_name)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"エラー: プロンプトテンプレートファイルが見つかりません: {template_path}")
            return ""
        except Exception as e:
            print(f"エラー: プロンプトテンプレートファイルの読み込み中にエラーが発生しました: {e}")
            return ""

    def build_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        テンプレートを読み込み、指定されたコンテキスト情報でプレースホルダーを置換して
        最終的なプロンプト文字列を構築する。

        Args:
            template_name (str): 使用するテンプレートファイル名。
            context (Dict[str, Any]): テンプレートに埋め込む値の辞書。
                                      キーがプレースホルダー名 (例: "movie_title")、
                                      バリューが埋め込む値。

        Returns:
            str: 構築されたプロンプト文字列。テンプレートが見つからない場合は空文字列。
        """
        template_content = self.load_template(template_name)
        if not template_content:
            return ""

        prompt = template_content
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            prompt = prompt.replace(placeholder, str(value)) # 値は文字列に変換して埋め込む

        return prompt
