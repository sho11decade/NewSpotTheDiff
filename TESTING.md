# テストガイド

このドキュメントでは、デプロイ前のテストと検証手順を説明します。

## 目次
- [ローカル環境でのテスト](#ローカル環境でのテスト)
- [SEOとメタタグの検証](#seoとメタタグの検証)
- [セキュリティヘッダーの確認](#セキュリティヘッダーの確認)
- [パフォーマンステスト](#パフォーマンステスト)
- [デプロイ前チェックリスト](#デプロイ前チェックリスト)

## ローカル環境でのテスト

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. FastSAMモデルのダウンロード

```bash
python scripts/download_model.py
```

### 3. データベースの初期化

```bash
python scripts/init_db.py
```

### 4. 開発サーバーの起動

```bash
python run.py
```

アプリケーションは`http://localhost:5000`でアクセスできます。

### 5. 基本機能のテスト

#### 画像アップロード
1. トップページにアクセス
2. テスト画像をドラッグ＆ドロップ
3. プレビューが表示されることを確認
4. ファイル検証が動作することを確認（サイズ、形式）

#### 間違い探し生成
1. 難易度を選択（簡単、普通、難しい）
2. 「間違い探しを生成」をクリック
3. 処理画面で進捗が表示されることを確認
4. 結果ページで以下を確認：
   - オリジナル画像と変更後の画像が表示される
   - 「違いを表示」ボタンが動作する
   - A4レイアウトのダウンロードができる

#### エラーハンドリング
1. サイズが大きすぎる画像をアップロード（>10MB）
2. サポートされていないフォーマット（例: BMP）
3. 不正なジョブIDでアクセス

## SEOとメタタグの検証

### 1. メタタグの確認

各ページのHTMLソースを表示して、以下のメタタグが含まれているか確認：

```bash
curl http://localhost:5000 | grep meta
```

確認項目：
- [ ] `<title>` タグ
- [ ] `<meta name="description">`
- [ ] `<meta name="keywords">`
- [ ] Open Graph タグ（`og:title`, `og:description`, `og:image`）
- [ ] Twitter Card タグ
- [ ] Canonical URL

### 2. sitemap.xmlの確認

```bash
curl http://localhost:5000/sitemap.xml
```

以下を確認：
- [ ] XMLが正しくフォーマットされている
- [ ] すべての主要ページが含まれている（/, /about, /privacy, /terms）
- [ ] URLが正しい（ドメイン含む）

### 3. robots.txtの確認

```bash
curl http://localhost:5000/robots.txt
```

以下を確認：
- [ ] APIエンドポイントが禁止されている（Disallow: /api/）
- [ ] 出力ディレクトリが禁止されている（Disallow: /outputs/）
- [ ] sitemap.xmlへのリンクが含まれている

### 4. OG画像の確認

```bash
# OG画像が存在するか確認
curl -I http://localhost:5000/static/og-image.svg
```

### 5. SEOツールでの検証

以下のオンラインツールを使用（デプロイ後）：

- **Google Rich Results Test**: https://search.google.com/test/rich-results
- **Facebook Sharing Debugger**: https://developers.facebook.com/tools/debug/
- **Twitter Card Validator**: https://cards-dev.twitter.com/validator

## セキュリティヘッダーの確認

### 1. ヘッダーの検証（開発環境）

```bash
curl -I http://localhost:5000
```

確認項目（開発環境では一部無効）：
- [ ] `Content-Security-Policy`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: SAMEORIGIN`

### 2. 本番環境での検証

デプロイ後、以下のツールで検証：

```bash
# Security Headersの確認
curl -I https://spotthediff.ricezero.fun
```

オンラインツール：
- **Security Headers**: https://securityheaders.com/
- **Mozilla Observatory**: https://observatory.mozilla.org/

確認項目（本番環境）：
- [ ] `Strict-Transport-Security`（HSTS）
- [ ] `Content-Security-Policy`（CSP）
- [ ] HTTPからHTTPSへのリダイレクト

### 3. CSP違反の確認

ブラウザの開発者ツールのコンソールを開いて、CSP違反のエラーがないか確認：

```
Content Security Policy directive ...
```

## Google Analyticsの確認

### 1. 環境変数の設定

`.env`ファイルまたは環境変数に追加：

```bash
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

### 2. タグの確認

ページのHTMLソースを表示して、GAタグが含まれているか確認：

```bash
curl http://localhost:5000 | grep googletagmanager
```

### 3. 動作確認（デプロイ後）

1. Google Analytics ダッシュボードにアクセス
2. リアルタイムレポートを開く
3. サイトにアクセスしてアクティブユーザーが表示されるか確認

## パフォーマンステスト

### 1. ページ読み込み速度

```bash
# curlを使用して応答時間を測定
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000
```

`curl-format.txt`の内容：
```
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
```

### 2. 画像処理時間

処理時間の目安：
- 簡単: 8-12秒
- 普通: 10-14秒
- 難しい: 12-16秒

複数の画像でテストして平均処理時間を確認。

### 3. 同時リクエストのテスト

```bash
# Apache Benchを使用（オプション）
ab -n 100 -c 10 http://localhost:5000/
```

## レート制限のテスト

### 1. アップロード制限

短時間に複数回アップロードして、レート制限が動作するか確認：

```bash
# 11回連続でアップロード（制限: 10/分）
for i in {1..11}; do
  curl -X POST -F "file=@test.jpg" http://localhost:5000/api/upload
  echo ""
done
```

11回目で`429 Too Many Requests`が返されることを確認。

### 2. 生成制限

同様に、生成エンドポイントでもテスト（制限: 5/分）。

## デプロイ前チェックリスト

### コード品質

- [ ] すべてのテストがパスする（`pytest`）
- [ ] Lintエラーがない（`ruff check .`）
- [ ] 未使用のimportがない
- [ ] コメントアウトされたコードを削除

### 設定

- [ ] `requirements.txt`が最新
- [ ] `.env.example`が更新されている
- [ ] `.gitignore`に機密情報が含まれていない
- [ ] `SECRET_KEY`が本番用に変更されている

### ドキュメント

- [ ] README.mdが最新
- [ ] README_JP.mdが最新
- [ ] DEPLOYMENT.mdが正確
- [ ] APIドキュメントが更新されている

### セキュリティ

- [ ] 機密情報がコミットされていない
- [ ] 環境変数が適切に設定されている
- [ ] セキュリティヘッダーが有効
- [ ] レート制限が設定されている
- [ ] CSRFトークンが有効（該当する場合）

### 機能

- [ ] すべてのページが正常に表示される
- [ ] 画像アップロードが動作する
- [ ] 間違い探し生成が動作する
- [ ] エラーハンドリングが適切
- [ ] ファイル検証が動作する

### SEO

- [ ] すべてのページにメタタグが設定されている
- [ ] OG画像が存在する
- [ ] sitemap.xmlが生成される
- [ ] robots.txtが設定されている
- [ ] Canonical URLが設定されている

### パフォーマンス

- [ ] 画像が適切に最適化されている
- [ ] 静的ファイルがキャッシュされている
- [ ] 不要なログ出力がない
- [ ] データベースクエリが最適化されている

### デプロイメント

- [ ] Start Commandが正しい
- [ ] ポート設定が正しい（8080）
- [ ] 環境変数がLeapcellに設定されている
- [ ] FastSAMモデルの配置方法が決定されている
- [ ] ドメイン設定が準備されている

## トラブルシューティング

### よくある問題

1. **画像が表示されない**
   - staticフォルダのパスを確認
   - ブラウザのキャッシュをクリア

2. **CSP違反エラー**
   - config.pyのCSP設定を確認
   - 外部リソースのURLが許可されているか確認

3. **Google Analyticsが動作しない**
   - 環境変数が正しく設定されているか確認
   - ブラウザのアドブロッカーを無効化

4. **レート制限が動作しない**
   - RATELIMIT_ENABLEDがTrueか確認
   - Redisが正しく設定されているか確認（本番環境）

## テスト後のアクション

すべてのテストが完了したら：

1. 変更をコミット
   ```bash
   git add .
   git commit -m "Add production deployment features"
   git push origin main
   ```

2. Leapcellにデプロイ
3. 本番環境で再度テスト
4. Google Search Consoleにサイトマップを送信
5. Google Analyticsでトラッキングを確認

---

製作: RiceZero
最終更新: 2026-02-08
