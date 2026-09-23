"""Build the immutable COCO baseline used by the C6 release-gate demo."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


APPROVED_CATEGORIES = [
    {"id": 1, "name": "car", "supercategory": "vehicle"},
    {"id": 2, "name": "truck", "supercategory": "vehicle"},
    {"id": 3, "name": "bus", "supercategory": "vehicle"},
    {"id": 4, "name": "person", "supercategory": "vulnerable_road_user"},
    {"id": 5, "name": "rider", "supercategory": "vulnerable_road_user"},
    {"id": 6, "name": "motor", "supercategory": "two_wheeler"},
    {"id": 7, "name": "bike", "supercategory": "two_wheeler"},
    {"id": 8, "name": "traffic light", "supercategory": "traffic_control"},
    {"id": 9, "name": "traffic sign", "supercategory": "traffic_control"},
]
CATEGORY_IDS = {category["name"]: category["id"] for category in APPROVED_CATEGORIES}


def build_release(source_root: Path, output_root: Path) -> dict:
    """Convert the raw Supervisely sample into a canonical COCO trusted release."""
    image_directory = source_root / "val" / "img"
    annotation_directory = source_root / "val" / "ann"
    if not image_directory.is_dir() or not annotation_directory.is_dir():
        raise ValueError("source root must contain val/img and val/ann directories")

    if output_root.exists():
        shutil.rmtree(output_root)
    (output_root / "annotations").mkdir(parents=True)
    linked_images = output_root / "images"
    linked_images.mkdir()

    images = []
    annotations = []
    manifest_images = []
    annotation_id = 1

    for image_id, image_path in enumerate(sorted(image_directory.glob("*.jpg")), start=1):
        annotation_path = annotation_directory / f"{image_path.name}.json"
        if not annotation_path.is_file():
            raise ValueError(f"missing annotation for {image_path.name}")
        source_annotation = read_json(annotation_path)
        width, height = source_dimensions(source_annotation, image_path.name)
        image_record = {"id": image_id, "file_name": image_path.name, "width": width, "height": height}
        images.append(image_record)

        link_path = linked_images / image_path.name
        link_path.symlink_to(image_path.resolve())
        manifest_images.append({**image_record, "sha256": sha256(image_path)})

        for source_object in source_annotation.get("objects", []):
            annotation = coco_annotation(source_object, image_id, annotation_id)
            if annotation is not None:
                annotations.append(annotation)
                annotation_id += 1

    coco = {"info": {"description": "BDD100K ADAS trusted demo release v1"}, "images": images, "annotations": annotations, "categories": APPROVED_CATEGORIES}
    splits = deterministic_splits([image["id"] for image in images])
    contract = {
        "release_name": "vinfast_relevant_adas_trusted_v1",
        "format": "COCO",
        "bbox_format": "xywh_pixels",
        "source_dataset": "BDD100K Images 100K sample",
        "categories": APPROVED_CATEGORIES,
        "required_image_hash": "sha256",
        "forbid_cross_split_duplicates": True,
    }
    write_json(output_root / "annotations" / "instances.json", coco)
    write_json(output_root / "contract.json", contract)
    write_json(output_root / "manifest.json", {"images": manifest_images})
    write_json(output_root / "splits.json", splits)
    (output_root / "RELEASE.md").write_text(release_markdown(len(images), len(annotations), splits))
    return {"images": len(images), "annotations": len(annotations), "splits": {name: len(ids) for name, ids in splits.items()}}


def coco_annotation(source_object: dict, image_id: int, annotation_id: int) -> dict | None:
    if source_object.get("geometryType") != "rectangle":
        return None
    category_id = CATEGORY_IDS.get(source_object.get("classTitle"))
    exterior = source_object.get("points", {}).get("exterior", [])
    if category_id is None or len(exterior) != 2:
        return None
    (x1, y1), (x2, y2) = exterior
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    width, height = right - left, bottom - top
    if width <= 0 or height <= 0:
        return None
    return {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": [left, top, width, height],
        "area": width * height,
        "iscrowd": 0,
    }


def source_dimensions(source_annotation: dict, filename: str) -> tuple[int, int]:
    size = source_annotation.get("size", {})
    width, height = size.get("width"), size.get("height")
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        raise ValueError(f"invalid dimensions for {filename}")
    return width, height


def deterministic_splits(image_ids: list[int]) -> dict:
    total = len(image_ids)
    if total == 0:
        return {"train": [], "val": [], "test": []}
    train_count = max(1, total * 70 // 100)
    val_count = total * 15 // 100
    return {
        "train": image_ids[:train_count],
        "val": image_ids[train_count : train_count + val_count],
        "test": image_ids[train_count + val_count :],
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, content: dict) -> None:
    path.write_text(json.dumps(content, indent=2) + "\n")


def release_markdown(image_count: int, annotation_count: int, splits: dict) -> str:
    return "\n".join(
        [
            "# Trusted Release v1",
            "",
            "Generated from `BDD100k-datasample/val` by `scripts/build_trusted_release.py`.",
            "",
            f"- Images: {image_count}",
            f"- Rectangle detection annotations: {annotation_count}",
            f"- Split counts: train={len(splits['train'])}, val={len(splits['val'])}, test={len(splits['test'])}",
            "- The split is deterministic and for this demo only; it is not an official BDD100K split.",
            "- Raw source files are not modified; release images are symlinks to the raw files.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the C6 BDD100K trusted release")
    parser.add_argument("--source", type=Path, default=Path("BDD100k-datasample"))
    parser.add_argument("--output", type=Path, default=Path("data/trusted_v1"))
    arguments = parser.parse_args()
    result = build_release(arguments.source, arguments.output)
    print(f"Built trusted release: {result['images']} images, {result['annotations']} annotations, splits={result['splits']}")


if __name__ == "__main__":
    main()
