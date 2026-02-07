# 次世代型間違い探し自動生成システム - 実装計画とロードマップ

## 1. プロジェクト概要

### 1.1 目標
AI技術（SAM 2、LaMa、顕著性解析）を活用した間違い探し自動生成Webアプリケーションの構築

### 1.2 開発期間
- **フェーズ1（基盤構築）**: 2週間
- **フェーズ2（AI統合）**: 3週間
- **フェーズ3（UI/UX）**: 2週間
- **フェーズ4（テスト/最適化）**: 2週間
- **合計**: 9週間

---

## 2. 開発フェーズ

### フェーズ1: 基盤構築と環境セットアップ

#### 目標
プロジェクト基盤の構築とAIモデルの動作確認

#### タスク

**1.1 開発環境のセットアップ**
- [ ] Pythonプロジェクト構造の作成
- [ ] `pyproject.toml` (UV) の設定
- [ ] Gitリポジトリの初期化
- [ ] `.gitignore` の設定
- [ ] CUDA環境の確認とセットアップ

**1.2 AIモデルのダウンロードと検証**
- [ ] SAM 2モデルのダウンロード（Tinyモデル推奨）
- [ ] LaMaモデルのダウンロード（big-lama）
- [ ] 各モデルの動作確認スクリプト作成
- [ ] サンプル画像でのテスト実行

**1.3 Flaskアプリケーションの初期設定**
- [ ] Flaskプロジェクトの初期化
- [ ] ディレクトリ構造の作成
- [ ] 基本的なルーティング設定
- [ ] 設定ファイル（`config.py`）の作成
- [ ] ロギング設定

**成果物**
- 動作するFlaskアプリケーション
- 各AIモデルの動作確認完了
- プロジェクト基盤の完成

---

### フェーズ2: AIモジュールの実装

#### 目標
各AI技術をPythonモジュールとして実装し、統合

#### タスク

**2.1 SAM 2セグメンテーションモジュール**
- [ ] `services/sam2_service.py` の実装
  - モデルロード機能
  - 画像セグメンテーション機能
  - セグメントフィルタリング機能
- [ ] 単体テストの作成
- [ ] サンプル画像での動作検証

**2.2 顕著性解析モジュール**
- [ ] `services/saliency_service.py` の実装
  - OpenCV Saliency APIの統合
  - 顕著性マップ生成機能
  - セグメント顕著性スコア計算
- [ ] 単体テストの作成
- [ ] 可視化スクリプトの作成

**2.3 LaMa画像補完モジュール**
- [ ] `services/lama_service.py` の実装
  - モデルロード機能
  - 単一マスク補完機能
  - バッチ補完機能
- [ ] 補完品質のテスト
- [ ] リファインメント機能の評価

**2.4 間違い生成オーケストレーター**
- [ ] `services/difference_generator.py` の実装
  - セグメント選択ロジック
  - 難易度調整機能
  - 色変更機能
  - 物体複製機能
  - メタデータ生成
- [ ] 統合テストの作成
- [ ] エンドツーエンドのパイプライン検証

**成果物**
- 全AIモジュールの実装完了
- 単体/統合テストの完了
- サンプル出力の生成成功

---

### フェーズ3: Web UIとバックエンドAPI

#### 目標
ユーザーフレンドリーなWebインターフェースの構築

#### タスク

**3.1 バックエンドAPIの実装**
- [ ] `/api/upload` エンドポイント実装
  - ファイルアップロード処理
  - バリデーション
  - 安全なファイル保存
- [ ] `/api/generate` エンドポイント実装
  - 非同期処理の導入
  - ジョブキュー管理
  - エラーハンドリング
- [ ] `/api/status/<job_id>` エンドポイント実装
  - 処理ステータス確認
  - 進捗情報の返却
- [ ] `/api/result/<job_id>` エンドポイント実装
  - 結果データの返却
  - 画像URLの生成

**3.2 フロントエンド実装**
- [ ] トップページ (`templates/index.html`)
  - ヒーローセクション
  - 使い方説明
  - デモ動画/画像
- [ ] アップロードページ (`templates/upload.html`)
  - ドラッグ&ドロップUI
  - プレビュー表示
  - 難易度選択
- [ ] 処理中ページ (`templates/processing.html`)
  - プログレスバー
  - 処理ステップ表示
  - 推定残り時間
- [ ] 結果表示ページ (`templates/result.html`)
  - サイドバイサイド比較表示
  - 差異のハイライト機能
  - ダウンロードボタン

**3.3 JavaScript実装**
- [ ] `static/js/upload.js`
  - ファイル選択処理
  - ドラッグ&ドロップ処理
  - バリデーション
- [ ] `static/js/processing.js`
  - 進捗ポーリング
  - リアルタイム更新
- [ ] `static/js/result.js`
  - 画像比較機能
  - ダウンロード処理

**3.4 CSS/デザイン**
- [ ] `static/css/style.css`
  - レスポンシブデザイン
  - モダンなUI
  - アニメーション

**成果物**
- 完全なWebアプリケーション
- 直感的なUI/UX
- エンドツーエンドの動作確認

---

### フェーズ4: テスト、最適化、ドキュメント

#### 目標
品質保証、性能最適化、包括的なドキュメント作成

#### タスク

**4.1 包括的テスト**
- [ ] 単体テストの拡充
  - 全モジュールのカバレッジ80%以上
- [ ] 統合テストの実装
  - AIパイプライン全体のテスト
  - エッジケースの検証
- [ ] E2Eテストの実装
  - ブラウザテスト（Selenium/Playwright）
  - 複数画像での動作確認
- [ ] 性能テスト
  - 処理時間の計測
  - GPU/メモリ使用率の監視
  - ボトルネックの特定

**4.2 性能最適化**
- [ ] GPUメモリの最適化
  - バッチサイズの調整
  - モデルの軽量化検討
- [ ] 処理時間の短縮
  - 並列処理の導入
  - キャッシング戦略
- [ ] データベースクエリの最適化
- [ ] 画像サイズの最適化

**4.3 セキュリティ強化**
- [ ] ファイルアップロードのセキュリティ検証
- [ ] CSRF/XSS対策の確認
- [ ] レート制限の実装
- [ ] エラーメッセージの精査

**4.4 ドキュメント整備**
- [ ] README.md の作成
  - プロジェクト説明
  - セットアップ手順
  - 使用方法
- [ ] 開発者向けドキュメント
  - アーキテクチャ説明
  - API仕様書
  - コーディング規約
- [ ] ユーザーマニュアル
  - 操作手順
  - トラブルシューティング

**4.5 デプロイメント準備**
- [ ] Docker化
  - Dockerfile作成
  - docker-compose.yml作成
- [ ] 本番環境設定
  - Gunicorn設定
  - Nginx設定
- [ ] CI/CDパイプライン（オプション）
  - GitHub Actionsの設定
  - 自動テストの実行

**成果物**
- 高品質なアプリケーション
- 包括的なテストスイート
- 完全なドキュメント
- デプロイ可能な状態

---

## 3. 詳細実装計画

### 3.1 Week 1: 環境構築とプロジェクト初期化

**Day 1-2: 開発環境セットアップ**
```bash
# プロジェクト構造作成
mkdir -p spot_the_diff/{app/{routes,services,utils,models,static/{css,js,images},templates},models,uploads,outputs,tests,config,scripts,doc}

# UV環境の初期化
uv init
uv venv
source .venv/bin/activate

# pyproject.tomlの設定
[project]
name = "spot-the-diff"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "flask>=3.0.0",
    "pillow>=10.0.0",
    "opencv-python>=4.8.0",
    "numpy>=1.24.0",
    "torch>=2.5.0",
    "torchvision>=0.20.0",
    "pytest>=7.4.0",
]
```

**Day 3-4: AIモデルのダウンロード**
```python
# scripts/download_models.py
import os
import urllib.request
from pathlib import Path

def download_sam2():
    """SAM 2 Tinyモデルのダウンロード"""
    model_dir = Path("models/sam2")
    model_dir.mkdir(parents=True, exist_ok=True)

    url = "https://dl.fbaipublicfiles.com/segment_anything_2/sam2_hiera_tiny.pt"
    output_path = model_dir / "sam2_hiera_tiny.pt"

    if not output_path.exists():
        print("Downloading SAM 2 Tiny...")
        urllib.request.urlretrieve(url, output_path)
        print("Download complete!")

def download_lama():
    """LaMaモデルのダウンロード"""
    # Hugging Faceからダウンロード
    pass

if __name__ == "__main__":
    download_sam2()
    download_lama()
```

**Day 5-7: Flask初期設定と基本構造**
```python
# app/__init__.py
from flask import Flask
from config.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ブループリント登録
    from app.routes import main, upload, generate
    app.register_blueprint(main.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(generate.bp)

    return app

# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

### 3.2 Week 2-4: AIモジュール実装

**Week 2: SAM 2とSaliency実装**

```python
# app/services/sam2_service.py
import torch
import numpy as np
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Segment:
    mask: np.ndarray
    bbox: List[int]
    area: int
    score: float
    saliency_score: float = 0.0

class SAM2Service:
    def __init__(self, model_path: str, device: str = 'cuda'):
        self.device = device
        self.model = self._load_model(model_path)

    def _load_model(self, model_path: str):
        """SAM 2モデルをロード"""
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor

        checkpoint = Path(model_path)
        config = "sam2_hiera_t.yaml"

        sam2_model = build_sam2(config, checkpoint, device=self.device)
        predictor = SAM2ImagePredictor(sam2_model)
        return predictor

    def segment_image(self, image: np.ndarray,
                     min_area: int = 1000,
                     max_area: int = None) -> List[Segment]:
        """
        画像をセグメント化

        Args:
            image: RGB画像 (H, W, 3)
            min_area: 最小セグメント面積
            max_area: 最大セグメント面積

        Returns:
            List[Segment]: セグメントリスト
        """
        self.model.set_image(image)

        # 自動マスク生成
        masks = self.model.generate(image)

        segments = []
        for mask_data in masks:
            mask = mask_data['segmentation']
            area = mask.sum()

            # 面積フィルタ
            if area < min_area:
                continue
            if max_area and area > max_area:
                continue

            # バウンディングボックス計算
            bbox = self._compute_bbox(mask)

            segment = Segment(
                mask=mask,
                bbox=bbox,
                area=int(area),
                score=float(mask_data.get('stability_score', 0.0))
            )
            segments.append(segment)

        return segments

    def _compute_bbox(self, mask: np.ndarray) -> List[int]:
        """マスクからバウンディングボックスを計算"""
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        return [int(cmin), int(rmin), int(cmax), int(rmax)]
```

```python
# app/services/saliency_service.py
import cv2
import numpy as np
from typing import List

class SaliencyService:
    def __init__(self, method: str = 'spectral_residual'):
        """
        Args:
            method: 'spectral_residual', 'fine_grained', 'bing'
        """
        self.method = method
        self.saliency = self._create_saliency_detector()

    def _create_saliency_detector(self):
        if self.method == 'spectral_residual':
            return cv2.saliency.StaticSaliencySpectralResidual_create()
        elif self.method == 'fine_grained':
            return cv2.saliency.StaticSaliencyFineGrained_create()
        else:
            raise ValueError(f"Unknown method: {self.method}")

    def compute_saliency_map(self, image: np.ndarray) -> np.ndarray:
        """
        顕著性マップを生成

        Args:
            image: RGB画像 (H, W, 3)

        Returns:
            np.ndarray: 正規化された顕著性マップ (H, W) [0.0-1.0]
        """
        success, saliency_map = self.saliency.computeSaliency(image)

        if not success:
            raise RuntimeError("Saliency computation failed")

        # 正規化
        saliency_map = cv2.normalize(
            saliency_map, None, 0, 1, cv2.NORM_MINMAX
        )

        return saliency_map

    def compute_segment_saliency(self, saliency_map: np.ndarray,
                                 segment: 'Segment') -> float:
        """
        セグメントの平均顕著性スコアを計算

        Returns:
            float: 顕著性スコア [0.0-1.0]
        """
        masked_saliency = saliency_map[segment.mask]
        return float(np.mean(masked_saliency))

    def rank_segments(self, segments: List['Segment'],
                     saliency_map: np.ndarray) -> List['Segment']:
        """セグメントを顕著性でランク付け"""
        for segment in segments:
            segment.saliency_score = self.compute_segment_saliency(
                saliency_map, segment
            )

        # 顕著性スコアの昇順でソート（低い方が目立ちにくい）
        return sorted(segments, key=lambda s: s.saliency_score)
```

**Week 3: LaMa統合と色変更機能**

```python
# app/services/lama_service.py
import torch
import numpy as np
from pathlib import Path
from PIL import Image

class LaMaService:
    def __init__(self, model_path: str, device: str = 'cuda'):
        self.device = device
        self.model = self._load_model(model_path)

    def _load_model(self, model_path: str):
        """LaMaモデルをロード"""
        # LaMaの実装に従ってロード
        checkpoint = torch.load(model_path, map_location=self.device)
        model = ... # LaMaモデルの初期化
        model.load_state_dict(checkpoint)
        model.eval()
        return model

    def inpaint(self, image: np.ndarray, mask: np.ndarray,
                refine: bool = True) -> np.ndarray:
        """
        画像補完

        Args:
            image: RGB画像 (H, W, 3) [0-255]
            mask: バイナリマスク (H, W) [0 or 1]
            refine: リファインメント処理

        Returns:
            np.ndarray: 補完画像 (H, W, 3) [0-255]
        """
        # 前処理
        image_tensor = self._preprocess_image(image)
        mask_tensor = self._preprocess_mask(mask)

        # 推論
        with torch.no_grad():
            output = self.model(image_tensor, mask_tensor)

        # 後処理
        result = self._postprocess(output)

        if refine:
            result = self._refine(result, mask)

        return result

    def _preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """画像の前処理"""
        image = image.astype(np.float32) / 255.0
        image = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0)
        return image.to(self.device)

    def _preprocess_mask(self, mask: np.ndarray) -> torch.Tensor:
        """マスクの前処理"""
        mask = mask.astype(np.float32)
        mask = torch.from_numpy(mask).unsqueeze(0).unsqueeze(0)
        return mask.to(self.device)

    def _postprocess(self, output: torch.Tensor) -> np.ndarray:
        """出力の後処理"""
        output = output.squeeze(0).permute(1, 2, 0).cpu().numpy()
        output = (output * 255).clip(0, 255).astype(np.uint8)
        return output
```

```python
# app/utils/image_utils.py
import cv2
import numpy as np
from typing import Tuple

def change_color(image: np.ndarray, mask: np.ndarray,
                hue_shift: int = None) -> np.ndarray:
    """
    物体の色を変更

    Args:
        image: RGB画像
        mask: バイナリマスク
        hue_shift: 色相シフト量（0-180）、Noneの場合はランダム

    Returns:
        色変更後の画像
    """
    # BGR → HSV変換
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)

    # ランダムな色相シフト
    if hue_shift is None:
        hue_shift = np.random.randint(30, 150)

    # マスク領域の色相を変更
    hsv[:, :, 0][mask] = (hsv[:, :, 0][mask] + hue_shift) % 180

    # HSV → RGB変換
    hsv = hsv.astype(np.uint8)
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    return result

def duplicate_object(image: np.ndarray, segment: 'Segment',
                    offset: Tuple[int, int] = None) -> np.ndarray:
    """
    物体を複製して配置

    Args:
        image: RGB画像
        segment: セグメント情報
        offset: 配置オフセット (dx, dy)、Noneの場合は自動計算

    Returns:
        オブジェクト追加後の画像
    """
    result = image.copy()

    # セグメント領域の抽出
    x1, y1, x2, y2 = segment.bbox
    obj_region = image[y1:y2, x1:x2].copy()
    obj_mask = segment.mask[y1:y2, x1:x2]

    # 配置位置の決定
    if offset is None:
        offset = _find_empty_space(image, segment)

    dx, dy = offset
    new_x1 = x1 + dx
    new_y1 = y1 + dy
    new_x2 = new_x1 + (x2 - x1)
    new_y2 = new_y1 + (y2 - y1)

    # 画像範囲内チェック
    if new_x2 > image.shape[1] or new_y2 > image.shape[0]:
        return result

    # マスク領域のみコピー
    result[new_y1:new_y2, new_x1:new_x2][obj_mask] = obj_region[obj_mask]

    return result

def _find_empty_space(image: np.ndarray, segment: 'Segment') -> Tuple[int, int]:
    """空いているスペースを探す"""
    # 簡易実装：ランダムなオフセット
    h, w = image.shape[:2]
    x1, y1, x2, y2 = segment.bbox
    obj_w = x2 - x1
    obj_h = y2 - y1

    max_dx = w - x2 - obj_w
    max_dy = h - y2 - obj_h

    if max_dx > 0 and max_dy > 0:
        dx = np.random.randint(50, max(51, max_dx))
        dy = np.random.randint(50, max(51, max_dy))
        return (dx, dy)

    return (0, 0)
```

**Week 4: オーケストレーター実装**

```python
# app/services/difference_generator.py
import random
import time
from typing import List, Tuple, Dict
from dataclasses import dataclass, asdict
import numpy as np

@dataclass
class Difference:
    id: int
    type: str  # 'deletion', 'color_change', 'addition'
    bbox: List[int]
    polygon: List[List[int]]
    saliency_score: float
    description: str
    original_color: List[int] = None
    new_color: List[int] = None

@dataclass
class GenerationResult:
    modified_image: np.ndarray
    differences: List[Difference]
    metadata: Dict

class DifferenceGenerator:
    def __init__(self, sam2_service, saliency_service, lama_service):
        self.sam2 = sam2_service
        self.saliency = saliency_service
        self.lama = lama_service

        self.difficulty_config = {
            'easy': {'num_changes': 3, 'saliency_max': 0.7},
            'medium': {'num_changes': 5, 'saliency_max': 0.5},
            'hard': {'num_changes': 8, 'saliency_max': 0.3}
        }

    def generate(self, image: np.ndarray,
                difficulty: str = 'medium') -> GenerationResult:
        """間違い探し画像を生成"""
        start_time = time.time()

        # 1. セグメンテーション
        seg_start = time.time()
        segments = self.sam2.segment_image(image)
        seg_time = time.time() - seg_start

        # 2. 顕著性解析
        sal_start = time.time()
        saliency_map = self.saliency.compute_saliency_map(image)
        ranked_segments = self.saliency.rank_segments(segments, saliency_map)
        sal_time = time.time() - sal_start

        # 3. セグメント選択
        selected = self._select_segments(ranked_segments, difficulty)

        # 4. 変更適用
        inp_start = time.time()
        modified_image, differences = self._apply_changes(image, selected)
        inp_time = time.time() - inp_start

        total_time = time.time() - start_time

        # 5. メタデータ生成
        metadata = self._create_metadata(
            differences, difficulty,
            seg_time, sal_time, inp_time, total_time
        )

        return GenerationResult(modified_image, differences, metadata)

    def _select_segments(self, segments: List,
                        difficulty: str) -> List:
        """難易度に基づいてセグメントを選択"""
        config = self.difficulty_config[difficulty]
        num_changes = config['num_changes']
        saliency_max = config['saliency_max']

        # 顕著性フィルタリング
        filtered = [s for s in segments
                   if s.saliency_score <= saliency_max]

        # ランダムサンプリング
        n = min(num_changes, len(filtered))
        return random.sample(filtered, n)

    def _apply_changes(self, image: np.ndarray, segments: List) -> Tuple:
        """変更を適用"""
        from app.utils.image_utils import change_color, duplicate_object

        modified = image.copy()
        differences = []

        change_types = ['deletion', 'color_change', 'addition']

        for idx, segment in enumerate(segments):
            change_type = random.choice(change_types)

            if change_type == 'deletion':
                modified = self.lama.inpaint(modified, segment.mask)
                desc = "Object removed"

            elif change_type == 'color_change':
                original_color = self._get_avg_color(modified, segment.mask)
                modified = change_color(modified, segment.mask)
                new_color = self._get_avg_color(modified, segment.mask)
                desc = "Color changed"

            elif change_type == 'addition':
                modified = duplicate_object(modified, segment)
                desc = "Object duplicated"

            # Polygon抽出（輪郭）
            polygon = self._extract_polygon(segment.mask)

            diff = Difference(
                id=idx + 1,
                type=change_type,
                bbox=segment.bbox,
                polygon=polygon,
                saliency_score=segment.saliency_score,
                description=desc
            )

            if change_type == 'color_change':
                diff.original_color = original_color
                diff.new_color = new_color

            differences.append(diff)

        return modified, differences

    def _get_avg_color(self, image: np.ndarray, mask: np.ndarray) -> List[int]:
        """マスク領域の平均色を取得"""
        colors = image[mask]
        avg_color = np.mean(colors, axis=0).astype(int).tolist()
        return avg_color

    def _extract_polygon(self, mask: np.ndarray) -> List[List[int]]:
        """マスクから輪郭ポリゴンを抽出"""
        import cv2
        contours, _ = cv2.findContours(
            mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        if len(contours) > 0:
            largest = max(contours, key=cv2.contourArea)
            polygon = largest.squeeze().tolist()
            return polygon if isinstance(polygon[0], list) else [polygon]
        return []

    def _create_metadata(self, differences, difficulty,
                        seg_time, sal_time, inp_time, total_time) -> Dict:
        """メタデータを生成"""
        return {
            'difficulty': difficulty,
            'total_differences': len(differences),
            'differences': [asdict(d) for d in differences],
            'processing_steps': {
                'segmentation_time': round(seg_time, 2),
                'saliency_time': round(sal_time, 2),
                'inpainting_time': round(inp_time, 2),
                'total_time': round(total_time, 2)
            },
            'model_versions': {
                'sam2': 'SAM 2 Tiny',
                'lama': 'big-lama',
                'saliency': 'opencv-spectral-residual'
            }
        }
```

---

### 3.3 Week 5-6: Web UI実装

**Week 5: バックエンドAPI**

```python
# app/routes/upload.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid
from pathlib import Path
from app.utils.validation import validate_image_file

bp = Blueprint('upload', __name__, url_prefix='/api')

@bp.route('/upload', methods=['POST'])
def upload_image():
    """画像アップロードエンドポイント"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # バリデーション
        validate_image_file(file)

        # 安全なファイル名生成
        ext = file.filename.rsplit('.', 1)[1].lower()
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.{ext}"

        # 保存
        upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(exist_ok=True)
        filepath = upload_dir / filename
        file.save(filepath)

        # 画像情報取得
        from PIL import Image
        img = Image.open(filepath)
        width, height = img.size

        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': file.filename,
            'size': filepath.stat().st_size,
            'dimensions': [width, height]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

```python
# app/routes/generate.py
from flask import Blueprint, request, jsonify, current_app
from concurrent.futures import ThreadPoolExecutor
import uuid
from pathlib import Path

bp = Blueprint('generate', __name__, url_prefix='/api')

# グローバルExecutor
executor = ThreadPoolExecutor(max_workers=3)

# ジョブステータス管理
job_status = {}

@bp.route('/generate', methods=['POST'])
def generate_difference():
    """間違い探し生成エンドポイント"""
    data = request.json

    file_id = data.get('file_id')
    difficulty = data.get('difficulty', 'medium')

    if not file_id:
        return jsonify({'error': 'file_id is required'}), 400

    # ファイル存在確認
    upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
    filepath = next(upload_dir.glob(f"{file_id}.*"), None)

    if not filepath:
        return jsonify({'error': 'File not found'}), 404

    # ジョブID生成
    job_id = f"job_{uuid.uuid4().hex}"

    # 非同期処理開始
    job_status[job_id] = {
        'status': 'queued',
        'progress': 0,
        'current_step': 'Queued'
    }

    executor.submit(process_generation, job_id, filepath, difficulty)

    return jsonify({
        'success': True,
        'job_id': job_id,
        'status': 'queued',
        'estimated_time': 90
    })

def process_generation(job_id, filepath, difficulty):
    """バックグラウンド処理"""
    try:
        from app.services.difference_generator import DifferenceGenerator
        from app import sam2_service, saliency_service, lama_service
        from PIL import Image
        import numpy as np

        # ステータス更新
        job_status[job_id] = {
            'status': 'processing',
            'progress': 10,
            'current_step': 'Loading image'
        }

        # 画像読み込み
        image = np.array(Image.open(filepath))

        # 生成処理
        job_status[job_id]['progress'] = 30
        job_status[job_id]['current_step'] = 'Segmentation'

        generator = DifferenceGenerator(
            sam2_service, saliency_service, lama_service
        )
        result = generator.generate(image, difficulty)

        # 結果保存
        job_status[job_id]['progress'] = 90
        job_status[job_id]['current_step'] = 'Saving results'

        output_dir = Path('outputs') / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # 画像保存
        Image.fromarray(image).save(output_dir / 'original.png')
        Image.fromarray(result.modified_image).save(output_dir / 'modified.png')

        # メタデータ保存
        import json
        with open(output_dir / 'metadata.json', 'w') as f:
            json.dump(result.metadata, f, indent=2)

        # 完了ステータス
        job_status[job_id] = {
            'status': 'completed',
            'progress': 100,
            'current_step': 'Finished',
            'result_path': str(output_dir)
        }

    except Exception as e:
        job_status[job_id] = {
            'status': 'failed',
            'error': str(e)
        }

@bp.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """処理ステータス取得"""
    if job_id not in job_status:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(job_status[job_id])

@bp.route('/result/<job_id>', methods=['GET'])
def get_result(job_id):
    """結果取得"""
    if job_id not in job_status:
        return jsonify({'error': 'Job not found'}), 404

    status = job_status[job_id]

    if status['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400

    output_dir = Path(status['result_path'])

    import json
    with open(output_dir / 'metadata.json') as f:
        metadata = json.load(f)

    return jsonify({
        'success': True,
        'job_id': job_id,
        'original_image_url': f'/outputs/{job_id}/original.png',
        'modified_image_url': f'/outputs/{job_id}/modified.png',
        'metadata': metadata
    })
```

**Week 6: フロントエンド実装**

```html
<!-- templates/upload.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>画像アップロード - 間違い探し自動生成</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>間違い探し自動生成システム</h1>

        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📷</div>
            <p>画像をドラッグ&ドロップ</p>
            <p>または</p>
            <button class="btn-primary" onclick="document.getElementById('fileInput').click()">
                ファイルを選択
            </button>
            <input type="file" id="fileInput" accept="image/png,image/jpeg" style="display: none;">
        </div>

        <div id="previewArea" style="display: none;">
            <img id="previewImage" alt="Preview">
            <div class="difficulty-selector">
                <label>難易度:</label>
                <select id="difficulty">
                    <option value="easy">簡単</option>
                    <option value="medium" selected>普通</option>
                    <option value="hard">難しい</option>
                </select>
            </div>
            <button class="btn-success" id="generateBtn">生成開始</button>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/upload.js') }}"></script>
</body>
</html>
```

```javascript
// static/js/upload.js
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewArea = document.getElementById('previewArea');
const previewImage = document.getElementById('previewImage');
const generateBtn = document.getElementById('generateBtn');

let uploadedFileId = null;

// ドラッグ&ドロップ
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// ファイル選択
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// ファイル処理
async function handleFile(file) {
    // バリデーション
    if (!file.type.startsWith('image/')) {
        alert('画像ファイルを選択してください');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        alert('ファイルサイズは10MB以下にしてください');
        return;
    }

    // プレビュー表示
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadArea.style.display = 'none';
        previewArea.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // アップロード
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            uploadedFileId = data.file_id;
        } else {
            alert('アップロードに失敗しました: ' + data.error);
        }
    } catch (error) {
        alert('エラーが発生しました: ' + error.message);
    }
}

// 生成開始
generateBtn.addEventListener('click', async () => {
    if (!uploadedFileId) {
        alert('画像をアップロードしてください');
        return;
    }

    const difficulty = document.getElementById('difficulty').value;

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: uploadedFileId,
                difficulty: difficulty
            })
        });

        const data = await response.json();

        if (data.success) {
            // 処理中ページへ遷移
            window.location.href = `/processing?job_id=${data.job_id}`;
        } else {
            alert('生成リクエストに失敗しました: ' + data.error);
        }
    } catch (error) {
        alert('エラーが発生しました: ' + error.message);
    }
});
```

---

### 3.4 Week 7-8: テストと最適化

```python
# tests/test_services.py
import pytest
import numpy as np
from app.services.sam2_service import SAM2Service
from app.services.saliency_service import SaliencyService
from app.services.lama_service import LaMaService

@pytest.fixture
def test_image():
    """テスト用画像"""
    return np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)

def test_sam2_segmentation(test_image):
    service = SAM2Service('models/sam2/sam2_hiera_tiny.pt')
    segments = service.segment_image(test_image)

    assert len(segments) > 0
    for segment in segments:
        assert segment.mask.shape == (512, 512)
        assert len(segment.bbox) == 4
        assert segment.area > 0

def test_saliency_computation(test_image):
    service = SaliencyService()
    saliency_map = service.compute_saliency_map(test_image)

    assert saliency_map.shape == (512, 512)
    assert 0 <= saliency_map.min() <= saliency_map.max() <= 1

# さらにテストを追加...
```

---

### 3.5 Week 9: ドキュメントとデプロイ準備

```markdown
# README.md

# 次世代型間違い探し自動生成システム

AI技術を活用して、画像から自動的に間違い探し問題を生成するWebアプリケーション。

## 特徴

- **最新AI技術**: SAM 2、LaMa、顕著性解析を統合
- **簡単操作**: 画像をアップロードするだけで自動生成
- **難易度調整**: 簡単・普通・難しいの3段階

## セットアップ

### 必要環境

- Python 3.10以上
- CUDA対応GPU (推奨)
- 16GB以上のRAM

### インストール

\`\`\`bash
# リポジトリのクローン
git clone <repository_url>
cd NewSpotTheDiff

# UV環境のセットアップ
uv venv
source .venv/bin/activate

# 依存関係のインストール
uv pip install -e .

# AIモデルのダウンロード
python scripts/download_models.py
\`\`\`

### 起動

\`\`\`bash
python run.py
\`\`\`

ブラウザで http://localhost:5000 にアクセス

## 使い方

1. 画像をアップロード
2. 難易度を選択
3. 「生成開始」ボタンをクリック
4. 完成した間違い探しをダウンロード

## ドキュメント

- [要件定義書](doc/requirements.md)
- [システム設計書](doc/system_architecture.md)
- [実装計画](doc/implementation_plan.md)

## ライセンス

MIT License
```

---

## 4. リスク管理と対応策

| リスク | 発生確率 | 影響度 | 対応策 |
|--------|---------|--------|---------|
| GPU環境構築の遅延 | 中 | 高 | クラウドGPU（Colab、AWS）の準備 |
| AIモデルの処理時間超過 | 高 | 中 | 軽量モデルの採用、段階的最適化 |
| 画像補完品質の問題 | 中 | 中 | 複数モデルの比較、ハイパラ調整 |
| フロントエンド実装の遅延 | 低 | 低 | テンプレートライブラリの活用 |

---

## 5. 成功基準

### MVP (Minimum Viable Product)
- [ ] 1枚の画像から間違い探しを生成できる
- [ ] 3つの難易度レベルが機能する
- [ ] 処理時間が2分以内
- [ ] 生成画像が視覚的に自然

### 初期リリース
- [ ] 10名の同時ユーザーに対応
- [ ] UIが直感的で使いやすい
- [ ] エラーハンドリングが適切
- [ ] ドキュメントが完備

---

**文書バージョン**: 1.0
**最終更新日**: 2026-02-08
**作成者**: Claude Code
