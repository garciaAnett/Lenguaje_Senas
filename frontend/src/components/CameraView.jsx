import { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';

const CameraView = forwardRef(function CameraView({ onCapture }, ref) {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const [cameraOn, setCameraOn] = useState(false);
  const [recording, setRecording] = useState(false);
  const [error, setError] = useState(null);

  useImperativeHandle(ref, () => ({ startRecording, stopRecording }));

  async function startCamera() {
    setError(null);

    if (!navigator.mediaDevices?.getUserMedia) {
      setError('Tu navegador no soporta acceso a la cámara. Usa Chrome o Firefox en localhost.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      setCameraOn(true);
    } catch (err) {
      const mensajes = {
        NotAllowedError: 'Permiso de cámara denegado. Haz clic en el candado de la barra de direcciones y permite la cámara, luego recarga.',
        NotFoundError: 'No se encontró ninguna cámara conectada.',
        NotReadableError: 'La cámara está siendo usada por otra aplicación. Ciérrala e intenta de nuevo.',
        OverconstrainedError: 'La cámara no cumple los requisitos mínimos.',
      };
      setError(mensajes[err.name] || `Error (${err.name}): ${err.message}`);
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach(t => t.stop());
    setCameraOn(false);
    setRecording(false);
  }

  function startRecording() {
    if (!streamRef.current) return;
    chunksRef.current = [];
    const recorder = new MediaRecorder(streamRef.current, { mimeType: 'video/webm' });
    recorder.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data); };
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      onCapture(blob);
    };
    mediaRecorderRef.current = recorder;
    recorder.start();
    setRecording(true);
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  }

  useEffect(() => () => stopCamera(), []);

  return (
    <div className="camera-container">
      <video ref={videoRef} autoPlay playsInline muted className={`camera-feed ${cameraOn ? 'active' : ''}`} />
      {!cameraOn && <div className="camera-placeholder">Cámara apagada</div>}
      {error && <p className="error-msg">{error}</p>}
      <div className="camera-controls">
        {!cameraOn
          ? <button className="btn btn-primary" onClick={startCamera}>Activar cámara</button>
          : <button className="btn btn-danger" onClick={stopCamera}>Apagar cámara</button>
        }
        {cameraOn && !recording && (
          <button className="btn btn-record" onClick={startRecording}>Capturar seña</button>
        )}
        {recording && (
          <button className="btn btn-stop" onClick={stopRecording}>Detener</button>
        )}
      </div>
      {recording && <div className="recording-indicator">● Grabando...</div>}
    </div>
  );
});

export default CameraView;
