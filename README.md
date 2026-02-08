---
title: Spot the Diff - AI間違い探し自動生成
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Spot the Diff - AI間違い探し自動生成

AIを使用して自動的に間違い探しパズルを生成するWebアプリケーションです。画像をアップロードするだけで、高品質な間違い探しパズルを数分で作成できます。

## 🌟 特徴

- **AI自動生成**: FastSAMモデルを使用した高精度なオブジェクトセグメンテーション
- **3つの難易度**: 簡単（3箇所）・普通（5箇所）・難しい（7箇所）から選択可能
- **印刷対応**: A4サイズのレイアウトで出力（300 DPI）
- **答え付き画像**: 解答確認用の画像も自動生成
- **高速処理**: 最適化されたアルゴリズムで2-3分で生成

## 🚀 使い方

1. **画像をアップロード**
   - 対応フォーマット: PNG、JPG、JPEG
   - 画像サイズ: 512px - 4096px
   - ファイルサイズ: 最大10MB

2. **難易度を選択**
   - 簡単: 3箇所の違い（大きく分かりやすい変更）
   - 普通: 5箇所の違い（ミックスサイズ）
   - 難しい: 7箇所の違い（小さく繊細な変更）

3. **生成ボタンをクリック**
   - 処理時間: 約2-3分

4. **結果を確認・ダウンロード**
   - オリジナル画像
   - 間違い探し画像
   - 答え付き画像（赤丸で違いを表示）
   - A4レイアウト（印刷用）

## 🔧 技術スタック

| コンポーネント | 技術 | 用途 |
|-----------|------|-----|
| Webフレームワーク | Flask 3.x | HTTPリクエスト処理 |
| AIモデル | FastSAM (Ultralytics) | オブジェクトセグメンテーション |
| 画像処理 | OpenCV, Pillow | インペインティング、色変更、合成 |
| 数値計算 | NumPy, scikit-image | 配列操作、画像解析 |
| データベース | SQLite | ジョブステータス管理 |
| デプロイ | Hugging Face Spaces | Docker SDK |

## 📊 システム要件

- **RAM**: 16GB（Hugging Face Spaces提供）
- **モデルサイズ**: 1.3GB (FastSAM-x)
- **処理時間**: 2-3分/画像
- **ポート**: 7860（Hugging Face Spaces標準）

## 🛠️ ローカル開発

### 前提条件

- Python 3.10以上
- 4GB以上のRAM推奨（ローカル実行時）

### セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/sho11decade/NewSpotTheDiff.git
cd NewSpotTheDiff

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# モデルのダウンロード
python scripts/download_model.py

# アプリケーションの起動
python run.py
```

アプリケーションは http://localhost:5000 で起動します。

## 🐳 Docker（ローカル）

```bash
# イメージのビルド
docker build -t spotdiff .

# コンテナの実行
docker run -p 7860:7860 spotdiff
```

http://localhost:7860 でアクセスできます。

## 🎯 アーキテクチャ

```
アップロード → FastSAM → セグメント選択 → 3種類の変更 → 画像合成 → A4レイアウト
                           ├─ オブジェクト削除（インペインティング）
                           ├─ 色変更（HSV変換）
                           └─ オブジェクト複製（貼り付け）
```

### 処理フロー

1. **画像前処理**: アップロードされた画像を768pxにリサイズ（メモリ最適化）
2. **オブジェクト検出**: FastSAMで全オブジェクトをセグメント化
3. **品質フィルタリング**: エッジの滑らかさ、形状、サイズで高品質なセグメントを選択
4. **差異生成**: 難易度に応じて3-7個の変更を適用
5. **答え可視化**: 赤丸で違いをマーキング
6. **A4レイアウト**: 印刷用300 DPIフォーマットで出力

## 🚀 Hugging Face Spacesへのデプロイ

詳細な手順は [DEPLOYMENT_HF.md](DEPLOYMENT_HF.md) を参照してください。

### クイックデプロイ

1. Hugging Face Spacesで新しいSpaceを作成
2. SDK: Docker を選択
3. GitHubリポジトリを接続
4. 自動デプロイ開始（ビルド時間: 約10-15分）

## 📝 ライセンス

MIT License

## 👤 作者

RiceZero

## 🙏 謝辞

- [FastSAM](https://github.com/CASIA-IVA-Lab/FastSAM) - Fast Segment Anything Model
- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLO framework
- [Hugging Face Spaces](https://huggingface.co/spaces) - ML app hosting
- [OpenCV](https://opencv.org/) - Computer vision library

## 🔗 リンク

- [GitHub Repository](https://github.com/sho11decade/NewSpotTheDiff)
- [Deployment Guide (Hugging Face)](DEPLOYMENT_HF.md)
- [Original Deployment Guide (Leapcell)](DEPLOYMENT.md)

---

Made with ❤️ by RiceZero | Powered by FastSAM and Hugging Face Spaces