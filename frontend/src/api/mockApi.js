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
    if (res.ok) return await res.json();
  } catch {
    // backend not available yet — use mock
  }
  const word = MOCK_WORDS[Math.floor(Math.random() * MOCK_WORDS.length)];
  const confidence = +(0.65 + Math.random() * 0.30).toFixed(2);
  return { palabra: word, confianza: confidence, mock: true };
}
