import pandas as pd

# 합치고 싶은 CSV 파일들의 경로 목록을 직접 지정합니다.
# 예시:
# file_paths = [
#     '/content/객체지향프로그래밍.csv',
#     '/content/자료구조.csv',
#     '/content/운영체제.csv'
# ]
# 현재 디렉토리에 있는 파일들을 예시로 사용합니다.
# 실제 파일명으로 수정해주세요.
file_paths = [
    '/finetuning/data/'
    '객체지향프로그래밍.csv', # 제공해주신 파일
    # '다른과목1.csv',
    # '다른과목2.csv'
]

# 각 CSV 파일을 읽어 DataFrame 리스트에 저장합니다.
all_dataframes = []
for file_path in file_paths:
    try:
        df = pd.read_csv(file_path)
        # 파일명을 기반으로 '출처파일' 컬럼을 추가할 수도 있습니다 (선택 사항).
        # import os
        # df['출처파일'] = os.path.basename(file_path)
        all_dataframes.append(df)
        print(f"'{file_path}' 파일을 성공적으로 읽었습니다.")
    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    except Exception as e:
        print(f"'{file_path}' 파일을 읽는 중 오류 발생: {e}")


# 모든 DataFrame을 하나로 합칩니다.
if all_dataframes:
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    # ignore_index=True 옵션은 기존 파일들의 인덱스를 무시하고 새로운 연속적인 인덱스를 부여합니다.

    print("\n모든 CSV 파일이 성공적으로 합쳐졌습니다.")

    # 합쳐진 DataFrame 확인 (처음 5개 행)
    print("\n--- 합쳐진 DataFrame (상위 5개 행) ---")
    print(combined_df.head())

    # 합쳐진 DataFrame 정보 확인
    print("\n--- 합쳐진 DataFrame 정보 ---")
    combined_df.info()

    # (선택 사항) 합쳐진 DataFrame을 새로운 CSV 파일로 저장
    # 저장 시 encoding을 'utf-8-sig'로 하면 Excel에서 한글 깨짐 없이 열 수 있습니다.
    # combined_df.to_csv('combined_subject_problems.csv', index=False, encoding='utf-8-sig')
    # print("\n합쳐진 데이터가 'combined_subject_problems.csv' 파일로 저장되었습니다.")
else:
    print("합칠 CSV 파일이 없거나 파일을 읽는 데 실패했습니다.")