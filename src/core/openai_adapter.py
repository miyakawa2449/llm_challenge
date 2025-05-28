from openai import OpenAI
from src.config import settings

class OpenAIAdapter:
    """
    OpenAI APIを利用してテキスト生成を行うためのアダプタークラス。
    """

    def __init__(self, api_key: str = None, default_model: str = None):
        """
        OpenAIAdapterのコンストラクタ。

        Args:
            api_key (str, optional): OpenAI APIキー。Noneの場合、settingsから読み込む。
            default_model (str, optional): デフォルトで使用するモデル名。Noneの場合、settingsから読み込む。
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        # デフォルトモデルはここで設定するか、呼び出し側で必ず指定するようにする
        # main.py で FINETUNED_MODEL_ID が渡されることを期待
        self.default_model = default_model or settings.DEFAULT_MODEL_NAME

    def generate_text(self, messages: list, generation_params: dict = None) -> str:
        """
        OpenAI APIを使用してテキストを生成する。

        Args:
            messages (list): システムメッセージとユーザープロンプトを含むメッセージのリスト。
            generation_params (dict, optional): テキスト生成に関する追加パラメータ。

        Returns:
            str: LLMによって生成されたテキスト。エラー時はエラーメッセージを返す。
        """
        # 渡された generation_params をコピーして操作する
        params_for_api = generation_params.copy() if generation_params else {}

        # model パラメータを params_for_api から取り出す。
        # なければ、インスタンスのデフォルトモデルを使用する。
        # main.py で FINETUNED_MODEL_ID を指定しているので、それが優先される。
        model_to_use = params_for_api.pop('model', self.default_model)

        try:
            # client.chat.completions.create に model を明示的に渡し、
            # 残りのパラメータを **params_for_api で展開する
            response = self.client.chat.completions.create(
                model=model_to_use, # model はここで一度だけ指定
                messages=messages,
                **params_for_api  # ここにはもう 'model' は含まれない
            )
            return response.choices[0].message.content
        except Exception as e:
            error_message = f"エラー: OpenAI API呼び出し中にエラーが発生しました ({e})"
            print(error_message) # ターミナルにもエラー出力
            # エラーを呼び出し元に伝えるために、エラーメッセージを含む文字列を返すか、
            # カスタム例外を発生させることを検討してください。
            # ここでは、main.py のエラー処理に合わせてエラーメッセージ文字列を返します。
            return error_message

    # 将来的にOpenAI特有の他の機能 (例: ファインチューニングジョブの作成・管理) を
    # 実装する場合は、ここに追加のメソッドを定義できる。
    # def create_finetuning_job(self, training_file_id: str, model: str = "gpt-3.5-turbo"):
    #     pass