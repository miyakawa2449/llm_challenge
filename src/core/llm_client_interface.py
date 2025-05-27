from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMClientInterface(ABC):
    """
    大規模言語モデル(LLM)クライアントの共通インターフェース。
    異なるLLMサービスを利用する場合でも、このインターフェースを実装することで、
    アプリケーションの他の部分への影響を最小限に抑えることを目指す。
    """

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        model: str = None,
        **kwargs: Any
    ) -> str:
        """
        指定されたプロンプトに基づいてテキストを生成する。

        Args:
            prompt (str): LLMへの入力プロンプト。
            temperature (float): 生成テキストのランダム性を制御する値 (例: 0.0-1.0)。
                                 値が低いほど決定的、高いほどランダムになる。
            max_tokens (int): 生成されるテキストの最大トークン数。
            model (str, optional): 使用するモデルの名前やID。Noneの場合、クライアントのデフォルトモデルを使用。
            **kwargs: その他、各LLMクライアント特有の追加パラメータ。

        Returns:
            str: LLMによって生成されたテキスト。エラー時は空文字列や例外を返すことも検討。
        """
        pass

    # 将来的に他の共通機能 (例: 埋め込み生成、ファインチューニングジョブの管理など) が
    # 必要になった場合は、ここに追加の抽象メソッドを定義できる。
    # @abstractmethod
    # def get_embeddings(self, text: str, model: str = None) -> List[float]:
    #     pass