// src/App.js
import React, { useState } from "react";
import axios from "axios";

const subjects = [
  "객체지향프로그래밍","디지털논리회로","디지털시스템설계","멀티미디어",
  "자료구조론","컴퓨터네트워크","회로이론1","기계학습개론",
  "데이터베이스설계","신호및시스템","알고리즘설계","전자기학1",
  "정보보호론","확률변수"
];

const API = process.env.REACT_APP_API_URL;

function App() {
  const [selectedSubject, setSelectedSubject] = useState("");
  const [sessionId, setSessionId]           = useState(null);
  const [selectedIdx, setSelectedIdx]       = useState(null);
  const [modelA, setModelA]                 = useState(null);
  const [modelB, setModelB]                 = useState(null);
  const [selectedModel, setSelectedModel]   = useState("");
  const [feedback, setFeedback]             = useState("");
  const [loading, setLoading]               = useState(false);
  const [error, setError]                   = useState("");
  const [quizExhausted, setQuizExhausted]   = useState(false);

  const handleSubjectSelect = async (subject) => {
    setLoading(true);
    setError("");
    setQuizExhausted(false);
    try {
      const res = await axios.post(`${API}/compare_models/`, { subject });
      setSelectedSubject(subject);
      setSessionId(res.data.session_id);
      setSelectedIdx(res.data.idx);
      setModelA(res.data.model_a);
      setModelB(res.data.model_b);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 404) {
        setSelectedSubject("");
        setQuizExhausted(true);
        setError("");
      } else {
        setError("문제 생성에 실패했습니다.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleModelSelect = async (which) => {
    if (!sessionId || selectedIdx === null) return;
    setLoading(true);
    setError("");
    try {
      await axios.post(`${API}/save_selection/`, {
        session_id: sessionId,
        subject: selectedSubject,
        idx: selectedIdx,
        selected_model: which
      });
      setSelectedModel(which);
    } catch (err) {
      console.error(err);
      setError("모델 선택 저장에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!sessionId) return;
    setLoading(true);
    setError("");
    try {
      await axios.post(`${API}/submit_feedback/`, {
        session_id: sessionId,
        feedback
      });
      alert("피드백이 성공적으로 저장되었습니다!");
    } catch (err) {
      console.error(err);
      setError("피드백 제출에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App" style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1>LLM Quiz Comparison</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {loading && <p>로딩중...</p>}

      {quizExhausted && !loading && (
        <section style={{ marginTop: 32 }}>
          <h2 style={{ color: "orange" }}>📛 문제가 소진되었습니다.</h2>
          <p style={{ color: "#ddd" }}>선택한 과목의 모든 문제가 이미 사용되었습니다.</p>
          <button
            onClick={() => {
              setSelectedSubject("");
              setQuizExhausted(false);
              setError("");
            }}
            style={{ marginTop: 16, padding: "10px 20px", background: "#444", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}
          >
            과목 선택으로 돌아가기
          </button>
        </section>
      )}

      {!selectedSubject && !quizExhausted && !loading && (
        <section>
          <h2>🔍 과목을 선택하세요</h2>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
            {subjects.map(subj => (
              <button
                key={subj}
                onClick={() => handleSubjectSelect(subj)}
                style={{ padding: "8px 16px", margin: 4, backgroundColor: "#444", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}
              >
                {subj}
              </button>
            ))}
          </div>
        </section>
      )}

      {selectedSubject && modelA && modelB && !selectedModel && !loading && (
        <section style={{ marginTop: 24 }}>
          <button
            onClick={() => {
              setSelectedSubject("");
              setModelA(null);
              setModelB(null);
              setSessionId(null);
              setSelectedIdx(null);
            }}
            style={{ marginBottom: 12, background: "transparent", border: "none", color: "#61dafb", cursor: "pointer" }}
          >
            ⬅️ 과목 선택으로 돌아가기
          </button>

          <div style={{ display: "flex", gap: 16 }}>
            {[{ label: "A", data: modelA }, { label: "B", data: modelB }].map(({ label, data }) => (
              <div key={label} style={{ flex: 1, background: "#333", padding: 16, borderRadius: 6, position: "relative" }}>
                <div style={{ position: "absolute", top: -10, left: 16, background: "#333", padding: "2px 8px", fontWeight: "bold", borderRadius: 4 }}>
                  Model {label}
                </div>
                <p style={{ color: "#ddd" }}>{data.question}</p>
                {data.choices.map((c, i) => (
                  <p key={i} style={{ color: "#ccc" }}>{i + 1}. {c}</p>
                ))}
                <p style={{ color: "#66ff66", marginTop: 8 }}><strong>정답:</strong> {data.answer}</p>
                <div style={{ background: "#222", color: "#99ccff", padding: "8px", marginTop: "4px", borderRadius: "4px", maxHeight: "100px", overflowY: "auto", whiteSpace: "pre-wrap" }}>
                  <strong>해설:</strong> {data.explanation}
                </div>
                <button
                  onClick={() => handleModelSelect(label)}
                  style={{ marginTop: 12, width: "100%", padding: 10, background: "#4caf50", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}
                >
                  Select Model {label}
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {selectedModel && !loading && (
        <section style={{ marginTop: 32 }}>
          <div style={{ marginBottom: 12 }}>
            <button onClick={() => setSelectedModel("")} style={{ marginRight: 12, background: "transparent", border: "none", color: "#61dafb", cursor: "pointer" }}>
              ⬅️ 비교 화면으로 돌아가기
            </button>
            <button onClick={() => {
              setSelectedSubject("");
              setSelectedModel("");
              setModelA(null);
              setModelB(null);
              setSessionId(null);
              setSelectedIdx(null);
              setFeedback("");
            }} style={{ background: "transparent", border: "none", color: "#61dafb", cursor: "pointer" }}>
              🏠 과목 선택으로 돌아가기
            </button>
          </div>
          <h2>✅ 선택된 모델: Model {selectedModel}</h2>
          <p style={{ color: "#ddd" }}>
            문제: {(selectedModel === "A" ? modelA.question : modelB.question)}
          </p>
          {(selectedModel === "A" ? modelA.choices : modelB.choices).map((c, i) => (
            <p key={i} style={{ color: "#ccc" }}>{i + 1}) {c}</p>
          ))}
          <p style={{ color: "#9f9", marginTop: 12 }}>
            정답: {(selectedModel === "A" ? modelA.answer : modelB.answer)}
          </p>
          <p style={{ color: "#bbb" }}>
            해설: {(selectedModel === "A" ? modelA.explanation : modelB.explanation)}
          </p>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="추가 피드백을 입력하세요"
            style={{ width: "100%", height: 100, marginTop: 12, padding: 10, borderRadius: 4, border: "1px solid #555", background: "#222", color: "#fff" }}
          />
          <button
            onClick={handleFeedbackSubmit}
            style={{ marginTop: 12, padding: "10px 20px", background: "#4caf50", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}
          >
            피드백 제출
          </button>
        </section>
      )}
    </div>
  );
}

export default App;
