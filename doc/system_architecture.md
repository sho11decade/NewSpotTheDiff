# 次世代型間違い探し自動生成システム - システム設計書

## 1. システムアーキテクチャ概要

### 1.1 アーキテクチャパターン
本システムは**レイヤードアーキテクチャ**を採用し、以下の層で構成されます。

```
┌─────────────────────────────────────────────┐
│         Presentation Layer (Web UI)         │
│              (Flask + HTML/CSS/JS)          │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│          Application Layer (Flask)          │
│        (ルーティング、リクエスト処理)           │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│          Business Logic Layer               │
│    (間違い探し生成ロジック、AIオーケストレーション) │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│           AI Processing Layer               │
│  ┌──────────┬──────────┬──────────────┐    │
│  │ SAM 2    │  LaMa    │ Saliency API │    │
│  │ Module   │  Module  │   Module     │    │
│  └──────────┴──────────┴──────────────┘    │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│         Data Access Layer                    │
│      (ファイルシステム、SQLite)                │
└─────────────────────────────────────────────┘
```

### 1.2 技術スタック

| レイヤー | 技術 | 目的 |
|----------|------|------|
| フロントエンド | HTML5, CSS3, JavaScript | ユーザーインターフェース |
| バックエンド | Flask 3.x | Webフレームワーク |
| AI処理 | PyTorch 2.5+, TensorFlow | AI推論エンジン |
| 画像処理 | OpenCV, Pillow | 画像の前処理・後処理 |
| データベース | SQLite 3 | メタデータ管理 |
| 環境管理 | UV | Pythonパッケージ管理 |
| GPU処理 | CUDA 12.1+ | GPU計算の高速化 |

---

## 2. システム構成図

### 2.1 デプロイメント構成

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                        │
│              (Chrome, Firefox, Safari, Edge)             │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  Web Server (Flask)                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │            Static Files Handler                    │  │
│  │       (HTML, CSS, JS, Generated Images)            │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Application Server                       │  │
│  │   - ルーティング                                     │  │
│  │   - セッション管理                                   │  │
│  │   - ファイルアップロード処理                          │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│                AI Processing Service                     │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐   │
│  │   SAM 2     │  │    LaMa     │  │ Saliency Map  │   │
│  │   Service   │  │   Service   │  │    Service    │   │
│  └─────────────┘  └─────────────┘  └───────────────┘   │
│                   GPU Utilization                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  Data Storage Layer                      │
│  ┌───────────────────┐  ┌─────────────────────────┐    │
│  │  File System      │  │      SQLite DB          │    │
│  │  (Uploads/Output) │  │   (Metadata/History)    │    │
│  └───────────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 コンポーネント構成

```
spot_the_diff/
├── app/
│   ├── __init__.py              # Flaskアプリ初期化
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py              # メインページルート
│   │   ├── upload.py            # アップロード処理
│   │   └── generate.py          # 生成処理エンドポイント
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_processor.py   # 画像前処理サービス
│   │   ├── sam2_service.py      # SAM 2セグメンテーション
│   │   ├── lama_service.py      # LaMa画像補完
│   │   ├── saliency_service.py  # 顕著性解析
│   │   └── difference_generator.py # 間違い生成ロジック
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_handler.py      # ファイル操作ユーティリティ
│   │   ├── validation.py        # バリデーション関数
│   │   └── image_utils.py       # 画像ユーティリティ
│   ├── models/
│   │   ├── __init__.py
│   │   └── generation_history.py # データモデル定義
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   └── upload.js
│   │   └── images/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── upload.html
│       ├── processing.html
│       └── result.html
├── models/                      # AIモデルチェックポイント
│   ├── sam2/
│   ├── lama/
│   └── deepgaze/
├── uploads/                     # アップロードされた画像
├── outputs/                     # 生成結果
├── tests/
│   ├── test_services.py
│   ├── test_routes.py
│   └── test_integration.py
├── config/
│   ├── config.py                # 設定ファイル
│   └── logging_config.py        # ロギング設定
├── scripts/
│   ├── download_models.py       # モデルダウンロードスクリプト
│   └── setup_env.py             # 環境セットアップ
├── pyproject.toml               # UVプロジェクト設定
├── requirements.txt
└── run.py                       # アプリケーションエントリーポイント
```

---

## 3. データフロー設計

### 3.1 メイン処理フロー

```
[1] ユーザーが画像をアップロード
     ↓
[2] バリデーション（形式、サイズ、解像度）
     ↓
[3] 画像の前処理・正規化
     ↓
[4] SAM 2による物体セグメンテーション
     - 物体検出
     - マスク生成
     - セグメント情報抽出
     ↓
[5] 顕著性マップ生成 (OpenCV Saliency API)
     - 画像全体の顕著性解析
     - 各セグメントの顕著性スコア算出
     ↓
[6] 間違い生成戦略の決定
     - 難易度に基づく物体選択
     - 変更タイプの決定（削除/色変更/追加）
     - 優先順位付け
     ↓
[7] 各変更の適用
     ├─ 削除 → LaMaでInpainting
     ├─ 色変更 → OpenCVで色空間変換
     └─ 追加 → セグメントの複製と配置
     ↓
[8] 結果画像の生成と後処理
     ↓
[9] メタデータの作成（JSON）
     - 変更箇所の座標
     - 変更タイプ
     - 処理時間
     ↓
[10] データベースへの保存
     ↓
[11] ユーザーへの結果表示
```

### 3.2 データモデル

#### 3.2.1 GenerationHistory（SQLite）

```sql
CREATE TABLE generation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    original_path TEXT NOT NULL,
    output_path TEXT NOT NULL,
    difficulty TEXT NOT NULL,  -- 'easy', 'medium', 'hard'
    num_differences INTEGER NOT NULL,
    processing_time REAL NOT NULL,
    metadata TEXT NOT NULL,    -- JSON形式のメタデータ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_session_id ON generation_history(session_id);
CREATE INDEX idx_expires_at ON generation_history(expires_at);
```

#### 3.2.2 差異情報メタデータ（JSON）

```json
{
  "differences": [
    {
      "id": 1,
      "type": "deletion",  // "deletion", "color_change", "addition"
      "bbox": [100, 150, 250, 300],  // [x1, y1, x2, y2]
      "polygon": [[120, 160], [130, 170], ...],  // セグメント輪郭
      "saliency_score": 0.35,
      "description": "Tree removed from background"
    },
    {
      "id": 2,
      "type": "color_change",
      "bbox": [400, 200, 500, 350],
      "original_color": [120, 80, 60],
      "new_color": [180, 100, 70],
      "saliency_score": 0.62,
      "description": "Car color changed from brown to red"
    }
  ],
  "difficulty": "medium",
  "total_differences": 5,
  "processing_steps": {
    "segmentation_time": 28.5,
    "saliency_time": 12.3,
    "inpainting_time": 45.7,
    "total_time": 92.1
  },
  "model_versions": {
    "sam2": "SAM 2 Tiny",
    "lama": "big-lama",
    "saliency": "opencv-spectral-residual"
  }
}
```

---

## 4. AIモジュール設計

### 4.1 SAM 2セグメンテーションモジュール

**責務**: 画像内の物体を検出し、ピクセル単位のセグメンテーションマスクを生成

```python
class SAM2Service:
    def __init__(self, model_type='tiny', device='cuda'):
        """
        Args:
            model_type: 'tiny', 'small', 'base_plus', 'large'
            device: 'cuda' or 'cpu'
        """
        self.model = self._load_model(model_type)
        self.device = device
        self.predictor = SAM2ImagePredictor(self.model)

    def segment_image(self, image: np.ndarray) -> List[Segment]:
        """
        画像をセグメント化

        Returns:
            List[Segment]: 検出された全セグメント
                - mask: バイナリマスク (H, W)
                - bbox: バウンディングボックス [x1, y1, x2, y2]
                - score: 信頼度スコア
                - area: セグメント面積
        """
        pass

    def filter_segments(self, segments: List[Segment],
                       min_area: int = 1000) -> List[Segment]:
        """小さすぎるセグメントをフィルタリング"""
        pass
```

**処理フロー**:
1. 画像をモデルに入力
2. 自動マスク生成（`predictor.set_image`）
3. セグメント情報の抽出（マスク、バウンディングボックス、面積）
4. 小さすぎる/大きすぎるセグメントのフィルタリング
5. セグメントリストの返却

### 4.2 顕著性解析モジュール

**責務**: 画像の顕著性マップを生成し、各セグメントの注目度を評価

```python
class SaliencyService:
    def __init__(self, method='spectral_residual'):
        """
        Args:
            method: 'spectral_residual', 'fine_grained', 'bing'
        """
        self.saliency = cv2.saliency.StaticSaliencySpectralResidual_create()

    def compute_saliency_map(self, image: np.ndarray) -> np.ndarray:
        """
        顕著性マップを生成

        Returns:
            np.ndarray: 顕著性マップ (H, W) [0.0 - 1.0]
        """
        pass

    def compute_segment_saliency(self, saliency_map: np.ndarray,
                                 segment: Segment) -> float:
        """
        セグメントの平均顕著性スコアを計算

        Returns:
            float: 顕著性スコア [0.0 - 1.0]
        """
        mask_area = segment.mask
        return np.mean(saliency_map[mask_area])

    def rank_segments(self, segments: List[Segment],
                     saliency_map: np.ndarray) -> List[Segment]:
        """セグメントを顕著性スコアでランク付け"""
        pass
```

**処理フロー**:
1. OpenCV Saliency APIで顕著性マップ生成
2. 各セグメントのマスク領域内の平均顕著性を計算
3. セグメントを顕著性スコアでソート
4. ランク付けされたセグメントリストを返却

### 4.3 LaMa画像補完モジュール

**責務**: 選択された物体を削除し、周囲から自然に補完

```python
class LaMaService:
    def __init__(self, model_path: str, device='cuda'):
        self.model = self._load_model(model_path)
        self.device = device

    def inpaint(self, image: np.ndarray, mask: np.ndarray,
                refine: bool = True) -> np.ndarray:
        """
        画像補完を実行

        Args:
            image: 入力画像 (H, W, 3)
            mask: バイナリマスク (H, W), 1=削除領域
            refine: リファインメント処理の有効化

        Returns:
            np.ndarray: 補完された画像 (H, W, 3)
        """
        pass

    def batch_inpaint(self, image: np.ndarray,
                     masks: List[np.ndarray]) -> np.ndarray:
        """複数マスクを順次適用して補完"""
        result = image.copy()
        for mask in masks:
            result = self.inpaint(result, mask)
        return result
```

**処理フロー**:
1. 削除対象のセグメントマスクを準備
2. マスク領域を白（1）、その他を黒（0）に設定
3. LaMaモデルで補完画像を生成
4. オプションでリファインメント処理
5. 補完された画像を返却

### 4.4 間違い生成オーケストレーター

**責務**: 全体の間違い生成ロジックを統括

```python
class DifferenceGenerator:
    def __init__(self, sam2_service: SAM2Service,
                 saliency_service: SaliencyService,
                 lama_service: LaMaService):
        self.sam2 = sam2_service
        self.saliency = saliency_service
        self.lama = lama_service

    def generate(self, image: np.ndarray,
                difficulty: str = 'medium') -> GenerationResult:
        """
        間違い探し画像を生成

        Args:
            image: 入力画像
            difficulty: 'easy', 'medium', 'hard'

        Returns:
            GenerationResult:
                - modified_image: 変更後の画像
                - differences: 差異情報リスト
                - metadata: メタデータ
        """
        # 1. セグメンテーション
        segments = self.sam2.segment_image(image)

        # 2. 顕著性解析
        saliency_map = self.saliency.compute_saliency_map(image)
        ranked_segments = self.saliency.rank_segments(segments, saliency_map)

        # 3. 難易度に基づく選択
        selected = self._select_segments(ranked_segments, difficulty)

        # 4. 変更タイプの決定と適用
        modified_image, differences = self._apply_changes(
            image, selected
        )

        # 5. メタデータ生成
        metadata = self._create_metadata(differences)

        return GenerationResult(modified_image, differences, metadata)

    def _select_segments(self, segments: List[Segment],
                        difficulty: str) -> List[Segment]:
        """難易度に基づいてセグメントを選択"""
        num_changes = {'easy': 3, 'medium': 5, 'hard': 8}[difficulty]
        saliency_threshold = {'easy': 0.6, 'medium': 0.4, 'hard': 0.2}[difficulty]

        filtered = [s for s in segments
                   if s.saliency_score <= saliency_threshold]
        return random.sample(filtered, min(num_changes, len(filtered)))

    def _apply_changes(self, image: np.ndarray,
                      segments: List[Segment]) -> Tuple[np.ndarray, List[Difference]]:
        """変更を適用"""
        modified = image.copy()
        differences = []

        for segment in segments:
            change_type = random.choice(['deletion', 'color_change', 'addition'])

            if change_type == 'deletion':
                modified = self.lama.inpaint(modified, segment.mask)
            elif change_type == 'color_change':
                modified = self._change_color(modified, segment)
            elif change_type == 'addition':
                modified = self._duplicate_object(modified, segment)

            differences.append(Difference(
                type=change_type,
                segment=segment,
                ...
            ))

        return modified, differences

    def _change_color(self, image: np.ndarray, segment: Segment) -> np.ndarray:
        """物体の色を変更"""
        # HSV色空間での色相シフト
        pass

    def _duplicate_object(self, image: np.ndarray, segment: Segment) -> np.ndarray:
        """物体を複製して配置"""
        pass
```

---

## 5. API設計

### 5.1 エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/` | トップページ |
| GET | `/upload` | アップロードページ |
| POST | `/api/upload` | 画像アップロード |
| POST | `/api/generate` | 間違い探し生成 |
| GET | `/api/status/<job_id>` | 処理ステータス確認 |
| GET | `/api/result/<job_id>` | 結果取得 |
| GET | `/result/<job_id>` | 結果表示ページ |
| POST | `/api/download/<job_id>` | 画像ダウンロード |

### 5.2 APIスキーマ

#### POST /api/upload

**リクエスト**:
```http
POST /api/upload HTTP/1.1
Content-Type: multipart/form-data

file: <image_file>
```

**レスポンス**:
```json
{
  "success": true,
  "file_id": "abc123def456",
  "filename": "example.jpg",
  "size": 2048576,
  "dimensions": [1920, 1080]
}
```

#### POST /api/generate

**リクエスト**:
```json
{
  "file_id": "abc123def456",
  "difficulty": "medium",
  "num_differences": 5
}
```

**レスポンス**:
```json
{
  "success": true,
  "job_id": "job_xyz789",
  "status": "processing",
  "estimated_time": 90
}
```

#### GET /api/status/<job_id>

**レスポンス**:
```json
{
  "job_id": "job_xyz789",
  "status": "completed",  // "queued", "processing", "completed", "failed"
  "progress": 100,
  "current_step": "Finished",
  "processing_time": 87.3
}
```

#### GET /api/result/<job_id>

**レスポンス**:
```json
{
  "success": true,
  "job_id": "job_xyz789",
  "original_image_url": "/outputs/job_xyz789/original.png",
  "modified_image_url": "/outputs/job_xyz789/modified.png",
  "differences": [...],
  "metadata": {...}
}
```

---

## 6. セキュリティ設計

### 6.1 脅威分析

| 脅威 | 影響 | 対策 |
|------|------|------|
| 悪意のあるファイルアップロード | 高 | ファイル形式検証、サイズ制限、スキャン |
| パストラバーサル攻撃 | 高 | ファイル名のサニタイズ、UUID使用 |
| DoS攻撃 | 中 | レート制限、タイムアウト設定 |
| XSS攻撃 | 中 | 入力エスケープ、CSP設定 |
| CSRF攻撃 | 中 | CSRFトークン |
| セッションハイジャック | 中 | Secure Cookie、HTTPOnly |

### 6.2 実装詳細

#### ファイルアップロードの検証

```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(file):
    # 拡張子チェック
    if not allowed_file(file.filename):
        raise ValidationError("Invalid file type")

    # ファイルサイズチェック
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValidationError("File too large")

    # 実際の画像形式チェック
    try:
        img = Image.open(file)
        img.verify()
    except:
        raise ValidationError("Invalid image file")

    # 安全なファイル名生成
    filename = f"{uuid.uuid4()}.{file.filename.rsplit('.', 1)[1].lower()}"
    return filename
```

#### CSRFトークン

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# 全POSTリクエストで自動検証
```

#### レート制限

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/generate', methods=['POST'])
@limiter.limit("5 per minute")
def generate():
    pass
```

---

## 7. 性能設計

### 7.1 性能目標

| 項目 | 目標値 | 測定方法 |
|------|--------|---------|
| 画像アップロード時間 | < 5秒 | クライアント測定 |
| 物体セグメンテーション | < 30秒 | サーバーログ |
| 顕著性解析 | < 15秒 | サーバーログ |
| 画像補完（1物体） | < 15秒 | サーバーログ |
| 総処理時間 | < 120秒 | エンドツーエンド |
| 同時処理数 | 最大3ジョブ | GPU利用率監視 |

### 7.2 最適化戦略

#### GPU利用の最適化

```python
# バッチ処理でGPU利用率向上
def batch_process_segments(segments, batch_size=4):
    results = []
    for i in range(0, len(segments), batch_size):
        batch = segments[i:i+batch_size]
        results.extend(model(batch))
    return results

# torch.compile最適化
model = torch.compile(model, mode='max-autotune')

# Mixed Precision Training (AMP)
from torch.cuda.amp import autocast
with autocast():
    output = model(input)
```

#### キャッシング戦略

```python
from functools import lru_cache

# 顕著性マップのキャッシング
@lru_cache(maxsize=100)
def get_saliency_map(image_hash):
    return compute_saliency_map(image)
```

#### 非同期処理

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=3)

@app.route('/api/generate', methods=['POST'])
def generate():
    job_id = str(uuid.uuid4())
    executor.submit(process_generation, job_id, data)
    return jsonify({'job_id': job_id, 'status': 'queued'})
```

---

## 8. エラーハンドリング戦略

### 8.1 エラー分類

| カテゴリ | エラーコード | 説明 |
|----------|-------------|------|
| バリデーション | 400 | 不正なリクエスト |
| 認証 | 401 | 未認証 |
| リソース不足 | 503 | GPU/メモリ不足 |
| 処理失敗 | 500 | AI処理エラー |
| タイムアウト | 504 | 処理時間超過 |

### 8.2 実装例

```python
class ProcessingError(Exception):
    """AI処理エラー"""
    pass

class ResourceExhaustedError(Exception):
    """リソース不足エラー"""
    pass

@app.errorhandler(ProcessingError)
def handle_processing_error(e):
    logger.error(f"Processing failed: {str(e)}")
    return jsonify({
        'error': 'processing_failed',
        'message': 'Failed to generate spot-the-difference image',
        'details': str(e)
    }), 500

@app.errorhandler(ResourceExhaustedError)
def handle_resource_error(e):
    return jsonify({
        'error': 'resource_exhausted',
        'message': 'Server is currently busy. Please try again later.',
        'retry_after': 60
    }), 503
```

---

## 9. ログおよび監視設計

### 9.1 ログレベル

| レベル | 用途 |
|--------|------|
| DEBUG | 詳細なデバッグ情報 |
| INFO | 通常の動作ログ |
| WARNING | 警告（処理は継続） |
| ERROR | エラー（処理失敗） |
| CRITICAL | 致命的エラー |

### 9.2 ログ出力内容

```python
import logging
import json

logger = logging.getLogger(__name__)

# 構造化ログ
def log_processing_step(job_id, step, duration, status):
    logger.info(json.dumps({
        'job_id': job_id,
        'step': step,
        'duration_sec': duration,
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }))

# 使用例
log_processing_step(
    job_id='job_123',
    step='segmentation',
    duration=28.5,
    status='completed'
)
```

### 9.3 監視メトリクス

```python
# GPUメモリ使用率
def get_gpu_memory_usage():
    import torch
    allocated = torch.cuda.memory_allocated() / 1024**3
    reserved = torch.cuda.memory_reserved() / 1024**3
    return {'allocated_gb': allocated, 'reserved_gb': reserved}

# 処理時間メトリクス
from functools import wraps
import time

def monitor_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper
```

---

## 10. テスト戦略

### 10.1 テストピラミッド

```
       ┌─────────────┐
       │ E2E Tests   │  10%
       └─────────────┘
    ┌──────────────────┐
    │ Integration Tests│  30%
    └──────────────────┘
 ┌────────────────────────┐
 │    Unit Tests          │  60%
 └────────────────────────┘
```

### 10.2 単体テスト

```python
# tests/test_services.py
import pytest
import numpy as np

def test_sam2_segmentation():
    service = SAM2Service(model_type='tiny')
    image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    segments = service.segment_image(image)

    assert len(segments) > 0
    assert all(s.mask.shape == (512, 512) for s in segments)

def test_saliency_computation():
    service = SaliencyService()
    image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    saliency_map = service.compute_saliency_map(image)

    assert saliency_map.shape == (512, 512)
    assert 0 <= saliency_map.min() <= saliency_map.max() <= 1
```

### 10.3 統合テスト

```python
# tests/test_integration.py
def test_full_generation_pipeline():
    # テスト画像の準備
    test_image = Image.open('tests/fixtures/test_image.jpg')
    image_array = np.array(test_image)

    # 統合処理
    generator = DifferenceGenerator(sam2, saliency, lama)
    result = generator.generate(image_array, difficulty='medium')

    assert result.modified_image is not None
    assert len(result.differences) >= 3
    assert result.metadata['difficulty'] == 'medium'
```

### 10.4 E2Eテスト

```python
# tests/test_e2e.py
def test_upload_and_generate(client):
    # 画像アップロード
    response = client.post('/api/upload', data={
        'file': (BytesIO(test_image_bytes), 'test.jpg')
    })
    assert response.status_code == 200
    file_id = response.json['file_id']

    # 生成リクエスト
    response = client.post('/api/generate', json={
        'file_id': file_id,
        'difficulty': 'medium'
    })
    assert response.status_code == 200
    job_id = response.json['job_id']

    # 結果確認
    time.sleep(90)  # 処理完了待機
    response = client.get(f'/api/result/{job_id}')
    assert response.status_code == 200
    assert 'modified_image_url' in response.json
```

---

## 11. デプロイメント戦略

### 11.1 開発環境セットアップ

```bash
# 1. UVのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. プロジェクトのクローン
git clone <repository_url>
cd NewSpotTheDiff

# 3. UV環境のセットアップ
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 4. 依存関係のインストール
uv pip install -e ".[dev]"

# 5. AIモデルのダウンロード
python scripts/download_models.py

# 6. データベース初期化
python scripts/init_db.py

# 7. 開発サーバー起動
python run.py
```

### 11.2 プロダクション環境

```bash
# Gunicornでの起動
gunicorn -w 4 -b 0.0.0.0:8000 \
  --timeout 300 \
  --worker-class sync \
  run:app

# Nginxリバースプロキシ設定
server {
    listen 80;
    server_name example.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/app/static;
        expires 30d;
    }
}
```

### 11.3 Docker化

```dockerfile
# Dockerfile
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3.10 python3-pip

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

RUN python3 scripts/download_models.py

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
    environment:
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 12. 今後の拡張性

### 12.1 マイクロサービス化

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│  API Gateway │────▶│   Upload     │
│   Service    │     │   Service    │     │   Service    │
└──────────────┘     └──────────────┘     └──────────────┘
                             │
                             ├────────────▶ ┌──────────────┐
                             │              │Segmentation  │
                             │              │  Service     │
                             │              └──────────────┘
                             │
                             ├────────────▶ ┌──────────────┐
                             │              │  Saliency    │
                             │              │  Service     │
                             │              └──────────────┘
                             │
                             └────────────▶ ┌──────────────┐
                                            │  Inpainting  │
                                            │  Service     │
                                            └──────────────┘
```

### 12.2 スケーラビリティ

- **水平スケーリング**: 複数のGPUサーバーでロードバランシング
- **メッセージキュー**: Redis/RabbitMQによる非同期ジョブ処理
- **分散ストレージ**: S3/GCSへの画像保存
- **CDN**: 生成画像の配信最適化

---

**文書バージョン**: 1.0
**最終更新日**: 2026-02-08
**作成者**: Claude Code
