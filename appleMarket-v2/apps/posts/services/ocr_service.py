import os
import re
import tempfile
from decimal import Decimal, InvalidOperation

import cv2
from paddleocr import PaddleOCR


_ocr = None


def get_ocr():
    global _ocr

    if _ocr is None:
        _ocr = PaddleOCR(
            use_angle_cls=True,
            lang="korean",
            use_gpu=False,
            show_log=False,
        )

    return _ocr


def preprocess_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("이미지를 읽을 수 없습니다.")

    height, width = image.shape[:2]
    longest_side = max(height, width)

    # 작은 이미지는 확대
    if longest_side < 1800:
        scale = 1800 / longest_side
        image = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    # 회색조 변환
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    # 노이즈 제거
    gray = cv2.bilateralFilter(
        gray,
        7,
        45,
        45,
    )

    # 글자와 배경 대비 강화
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    file_descriptor, processed_path = tempfile.mkstemp(
        suffix=".png"
    )
    os.close(file_descriptor)

    cv2.imwrite(
        processed_path,
        binary,
    )

    return processed_path


def extract_texts(result):
    texts = []

    if not result:
        return texts

    for page in result:
        # PaddleOCR 3.x 결과 형식
        if hasattr(page, "json"):
            data = page.json

            if callable(data):
                data = data()

            if isinstance(data, dict):
                page_data = data.get(
                    "res",
                    data,
                )

                texts.extend(
                    page_data.get(
                        "rec_texts",
                        [],
                    )
                )
                continue

        if isinstance(page, dict):
            page_data = page.get(
                "res",
                page,
            )

            texts.extend(
                page_data.get(
                    "rec_texts",
                    [],
                )
            )
            continue

        # PaddleOCR 2.x 결과 형식
        if isinstance(page, list):
            for line in page:
                if (
                    isinstance(line, (list, tuple))
                    and len(line) >= 2
                    and isinstance(
                        line[1],
                        (list, tuple),
                    )
                    and line[1]
                ):
                    texts.append(
                        str(line[1][0])
                    )

    return [
        str(text).strip()
        for text in texts
        if str(text).strip()
    ]


def run_ocr(image_path):
    result = get_ocr().ocr(
        image_path,
        cls=True,
    )

    return extract_texts(result)


def normalize_ocr_text(text):
    normalized = (
        str(text)
        .strip()
        .lower()
    )

    replacements = {
        "kca!": "kcal",
        "kca|": "kcal",
        "kca1": "kcal",
        "탄수화믈": "탄수화물",
        "단백짙": "단백질",
        "단백칠": "단백질",
        "포화지밤": "포화지방",
        "콜레스테볼": "콜레스테롤",
        "나트륭": "나트륨",
        "나트룸": "나트륨",
        "나트룹": "나트륨",
    }

    for before, after in replacements.items():
        normalized = normalized.replace(
            before,
            after,
        )

    return normalized


def extract_number(text):
    match = re.search(
        r"(?<!\d)"
        r"(\d+(?:[.,]\d+)?)"
        r"(?!\d)",
        text,
    )

    if not match:
        return None

    try:
        return Decimal(
            match.group(1).replace(
                ",",
                ".",
            )
        )
    except InvalidOperation:
        return None


def find_calories(tokens):
    normalized_tokens = [
        normalize_ocr_text(token)
        for token in tokens
    ]

    for index, token in enumerate(
        normalized_tokens
    ):
        # 같은 토큰에 "390 kcal"처럼 있는 경우
        if "kcal" in token:
            number = extract_number(token)

            if number is not None:
                return number.quantize(
                    Decimal("0.01")
                )

        # 숫자와 kcal가 분리된 경우
        if token == "kcal" and index > 0:
            number = extract_number(
                normalized_tokens[index - 1]
            )

            if number is not None:
                return number.quantize(
                    Decimal("0.01")
                )

    return None


def find_nutrient_value(
    tokens,
    keywords,
    excluded_keywords=None,
):
    excluded_keywords = excluded_keywords or []

    normalized_tokens = [
        normalize_ocr_text(token)
        for token in tokens
    ]

    nutrient_names = [
        "나트륨",
        "탄수화물",
        "당류",
        "식이섬유",
        "지방",
        "트랜스지방",
        "포화지방",
        "콜레스테롤",
        "단백질",
    ]

    for index, token in enumerate(normalized_tokens):
        if not any(keyword in token for keyword in keywords):
            continue

        if any(excluded in token for excluded in excluded_keywords):
            continue

        for next_index in range(
            index + 1,
            min(index + 8, len(normalized_tokens)),
        ):
            candidate = normalized_tokens[next_index]

            if any(
                nutrient in candidate
                for nutrient in nutrient_names
            ):
                break

            # 29g, 15g28%, 16g3%처럼
            # 값과 g, 퍼센트가 한 토큰에 붙은 경우
            gram_match = re.search(
                r"(\d+(?:[.,]\d+)?)\s*g",
                candidate,
            )

            if gram_match:
                amount_text = gram_match.group(1)
                amount = Decimal(
                    amount_text.replace(",", ".")
                )

                percent_match = re.search(
                    r"g\s*(\d+)\s*%",
                    candidate,
                )

                percent = (
                    Decimal(percent_match.group(1))
                    if percent_match
                    else None
                )

                # 지방 1.6g 3%가 16g3%로 인식된 경우
                if (
                    "지방" in keywords
                    and amount >= Decimal("10")
                    and percent is not None
                    and percent <= Decimal("5")
                ):
                    amount /= Decimal("10")

                return amount.quantize(
                    Decimal("0.01")
                )

            # 퍼센트만 있는 토큰은 함유량이 아님
            if "%" in candidate:
                continue

            number = extract_number(candidate)

            if number is None:
                continue

            next_token = (
                normalized_tokens[next_index + 1]
                if next_index + 1 < len(normalized_tokens)
                else ""
            )

            # 단백질 1g 2%가 '19', '2%'로 인식된 경우
            if (
                "단백질" in keywords
                and number >= Decimal("10")
                and "%" in next_token
            ):
                percent = extract_number(next_token)

                if (
                    percent is not None
                    and percent <= Decimal("5")
                    and str(candidate).endswith("9")
                ):
                    corrected = str(candidate)[:-1]

                    if corrected:
                        number = Decimal(corrected)

            nearby_tokens = normalized_tokens[
                max(index, next_index - 1):
                min(len(normalized_tokens), next_index + 2)
            ]

            nearby = " ".join(nearby_tokens)

            if "mg" in nearby:
                number /= Decimal("1000")

            return number.quantize(
                Decimal("0.01")
            )

    return None


def find_protein_fallback(tokens):
    normalized_tokens = [
        normalize_ocr_text(token)
        for token in tokens
    ]

    for index, token in enumerate(
        normalized_tokens
    ):
        if "단백질" not in token:
            continue

        for candidate in normalized_tokens[
            index + 1:index + 7
        ]:
            # 예: 실제 3g 7%가 OCR에서 38g7%로 인식된 경우
            merged_match = re.search(
                r"(\d+)g(\d+)%",
                candidate,
            )

            if merged_match:
                amount_text = merged_match.group(1)
                percent_text = merged_match.group(2)

                amount = Decimal(amount_text)
                percent = Decimal(percent_text)

                # 38g7% → 3g 7% 보정
                if (
                    amount >= 30
                    and percent <= 10
                    and amount_text.endswith("8")
                ):
                    corrected = amount_text[:-1]

                    if corrected:
                        amount = Decimal(corrected)

                return amount.quantize(
                    Decimal("0.01")
                )

            # 일반적인 3g 형식
            compact_match = re.search(
                r"(\d+(?:[.,]\d+)?)\s*g",
                candidate,
            )

            if compact_match:
                try:
                    return Decimal(
                        compact_match
                        .group(1)
                        .replace(",", ".")
                    ).quantize(
                        Decimal("0.01")
                    )
                except InvalidOperation:
                    continue

            number = extract_number(candidate)

            if (
                number is not None
                and "%" not in candidate
                and "mg" not in candidate
                and number <= Decimal("30")
            ):
                return number.quantize(
                    Decimal("0.01")
                )

    return None


def parse_nutrition(texts):
    calories = find_calories(texts)

    carbohydrate = find_nutrient_value(
        texts,
        keywords=[
            "탄수화물",
        ],
    )

    protein = find_nutrient_value(
        texts,
        keywords=[
            "단백질",
        ],
    )

    if protein is None:
        protein = find_protein_fallback(
            texts
        )

    fat = find_nutrient_value(
        texts,
        keywords=[
            "지방",
        ],
        excluded_keywords=[
            "트랜스지방",
            "포화지방",
        ],
    )

    return {
        "calories": (
            str(calories)
            if calories is not None
            else ""
        ),
        "carbohydrate": (
            str(carbohydrate)
            if carbohydrate is not None
            else ""
        ),
        "protein": (
            str(protein)
            if protein is not None
            else ""
        ),
        "fat": (
            str(fat)
            if fat is not None
            else ""
        ),
        "raw_text": texts,
    }


def analyze_nutrition_image(image_path):
    processed_path = preprocess_image(
        image_path
    )

    try:
        # 원본 이미지 OCR
        original_texts = run_ocr(
            image_path
        )

        # 전처리 이미지 OCR
        processed_texts = run_ocr(
            processed_path
        )

        # 두 결과를 합쳐 누락 가능성 감소
        texts = (
            original_texts
            + processed_texts
        )

        print(
            "원본 OCR 결과:",
            original_texts,
        )

        print(
            "전처리 OCR 결과:",
            processed_texts,
        )

        result = parse_nutrition(
            texts
        )

        if not any(
            result[key]
            for key in (
                "calories",
                "carbohydrate",
                "protein",
                "fat",
            )
        ):
            result["warning"] = (
                "영양성분을 충분히 "
                "인식하지 못했습니다. "
                "더 선명한 이미지를 "
                "사용하거나 직접 입력해주세요."
            )

        return result

    finally:
        if os.path.exists(
            processed_path
        ):
            os.remove(
                processed_path
            )