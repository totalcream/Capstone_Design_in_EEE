import pandas as pd
from datasets import Dataset, DatasetDict  # DatasetDict는 현재 코드에서 직접 사용되진 않지만, 일반적인 임포트
import os


# 전역 스코프에 함수 정의
def create_alpaca_formatted_text(instruction: str, response: str, input_text: str = "") -> str:
    # ... (이 함수 내용은 이전과 동일) ...
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


# 전역 스코프에 함수 정의
def format_ox_quiz_sample(row: pd.Series) -> str | None:
    # ... (이 함수 내용은 이전과 동일) ...
    try:
        subject = row.get('과목명', 'N/A')
        question = row.get('질문', '')
        answer = str(row.get('정답', ''))  # 정답이 숫자일 수도 있으므로 문자열로 변환
        explanation = row.get('해설', '')

        if not question or not answer:  # 필수 정보 누락 시
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
        # ---!!! 중요 수정 지점 !!!---
        # 객관식 문제의 내용도 '질문' 컬럼에서 가져오도록 수정합니다.
        question = row.get('질문', '')  # '문제' 대신 '질문' 사용

        options = []
        for i in range(1, 6):
            option_text = row.get(f'보기{i}')
            # pd.notna()는 NaN을 체크하고, str(option_text).strip()은 빈 문자열이나 공백만 있는 경우를 체크
            if pd.notna(option_text) and str(option_text).strip():
                options.append(f"{i}: {str(option_text).strip()}")  # strip()을 추가하여 앞뒤 공백 제거

        answer_num = str(row.get('정답', ''))  # 정답이 숫자일 수 있으므로 문자열로
        explanation = row.get('해설', '')

        # 필수 정보 누락 시 (특히 options 리스트가 비어있으면 안 됨)
        if not question or not options or not answer_num:
            # 누락 원인 로깅 (필요시 주석 해제)
            # print(f"MC 누락: Q='{question}', Opts_count={len(options)}, Ans='{answer_num}', Row_idx={row.name if hasattr(row, 'name') else 'N/A'}")
            return None

        instruction = f"다음은 [{subject}] 과목의 객관식 문제입니다. 문제와 보기를 읽고 정답 번호와 해설을 제공해주세요."

        options_str = "\n".join(options)
        input_text = f"문제: {question}\n보기:\n{options_str}"
        # 정답 번호가 보기 텍스트의 일부로 포함되지 않도록 주의 (예: "정답: 2. 랜덤변수는 ...")
        # 현재는 정답 번호만 출력하고, 해설에서 상세 내용을 제공
        response = f"정답: {answer_num}\n해설: {explanation}"

        return create_alpaca_formatted_text(instruction, response, input_text)
    except Exception as e:
        print(f"Error formatting multiple choice sample: {e} - Row: {row.to_dict()}")
        return None


# load_and_process_csv 함수는 이전 디버깅 버전과 동일하게 사용하면 됩니다.
# 해당 함수 내에서 객관식 문제를 처리할 때 아래와 같이 되어 있는지 확인합니다.
# (이 부분은 이미 이전 디버깅 코드에서 올바르게 되어 있을 것입니다)
# elif problem_type == '객관식':
#     original_question_mc = row.get('질문', '') # <--- 이 부분이 '질문'으로 되어 있는지 확인
#     ...
#     if not original_question_mc or not original_options_mc or not original_answer_mc:
#         skipped_mc_missing_data_count += 1
#     else:
#         formatted_sample = format_multiple_choice_sample(row)

# 이 함수는 위에서 정의된 format_ox_quiz_sample 등을 호출
def load_and_process_csv(csv_file_path: str) -> Dataset | None:
    # ... (이 함수 내용은 이전 디버깅 버전과 거의 동일) ...
    if not os.path.exists(csv_file_path):
        print(f"오류: CSV 파일 '{csv_file_path}'을(를) 찾을 수 없습니다.")
        return None

    try:
        df = pd.read_csv(csv_file_path)
        print(f"'{csv_file_path}' 파일을 성공적으로 로드했습니다. 총 {len(df)}개의 데이터.")
    except Exception as e:
        print(f"오류: CSV 파일 '{csv_file_path}'을(를) 로드하는 중 오류 발생: {e}")
        return None

    for i in range(1, 6):
        col_name = f'보기{i}'
        if col_name in df.columns:
            df[col_name] = df[col_name].astype(str)

    skipped_unknown_type_count = 0
    skipped_ox_missing_data_count = 0
    skipped_mc_missing_data_count = 0
    processed_count = 0

    print("\n--- '문제유형' 컬럼 분석 ---")
    if '문제유형' in df.columns:
        print(df['문제유형'].value_counts(dropna=False))
    else:
        print("'문제유형' 컬럼이 CSV 파일에 없습니다.")
        return None

    formatted_texts = []
    for index, row in df.iterrows():
        problem_type = row.get('문제유형', '').strip()
        formatted_sample = None

        if problem_type == 'OX':
            original_question = row.get('질문', '')  # '질문' 컬럼 확인!
            original_answer = str(row.get('정답', ''))
            if not original_question or not original_answer:
                skipped_ox_missing_data_count += 1
            else:
                # 여기서 format_ox_quiz_sample 호출
                formatted_sample = format_ox_quiz_sample(row)  # <--- 이 호출이 가능해야 함

        elif problem_type == '객관식':
            original_question_mc = row.get('질문', '')
            original_options_mc = [row.get(f'보기{i}') for i in range(1, 6) if
                                   pd.notna(row.get(f'보기{i}')) and str(row.get(f'보기{i}')).strip()]
            original_answer_mc = str(row.get('정답', ''))
            if not original_question_mc or not original_options_mc or not original_answer_mc:
                skipped_mc_missing_data_count += 1
            else:
                # 여기서 format_multiple_choice_sample 호출
                formatted_sample = format_multiple_choice_sample(row)  # <--- 이 호출이 가능해야 함
        else:
            skipped_unknown_type_count += 1

        if formatted_sample:
            formatted_texts.append({"text": formatted_sample})
            processed_count += 1

    # ... (나머지 디버깅 출력 및 Dataset 생성 부분은 이전과 동일) ...
    print(f"\n--- 데이터 처리 요약 ---")
    print(f"총 로드된 행 수: {len(df)}")
    print(f"성공적으로 가공된 샘플 수: {processed_count}")
    print(f"누락 - 알 수 없는 문제 유형: {skipped_unknown_type_count}")
    print(f"누락 - OX 퀴즈 필수 데이터 부족: {skipped_ox_missing_data_count}")
    print(f"누락 - 객관식 퀴즈 필수 데이터 부족: {skipped_mc_missing_data_count}")
    total_skipped = skipped_unknown_type_count + skipped_ox_missing_data_count + skipped_mc_missing_data_count
    print(f"총 누락된 샘플 수: {total_skipped}")
    print(
        f"검증 (로드된 행 - 누락된 샘플 == 가공된 샘플): {len(df)} - {total_skipped} == {processed_count}  -> {len(df) - total_skipped == processed_count}")

    if not formatted_texts:
        print("가공된 데이터가 없습니다. 데이터 형식이나 내용을 확인해주세요.")
        return None

    hf_dataset = Dataset.from_list(formatted_texts)
    return hf_dataset


def main():
    # ... (main 함수 내용은 이전과 동일) ...
    base_dir = os.path.dirname(os.path.abspath(__file__))
    combined_csv_path = os.path.join('data', 'combined_all_questions.csv')  # 경로 확인 필요
    print(f"처리할 CSV 파일 경로: {combined_csv_path}")

    hf_dataset = load_and_process_csv(combined_csv_path)

    if hf_dataset:
        print("\n--- Hugging Face Dataset 정보 ---")
        print(hf_dataset)
        print("\n--- 데이터셋 샘플 (처음 3개) ---")
        for i in range(min(3, len(hf_dataset))):
            print(f"\n--- 샘플 {i + 1} ---")
            print(hf_dataset[i]['text'])
        output_dataset_path = os.path.join('data', 'prepared_finetuning_dataset_arrow')
        hf_dataset.save_to_disk(output_dataset_path)
        print(f"\n처리된 데이터셋이 Arrow 형식으로 '{output_dataset_path}'에 저장되었습니다.")


if __name__ == "__main__":
    main()