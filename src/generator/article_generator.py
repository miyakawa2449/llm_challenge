from src.core.adapters.openai_adapter import OpenAIAdapter
from src.prompts.prompt_manager import PromptManager
from src.config import settings # settings.py から設定をインポート
from typing import Dict, Any

class ArticleGenerator:
    """
    映画レビュー記事の生成を行うクラス。
    LLMクライアントとプロンプトマネージャーを利用する。
    """
    def __init__(self, llm_client: OpenAIAdapter = None, prompt_manager: PromptManager = None):
        """
        ArticleGeneratorのコンストラクタ。

        Args:
            llm_client (OpenAIAdapter, optional): 使用するLLMクライアント。
                                                Noneの場合、デフォルトのOpenAIAdapterを初期化。
            prompt_manager (PromptManager, optional): 使用するプロンプトマネージャー。
                                                     Noneの場合、デフォルトのPromptManagerを初期化。
        """
        self.llm_client = llm_client if llm_client else OpenAIAdapter()
        self.prompt_manager = prompt_manager if prompt_manager else PromptManager()

    def generate_movie_review(
        self,
        movie_title: str,
        user_blog_style_example: str,
        tone_and_style_details: str = "親しみやすく、読者の興味を引くように。", # デフォルト値
        other_notes: str = "特になし。", # デフォルト値
        template_name: str = "movie_review_template.txt",
        generation_params: Dict[str, Any] = None
    ) -> str:
        """
        指定された情報に基づいて映画レビュー記事を生成する。

        Args:
            movie_title (str): レビュー対象の映画タイトル。
            user_blog_style_example (str): ユーザーのブログ文体の例。
            tone_and_style_details (str, optional): 記事のトーンやスタイルの詳細指示。
            other_notes (str, optional): その他特記事項。
            template_name (str, optional): 使用するプロンプトテンプレート名。
            generation_params (Dict[str, Any], optional): LLMに渡す生成パラメータ
                                                        (temperature, max_tokensなど)。
                                                        Noneの場合、settingsのデフォルト値が使用される。

        Returns:
            str: 生成された映画レビュー記事。エラー時は空文字列やエラーメッセージ。
        """
        context = {
            "movie_title": movie_title,
            "user_blog_style_example": user_blog_style_example,
            "tone_and_style_details": tone_and_style_details,
            "other_notes": other_notes,
        }

        prompt = self.prompt_manager.build_prompt(template_name, context)
        if not prompt:
            return "エラー: プロンプトの構築に失敗しました。"

        # LLMへのリクエストパラメータを設定
        # generation_paramsが指定されていればそれを使用し、なければ空の辞書を渡す
        # (OpenAIAdapter側でsettingsのデフォルト値が使われる)
        params_to_use = generation_params if generation_params else {}

        try:
            # print(f"--- Generating article with prompt ---") # デバッグ用
            # print(prompt)
            # print(f"--- Generation parameters ---")
            # print(params_to_use)

            generated_article = self.llm_client.generate_text(
                prompt=prompt,
                **params_to_use # temperature, max_tokensなどをキーワード引数として渡す
            )
            return generated_article
        except Exception as e:
            print(f"記事生成中にエラーが発生しました: {e}")
            return f"エラー: 記事生成中に予期せぬ問題が発生しました ({e})"
