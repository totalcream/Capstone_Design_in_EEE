import pandas as pd
import glob # 파일 경로 패턴 매칭을 위한 라이브러리
import os   # 운영체제 관련 기능을 위한 라이브러리

def get_csv_file_paths(folder_path: str) -> list:
    """
    지정된 폴더 내의 모든 CSV 파일 경로를 리스트로 반환합니다.

    Args:
        folder_path (str): CSV 파일들이 있는 폴더의 경로.

    Returns:
        list: CSV 파일 경로들의 리스트. 파일이 없으면 빈 리스트를 반환.
    """
    if not os.path.isdir(folder_path):
        print(f"오류: '{folder_path}' 폴더를 찾을 수 없습니다.")
        return []

    # os.path.join을 사용하여 운영체제에 독립적인 경로를 만듭니다.
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

    if not csv_files:
        print(f"경고: '{folder_path}' 폴더에서 CSV 파일을 찾지 못했습니다.")
    else:
        print(f"\n'{folder_path}' 폴더에서 다음 CSV 파일들을 찾았습니다:")
        for f_path in csv_files:
            print(f" - {f_path}")
    return csv_files

def combine_csv_files(file_paths: list) -> pd.DataFrame | None:
    """
    주어진 파일 경로 리스트의 CSV 파일들을 읽어 하나의 DataFrame으로 합칩니다.

    Args:
        file_paths (list): CSV 파일 경로들의 리스트.

    Returns:
        pd.DataFrame | None: 합쳐진 DataFrame. 파일 읽기 실패 시 None 반환.
    """
    all_dataframes = []
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            all_dataframes.append(df)
            print(f"'{file_path}' 파일을 성공적으로 읽었습니다.")
        except Exception as e:
            print(f"'{file_path}' 파일을 읽는 중 오류 발생: {e}")

    if not all_dataframes:
        return None

    try:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print("\n모든 CSV 파일이 성공적으로 합쳐졌습니다.")
        return combined_df
    except Exception as e:
        print(f"DataFrame을 합치는 중 오류 발생: {e}")
        return None

def save_dataframe_to_csv(df: pd.DataFrame, output_folder: str, filename: str) -> bool:
    """
    DataFrame을 지정된 폴더에 CSV 파일로 저장합니다.

    Args:
        df (pd.DataFrame): 저장할 DataFrame.
        output_folder (str): 파일을 저장할 폴더 경로.
        filename (str): 저장할 파일의 이름 (확장자 포함).

    Returns:
        bool: 저장 성공 시 True, 실패 시 False.
    """
    if not os.path.isdir(output_folder):
        try:
            os.makedirs(output_folder, exist_ok=True) # 폴더가 없으면 생성
            print(f"'{output_folder}' 폴더를 생성했습니다.")
        except Exception as e:
            print(f"'{output_folder}' 폴더 생성 중 오류 발생: {e}")
            return False

    output_path = os.path.join(output_folder, filename)
    try:
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n합쳐진 데이터가 '{output_path}' 파일로 성공적으로 저장되었습니다.")
        return True
    except Exception as e:
        print(f"\n'{output_path}' 파일로 저장 중 오류 발생: {e}")
        return False

def main():
    """
    메인 실행 함수.
    """
    # 현재 작업 디렉토리 확인
    current_working_directory = os.getcwd()
    print(f"현재 작업 디렉토리: {current_working_directory}")

    # CSV 파일들이 저장된 'data' 폴더 경로 설정
    data_folder_name = 'data' # 현재 작업 디렉토리 내의 'data' 폴더

    # 1. CSV 파일 경로 가져오기
    csv_file_list = get_csv_file_paths(data_folder_name)

    if not csv_file_list:
        print("처리할 CSV 파일이 없습니다. 스크립트를 종료합니다.")
        return

    # 2. CSV 파일들 합치기
    combined_dataframe = combine_csv_files(csv_file_list)

    if combined_dataframe is None:
        print("CSV 파일들을 합치는 데 실패했습니다. 스크립트를 종료합니다.")
        return

    # 합쳐진 DataFrame 정보 출력 (선택 사항)
    print("\n--- 합쳐진 DataFrame (상위 5개 행) ---")
    print(combined_dataframe.head())
    print("\n--- 합쳐진 DataFrame 정보 ---")
    combined_dataframe.info()
    if '과목명' in combined_dataframe.columns:
        print("\n--- 포함된 과목명 종류 ---")
        print(combined_dataframe['과목명'].unique())

    # 3. 합쳐진 DataFrame을 CSV 파일로 저장
    output_filename = 'combined_all_questions.csv' # 저장할 파일명
    save_successful = save_dataframe_to_csv(combined_dataframe, data_folder_name, output_filename)

    if save_successful:
        print(f"\n작업 완료. 합쳐진 파일은 '{os.path.join(data_folder_name, output_filename)}'에 저장되었습니다.")
    else:
        print("\n파일 저장에 실패했습니다.")

if __name__ == "__main__":
    main()