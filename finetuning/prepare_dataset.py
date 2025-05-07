import pandas as pd
from datasets import Dataset, DatasetDict
import os

def create_alpaca_formatted_text(instruction: str, response: str, input_text: str = "") -> str:
    """
    Alpaca 스타일의 프롬프트를 생성합니다.
    입력이 없는 경우 (input_text=""), instruction-response 쌍을 만듭니다.
    """
    if input_text:
        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input_text}

### Response:
{response}"""
    else:
        return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
{response}"""

def format_ox_quiz_sample(row: pd.Series) -> str | None:
    """
    OX 퀴즈 데이터 행을 Alpaca 형식의 텍스트로 변환합니다.
    """
    try:
        subject = row.get('과목명', 'N/A')
        question = row.get('질문', '')
        answer = str(row.get('정답', '')) # 정답이 숫자일 수도 있으므로 문자열로 변환
        explanation = row.get('해설', '')

        if not question or not answer: # 필수 정보 누락 시
            return None

        instruction = f"다음은 [{subject}] 과목의 OX 퀴즈입니다. 주어진 질문에 대해 O 또는 X로 답하고, 그 이유를 간략히 설명해주세요."
        input_text = f"질문: {question}"
        response = f"정답: {answer}\n해설: {explanation}"

        return create_alpaca_formatted_text(instruction, response, input_text)
    except Exception as e:
        print(f"Error formatting OX quiz sample: {e} - Row: {row.to_dict()}")
        return None


def format_multiple_choice_sample(row: pd.Series) -> str | None:
    """
    객관식 퀴즈 데이터 행을 Alpaca 형식의 텍스트로 변환합니다.
    """
    try:
        subject = row.get('과목명', 'N/A')
        question = row.get('문제', '') # 객관식은 '문제' 컬럼 사용
        
        options = []
        for i in range(1, 6):
            option_text = row.get(f'보기{i}')
            if pd.notna(option_text) and str(option_text).strip(): # NaN이 아니고 빈 문자열이 아닐 경우
                options.append(f"{i}: {option_text}")
        
        # 정답이 숫자일 수 있으므로 문자열로 변환
        # CSV에서 정답이 "3" 과 같이 문자열로 저장되어 있다면 그대로 사용, 숫자라면 str() 처리
        answer_num = str(row.get('정답', ''))
        explanation = row.get('해설', '')

        if not question or not options or not answer_num: # 필수 정보 누락 시
            # print(f"Skipping row due to missing data (MC): Question: {question}, Options: {options}, Answer: {answer_num}")
            return None

        instruction = f"다음은 [{subject}] 과목의 객관식 문제입니다. 문제와 보기를 읽고 정답 번호와 해설을 제공해주세요."
        
        options_str = "\n".join(options)
        input_text = f"문제: {question}\n보기:\n{options_str}"
        response = f"정답: {answer_num}\n해설: {explanation}"
        
        return create_alpaca_formatted_text(instruction, response, input_text)
    except Exception as e:
        print(f"Error formatting multiple choice sample: {e} - Row: {row.to_dict()}")
        return None


def load_and_process_csv(csv_file_path: str) -> Dataset | None:
    """
    합쳐진 CSV 파일을 로드하고, 문제 유형에 맞게 가공하여 Hugging Face Dataset으로 변환합니다.
    """
    if not os.path.exists(csv_file_path):
        print(f"오류: CSV 파일 '{csv_file_path}'을(를) 찾을 수 없습니다.")
        return None

    try:
        df = pd.read_csv(csv_file_path)
        print(f"'{csv_file_path}' 파일을 성공적으로 로드했습니다. 총 {len(df)}개의 데이터.")
    except Exception as e:
        print(f"오류: CSV 파일 '{csv_file_path}'을(를) 로드하는 중 오류 발생: {e}")
        return None

    # 결측치가 많은 보기 컬럼을 미리 문자열로 변환 (오류 방지)
    for i in range(1, 6):
        col_name = f'보기{i}'
        if col_name in df.columns:
            df[col_name] = df[col_name].astype(str)


    formatted_texts = []
    for index, row in df.iterrows():
        problem_type = row.get('문제유형', '').strip()
        formatted_sample = None

        if problem_type == 'OX':
            # '질문' 컬럼을 사용하도록 수정 (제공된 이미지 기준)
            # OX 퀴즈의 경우 '문제' 컬럼을 '질문'으로 간주하는 경우가 많음. CSV 헤더에 따라 조정 필요.
            # 만약 CSV에 '문제'와 '질문' 컬럼이 모두 있다면, OX 퀴즈는 '질문'을 사용하고, 객관식은 '문제'를 사용.
            # 제공된 이미지에서는 OX 유형도 '질문' 컬럼에 내용이 있음.
            # 원본 CSV 파일 컬럼명이 "질문"인 경우:
            formatted_sample = format_ox_quiz_sample(row)

        elif problem_type == '객관식':
            formatted_sample = format_multiple_choice_sample(row)
        else:
            print(f"알 수 없는 문제 유형입니다: '{problem_type}' - 행 번호: {index}")

        if formatted_sample:
            formatted_texts.append({"text": formatted_sample})
        # else:
            # print(f"Skipping row {index} due to formatting error or missing data.")


    if not formatted_texts:
        print("가공된 데이터가 없습니다. 데이터 형식이나 내용을 확인해주세요.")
        return None

    print(f"총 {len(formatted_texts)}개의 샘플이 성공적으로 가공되었습니다.")
    # 리스트 오브 딕셔너리 형태를 Dataset으로 변환
    hf_dataset = Dataset.from_list(formatted_texts)
    return hf_dataset

def main():
    # `combined_all_questions.csv` 파일이 이전 스크립트에서 `data` 폴더에 저장되었다고 가정
    # 현재 스크립트가 `data` 폴더와 같은 레벨에 있다고 가정
    # 또는 `data` 폴더가 스크립트의 하위 폴더에 있다면 경로 수정 필요.
    
    # 예시: 스크립트가 프로젝트 루트에 있고, CSV 파일은 ./data/combined_all_questions.csv 에 있는 경우
    # data_folder = 'data'
    # combined_csv_filename = 'combined_all_questions.csv' # 이전 단계에서 생성된 파일명

    # 현재 디렉토리의 'data' 폴더 안에 있다고 가정
    # 만약 'prepare_dataset.py'가 'finetuning' 폴더에 있고,
    # CSV 파일이 'finetuning/data/combined_all_questions.csv'에 있다면 아래 경로 사용
    base_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트 파일이 있는 디렉토리
    
    # combined_csv_path = os.path.join(base_dir, 'data', 'combined_all_questions.csv')
    # 위 경로는 스크립트 파일 기준 하위 data 폴더를 의미함.
    # 만약 이전 스크립트가 `finetuning` 폴더에 `data` 폴더를 만들고 그 안에 저장했다면,
    # 그리고 이 스크립트도 `finetuning` 폴더에서 실행한다면:
    combined_csv_path = os.path.join('data', 'combined_all_questions.csv')


    print(f"처리할 CSV 파일 경로: {combined_csv_path}")

    hf_dataset = load_and_process_csv(combined_csv_path)

    if hf_dataset:
        print("\n--- Hugging Face Dataset 정보 ---")
        print(hf_dataset)

        # 데이터셋의 일부 내용 확인
        print("\n--- 데이터셋 샘플 (처음 3개) ---")
        for i in range(min(3, len(hf_dataset))):
            print(f"\n--- 샘플 {i+1} ---")
            print(hf_dataset[i]['text']) # 'text' 필드에 모든 내용이 담겨있음

        # (선택 사항) 데이터셋을 저장하거나 바로 SFTTrainer에 사용할 수 있음
        # 예: 데이터셋 저장
        # output_dataset_path = os.path.join('data', 'prepared_finetuning_dataset_arrow')
        # hf_dataset.save_to_disk(output_dataset_path)
        # print(f"\n처리된 데이터셋이 Arrow 형식으로 '{output_dataset_path}'에 저장되었습니다.")

        # 예: 학습/검증용으로 분할 (80% train, 20% test)
        # dataset_dict = hf_dataset.train_test_split(test_size=0.2, seed=42)
        # print("\n--- 분할된 데이터셋 정보 ---")
        # print(dataset_dict)
        # train_dataset = dataset_dict['train']
        # eval_dataset = dataset_dict['test']
        # print(f"학습 데이터셋 크기: {len(train_dataset)}")
        # print(f"검증 데이터셋 크기: {len(eval_dataset)}")


if __name__ == "__main__":
    main()