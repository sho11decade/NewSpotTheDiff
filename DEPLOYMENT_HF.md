# Hugging Face Spacesへのデプロイメントガイド

このガイドでは、NewSpotTheDiff（AI間違い探し自動生成アプリ）をHugging Face Spacesにデプロイする手順を説明します。

## ✨ Hugging Face Spacesの利点

- **16GB RAM無料**: AI/MLアプリに最適な大容量メモリ
- **完全無料**: 公開Spaceなら無料で利用可能
- **簡単デプロイ**: Git push で自動デプロイ
- **ML専用**: AIモデルのホスティングに最適化
- **コミュニティ**: 大規模なML/AIコミュニティ

## 📋 前提条件

- Hugging Face アカウント（[huggingface.co](https://hugging face.co) で無料登録）
- GitHubアカウント（リポジトリ連携用）
- 基本的なGit操作の知識

## 🚀 デプロイ手順

### ステップ1: Hugging Face Spaceの作成

1. **Hugging Faceにログイン**
   - https://huggingface.co にアクセス
   - アカウントにログイン

2. **新しいSpaceを作成**
   - 右上の「New」から「Space」を選択
   - または https://huggingface.co/new-space に直接アクセス

3. **Space設定**
   - **Space name**: `spot-the-diff`（または任意の名前）
   - **SDK**: `Docker` を選択（重要！）
   - **License**: `MIT`
   - **Visibility**: `Public`（無料枠を利用する場合）
   - **Hardware**: `CPU basic` (16GB RAM, 2 vCPU) - 無料

### ステップ2: GitHubリポジトリの連携

#### オプションA: GitHub連携（推奨）

1. **Settingsタブ** に移動
2. **Repository** セクションで**GitHub**を選択
3. **GitHubリポジトリ**を接続
   - リポジトリ: `https://github.com/sho11decade/NewSpotTheDiff`
   - ブランチ: `main`

4. **自動同期を有効化**
   - 「Sync on every commit」をON

これで、GitHubにpushすると自動的にHugging Face Spacesにデプロイされます。

#### オプションB: 直接Gitプッシュ

```bash
# Hugging Face Spacesのリモートを追加
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/spot-the-diff

# プッシュ
git push hf main
```

### ステップ3: ビルド確認

1. **Logsタブ**でビルドログを確認
2. ビルド時間: 約10-15分（初回）
   - 依存関係のインストール
   - FastSAMモデルのダウンロード（1.3GB）
   - Dockerイメージのビルド

3. **ビルド成功の確認**
   ```
   Container build succeeded
   Starting Gunicorn...
   Listening at: http://0.0.0.0:7860
   ```

### ステップ4: アプリケーションアクセス

ビルドが完了すると、Spaceのメインページからアプリにアクセスできます：

```
https://huggingface.co/spaces/YOUR_USERNAME/spot-the-diff
```

## ⚙️ 環境変数設定（オプション）

Hugging Face Spacesで環境変数を設定する場合：

1. **Settings** タブに移動
2. **Repository secrets** セクション
3. 以下の秘密鍵を追加（任意）:

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `SECRET_KEY` | ランダムな文字列 | Flaskセッション用シークレット |
| `GOOGLE_ANALYTICS_ID` | `G-XXXXXXXXXX` | Google Analytics測定ID（任意） |

**注意**: `FLASK_ENV`, `YOLO_CONFIG_DIR`, `TORCH_HOME`はDockerfileで自動設定されるため不要です。

## 🎛️ ハードウェア設定

### 無料枠（CPU basic）

- **RAM**: 16GB
- **CPU**: 2 vCPU
- **ストレージ**: 50GB (ephemeral)
- **料金**: 無料
- **制限**: 非アクティブ時にスリープ

### 有料アップグレード（必要に応じて）

スリープを防ぐ場合は、有料ハードウェアにアップグレード：

- **CPU Upgrade**: $0.03/hour (8 vCPU, 32GB RAM)すなわち 約$22/月
- **常時起動**: スリープなし

**Settings** → **Hardware** からアップグレード可能。

## 📁 ファイル構造

Hugging Face Spaces用に以下の ファイルが含まれています：

```
NewSpotTheDiff/
├── Dockerfile             # ビルド設定（ポート7860対応）
├── .dockerignore          # Dockerイメージから除外するファイル
├── README.md              # Spaceの説明（HF用メタデータ含む）
├── DEPLOYMENT_HF.md       # このファイル
├── requirements.txt       # Python依存関係
├── run.py                 # アプリエントリーポイント
└── src/                   # アプリケーションコード
```

### README.mdのメタデータ

HugginFace SpacesはREADME.mdの先頭にあるYAMLメタデータを読み取ります：

```yaml
---
title: Spot the Diff - AI間違い探し自動生成
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---
```

## 🔧 Dockerfileのポイント

```dockerfile
# ポート7860を使用（Hugging Face Spaces標準）
EXPOSE 7860

# Gunicornで起動（ワーカー2、タイムアウト300秒）
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "--timeout", "300", "--max-requests", "200", "run:app"]
```

### メモリ最適化

- **ワーカー数**: 2（16GB RAMで余裕あり）
- **画像サイズ**: 768px（メモリ節約）
- **max-requests**: 200（メモリリーク防止）

## 🐛 トラブルシューティング

### ビルドエラー

**エラー: `Container build failed`**

解決策:
- Logsタブで詳細なエラーメッセージを確認
- 依存関係の問題: `requirements.txt`を確認
- システムライブラリの問題: Doc kerfileの`apt-get install`セクションを確認

**エラー: `Read-only file system`**

解決策:
- `/tmp`ディレクトリを使用（Dockerfileで設定済み）
- `FLASK_ENV=production`が設定されていることを確認

### ランタイムエラー

**エラー: `Application startup timeout`**

原因:
- FastSAMモデルのダウンロード中

解決策:
- ビルド時にモデルをダウンロード（Dockerfileで実装済み）
- ログで`FastSAM model is ready`を確認

**エラー: `Out of memory`**

解決策:
- 無料枠の16GB RAMで通常は十分
- ワーカー数を1に減らす（Dockerfileを編集）
- 画像サイズを小さくする（`src/config.py`を編集）

### Space がスリープする

**問題**: 非アクティブ後にSpaceがスリープ

解決策:
- 無料枠では正常な動作
- 常時起動が必要な場合は有料ハードウェアにアップグレード（$22/月）

## 🔄 更新とデプロイ

### GitHub連携時

```bash
# ローカルで変更
git add .
git commit -m "Update feature"

# GitHubにプッシュ
git push origin main

# Hugging Face Spacesが自動的に再デプロイ
```

### 直接プッシュ時

```bash
# 変更をコミット
git add .
git commit -m "Update feature"

# Hugging Face Spacesに直接プッシュ
git push hf main
```

## 📊 パフォーマンス

### ビルド時間

- **初回ビルド**: 10-15分
  - 依存関係インストール: 5分
  - FastSAMモデルダウンロード: 5-8分
  - Dockerイメージビルド: 2分

- **2回目以降**: 2-5分（キャッシュ利用）

### 実行時パフォーマンス

- **起動時間**: 30-60秒（モデルのプリロード）
- **リクエスト処理**: 2-3分/画像
  - オブジェクト検出: 30-45秒
  - 差異生成: 45-60秒
  - 画像合成: 30-45秒

## 💡 最適化のヒント

### メモリ使用量を削減

`src/config.py`を編集:

```python
# 処理画像サイズを小さく
PROCESSING_IMAGE_SIZE = 512  # デフォルト: 768

# ワーカー数を1に
MAX_WORKERS = 1  # デフォルト: 1
```

### 起動時間を短縮

Dockerfileでモデルの事前ダウンロードをスキップ:

```dockerfile
# この行をコメントアウト
# RUN python scripts/download_model.py || echo "Model will be downloaded on first request"
```

**注意**: 初回リクエスト時にモデルをダウンロードするため、初回が遅くなります。

## 🌐 カスタムドメイン

Hugging Face Spacesは現時点ではカスタムドメインをサポートしていません。Spaceへのアクセスは常に：

```
https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
```

形式になります。

## 📚 参考リンク

- [Hugging Face Spaces公式ドキュメント](https://huggingface.co/docs/hub/spaces)
- [Docker SDK ガイド](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Spaces ハードウェア設定](https://huggingface.co/docs/hub/spaces-gpus)
- [FastSAM公式リポジトリ](https://github.com/CASIA-IVA-Lab/FastSAM)

## 💬 サポート

問題が発生した場合：

1. [Hugging Face Community](https://huggingface.co/spaces) でサポートを求める
2. [GitHubリポジトリ](https://github.com/sho11decade/NewSpotTheDiff) でIssueを作成
3. Hugging Face Spaces の[Discord コミュニティ](https://hf.co/join/discord)で質問

---

製作: RiceZero
最終更新: 2026-02-08
