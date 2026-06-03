const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const MOCK_WORDS = ['Hola', 'Gracias', 'Sí', 'No', 'Ayuda', 'Agua', 'Comida', 'Baño', 'Casa', 'Escuela', 'Amigo', 'Familia', 'Perdón', 'Por favor', 'Adiós'];

export async function checkHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    if (res.ok) return await res.json();
  } catch {
    // backend not available yet — use mock
  }
  return { status: 'mock', message: 'Backend mock activo' };
}

export async function predict(videoBlob) {
  try {
    const form = new FormData();
    form.append('video', videoBlob, 'clip.webm');
    const res = await fetch(`${BASE_URL}/predict`, { method: 'POST', body: form });
    if (res.ok) {
      const data = await res.json();
      return {
        palabra: data.prediccion.palabra,
        confianza: data.prediccion.confianza,
        top3: data.top3,
        mock: data.modo === 'mock',
      };
    }
  } catch {
    // backend not available yet — use mock
  }
  const word = MOCK_WORDS[Math.floor(Math.random() * MOCK_WORDS.length)];
  const confidence = +(0.65 + Math.random() * 0.30).toFixed(2);
  return { palabra: word, confianza: confidence, mock: true };
}

export async function uploadClip(videoBlob, palabra) {
  const form = new FormData();
  form.append('video', videoBlob, 'clip.webm');
  form.append('palabra', palabra);
  form.append('participante', 'anett');
  form.append('duracion', '3.0');
  form.append('fps', '30');
  const res = await fetch(`${BASE_URL}/dataset/upload`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  const data = await res.json();
  // Normaliza respuesta de Rodrigo al formato que usa DatasetCapture
  return {
    clip_numero: data.entry?.sample_id ?? '?',
    total_clips_palabra: data.entry?.split ?? '?',
    palabra: data.entry?.palabra ?? palabra,
  };
}

export async function getDatasetStats() {
  try {
    const res = await fetch(`${BASE_URL}/dataset/stats`);
    if (res.ok) {
      const data = await res.json();
      // Normaliza respuesta de Rodrigo: { por_clase: [{palabra, total}] }
      const por_palabra = {};
      if (data.por_clase) {
        data.por_clase.forEach(c => { por_palabra[c.palabra] = c.total; });
      }
      return { total: data.total_clips ?? 0, por_palabra };
    }
  } catch { }
  return { total: 0, por_palabra: {} };
}
