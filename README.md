# Lenguaje de Señas - MVP Traducción en Tiempo Real

Proyecto de la materia Emergentes II. Traducción de lenguaje de señas en tiempo real usando VideoMAE + Hugging Face.

**Equipo:** Anett Garcia · Rodrigo Villarroel  
**Stakeholder:** Ing. Claudia Ureña  
**Periodo:** 27/05/2026 – 17/06/2026  
**Trello:** https://trello.com/invite/b/6a0a5e644863ac39b0f6d78e/ATTI604adf889414c4ca1ed65266ac86a9a19BAF86FC/proyecto-emergentes-2  
**GitHub:** https://github.com/garciaAnett/Lenguaje_Senas.git

---

## Descripción

MVP web capaz de reconocer 15 palabras en lenguaje de señas y mostrar su traducción en texto en tiempo real. El usuario activa la cámara, realiza una seña, y el sistema captura clips cortos de video para clasificarlos mediante VideoMAE gestionado con Hugging Face.

**Palabras del MVP:** Hola, Gracias, Sí, No, Ayuda, Agua, Comida, Baño, Casa, Escuela, Amigo, Familia, Perdón, Por favor, Adiós.

---

## Roles

| Integrante | Rol | Enfoque técnico |
|---|---|---|
| Anett Garcia | Full stack / Interfaz y validación funcional | React/Vite, consumo API, UX, pruebas, documentación funcional |
| Rodrigo Villarroel | Full stack / Modelo IA y entrenamiento | FastAPI, Hugging Face, VideoMAE, entrenamiento |
| Ing. Claudia Ureña | Stakeholder principal | Revisión y validación académica |

---

## Arquitectura

```
React/Vite → cámara web → captura de clip → FastAPI → /predict → palabra + confianza
```

| Componente | Tecnología | Uso |
|---|---|---|
| Frontend | React + Vite | Cámara, captura, pantalla de traducción |
| Backend API | FastAPI + Python | Rutas /health y /predict |
| Modelo IA | VideoMAE + Hugging Face | Clasificación de clips por seña |
| Gestión | Trello + GitHub | Sprints, evidencias, versiones |

---

## Plan de Sprints

### Sprint 0 — 22/05/2026 — Mockups ✅ COMPLETADO

**Objetivo:** Mockups de la aplicación y descripción del modelo de entrenamiento.

| Integrante | Tarea | Estado |
|---|---|---|
| Anett Garcia | Realizar los mockups en Figma | ✅ Hecho |
| Rodrigo Villarroel | Realizar los mockups | ✅ Hecho |

**Entregable:** FIGMA con diseño de la aplicación.

---

### Sprint 1 — 27/05/2026 — Base técnica del MVP

**Objetivo:** Construir base funcional del MVP.

| Integrante | Tareas | Estado |
|---|---|---|
| Anett Garcia | Crear frontend con cámara; pantalla inicial; panel de palabra/confianza; consumir `/health` y `/predict` mock; prueba visual | 🔄 En progreso |
| Rodrigo Villarroel | Crear repo y estructura; backend FastAPI; endpoint `/health`; endpoint `/predict` mock; preparar entorno Hugging Face | ⏳ Pendiente |

**Entregable:** Web inicial + backend activo + repo organizado.  
**Rama Anett:** `sprint1_Anett`

---

### Sprint 2 — 03/06/2026 — Dataset de video

**Objetivo:** Construir dataset de clips de video.

| Integrante | Tareas |
|---|---|
| Anett Garcia | Interfaz de captura; selector de palabra; grabar clips de 8 palabras; registrar evidencias; validar nombres y calidad |
| Rodrigo Villarroel | Servicio para guardar clips; dataset_index.csv; grabar clips de 7 palabras; preprocesar videos; dividir train/val/test |

**Entregable:** Dataset de 15 palabras + CSV índice.

---

### Sprint 3 — 10/06/2026 — Modelo e integración

**Objetivo:** Entrenar e integrar predicción.

| Integrante | Tareas |
|---|---|
| Anett Garcia | Enviar clips/secuencias al backend; vista de traducción en tiempo real; mostrar confianza; probar 8 palabras |
| Rodrigo Villarroel | Fine-tuning VideoMAE; entrenamiento; métricas; endpoint real `/predict`; optimización inicial |

**Entregable:** Modelo VideoMAE integrado con la web.

---

### Sprint 4 — 17/06/2026 — Cierre y demo

**Objetivo:** Estabilizar, probar y cerrar.

| Integrante | Tareas |
|---|---|
| Anett Garcia | Pulir interfaz; pruebas finales de 8 palabras; diagramas funcionales; evidencias; secciones del documento |
| Rodrigo Villarroel | Mejorar precisión; optimizar inferencia; corregir backend; README técnico; pruebas finales de 7 palabras |

**Entregable:** MVP final, Trello/GitHub, documento y demo.

---

## Dataset

- **Archivo índice:** `dataset_index.csv` (columnas: sample_id, palabra, class_id, participante, video_path, duracion, fps, split)
- **División:** 70% entrenamiento · 15% validación · 15% prueba
- **Duración por muestra:** ~2–3 segundos

---

## Reglas del equipo

1. Cada tarea debe registrarse y actualizarse en Trello.
2. Cada avance técnico debe respaldarse en GitHub o evidencia.
3. Las tareas se asignan de forma independiente para evitar bloqueos.
4. Una falta de cumplimiento genera una primera observación interna.
5. A la tercera falta, el integrante queda separado del equipo.
6. La separación será informada a la stakeholder para constancia académica.
