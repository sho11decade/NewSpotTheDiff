# ビルドエラー修正ガイド

## 問題の概要

Leapcellへのデプロイ時にビルドが失敗しました。これは主にOpenCVライブラリのインストールに必要なシステム依存関係が不足していることが原因です。

## 実施した修正

### 1. requirements.txtの変更

**変更前:**
```txt
opencv-python>=4.8
opencv-contrib-python>=4.8
```

**変更後:**
```txt
opencv-python-headless>=4.8
opencv-contrib-python-headless>=4.8
```

**理由:**
- `opencv-python-headless`はGUIライブラリ（GTK+、Qt等）への依存が少ない
- サーバー環境に最適化されている
- ビルド時の必要なシステムライブラリが少ない

### 2. ビルドスクリプトの作成

`build.sh`ファイルを作成し、以下を含めました：
- システム依存関係の自動インストール
- Pythonパッケージのインストール
- エラーハンドリング

### 3. apt.txtの作成

一部のプラットフォームがサポートしている`apt.txt`ファイルを作成し、必要なシステムパッケージをリストアップしました。

### 4. ドキュメントの更新

- `DEPLOYMENT.md` - トラブルシューティングセクションを強化
- `README.md` - 依存関係情報を更新
- `README_JP.md` - 日本語版も更新

## 推奨されるデプロイ方法

### 方法1: 拡張ビルドコマンド（最も確実）

Leapcellの設定で、Build Commandを以下に変更してください：

```bash
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 && pip install -r requirements.txt
```

**メリット:**
- 最も確実にビルドが成功する
- 必要なシステム依存関係を明示的にインストール
- デバッグが容易

### 方法2: ビルドスクリプトの使用

Build Commandを以下に変更：

```bash
chmod +x build.sh && ./build.sh
```

**メリット:**
- コマンドが短くて簡潔
- 依存関係の管理が容易
- 再利用可能

### 方法3: 標準ビルドコマンド（最もシンプル）

```bash
pip install -r requirements.txt
```

**注意:** `opencv-python-headless`に変更したので、この方法でも成功する可能性が高まりました。ただし、環境によっては方法1または2が必要な場合があります。

## 再デプロイ手順

1. **変更をコミットしてプッシュ**
   ```bash
   git add .
   git commit -m "Fix: Switch to opencv-python-headless and add build scripts"
   git push origin main
   ```

2. **Leapcellダッシュボードで設定を確認**
   - Build Command: 上記の方法1を推奨
   - Start Command: `gunicorn -w 2 -b :8080 --timeout 120 run:app`
   - Port: `8080`

3. **環境変数の確認**
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: ランダムな文字列
   - `SITE_DOMAIN`: `spotthediff.ricezero.fun`

4. **「Redeploy」ボタンをクリック**

5. **ビルドログを監視**
   - OpenCVのインストールが成功することを確認
   - エラーがないことを確認

## トラブルシューティング

### それでもビルドが失敗する場合

**エラーメッセージを確認:**
- ログの最後の行を確認
- 特定のパッケージで失敗している場合、そのパッケージ名をメモ

**可能な追加対策:**

1. **Pythonバージョンの確認**
   - Python 3.10以上を使用していることを確認

2. **メモリ不足の場合**
   - ワーカー数を減らす: `-w 1`
   - プランをアップグレード

3. **依存関係の競合**
   - 特定のバージョンを指定（例: `flask==3.0.0`）

4. **キャッシュの問題**
   - `pip install --no-cache-dir -r requirements.txt`を使用

## 成功の確認

ビルドが成功したら、以下を確認してください：

1. **アプリケーションが起動する**
   - 提供されたURLにアクセス
   - ホームページが表示される

2. **画像アップロードが動作する**
   - テスト画像をアップロード
   - エラーが表示されない

3. **間違い探し生成が動作する**
   - 生成ボタンをクリック
   - 処理画面が表示される
   - 結果が正常に表示される

## 追加のヘルプ

問題が解決しない場合：

1. **完全なビルドログを確認**
   - Leapcellダッシュボードでログ全体を確認
   - エラーメッセージをコピー

2. **Leapcellドキュメントを参照**
   - https://docs.leapcell.io/ja/examples/python/flask/

3. **GitHub Issuesで報告**
   - エラーメッセージを含めて報告
   - 使用した設定を記載

---

製作: RiceZero
最終更新: 2026-02-08
