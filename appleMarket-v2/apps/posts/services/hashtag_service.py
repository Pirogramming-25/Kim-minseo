from ultralytics import YOLO


_model = None


LABEL_MAP = {
    "person": "사람",
    "bicycle": "자전거",
    "car": "자동차",
    "motorcycle": "오토바이",
    "bus": "버스",
    "truck": "트럭",
    "backpack": "가방",
    "handbag": "가방",
    "suitcase": "캐리어",
    "umbrella": "우산",
    "sports ball": "스포츠",
    "skateboard": "스케이트보드",
    "chair": "의자",
    "couch": "소파",
    "bed": "침대",
    "dining table": "테이블",
    "tv": "TV",
    "laptop": "노트북",
    "mouse": "마우스",
    "keyboard": "키보드",
    "cell phone": "휴대폰",
    "microwave": "전자레인지",
    "oven": "오븐",
    "toaster": "토스터",
    "refrigerator": "냉장고",
    "book": "책",
    "clock": "시계",
    "vase": "화병",
    "scissors": "가위",
    "bottle": "병",
    "cup": "컵",
    "bowl": "그릇",
}


def get_model():
    global _model

    if _model is None:
        _model = YOLO("yolo11n.pt")

    return _model


def normalize_label(label):
    return LABEL_MAP.get(label, label.replace(" ", "_"))


def analyze_product_image(image_path):
    model = get_model()

    results = model.predict(
        source=image_path,
        conf=0.25,
        verbose=False,
    )

    hashtags = []

    for result in results:
        if result.boxes is None:
            continue

        for class_id in result.boxes.cls.tolist():
            label = result.names[int(class_id)]
            hashtag = normalize_label(label)

            if hashtag not in hashtags:
                hashtags.append(hashtag)

    return hashtags