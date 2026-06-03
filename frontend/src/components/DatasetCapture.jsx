import { useEffect, useRef, useState } from 'react';
import { uploadClip, getDatasetStats } from '../api/mockApi';

export default function DatasetCapture() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const recorderRef = useRef(null);
  const chunksRef = useRef([]);

  const [palabra, setPalabra] = useState('');
  const [cameraOn, setCameraOn] = useState(false);
  const [recording, setRecording] = useState(false);
  const [countdown, setCountdown] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null); // null | 'uploading' | 'ok' | 'error'
  const [uploadMsg, setUploadMsg] = useState('');
  const [stats, setStats] = useState({});
  const [cameraError, setCameraError] = useState(null);

  useEffect(() => {
    loadStats();
    return () => stopCamera();
  }, []);

  async function loadStats() {
    const data = await getDatasetStats();
    setStats(data.por_palabra || {});
  }

  async function startCamera() {
    setCameraError(null);
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError('Tu navegador no soporta acceso a cámara. Usa Chrome en localhost.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      setCameraOn(true);
    } catch (err) {
      const msgs = {
        NotAllowedError: 'Permiso de cámara denegado.',
        NotFoundError: 'No se encontró cámara.',
        NotReadableError: 'La cámara está siendo usada por otra app.',
      };
      setCameraError(msgs[err.name] || err.message);
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach(t => t.stop());
    setCameraOn(false);
    setRecording(false);
    setCountdown(null);
  }

  function startRecording() {
    if (!streamRef.current || !palabra.trim()) return;
    chunksRef.current = [];
    setUploadStatus(null);

    let secs = 3;
    setCountdown(secs);
    const interval = setInterval(() => {
      secs -= 1;
      if (secs > 0) {
        setCountdown(secs);
      } else {
        clearInterval(interval);
        setCountdown(null);
        recorderRef.current?.stop();
        setRecording(false);
      }
    }, 1000);

    const recorder = new MediaRecorder(streamRef.current, { mimeType: 'video/webm' });
    recorder.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data); };
    recorder.onstop = async () => {
      clearInterval(interval);
      setCountdown(null);
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      await handleUpload(blob);
    };
    recorderRef.current = recorder;
    recorder.start();
    setRecording(true);
  }

  function stopEarly() {
    recorderRef.current?.stop();
    setRecording(false);
    setCountdown(null);
  }

  async function handleUpload(blob) {
    setUploadStatus('uploading');
    try {
      const data = await uploadClip(blob, palabra.trim());
      setUploadStatus('ok');
      setUploadMsg(`Clip #${data.clip_numero} guardado — total: ${data.total_clips_palabra}`);
      await loadStats();
    } catch (err) {
      setUploadStatus('error');
      setUploadMsg(err.message);
    }
  }

  const palabrasGrabadas = Object.entries(stats).filter(([, count]) => count > 0);
  const totalClips = palabrasGrabadas.reduce((a, [, c]) => a + c, 0);
  const canRecord = cameraOn && !recording && palabra.trim().length > 0;

  return (
    <div className="dataset-capture">

      <div className="ds-header">
        <span className="ds-total-label">Total grabado</span>
        <span className="ds-total-count">{totalClips} clips</span>
        {palabrasGrabadas.length > 0 && (
          <span className="ds-total-label">· {palabrasGrabadas.length} palabra{palabrasGrabadas.length > 1 ? 's' : ''}</span>
        )}
      </div>

      <div className="ds-body">

        {/* Columna izquierda: cámara */}
        <div className="ds-camera-col">

          <div className="ds-word-input">
            <label>¿Qué seña vas a grabar?</label>
            <input
              type="text"
              placeholder="Escribe la palabra, ej: Hola"
              value={palabra}
              onChange={e => { setPalabra(e.target.value); setUploadStatus(null); }}
              disabled={recording}
              maxLength={40}
            />
          </div>

          <div className="ds-camera-box">
            <video ref={videoRef} autoPlay playsInline muted className={`camera-feed ${cameraOn ? 'active' : ''}`} />
            {!cameraOn && <div className="camera-placeholder">Cámara apagada</div>}
            {countdown !== null && <div className="ds-countdown">{countdown}</div>}
            {recording && countdown === null && <div className="recording-indicator">● Grabando...</div>}
          </div>

          {cameraError && <p className="error-msg">{cameraError}</p>}

          <div className="camera-controls">
            {!cameraOn
              ? <button className="btn btn-primary" onClick={startCamera}>Activar cámara</button>
              : <button className="btn btn-danger" onClick={stopCamera}>Apagar cámara</button>
            }
            {!recording && (
              <button className="btn btn-record" onClick={startRecording} disabled={!canRecord}>
                Grabar (3s)
              </button>
            )}
            {recording && (
              <button className="btn btn-stop" onClick={stopEarly}>Detener ya</button>
            )}
          </div>

          {!palabra.trim() && cameraOn && (
            <p className="ds-hint">Escribe la palabra arriba antes de grabar.</p>
          )}

          {uploadStatus && (
            <div className={`ds-upload-msg ds-upload-${uploadStatus}`}>
              {uploadStatus === 'uploading' && '⏳ Subiendo clip...'}
              {uploadStatus === 'ok'        && `✓ ${uploadMsg}`}
              {uploadStatus === 'error'     && `✗ ${uploadMsg}`}
            </div>
          )}
        </div>

        {/* Columna derecha: palabras grabadas */}
        <div className="ds-grid-col">
          <h3 className="ds-grid-title">
            {palabrasGrabadas.length === 0 ? 'Aún no hay clips grabados' : 'Clips grabados'}
          </h3>

          {palabrasGrabadas.length === 0 ? (
            <p className="ds-empty">Escribe una palabra, activa la cámara y graba tu primera seña.</p>
          ) : (
            <div className="ds-word-grid">
              {palabrasGrabadas.sort((a, b) => a[0].localeCompare(b[0])).map(([p, count]) => (
                <button
                  key={p}
                  className={`ds-word-card ${p === palabra.trim() ? 'selected' : ''}`}
                  onClick={() => { setPalabra(p); setUploadStatus(null); }}
                  disabled={recording}
                >
                  <span className="ds-card-word">{p}</span>
                  <span className="ds-card-count">{count} clip{count !== 1 ? 's' : ''}</span>
                </button>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
