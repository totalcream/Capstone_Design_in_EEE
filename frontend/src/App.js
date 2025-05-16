// src/App.js
import React, { useState } from "react";

const subjects = [
  "객체지향프로그래밍","디지털논리회로","디지털시스템설계","멀티미디어",
  "자료구조론","컴퓨터네트워크","회로이론1","기계학습개론",
  "데이터베이스설계","신호및시스템","알고리즘설계","전자기학1",
  "정보보호론","확률변수"
];

function App() {
  const [selectedSubject, setSelectedSubject] = useState("");
  const [problemsA, setProblemsA]       = useState("");
  const [problemsB, setProblemsB]       = useState("");
  const [selectedModel, setSelectedModel]= useState("");
  const [feedback, setFeedback]         = useState("");

  // 과목 클릭만으로 바로 Mock 문제 생성
  const handleSubjectSelect = (subject) => {
    setSelectedSubject(subject);
    setProblemsA("");
    setProblemsB("");
    setSelectedModel("");
    setFeedback("");

    // 여기서 실제로는 백엔드 호출: axios.post("/compare_models/", { subject })
    // 지금은 Mock 데이터
    const mockQA = `문제 1: ${subject} 예시 문제?\n1) 보기 A\n2) 보기 B\n3) 보기 C\n4) 보기 D\n\n정답: 1)\n해설: ${subject} 예시 해설입니다.`;

    setProblemsA(mockQA);
    setProblemsB(mockQA);
  };

  // 모델 선택
  const handleModelSelect = (model) => {
    setSelectedModel(model);
  };

  return (
    <div className="App" style={{ padding: 20, fontFamily: "sans-serif" }}>
      {/* 1) 과목 버튼 */}
      {!selectedSubject && (
        <section>
          <h1>🔍 과목을 선택하세요</h1>
          <div style={{
            display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center"
          }}>
            {subjects.map(subj => (
              <button 
                key={subj} 
                onClick={() => handleSubjectSelect(subj)}
                style={{
                  padding: "8px 16px", 
                  margin: 4,
                  backgroundColor: "#444",
                  color: "#fff",
                  border: "none",
                  borderRadius: 4,
                  cursor: "pointer"
                }}
              >
                {subj}
              </button>
            ))}
          </div>
        </section>
      )}

      {/* 2) Model A/B 문제 표시 */}
      {selectedSubject && problemsA && problemsB && !selectedModel && (
        <section style={{ marginTop: 24 }}>
          <button
            onClick={() => setSelectedSubject("")}
            style={{
              marginBottom: 12,
              background: "transparent",
              border: "none",
              color: "#61dafb",
              cursor: "pointer"
            }}
          >
            ⬅️ 과목 선택으로 돌아가기
          </button>
          <div style={{ display: "flex", gap: 16 }}>
            {/* A */}
            <div style={{
              flex: 1,
              background: "#333",
              padding: 16,
              borderRadius: 6,
              position: "relative"
            }}>
              <div style={{
                position: "absolute",
                top: -10,
                left: 16,
                background: "#333",
                padding: "2px 8px",
                fontWeight: "bold",
                borderRadius: 4
              }}>Model A</div>
              <pre style={{
                whiteSpace: "pre-wrap",
                maxHeight: 300,
                overflowY: "auto",
                background: "#222",
                color: "#ddd",
                padding: 8,
                borderRadius: 4
              }}>
                {problemsA}
              </pre>
              <button 
                onClick={() => handleModelSelect("A")}
                style={{
                  marginTop: 12,
                  width: "100%",
                  padding: 10,
                  background: "#4caf50",
                  color: "#fff",
                  border: "none",
                  borderRadius: 4,
                  cursor: "pointer"
                }}
              >
                Select Model A
              </button>
            </div>

            {/* B */}
            <div style={{
              flex: 1,
              background: "#333",
              padding: 16,
              borderRadius: 6,
              position: "relative"
            }}>
              <div style={{
                position: "absolute",
                top: -10,
                left: 16,
                background: "#333",
                padding: "2px 8px",
                fontWeight: "bold",
                borderRadius: 4
              }}>Model B</div>
              <pre style={{
                whiteSpace: "pre-wrap",
                maxHeight: 300,
                overflowY: "auto",
                background: "#222",
                color: "#ddd",
                padding: 8,
                borderRadius: 4
              }}>
                {problemsB}
              </pre>
              <button 
                onClick={() => handleModelSelect("B")}
                style={{
                  marginTop: 12,
                  width: "100%",
                  padding: 10,
                  background: "#4caf50",
                  color: "#fff",
                  border: "none",
                  borderRadius: 4,
                  cursor: "pointer"
                }}
              >
                Select Model B
              </button>
            </div>
          </div>
        </section>
      )}

      {/* 3) 선택된 모델 응답 + 피드백 */}
      {selectedModel && (
        <section style={{ marginTop: 32 }}>
          <button
            onClick={() => setSelectedModel("")}
            style={{
              marginBottom: 12,
              background: "transparent",
              border: "none",
              color: "#61dafb",
              cursor: "pointer"
            }}
          >
            ⬅️ 문제 비교로 돌아가기
          </button>
          <h2>✅ 선택된 모델: Model {selectedModel}</h2>
          <pre style={{
            whiteSpace: "pre-wrap",
            background: "#222",
            color: "#ddd",
            padding: 12,
            borderRadius: 4,
            maxHeight: 200,
            overflowY: "auto"
          }}>
            {selectedModel === "A" ? problemsA : problemsB}
          </pre>
          <textarea
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            placeholder="추가 피드백을 입력하세요"
            style={{
              width: "100%",
              height: 100,
              marginTop: 12,
              padding: 10,
              borderRadius: 4,
              border: "1px solid #555",
              background: "#222",
              color: "#fff"
            }}
          />
          <button
            onClick={() => alert(`피드백 제출: ${feedback}`)}
            style={{
              marginTop: 12,
              padding: "10px 20px",
              background: "#4caf50",
              color: "#fff",
              border: "none",
              borderRadius: 4,
              cursor: "pointer"
            }}
          >
            피드백 제출
          </button>
        </section>
      )}
    </div>
  );
}

export default App;
