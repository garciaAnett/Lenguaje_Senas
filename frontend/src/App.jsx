import { useRef, useState } from 'react';
import CameraView from './components/CameraView';
import PredictionPanel from './components/PredictionPanel';
import HealthStatus from './components/HealthStatus';
import DatasetCapture from './components/DatasetCapture';
import { predict } from './api/mockApi';
import './App.css';

export default function App() {
  const cameraRef = useRef(null);
  const [mode, setMode] = useState('traduccion'); // 'traduccion' | 'dataset'
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  async function handleCapture(blob) {
    setLoading(true);
    setResult(null);
    const data = await predict(blob);
    setResult(data);
    setHistory(prev => [{ ...data, ts: new Date().toLocaleTimeString() }, ...prev].slice(0, 10));
    setLoading(false);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Lenguaje de Señas</h1>
        <p>Traducción en tiempo real · MVP Emergentes II</p>
        <div className="mode-tabs">
          <button
            className={`mode-tab ${mode === 'traduccion' ? 'active' : ''}`}
            onClick={() => setMode('traduccion')}
          >
            Traducción
          </button>
          <button
            className={`mode-tab ${mode === 'dataset' ? 'active' : ''}`}
            onClick={() => setMode('dataset')}
          >
            Grabar Dataset
          </button>
        </div>
        <HealthStatus />
      </header>

      {mode === 'traduccion' ? (
        <main className="app-main">
          <section className="camera-section">
            <h2>Cámara</h2>
            <CameraView ref={cameraRef} onCapture={handleCapture} />
          </section>

          <section className="result-section">
            <h2>Traducción</h2>
            <PredictionPanel result={result} loading={loading} />

            {history.length > 0 && (
              <div className="history">
                <h3>Historial reciente</h3>
                <ul>
                  {history.map((item, i) => (
                    <li key={i}>
                      <span className="hist-word">{item.palabra}</span>
                      <span className="hist-conf">{Math.round(item.confianza * 100)}%</span>
                      <span className="hist-time">{item.ts}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        </main>
      ) : (
        <main className="app-main-full">
          <DatasetCapture />
        </main>
      )}

      <footer className="app-footer">
        <p>Sprint 2 — Anett Garcia · Rodrigo Villarroel · Emergentes II 2026</p>
      </footer>
    </div>
  );
}
