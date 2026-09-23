import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_trusted_release import APPROVED_CATEGORIES, build_release


class TrustedReleaseBuilderTest(unittest.TestCase):
    def test_build_release_converts_only_approved_rectangles(self):
        with tempfile.TemporaryDirectory() as directory:
            source_root, output_root = create_source_fixture(Path(directory))

            build_release(source_root, output_root)

            coco = read_json(output_root / "annotations" / "instances.json")
            self.assertEqual(len(coco["images"]), 1)
            self.assertEqual(len(coco["annotations"]), 1)
            self.assertEqual(coco["annotations"][0]["bbox"], [10, 20, 20, 40])
            self.assertEqual(coco["annotations"][0]["category_id"], 1)
            self.assertEqual(coco["categories"], APPROVED_CATEGORIES)

    def test_build_release_writes_contract_manifest_splits_and_links(self):
        with tempfile.TemporaryDirectory() as directory:
            source_root, output_root = create_source_fixture(Path(directory))

            build_release(source_root, output_root)

            contract = read_json(output_root / "contract.json")
            manifest = read_json(output_root / "manifest.json")
            splits = read_json(output_root / "splits.json")
            image_link = output_root / "images" / "frame.jpg"

            self.assertEqual(contract["format"], "COCO")
            self.assertEqual(len(contract["categories"]), 9)
            self.assertEqual(manifest["images"][0]["width"], 1280)
            self.assertEqual(manifest["images"][0]["height"], 720)
            self.assertEqual(len(manifest["images"][0]["sha256"]), 64)
            self.assertEqual(splits, {"train": [1], "val": [], "test": []})
            self.assertTrue(image_link.is_symlink())


def create_source_fixture(root):
    source_root = root / "source"
    image_directory = source_root / "val" / "img"
    annotation_directory = source_root / "val" / "ann"
    image_directory.mkdir(parents=True)
    annotation_directory.mkdir()
    (image_directory / "frame.jpg").write_bytes(b"fixture-image")
    annotation = {
        "size": {"width": 1280, "height": 720},
        "objects": [
            rectangle("car", [[10, 20], [30, 60]]),
            {"classTitle": "lane", "geometryType": "line", "points": {"exterior": [[0, 0], [1, 1]]}},
            {
                "classTitle": "drivable area",
                "geometryType": "polygon",
                "points": {"exterior": [[0, 0], [1, 0], [1, 1]]},
            },
        ],
    }
    (annotation_directory / "frame.jpg.json").write_text(json.dumps(annotation))
    return source_root, root / "trusted"


def rectangle(class_title, exterior):
    return {"classTitle": class_title, "geometryType": "rectangle", "points": {"exterior": exterior}}


def read_json(path):
    return json.loads(path.read_text())
