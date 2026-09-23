### C6: Dataset Semantic Integrity Gate

Dataset liên tục qua CVAT/COCO/YOLO/vendor merge/version. Class mapping, geometry hoặc metadata có thể sai mà file vẫn parse và training vẫn chạy.

---

### Challenge — Production Question

* **Xây Dataset Release Gate** phát hiện silent semantic corruption, không chỉ syntax errors.
* *“Convert/merge/version có làm đổi nghĩa dataset không?”*

---

### Yêu cầu tối thiểu

* Tự thiết kế ít nhất 5 corruption types
* Corrupted release vẫn phải parse được; ưu tiên case training vẫn chạy
* Có clean releases để đo false block
* Report root-cause/evidence, không chỉ PASS/FAIL

**Research space:** Schema/data contracts, round-trip tests, semantic diff, statistical checks, geometry invariants, class-map verification, lineage/hash, learned anomaly detection…

---

### Metrics & Notes

> **Primary metric**
> **Silent-defect Detection F1** — defect recall theo corruption type · precision · false-block rate trên clean release.

* **Secondary metric:** Root-cause localization accuracy · round-trip geometry error/IoU · runtime / 1k samples. (Stretch: policy-driven gate FAIL/WARN/PASS có configurable threshold và machine-readable report.)

> **Lưu ý / bẫy:**
> Case ưu tiên: corrupted release vẫn parse được và training vẫn chạy — đó mới là silent corruption thật sự nguy hiểm.
