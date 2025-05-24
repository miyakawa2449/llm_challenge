# LLMチャレンジ on Local Desktop

## 1. プロジェクト概要
このプロジェクトは、NVIDIA RTX 3060を搭載したローカルデスクトップ環境を活用し、大規模言語モデル (LLM) の実験、特にファインチューニングを行うことを目的としています。
個人の映画ブログ記事をデータセットとして用い、独自のスタイルを反映した文章生成モデルの構築を目指します。

## 2. プロジェクトの目的
- ローカルGPU環境でのLLM開発ワークフローの確立
- 少量データからの効率的なファインチューニング手法の探求
- 自分らしい文体を模倣するLLMの実現可能性の検証

## 3. 現在の進捗
- **環境構築完了**:
    - Windows 11 + WSL2 (Ubuntu 22.04)
    - NVIDIAドライバ、CUDA Toolkit 12.9、cuDNN
    - Python 3.10 (Miniconda + pyenv)
    - PyTorch 2.7.0 (CUDA 12.8対応ビルド)
- **GPU動作確認**: `check_pytorch_gpu.py` により、PyTorchがRTX 3060を正常に認識していることを確認済み。
- **バージョン管理**: GitおよびGitHubにて管理。

## 4. 環境セットアップの主要手順 (備忘録)
1. WSL2 Ubuntu環境構築
2. NVIDIAドライバ (Windows側) の最新化
3. CUDA Toolkit for WSL のインストール
4. cuDNN のインストール
5. `pyenv` と `Miniconda` を用いたPython環境 (`llm_env`) の構築
6. `llm_env` 環境へのPyTorch (GPU対応版) のインストール

## 5. 今後の予定
- 映画ブログ記事データの収集と前処理
- ベースとなるLLMの選定
- ファインチューニングスクリプトの実装と実行
- 生成結果の評価と改善

## 6. リポジトリ構成 (予定)
- `data/`: 学習データ格納用
- `src/`: ソースコード (前処理、学習、推論スクリプトなど)
- `models/`: 学習済みモデル保存用
- `notebooks/`: 実験用Jupyter Notebook
- `report/`: 作業レポート