# Diario de trabajo — Anett Garcia

Registro personal de tareas realizadas, cambios hechos y próximos pasos por sprint.

---

## Sprint 0 — 22/05/2026 — COMPLETADO ✅

**Tarea:** Realizar los mockups de la aplicación en Figma.  
**Estado:** Hecho.  
**Entregable:** Diseño en Figma de la interfaz del MVP.

---

## Sprint 1 — 27/05/2026 — EN PROGRESO 🔄

**Rama:** `sprint1_Anett`

### Tareas del plan

| # | Tarea | Estado |
|---|---|---|
| 1 | Crear frontend con React/Vite | ✅ Hecho |
| 2 | Pantalla inicial con diseño oscuro | ✅ Hecho |
| 3 | Componente de cámara (activar/apagar/grabar) | ✅ Hecho |
| 4 | Panel de palabra + barra de confianza | ✅ Hecho |
| 5 | Consumir `/health` (con fallback mock) | ✅ Hecho |
| 6 | Consumir `/predict` (con fallback mock) | ✅ Hecho |
| 7 | Historial de últimas predicciones | ✅ Hecho |
| 8 | Prueba visual en navegador | ⏳ Pendiente — correr `npm run dev` |

### Archivos creados en este sprint

```
frontend/
├── src/
│   ├── api/
│   │   └── mockApi.js          # Llamadas a /health y /predict con fallback mock
│   ├── components/
│   │   ├── CameraView.jsx      # Cámara web: activar, grabar clip, detener
│   │   ├── PredictionPanel.jsx # Muestra palabra reconocida + barra de confianza
│   │   └── HealthStatus.jsx    # Badge de estado del backend
│   ├── App.jsx                 # Layout principal + lógica de captura
│   ├── App.css                 # Estilos completos (tema oscuro)
│   └── index.css               # Reset base
├── .env.example                # Variable VITE_API_URL
└── package.json
```

### Cómo correr el frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Abre `http://localhost:5173` en el navegador.

### Comportamiento actual

- Si el backend de Rodrigo **no está corriendo**: la app usa respuestas mock (muestra la etiqueta naranja "MOCK").
- Si el backend **está corriendo** en `http://localhost:8000`: se conecta automáticamente a `/health` y `/predict`.
- El grabado captura un clip `.webm` desde la cámara y lo envía al endpoint.

---

## Sprint 2 — 03/06/2026 — PENDIENTE ⏳

### Tareas asignadas a Anett

| # | Tarea |
|---|---|
| 1 | Agregar interfaz de captura de clips (modo dataset) |
| 2 | Selector de palabra (lista de 15 palabras) |
| 3 | Grabar y guardar clips de **8 palabras**: Hola, Gracias, Sí, No, Ayuda, Agua, Comida, Baño |
| 4 | Registrar evidencias (capturas de pantalla / video) |
| 5 | Validar nombres de archivos y calidad de clips |

**Entregable:** Clips de 8 palabras grabados y validados, con evidencias.  
**Rama sugerida:** `sprint2_Anett`

---

## Sprint 3 — 10/06/2026 — PENDIENTE ⏳

### Tareas asignadas a Anett

| # | Tarea |
|---|---|
| 1 | Conectar el envío de clips/secuencias al backend real |
| 2 | Vista de traducción en tiempo real (ventana continua) |
| 3 | Mostrar confianza en tiempo real |
| 4 | Probar las 8 palabras con el modelo entrenado por Rodrigo |

**Entregable:** Interfaz funcional conectada al modelo VideoMAE.  
**Rama sugerida:** `sprint3_Anett`

---

## Sprint 4 — 17/06/2026 — PENDIENTE ⏳

### Tareas asignadas a Anett

| # | Tarea |
|---|---|
| 1 | Pulir interfaz (responsive, accesibilidad básica) |
| 2 | Pruebas finales de las 8 palabras |
| 3 | Diagramas funcionales del flujo de la aplicación |
| 4 | Evidencias (video demo, capturas) |
| 5 | Escribir secciones funcionales del documento final |

**Entregable:** Interfaz pulida + evidencias + secciones del documento.  
**Rama sugerida:** `sprint4_Anett`

---

## Notas técnicas

- El frontend consume `VITE_API_URL` del `.env`; por defecto apunta a `http://localhost:8000`.
- El mock devuelve una palabra aleatoria de las 15 del MVP con una confianza entre 65–95%.
- Para que el grabado funcione, el navegador debe tener permisos de cámara habilitados.
- Si el backend no tiene CORS configurado para `localhost:5173`, la llamada real fallará y usará el mock igualmente.
