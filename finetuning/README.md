## 디렉토리 및 파일 설명 (finetuning)

### 1. `uv`
- **이 폴더는 uv로 관리되고 있습니다.**
- **python Ver. 3.11**

### 2. 사용법
- **data폴더를 생성 후 과목 별 csv파일을 넣는다.**
- **main.py 파일을 실행**
- ```bash
  uv run main.py

### 2. `main.py`
- **과목 별 csv파일을 하나로 합치는 파이썬 코드.**

### 2. `prepare_dataset.py`
- **HugingFace Datasets를 사용해서 arrow폴더 생성.**
- **`combined_all_questions.csv`사용**

### 3. `data/`
- **이 폴더는 `gitignore`됨.**
- **`train/`**: 모델 학습에 사용되는 데이터셋.
- **`validation/`**: 학습 중 모델 성능을 검증하기 위한 데이터셋.
- **`test/`**: 최종 모델 평가에 사용되는 데이터셋.

### 4. `models/`
- **`pretrained/`**: 사전 학습된 모델 파일 저장.
- **`fine_tuned/`**: 파인튜닝된 모델 파일 저장.

### 5. `README.md`
- 현재 문서로, 폴더 구조와 사용 방법에 대한 설명을 포함.