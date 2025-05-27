from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from typing import Any, Dict, List # List を追加

from src.core.llm_client_interface import LLMClientInterface
from src.config import settings # settings.py から設定をインポート

class OpenAIAdapter(LLMClientInterface):
    """
    OpenAI APIを利用してテキスト生成を行うためのアダプタークラス。
    LLMClientInterfaceを実装する。
    """

    def __init__(self, api_key: str = None, default_model: str = None):
        """
        OpenAIAdapterのコンストラクタ。

        Args:
            api_key (str, optional): OpenAI APIキー。Noneの場合、settingsから読み込む。
            default_model (str, optional): デフォルトで使用するモデル名。Noneの場合、settingsから読み込む。
        """
        self.api_key = api_key if api_key else settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI APIキーが設定されていません。settings.pyまたは環境変数を確認してください。")

        self.client = OpenAI(api_key=self.api_key)
        self.default_model = default_model if default_model else settings.DEFAULT_MODEL_NAME

    def generate_text(
        self,
        prompt: str,
        temperature: float = None, # settingsからデフォルト値を取得するように変更
        max_tokens: int = None,    # settingsからデフォルト値を取得するように変更
        model: str = None,
        system_message: str = "あなたは優秀な映画ブロガーです。", # デフォルトのシステムメッセージ
        **kwargs: Any
    ) -> str:
        """
        OpenAI APIを使用してテキストを生成する。

        Args:
            prompt (str): ユーザーからの入力プロンプト。
            temperature (float, optional): 生成テキストのランダム性。Noneの場合、settingsのデフォルト値を使用。
            max_tokens (int, optional): 生成されるテキストの最大トークン数。Noneの場合、settingsのデフォルト値を使用。
            model (str, optional): 使用するモデルの名前やID。Noneの場合、アダプターのデフォルトモデルを使用。
            system_message (str, optional): システムロールに渡すメッセージ。
            **kwargs: OpenAI APIのChatCompletion.createに渡すその他の追加パラメータ。
                      (例: top_p, frequency_penalty, presence_penaltyなど)

        Returns:
            str: LLMによって生成されたテキスト。エラー時は空文字列を返す。
        """
        model_to_use = model if model else self.default_model
        temp_to_use = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
        tokens_to_use = max_tokens if max_tokens is not None else settings.DEFAULT_MAX_TOKENS

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        try:
            # print(f"--- OpenAI API Request ---") # デバッグ用
            # print(f"Model: {model_to_use}")
            # print(f"Temperature: {temp_to_use}")
            # print(f"Max Tokens: {tokens_to_use}")
            # print(f"System Message: {system_message}")
            # print(f"User Prompt: {prompt[:100]}...") # 長いプロンプトは一部表示
            # print(f"Additional kwargs: {kwargs}")

            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=temp_to_use,
                max_tokens=tokens_to_use,
                **kwargs # ここで追加のキーワード引数を展開
            )
            # print(f"--- OpenAI API Response ---") # デバッグ用
            # print(response)

            generated_text = response.choices[0].message.content.strip()
            return generated_text
        except APIError as e:
            print(f"OpenAI APIエラーが発生しました: {e}")
        except RateLimitError as e:
            print(f"OpenAI APIレート制限エラーが発生しました: {e}")
        except APITimeoutError as e:
            print(f"OpenAI APIタイムアウトエラーが発生しました: {e}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
        return "" # エラー時は空文字列を返す

    # 将来的にOpenAI特有の他の機能 (例: ファインチューニングジョブの作成・管理) を
    # 実装する場合は、ここに追加のメソッドを定義できる。
    # def create_finetuning_job(self, training_file_id: str, model: str = "gpt-3.5-turbo"):
    #     pass