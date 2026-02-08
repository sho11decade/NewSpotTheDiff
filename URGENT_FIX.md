# 🚨 緊急: FLASK_ENV=production を設定してください

## 問題

現在のエラーは **`FLASK_ENV=production` 環境変数が設定されていない** ことが原因です。

ログを見ると、アプリケーションは依然として `/app/instance` ディレクトリを使用しようとしています:

```
2026-02-08 05:14:33 [WARNING] src.utils.file_manager: Failed to create directory /app/instance/uploads
```

これは、**開発設定（DevelopmentConfig）が使用されている**ことを示しています。

## 解決方法

### ステップ1: Leapcellで環境変数を設定

Leapcellのプロジェクト設定で、以下の環境変数を**今すぐ**追加してください：

```
FLASK_ENV=production
```

### 設定手順

1. **Leapcellダッシュボードにアクセス**
   - プロジェクト「spot-the-diff」を開く

2. **環境変数セクションに移動**
   - 「Settings」または「Environment Variables」タブ

3. **環境変数を追加**
   ```
   Name:  FLASK_ENV
   Value: production
   ```

4. **その他の必須環境変数も追加**
   ```
   Name:  SECRET_KEY
   Value: [ランダムな文字列、例: your-secret-key-here-change-this]

   Name:  SITE_DOMAIN
   Value: spotthediff.ricezero.fun
   ```

5. **保存して再デプロイ**
   - 「Save」をクリック
   - 「Redeploy」をクリック

## なぜこれが重要か

| 設定 | 使用されるパス | 結果 |
|------|--------------|------|
| `FLASK_ENV=development` (デフォルト) | `/app/instance/uploads` | ❌ 読み取り専用エラー |
| `FLASK_ENV=production` | `/tmp/spotdiff/uploads` | ✅ 動作する |

`FLASK_ENV=production` を設定すると、アプリケーションは自動的に：
- ✅ `/tmp` ディレクトリを使用（書き込み可能）
- ✅ HTTPSを強制
- ✅ セキュリティヘッダーを有効化
- ✅ デバッグモードを無効化

## 完全な環境変数リスト

Leapcellで設定すべき環境変数：

```bash
# 必須
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
SITE_DOMAIN=spotthediff.ricezero.fun

# オプション
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
FORCE_HTTPS=true
```

## 期待される結果

`FLASK_ENV=production` を設定して再デプロイすると：

**成功時のログ:**
```
[INFO] Starting gunicorn
[INFO] Booting worker with pid: 26
[INFO] Database directory ensured: /tmp/spotdiff    ← これが表示される
[INFO] Database initialized: /tmp/spotdiff/spotdiff.db
[INFO] Security headers initialized
```

**エラーがなくなる:**
- ❌ `Failed to create directory /app/instance/uploads`
- ❌ `OSError: [Errno 30] Read-only file system: '/app/instance'`

## トラブルシューティング

### 環境変数が反映されない場合

1. **環境変数のスペルを確認**
   - `FLASK_ENV` (大文字)
   - `production` (小文字)

2. **再デプロイが必要**
   - 環境変数を追加/変更した後、必ず再デプロイ

3. **ログで確認**
   - 起動ログで `/tmp/spotdiff` が使用されているか確認

### それでもエラーが出る場合

以下の情報を提供してください：
1. Leapcellの環境変数スクリーンショット
2. 完全なビルド＆起動ログ
3. 使用しているLeapcellプラン

## 次のステップ

1. **今すぐ:** Leapcellで `FLASK_ENV=production` を設定
2. **保存:** 環境変数を保存
3. **再デプロイ:** 「Redeploy」をクリック
4. **確認:** ログで `/tmp/spotdiff` が使用されているか確認
5. **報告:** 成功したかどうか教えてください

---

**重要:** この環境変数なしでは、アプリケーションは起動できません！
