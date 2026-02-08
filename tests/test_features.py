"""
Manual testing script for NewSpotTheDiff application.

This script performs basic functionality tests to verify that
all implemented features are working correctly.
"""

import sys
import os
from pathlib import Path
import numpy as np
import cv2

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

from src.services.answer_visualizer import AnswerVisualizer
from src.services.a4_layout_composer import A4LayoutComposer
from src.services.inpainting import InpaintingService
from src.services.color_changer import ColorChanger
from src.services.object_duplicator import ObjectDuplicator
from src.services.quality_evaluator import QualityEvaluator
from src.models.difference import Difference
from src.models.segment import Segment


def test_answer_visualizer():
    """Test AnswerVisualizer class."""
    print("Testing AnswerVisualizer...")

    # Create test image
    image = np.zeros((500, 500, 3), dtype=np.uint8)
    image[:] = (200, 200, 200)  # Grey background

    # Create test differences
    differences = [
        Difference(
            id=1,
            type="deletion",
            bbox=[100, 100, 150, 150],
            saliency_score=0.5,
            description="テスト削除",
        ),
        Difference(
            id=2,
            type="color_change",
            bbox=[300, 200, 380, 280],
            saliency_score=0.3,
            description="テスト色変更",
        ),
    ]

    # Test visualizer
    visualizer = AnswerVisualizer()
    result = visualizer.draw_answers(image, differences)

    # Check that result is not None
    assert result is not None, "Result should not be None"
    assert result.shape == image.shape, "Result shape should match input"

    # Check that circles were drawn (image should be modified)
    assert not np.array_equal(result, image), "Image should be modified"

    print("✅ AnswerVisualizer test passed")
    return True


def test_a4_layout_composer():
    """Test A4LayoutComposer class."""
    print("Testing A4LayoutComposer...")

    # Create test images
    left_image = np.zeros((800, 600, 3), dtype=np.uint8)
    left_image[:] = (100, 150, 200)

    right_image = np.zeros((800, 600, 3), dtype=np.uint8)
    right_image[:] = (200, 150, 100)

    # Test composer
    composer = A4LayoutComposer()
    result = composer.compose_side_by_side(
        left_image,
        right_image,
        left_title="左画像",
        right_title="右画像",
        title="テストタイトル",
    )

    # Check dimensions
    assert result is not None, "Result should not be None"
    assert result.shape[0] == composer.A4_HEIGHT, f"Height should be {composer.A4_HEIGHT}"
    assert result.shape[1] == composer.A4_WIDTH, f"Width should be {composer.A4_WIDTH}"
    assert result.shape[2] == 3, "Should be 3-channel BGR image"

    print("✅ A4LayoutComposer test passed")
    return True


def test_inpainting_service():
    """Test InpaintingService class."""
    print("Testing InpaintingService...")

    # Create test image with object
    image = np.ones((300, 300, 3), dtype=np.uint8) * 200
    cv2.rectangle(image, (100, 100), (200, 200), (50, 50, 50), -1)

    # Create mask for the object
    mask = np.zeros((300, 300), dtype=np.uint8)
    cv2.rectangle(mask, (100, 100), (200, 200), 255, -1)

    # Test inpainting
    service = InpaintingService(method="auto")
    result = service.inpaint(image, mask)

    # Check that result is valid
    assert result is not None, "Result should not be None"
    assert result.shape == image.shape, "Result shape should match input"

    # Check that inpainting was applied (object area should be different)
    object_area_before = image[100:200, 100:200].mean()
    object_area_after = result[100:200, 100:200].mean()
    assert abs(object_area_before - object_area_after) > 10, "Inpainting should modify the object area"

    print("✅ InpaintingService test passed")
    return True


def test_color_changer():
    """Test ColorChanger class."""
    print("Testing ColorChanger...")

    # Create test image
    image = np.ones((200, 200, 3), dtype=np.uint8) * 100
    cv2.rectangle(image, (50, 50), (150, 150), (50, 100, 200), -1)

    # Create mask
    mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.rectangle(mask, (50, 50), (150, 150), 255, -1)

    # Test color changer
    changer = ColorChanger()
    result, hue_shift = changer.change_hue(image, mask)

    # Check that result is valid
    assert result is not None, "Result should not be None"
    assert result.shape == image.shape, "Result shape should match input"
    assert 30 <= hue_shift <= 180, f"Hue shift should be in range, got {hue_shift}"

    # Check that color was changed
    original_color = image[100, 100]
    changed_color = result[100, 100]
    assert not np.array_equal(original_color, changed_color), "Color should be changed"

    print("✅ ColorChanger test passed")
    return True


def test_object_duplicator():
    """Test ObjectDuplicator class."""
    print("Testing ObjectDuplicator...")

    # Create test image
    image = np.ones((400, 400, 3), dtype=np.uint8) * 150
    cv2.circle(image, (100, 100), 30, (50, 50, 200), -1)

    # Create segment
    mask = np.zeros((400, 400), dtype=np.uint8)
    cv2.circle(mask, (100, 100), 30, 255, -1)

    segment = Segment(
        id=1,
        mask=mask,
        bbox=[70, 70, 130, 130],
        area=int(np.pi * 30 * 30),
        confidence=0.95,
    )

    # Test duplicator
    duplicator = ObjectDuplicator()
    result, new_bbox = duplicator.duplicate(image, segment)

    # Check that result is valid
    assert result is not None, "Result should not be None"
    assert result.shape == image.shape, "Result shape should match input"

    # new_bbox could be None if placement fails, which is acceptable
    if new_bbox is not None:
        assert len(new_bbox) == 4, "New bbox should have 4 coordinates"
        print(f"  Object duplicated to: {new_bbox}")
    else:
        print("  Object duplication skipped (no valid placement found)")

    print("✅ ObjectDuplicator test passed")
    return True


def test_quality_evaluator():
    """Test QualityEvaluator class."""
    print("Testing QualityEvaluator...")

    evaluator = QualityEvaluator()

    # Create test image with a clean object
    image = np.ones((300, 300, 3), dtype=np.uint8) * 200

    # Create a circular mask (should pass quality check)
    mask = np.zeros((300, 300), dtype=np.uint8)
    cv2.circle(mask, (150, 150), 50, 255, -1)

    segment = Segment(
        id=1,
        mask=mask,
        bbox=[100, 100, 200, 200],
        area=int(np.pi * 50 * 50),
        confidence=0.95,
    )

    # Test segment quality evaluation
    is_acceptable, quality_score, reason = evaluator.evaluate_segment_quality(image, segment)

    assert isinstance(is_acceptable, bool), "is_acceptable should be boolean"
    assert 0.0 <= quality_score <= 1.0, f"Quality score should be 0-1, got {quality_score}"
    assert isinstance(reason, str), "Reason should be a string"

    print(f"  Segment quality: acceptable={is_acceptable}, score={quality_score:.2f}, reason={reason}")

    # Test modification quality evaluation
    original_region = image[100:200, 100:200].copy()
    modified_region = original_region.copy()
    # Make a slight modification
    modified_region[mask[100:200, 100:200] > 0] = [180, 180, 180]
    local_mask = mask[100:200, 100:200]

    is_acceptable_mod, quality_score_mod, reason_mod = evaluator.evaluate_modification_quality(
        original_region,
        modified_region,
        local_mask,
        "color_change",
    )

    assert isinstance(is_acceptable_mod, bool), "is_acceptable should be boolean"
    assert 0.0 <= quality_score_mod <= 1.0, f"Quality score should be 0-1, got {quality_score_mod}"

    print(f"  Modification quality: acceptable={is_acceptable_mod}, score={quality_score_mod:.2f}")

    print("✅ QualityEvaluator test passed")
    return True


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("Running NewSpotTheDiff Feature Tests")
    print("="*60)
    print()

    tests = [
        test_answer_visualizer,
        test_a4_layout_composer,
        test_inpainting_service,
        test_color_changer,
        test_object_duplicator,
        test_quality_evaluator,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()

    print("="*60)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
