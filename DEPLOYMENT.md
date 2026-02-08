# Leapcellへのデプロイメントガイド

このドキュメントでは、NewSpotTheDiffアプリケーションをLeapcellホスティングサービスにデプロイする手順を説明します。

## 目次
- [前提条件](#前提条件)
- [ステップ1: リポジトリの準備](#ステップ1-リポジトリの準備)
- [ステップ2: Leapcellプロジェクトの作成](#ステップ2-leapcellプロジェクトの作成)
- [ステップ3: 環境変数の設定](#ステップ3-環境変数の設定)
- [ステップ4: デプロイメント設定](#ステップ4-デプロイメント設定)
- [ステップ5: FastSAMモデルの配置](#ステップ5-fastsamモデルの配置)
- [ステップ6: デプロイ](#ステップ6-デプロイ)
- [ステップ7: カスタムドメインの設定](#ステップ7-カスタムドメインの設定)
- [トラブルシューティング](#トラブルシューティング)
- [メンテナンスとモニタリング](#メンテナンスとモニタリング)

## 前提条件

- GitHubアカウント
- Leapcellアカウント
- カスタムドメイン（オプション: spotthediff.ricezero.fun）
- Google Analyticsアカウント（オプション）

## ステップ1: リポジトリの準備

### 1.1 必要なファイルの確認

以下のファイルがリポジトリに含まれていることを確認してください：

```
NewSpotTheDiff/
├── requirements.txt          # 本番環境用依存関係（gunicorn含む）
├── run.py                    # アプリケーションエントリーポイント
├── src/
│   ├── app.py
│   └── config.py
└── README.md
```

### 1.2 requirements.txtの確認

`requirements.txt`に以下が含まれていることを確認：

```txt
flask>=3.0
pillow>=10.0
opencv-python-headless>=4.8
opencv-contrib-python-headless>=4.8
ultralytics>=8.0
numpy>=1.24
scikit-image>=0.21.0
flask-talisman>=1.0
flask-limiter>=3.5
gunicorn>=21.2
redis>=5.0
```

**重要:** `opencv-python-headless`を使用していますこれはGUIライブラリへの依存が少なく、サーバー環境に最適です。

### 1.3 GitHubへのプッシュ

```bash
git add .
git commit -m "Prepare for Leapcell deployment"
git push origin main
```

## ステップ2: Leapcellプロジェクトの作成

1. **Leapcellにログイン**
   - https://leapcell.io にアクセス
   - GitHubアカウントで認証

2. **新しいプロジェクトを作成**
   - 「New Project」をクリック
   - GitHubリポジトリを選択: `NewSpotTheDiff`
   - ブランチを選択: `main`

3. **プロジェクト名の設定**
   - Project Name: `spot-the-diff`
   - Description: AI-powered spot-the-difference puzzle generator

## ステップ3: 環境変数の設定

Leapcellのプロジェクト設定で以下の環境変数を設定してください：

### 必須の環境変数

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `SECRET_KEY` | ランダムな文字列（例: `your-secret-key-here-change-this`） | Flaskセッション用のシークレットキー |
| `SITE_DOMAIN` | `spotthediff.ricezero.fun` | あなたのドメイン名 |

### オプションの環境変数

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `GOOGLE_ANALYTICS_ID` | `G-XXXXXXXXXX` | Google Analytics測定ID |
| `RATELIMIT_STORAGE_URI` | `redis://your-redis-url` | Redisストレージ（高度な設定） |

### シークレットキーの生成方法

```python
import secrets
print(secrets.token_urlsafe(32))
```

または、bashで：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## ステップ4: デプロイメント設定

Leapcellのビルド設定で以下を入力してください：

### ビルド設定

| 設定項目 | 値 |
|---------|-----|
| **Runtime** | Python 3.10+ |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 2 -b :8080 --timeout 120 run:app` |
| **Port** | `8080` |

**重要:** OpenCVのインストールにシステムライブラリが必要です。標準のビルドコマンドで失敗する場合は、以下を使用してください：

```bash
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 && pip install -r requirements.txt
```

または、build.shスクリプトを使用：

```bash
chmod +x build.sh && ./build.sh
```

**注意:** `requirements.txt`では`opencv-python-headless`を使用しています。これはGUIライブラリへの依存が少なく、サーバー環境に適しています。

### Start Commandの説明

```bash
gunicorn -w 2 -b :8080 --timeout 120 run:app
```

- `-w 2`: ワーカープロセス数（CPUコアに応じて調整）
- `-b :8080`: バインドするポート
- `--timeout 120`: タイムアウト時間（画像処理に十分な時間を確保）
- `run:app`: `run.py`ファイルの`app`オブジェクトを起動

## ステップ5: FastSAMモデルの配置

FastSAMモデルは約1.3GBあり、Gitリポジトリに含めることはできません。以下の方法で対応してください：

### オプション1: 初回実行時に自動ダウンロード（推奨）

アプリケーションが初回実行時に自動的にモデルをダウンロードします。ただし、初回起動時に時間がかかります。

### オプション2: 永続ストレージの使用

Leapcellの永続ストレージ機能を使用して、モデルファイルを配置します：

1. Leapcellダッシュボードで「Storage」セクションに移動
2. 新しいボリュームを作成: `/app/instance/models`
3. FastSAM-x.ptをアップロード

### オプション3: 外部ストレージからのダウンロード

環境変数でモデルのURLを指定し、起動時にダウンロードするスクリプトを追加：

```bash
# Start Commandを変更
python scripts/download_model.py && gunicorn -w 2 -b :8080 --timeout 120 run:app
```

## ステップ6: デプロイ

1. **デプロイの開始**
   - Leapcellダッシュボードで「Deploy」をクリック
   - ビルドログを監視

2. **ビルドの確認**
   - ビルドログで依存関係のインストールを確認
   - エラーがないことを確認

3. **デプロイの完了**
   - デプロイが完了すると、一時的なURLが提供されます
   - 例: `https://spot-the-diff-xxxxx.leapcell.dev`

4. **動作確認**
   - 提供されたURLにアクセス
   - 画像をアップロードして間違い探しを生成してみる

## ステップ7: カスタムドメインの設定

### 7.1 Leapcellでのドメイン設定

1. Leapcellダッシュボードで「Domains」セクションに移動
2. 「Add Custom Domain」をクリック
3. ドメインを入力: `spotthediff.ricezero.fun`
4. DNS設定情報を確認（CNAMEレコード）

### 7.2 DNSレコードの設定

あなたのDNSプロバイダー（ricezero.fun）で以下を設定：

```
Type: CNAME
Name: spotthediff
Value: your-app.leapcell.dev
TTL: 3600
```

### 7.3 SSL/TLS証明書

Leapcellは自動的にLet's Encrypt証明書を発行します。数分待ってから、HTTPSでアクセスできることを確認してください：

```
https://spotthediff.ricezero.fun
```

## トラブルシューティング

### ビルドエラー

**エラー: `requirements.txt not found`**

解決策:
- リポジトリのルートに`requirements.txt`があることを確認
- ビルドコマンドが正しいことを確認

**エラー: `opencv-python installation failed`または`opencv-contrib-python installation failed`**

解決策1（推奨）:
- Build Commandにシステム依存関係のインストールを追加:
  ```bash
  apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 && pip install -r requirements.txt
  ```

解決策2:
- ビルドスクリプトを使用:
  ```bash
  chmod +x build.sh && ./build.sh
  ```

**注意:** プロジェクトでは既に`opencv-python-headless`を使用しており、GUIライブラリへの依存が少なくなっています。

### 起動エラー

**エラー: `ModuleNotFoundError: No module named 'src'`**

解決策:
- Start Commandが正しいことを確認: `gunicorn -w 2 -b :8080 --timeout 120 run:app`

**エラー: `FileNotFoundError: FastSAM model not found`**

解決策:
- 初回実行時にモデルが自動ダウンロードされるのを待つ
- または、手動でモデルを配置（ステップ5参照）

### ランタイムエラー

**エラー: `Worker timeout`**

解決策:
- Start Commandのタイムアウトを増やす:
  ```bash
  gunicorn -w 2 -b :8080 --timeout 180 run:app
  ```

**エラー: `Out of memory`**

解決策:
- ワーカー数を減らす: `-w 1`
- Leapcellプランをアップグレードしてメモリを増やす

### パフォーマンス問題

**処理が遅い**

最適化:
1. ワーカー数を調整（CPUコア数に応じて）
2. 画像処理サイズを小さくする（config.pyのPROCESSING_IMAGE_SIZE）
3. GPUインスタンスを使用（利用可能な場合）

## メンテナンスとモニタリング

### ログの確認

Leapcellダッシュボードでアプリケーションログを確認：

1. 「Logs」タブに移動
2. リアルタイムログを監視
3. エラーや警告を確認

### パフォーマンスモニタリング

Google Analyticsを使用してトラフィックとユーザー行動を追跡：

1. Google Analytics IDを環境変数に設定
2. ダッシュボードでアクセス統計を確認
3. ユーザーエンゲージメントを分析

### 定期的な更新

```bash
# 新しい変更をプッシュ
git add .
git commit -m "Update: your changes"
git push origin main

# Leapcellが自動的に再デプロイします
```

### セキュリティ更新

定期的に以下を実行してください：

1. 依存関係の更新
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   pip freeze > requirements.txt
   ```

2. SECRET_KEYの定期的な変更
3. セキュリティヘッダーの確認

### バックアップ

重要なデータのバックアップ：

1. データベース（SQLite）のバックアップ
2. アップロードされた画像の定期的なクリーンアップ
3. 設定ファイルのバックアップ

## スケーリング

トラフィックが増加した場合の対応：

### 水平スケーリング

1. ワーカー数を増やす
   ```bash
   gunicorn -w 4 -b :8080 --timeout 120 run:app
   ```

2. 複数インスタンスの展開
   - Leapcellで複数のインスタンスを起動
   - ロードバランサーを設定

### 垂直スケーリング

1. より大きなインスタンスサイズを選択
2. メモリとCPUを増やす

### データベーススケーリング

SQLiteから本番データベースへの移行：

1. PostgreSQLまたはMySQLへの移行
2. 環境変数でデータベースURLを設定
3. データベース接続コードの更新

## サポートとヘルプ

問題が発生した場合：

1. **Leapcellドキュメント**: https://docs.leapcell.io/ja/
2. **GitHub Issues**: プロジェクトのIssuesページ
3. **コミュニティ**: Leapcellコミュニティフォーラム

---

製作: RiceZero
最終更新: 2026-02-08
