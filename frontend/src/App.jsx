import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [solution, setSolution] = useState("");
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load and configure MathJax
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML";
    script.async = true;
    document.head.appendChild(script);

    script.onload = () => {
      window.MathJax.Hub.Config({
        tex2jax: {
          inlineMath: [["$", "$"], ["\\(", "\\)"]],
          displayMath: [["$$", "$$"], ["\\[", "\\]"]],
          processEscapes: true
        },
        showProcessingMessages: false,
        messageStyle: "none"
      });
      // Initial typesetting
      window.MathJax.Hub.Queue(["Typeset", window.MathJax.Hub]);
    };

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  const handleSolve = async () => {
    setLoading(true);
    setSolution("");
    setSteps([]);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/api/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      if (res.ok) {
        setSolution(data.solution || "");
        setSteps(data.steps || []);
        // Reprocess MathJax after state update
        if (window.MathJax) {
          setTimeout(() => {
            window.MathJax.Hub.Queue(["Typeset", window.MathJax.Hub]);
          }, 100); // Delay to ensure DOM updates
        }
      } else {
        setError(data.detail || "Something went wrong.");
      }
    } catch (err) {
      setError("Failed to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h2>Journey To Calculus Assistant</h2>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Enter an algebra problem (e.g., 2x + 3 = 7)"
      />
      <button onClick={handleSolve} disabled={loading}>
        {loading ? "Solving..." : "Solve"}
      </button>

      {solution && (
        <div className="result">
          <strong>Solution:</strong>{" "}
          {solution.includes("$") && !solution.includes("Error") ? (
            <span dangerouslySetInnerHTML={{ __html: solution }} />
          ) : (
            solution || "No solution"
          )}
          {steps.length > 0 && (
            <div className="steps">
              <strong>Steps:</strong>
              <ol>
                {steps.map((step, index) => (
                  <li key={index}>
                    {step.includes("$") && !step.includes("Error") ? (
                      <span dangerouslySetInnerHTML={{ __html: step }} />
                    ) : (
                      step || "No step available"
                    )}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}

export default App;