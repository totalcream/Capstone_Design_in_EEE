from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.ensemble import EnsembleRetriever
import re
from transformers import AutoProcessor, Gemma3ForConditionalGeneration
import torch
from langchain_text_splitters import TokenTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from pathlib import Path
from PIL import Image

#텍스트 문서 로드
file_path = "./data/회로이론.md"
try:
    with open(file_path, "r", encoding="utf-8") as f: docs = f.read()
except Exception as e: print(f"파일 읽기 오류: {e}"); raise

#토큰단위로 자르기
text_splitter = TokenTextSplitter(chunk_size=300, chunk_overlap=50)
split_docs = text_splitter.create_documents([docs])

# 텍스트 임베딩 & 벡터스토어 & 검색기
embeddings = HuggingFaceEmbeddings(model_name="nlpai-lab/KoE5")
vectorstore = Chroma.from_documents(split_docs, embeddings)

bm25_retriever = BM25Retriever.from_documents(split_docs)
bm25_retriever.k = 1
faiss_retriever = FAISS.from_documents(split_docs, embeddings).as_retriever(search_kwargs={"k":1})
ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever], weights=[0.3, 0.7])


#이미지 로드
image_dir = Path("tmp")
image_uris = sorted([str(p) for p in image_dir.glob("*.png")])

#이미지 임베딩 & 벡터스토어 & 검색기
image_embedding_function = OpenCLIPEmbeddings(
    model_name="ViT-H-14-378-quickgelu", checkpoint="dfn5b"
)

# DB 생성
image_db = Chroma(
    collection_name="multimodal",
    embedding_function=image_embedding_function,
)

# 이미지 추가
image_metadatas = [{"uri": uri} for uri in image_uris]
image_db.add_images(
    uris=image_uris,
    metadatas=image_metadatas
)

# Image Retriever 생성
image_retriever = image_db.as_retriever(search_kwargs={"k": 1})

# 프롬프트 빌더
def build_keyword_messages(x: dict) -> str:
    return (
        "<start_of_turn>user\n"
        "전기전자공학 전문가로서, 다음 문서에서 기술 중심 키워드 5개만 리스트로 추출하세요.\n"
        "일반 용어는 제외하고, 출력은 반드시 [\"키워드1\",\"키워드2\",...] 형식으로 해주세요.\n\n"
        f"[문서]\n{x['context']}\n"
        f"[이미지]\n{x['image']}\n"
        "<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

def build_summary_messages(x: dict) -> str:
    return (
        "<start_of_turn>user\n"
        f"전기전자공학 요약 전문가로서, '{x['keyword']}'에 대해 5문장 이내로 요약하세요. 반복은 피하고, 용어 번역은 하지 마세요.한글로 작성하세요.\n\n"
        f"[문서]\n{x['context']}\n"
        f"[이미지]\n{x['image']}\n"
        "<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

def build_quiz_messages(x: dict) -> str:
    return (
        "<start_of_turn>user\n"
        f"전자공학 시험 문제 출제자입니다. '{x['keyword']}' 관련 4지선다 문제 1개를 아래 형식으로 생성하세요. 한글로 작성하세요.\n"
        "문제: ...\n1) ...\n정답: 번호\n\n"
        f"[문서]\n{x['context']}\n"
        f"[이미지]\n{x['image']}\n"
        "<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

# llm 모델 설정
model_path = "C:/Users/user/PycharmProjects/PythonProject/cache/gemma-3-4b-it-safetensors"
model = Gemma3ForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.bfloat16, device_map="auto").eval()
processor = AutoProcessor.from_pretrained(model_path)

def run_gemma_chat(formatted_prompt):
    inputs = processor.tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[-1]
    with torch.inference_mode():
        outputs = model.generate(**inputs, max_new_tokens=1024)
    return processor.decode(outputs[0][input_len:], skip_special_tokens=True)


# 체인 구성 부분
keywords_chain = (
    RunnablePassthrough.assign(
        context=lambda x: "\n".join([d.page_content for d in ensemble_retriever.invoke(x["input"])]),
        image=lambda x: Image.open(image_retriever.invoke(x["input"])[0].metadata['uri']).convert("RGB")
    )
    | build_keyword_messages
    | run_gemma_chat
)

summary_chain = (
    RunnablePassthrough.assign(
        context=lambda x: "\n".join([d.page_content for d in ensemble_retriever.invoke(x["keyword"])]),
        image=lambda x: Image.open(image_retriever.invoke(x["keyword"])[0].metadata['uri']).convert("RGB"),
        keyword=lambda x: x["keyword"]
    )
    | build_summary_messages
    | run_gemma_chat
)

quiz_chain = (
    RunnablePassthrough.assign(
        context=lambda x: "\n".join([d.page_content for d in ensemble_retriever.invoke(x["keyword"])]),
        image=lambda x: Image.open(image_retriever.invoke(x["keyword"])[0].metadata['uri']).convert("RGB"),
        keyword=lambda x: x["keyword"]
    )
    | build_quiz_messages
    | run_gemma_chat
)

# 결과 저장 함수
def save_results_to_file(keywords, summary_results, quiz_results, filename="study_results.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# 추출된 핵심 키워드\n\n")
            for keyword in keywords: f.write(f"- {keyword}\n")
            f.write("\n---\n\n# 키워드별 요약\n\n")
            for kw, summary in summary_results: f.write(f"## {kw}\n{summary}\n\n")
            f.write("---\n\n# 학습 확인 퀴즈\n\n")
            for kw, quiz in quiz_results: f.write(f"## {kw} 관련 문제\n{quiz}\n\n")
    except Exception as e: print(f"파일 저장 오류: {e}")


try:
    # 키워드 추출 (입력 형식 수정)
    keywords_str = keywords_chain.invoke({"input": "강의 핵심 키워드 추출"})
    keywords = list(dict.fromkeys(re.findall(r"[\w가-힣]+", keywords_str)))[:5]
    print("추출된 키워드:", keywords)

    # 요약 및 퀴즈 생성
    summary_results = []
    quiz_results = []
    for keyword in keywords:
        summary = summary_chain.invoke({"keyword": keyword})
        quiz = quiz_chain.invoke({"keyword": keyword})
        summary_results.append((keyword, summary))
        quiz_results.append((keyword, quiz))

    # 결과 출력
    print("\n[키워드별 요약]")
    for kw, summary in summary_results: print(f"- {kw}: {summary}")
    print("\n[키워드별 퀴즈]")
    for kw, quiz in quiz_results: print(f"- {kw}: {quiz}")
    save_results_to_file(keywords, summary_results, quiz_results)

except Exception as e: print(f"오류 발생: {e}")
finally:
    if torch.cuda.is_available(): torch.cuda.empty_cache()
    if 'model' in locals(): del model