# Prompt 00 — Auditoría inicial del repositorio (pegar en Codex)

Actúa como ingeniero senior de Python/FastAPI, revisor de seguridad y mentor técnico. Trabajarás en el repositorio **DataTrust API** que acabo de abrir.

1. Lee `AGENTS.md`, `README.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md` y `docs/BACKLOG.md`.
2. Inspecciona el código existente ANTES de modificarlo. Identifica funcionalidades implementadas y discrepancias de documentación.
3. Ejecuta `python -m pytest -q` con las dependencias instaladas. No inventes salidas si falta una dependencia o falla un comando.
4. Revisa manejo de CSV mal formados, límites de archivo/filas, SQL parametrizado, privacidad e identificación de issues.
5. Entrega diagnóstico de bugs, deuda técnica y riesgos, priorizados por severidad.
6. Propón mejoras limitadas y medibles, sin generar nuevos archivos ni cambiar nada hasta completar el informe.
7. En español, explícame qué hace cada módulo como si estuviera aprendiendo ingeniería de software; incluye tres preguntas para comprobar comprensión.

Restricciones: no usar APIs externas, no publicar repositorio, no despliegues públicos, no manipular datos reales ni reemplazar todo el proyecto.
