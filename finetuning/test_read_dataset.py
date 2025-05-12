from datasets import load_from_disk

saved_splits_directory = 'data/prepared_finetuning_dataset_splits_arrow'
loaded_dataset_dict = load_from_disk(saved_splits_directory)

# 이제 loaded_dataset_dict['train'], loaded_dataset_dict['validation'], loaded_dataset_dict['test'] 로 각 스플릿에 접근 가능
train_data = loaded_dataset_dict['train']
val_data = loaded_dataset_dict['validation']
test_data = loaded_dataset_dict['test']

print(loaded_dataset_dict)