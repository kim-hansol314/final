import os
import json

BASE_PATH = "toss_ocr"

for folder_name in os.listdir(BASE_PATH):
    folder_path = os.path.join(BASE_PATH, folder_name)
    if not os.path.isdir(folder_path):
        continue
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # content_ordered가 비어있지 않고 첫번째가 type=="text"인 경우만 처리
            co = data.get("content_ordered", [])
            if co and co[0].get("type") == "text":
                data["title"] = co[0]["data"]
                data["content_ordered"] = co[1:]

                # 덮어쓰기(혹은 파일명 뒤에 _title 추가 등 선택 가능)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"변환 완료: {file_path}")
