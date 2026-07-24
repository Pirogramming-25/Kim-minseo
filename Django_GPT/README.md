# Django_GPT

Django와 Hugging Face `pipeline()`을 활용한 영어 텍스트 AI 분석 웹 서비스입니다.

## 1. 주요 기능

- 감정 분석
- 문서 요약
- 유해 표현 분석
- 고객 피드백 복합 분석
- 로그인 기반 접근 제한
- 사용자별 실행 기록 저장
- 최근 기록 5개 출력
- 복합 분석 재생성

## 2. 실행 방법

```bash
git clone <Repository URL>
cd Django_GPT

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`.env` 파일:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
HF_TOKEN=
```

## 3. 사용 모델

### 감정 분석

- Model ID: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Task: `text-classification`
- 입력 언어: 영어
- 출력: `negative`, `neutral`, `positive` 및 점수
- 라이선스: CC-BY-4.0

### 문서 요약

- Model ID: `sshleifer/distilbart-cnn-6-6`
- Task: `summarization`
- 입력 언어: 영어
- 출력: 영어 요약문
- 라이선스: 모델 카드 별도 표기 없음

### 유해 표현 분석

- Model ID: `unitary/toxic-bert`
- Task: `text-classification`
- 입력 언어: 영어
- 출력:
  - `toxic`
  - `severe_toxic`
  - `obscene`
  - `threat`
  - `insult`
  - `identity_hate`
- 라이선스: Apache-2.0

## 4. URL 및 접근 권한

| URL | 기능 | 접근 권한 |
| --- | --- | --- |
| `/sentiment/` | 감정 분석 | 비로그인 허용 |
| `/summarize/` | 문서 요약 | 로그인 필요 |
| `/moderate/` | 유해 표현 분석 | 로그인 필요 |
| `/combo/` | 복합 분석 | 로그인 필요 |

## 5. 로그인 제한

비로그인 사용자가 제한 페이지에 접근하면:

```text
로그인 페이지 이동
→ "로그인 후 이용해주세요" Alert
→ 로그인
→ 기존 페이지 복귀
```

Custom Decorator를 사용해 직접 URL 접근도 서버에서 제한합니다.

## 6. 실행 기록

로그인 사용자의 실행 결과를 `InferenceHistory`에 저장합니다.

- 사용자별 기록 분리
- 기능별 기록 분리
- 최신 기록부터 출력
- 화면에는 최근 5개만 표시

비로그인 사용자의 감정 분석 기록은 DB에 저장하지 않고 JavaScript 배열에서만 관리하므로 새로고침하면 초기화됩니다.

## 7. 복합 분석

처리 순서:

```text
사용자 원문
→ 문서 요약
→ 생성된 요약문 감정 분석
→ 생성된 요약문 유해 표현 분석
→ 통합 결과 출력
```

재생성 버튼을 누르면 동일한 원문으로 전체 Pipeline을 다시 실행하며, 결과를 새로운 DB 기록으로 저장합니다.

## 8. 주요 구현 내용

- 모델 Service 계층 분리
- `lru_cache` 기반 Lazy Loading
- Pipeline 객체 재사용
- CUDA / MPS / CPU Device 분기
- Django View 서버 입력 검증
- CSRF 보호
- 처리 중 UI
- 내부 오류 및 Traceback 미노출
- `.env` 기반 Token 관리

## 9. 프로젝트 구조

```text
Django_GPT/
├── config/
├── my_gpt/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── decorators.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```