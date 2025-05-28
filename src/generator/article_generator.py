from src.core.openai_adapter import OpenAIAdapter
from src.prompts.prompt_manager import PromptManager # 実際のPromptManagerを使用

class ArticleGenerator:
    """
    映画レビュー記事の生成を行うクラス。
    LLMクライアントとプロンプトマネージャーを利用する。
    """
    def __init__(self, client_adapter=None, prompt_manager=None):
        """
        ArticleGeneratorのコンストラクタ。

        Args:
            client_adapter (OpenAIAdapter, optional): OpenAIAdapterのインスタンス。
                                                     Noneの場合、デフォルトのOpenAIAdapterを初期化。
            prompt_manager (PromptManager, optional): 使用するプロンプトマネージャー。
                                                     Noneの場合、デフォルトのPromptManagerを初期化。
        """
        self.client = client_adapter or OpenAIAdapter()
        self.prompter = prompt_manager or PromptManager() # 実際のPromptManagerを使用

    def generate_movie_review(
        self,
        movie_title: str,
        user_blog_style_example: str = "",
        tone_and_style_details: str = "",
        other_notes: str = "",
        generation_params: dict = None # main.py から渡される
    ) -> str:
        """
        指定された情報に基づいて映画レビュー記事を生成する。

        Args:
            movie_title (str): レビュー対象の映画タイトル。
            user_blog_style_example (str): ユーザーのブログ文体の例。
            tone_and_style_details (str, optional): 記事のトーンやスタイルの詳細指示。
            other_notes (str, optional): その他特記事項。
            generation_params (dict, optional): LLMに渡す生成パラメータ
                                                (temperature, max_tokensなど)。
                                                Noneの場合、settingsのデフォルト値が使用される。

        Returns:
            str: 生成された映画レビュー記事。エラー時は空文字列やエラーメッセージ。
        """
        # PromptManagerを使用してプロンプトを構築
        # この部分はPromptManagerの実装に依存します
        # 例:
        # prompt_data = {
        #     "movie_title": movie_title,
        #     "user_blog_style_example": user_blog_style_example,
        #     "tone_and_style_details": tone_and_style_details,
        #     "other_notes": other_notes,
        # }
        # system_prompt = self.prompter.get_system_prompt_for_movie_review()
        # user_prompt = self.prompter.get_user_prompt_for_movie_review(prompt_data)
        # messages = [
        #     {"role": "system", "content": system_prompt},
        #     {"role": "user", "content": user_prompt},
        # ]

        # --- 以下は仮のプロンプト作成ロジックです。実際のPromptManagerを使ってください ---
        system_prompt_content = "あなたはプロの映画ブロガーです。依頼された映画の魅力的なレビュー記事を執筆してください。"
        user_prompt_content = f"映画「{movie_title}」について、以下の点を考慮してレビュー記事を作成してください。\n"
        if user_blog_style_example:
            user_prompt_content += f"\n参考にする文体:\n{user_blog_style_example}\n"
        if tone_and_style_details:
            user_prompt_content += f"\nトーンとスタイル: {tone_and_style_details}\n"
        if other_notes:
            user_prompt_content += f"\nその他の指示: {other_notes}\n"
        messages = [
            {"role": "system", "content": system_prompt_content},
            {"role": "user", "content": user_prompt_content.strip()}
        ]
        # --- 仮のプロンプト作成ロジックここまで ---

        try:
            # OpenAIAdapter の generate_text メソッドに messages と generation_params を渡す
            generated_text = self.client.generate_text(
                messages=messages,
                generation_params=generation_params # main.py から渡されたパラメータ
            )
            return generated_text
        except Exception as e:
            # ArticleGeneratorレベルでのエラーハンドリング
            error_message = f"エラー: 記事生成処理中に予期せぬ問題が発生しました ({e})"
            print(error_message)
            return error_message # main.py のエラー処理に合わせる
