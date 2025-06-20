import os
import json

BASE_PATH = "toss_ocr"

for folder_name in os.listdir(BASE_PATH):
    folder_path = os.path.join(BASE_PATH, folder_name)
    if not os.path.isdir(folder_path):
        continue
    merged = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json") and not filename.endswith("_merged.json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    merged.append(data)
                except Exception as e:
                    print(f"파일 오류: {file_path}: {e}")
    # 병합 결과 저장 (폴더명_merged.json)
    output_filename = f"{folder_name}_merged.json"
    output_path = os.path.join(folder_path, output_filename)
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(merged, out, ensure_ascii=False, indent=2)
    print(f"{folder_name}: {len(merged)}개 json -> {output_path} 저장")
