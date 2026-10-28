# Plan de cierre v1.0.0

Fecha de ejecución: 2026-10-27
Release objetivo: **Portfolio Local Release — Not Production Ready**

Este plan cierra el alcance general de DataTrust API. La versión `1.0.0` solo se
adoptará si todos los criterios P0 quedan comprobados localmente. No representa
un servicio público, una certificación de seguridad ni un producto empresarial.

## Línea base verificada

- Código inicial del cierre: `0.3.0`.
- Intérprete disponible: Python 3.12.14; Python 3.11 no está instalado.
- Suite: 109 casos descubiertos y 109 aprobados, sin warnings, en 7.03 s.
- Smoke HTTP real en `127.0.0.1`: carga, historial, detalle, paginación,
  exportación, 404 y rechazo 413 aprobados.
- Git local: rama `main`, sin commits, sin remoto y sin identidad de autor.
- Respaldo previo: `.local-backups/datatrust-v0.3.0-before-v1-close-20261027.zip`;
  SHA-256 `6A25037EF134CD38C9A90FB92EB96031296D1928029571D3DDAF5BD83C6FF730`.

## P0 — obligatorios para GO

| Criterio | Evidencia exigida |
|---|---|
| Escenarios sintéticos de 6 y 100 pedidos | Pruebas automatizadas sobre recursos empacados; 100 debe dar 90 válidas, 10 inválidas y 10 incidencias. |
| Recorrido funcional | API y navegador real: cargar, ver métricas, consultar incidencias y exportar. También un error controlado. |
| Límites y privacidad | Mantener pruebas de 2 MiB de archivo, límite multipart separado, 10.000 filas, filename neutral y ausencia de filas originales. |
| SQLite local | Mantener transacciones, cierre de conexiones, `busy_timeout`, 503 con `Retry-After`, backup y restauración sintéticos. |
| Instalación limpia | Crear un entorno aislado nuevo, instalar fuente, ejecutar suite completa, `compileall`, `pip check` y verificación JavaScript. |
| Wheel | Construir e instalar localmente el wheel en otro entorno; confirmar versión y recursos HTML/CSS/JS/SVG/JSON/CSV. |
| Versionado | `pyproject.toml`, paquete, OpenAPI, `/health`, wheel y documentación deben coincidir. |
| Higiene | Git sin secretos, bases, entornos, caches, backups ni artefactos de build destinados a seguimiento. |

Un fallo crítico sin resolver en cualquiera de estos puntos implica **NO GO** y
mantener la rama `0.3.x`.

## P1 — presentación de portafolio

- Mejorar únicamente los textos que explican filas inválidas frente a
  incidencias y ofrecer descargas claras para las demos de 6 y 100 pedidos.
- Completar README en español e inglés, guía de usuario, demo de reclutador,
  caso de estudio, extracto profesional y checklist de publicación.
- Documentar datos del autor pendientes y comparación MIT/Apache-2.0 sin añadir
  una licencia ni inventar identidad.
- Verificar responsive y accesibilidad básica en 360×800, 390×844, 768×1024 y
  1366×768 si el navegador automatizable está disponible.

## P2 — fuera de este cierre

- Autenticación, autorización, TLS, cifrado en reposo, retención y borrado.
- Multiusuario, múltiples workers, servicio cloud o exposición a Internet.
- Migraciones de esquema y política WAL para escenarios de mayor concurrencia.
- Editor/mapeador de columnas, conectores ERP, OCR, IA/ML y analítica comercial.
- Compatibilidad remota de CI/Docker y publicación, que requieren infraestructura
  o decisiones del titular.

## Secuencia de ejecución

1. Añadir pruebas que fallen por ausencia de los recursos demo.
2. Incorporar datos sintéticos y cambios mínimos de interfaz.
3. Ejecutar pruebas focalizadas y suite completa.
4. Si P0 está verde, alinear `1.0.0` y verificar fuente/wheel desde entornos
   nuevos.
5. Ejecutar E2E real, benchmark comparable y auditorías estáticas.
6. Completar documentación con resultados reales y congelar alcance.
