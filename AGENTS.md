# Instrucciones para Codex — DataTrust API

## Contexto
Proyecto educativo y de portafolio de ingeniería, con casos de datos sintéticos. `v1.0.0` es una **Portfolio Local Release — Not Production Ready** con alcance general congelado. El objetivo es conservar una demo reproducible de control de calidad de datos, no ampliarla indefinidamente.

## Antes de cambiar código
1. Lee README.md, docs/PRD.md, docs/ARCHITECTURE.md y docs/BACKLOG.md.
2. Inspecciona el código y ejecuta `python -m pytest -q`; reporta el resultado inicial.
3. Propón un plan de cambios corto y los criterios de aceptación; no reescribas todo.

## Reglas obligatorias
- Mantén Python >=3.11, FastAPI y SQLite por ahora.
- Sigue separación: HTTP en main.py, validaciones en validator.py, acceso SQL en store.py.
- Escribe al menos una prueba para cada comportamiento nuevo; no elimines pruebas para lograr un resultado verde.
- Nunca inventes resultados, benchmarks, capturas o niveles de seguridad.
- No incluyas API keys, secretos, datos personales reales ni archivos `.env` en Git.
- Nunca hagas cambios destructivos en bases de datos o archivos del usuario.
- Nunca envíes archivos ni información a servidores externos sin autorización explícita.
- Trata CSV de terceros como entrada no confiable: limita tamaños, valida tipo/esquema y evita persistir valores sensibles.
- No agregues modelos de IA para cálculos deterministas; primero demuestra valor sin APIs pagadas.
- No anuncies que el sistema es apto para producción; actualmente NO incluye autenticación, permisos, cifrado en reposo ni retención de datos.
- Actualiza documentación y changelog por cada hito.
- Pregunta antes de agregar servicios de pago o cambiar el objetivo del proyecto.
- Después de v1.0.0, acepta solo defectos bloqueantes concretos dentro del alcance. Autenticación, nube, multiusuario, conectores, IA/ML y nuevas funciones grandes pertenecen a otro proyecto o a una decisión explícita del titular.
- No configures identidad Git, licencia, remotos, commits ni publicación sin una instrucción posterior y explícita del titular.

## Entrega de cada tarea
1. Lista de archivos editados.
2. Explicación en español del cambio y cómo funciona.
3. Comandos ejecutados y resultado real de pruebas.
4. Limitaciones, riesgos y siguiente tarea sugerida.
