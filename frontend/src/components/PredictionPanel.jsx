export default function PredictionPanel({ result, loading }) {
  if (loading) {
    return (
      <div className="prediction-panel loading">
        <div className="spinner" />
        <p>Analizando seña...</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="prediction-panel empty">
        <p>Captura una seña para ver la traducción</p>
      </div>
    );
  }

  const percent = Math.round(result.confianza * 100);
  const barColor = percent >= 80 ? '#22c55e' : percent >= 60 ? '#f59e0b' : '#ef4444';

  return (
    <div className="prediction-panel result">
      {result.mock && <span className="mock-badge">MOCK</span>}
      <h2 className="predicted-word">{result.palabra}</h2>
      <p className="confidence-label">Confianza: <strong>{percent}%</strong></p>
      <div className="confidence-bar-track">
        <div className="confidence-bar-fill" style={{ width: `${percent}%`, background: barColor }} />
      </div>
    </div>
  );
}
