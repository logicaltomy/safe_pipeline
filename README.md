# safe_pipeline

Laboratorio academico de DevSecOps para la evaluacion `OCY1102: Ciberseguridad en Desarrollo`.

El proyecto implementa un flujo seguro de SDLC con:

- `Jenkins` para CI/CD
- `Docker Compose` para infraestructura local
- `Dependabot` y `pip-audit` para gestion y escaneo de dependencias
- `OWASP ZAP` para pruebas DAST
- `Prometheus` y `Grafana` para monitoreo

## Objetivo

Construir, probar, analizar y mitigar vulnerabilidades en una aplicacion web Flask de laboratorio, manteniendo trazabilidad tecnica y evidencias para auditoria.

## Estructura publicada

```text
.
├── .github/
│   └── dependabot.yml
├── Docs/
│   ├── Desarrollo EV3 (1).docx
│   └── Parcial 3_OCY1102_Instrucciones y Pauta_Estudiante (4).docx
├── app/
│   ├── __pycache__/
│   │   └── app.cpython-312.pyc
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── monitoring/
│   └── prometheus.yml
├── .gitignore
├── Jenkinsfile
├── README.md
├── dependency-audit.txt
└── docker-compose.yml
```

## Requisitos

- `Docker` y `Docker Compose`
- `Python 3`
- Navegador web para `Jenkins` y `Grafana`

## Artefactos locales no publicados

Durante el laboratorio pueden existir archivos adicionales de trabajo local que no necesariamente forman parte del snapshot publicado:

- `docs/evidence/`
- `reports/`
- `.venv/`
- `scripts/md_to_docx.py`

## Servicios

- `jenkins`: `http://localhost:8080`
- `safe_app`: `http://localhost:5001`
- `grafana`: `http://localhost:3000`
- `prometheus`: `http://localhost:9090`

## Aplicacion

La aplicacion web esta en [`app/app.py`](app/app.py).

Incluye:

- endpoint raiz `/`
- healthcheck `/health`
- endpoint de busqueda seguro `/search`
- endpoint de comentario seguro `/comment`
- metricas Prometheus en `/metrics`

## Pipeline

El pipeline esta definido en [`Jenkinsfile`](Jenkinsfile) e incluye:

- `Dependencies`
- `Build`
- `Test`
- `Dependency Security Test`
- `Deploy`
- `DAST Full Scan`

## Levantar el entorno

Desde la raiz del proyecto:

```bash
docker compose up -d --build jenkins safe_app prometheus grafana
```

## Comandos utiles

Ver contenedores:

```bash
docker ps
```

Recrear solo la aplicacion:

```bash
docker compose up -d --build safe_app
```

Verificar metricas:

```bash
curl http://localhost:5001/metrics
```

Generar eventos de seguridad para Grafana:

```bash
curl "http://localhost:5001/search?name=%27%20or%201%3D1%20--"
curl "http://localhost:5001/comment?message=%3Cscript%3Ealert(1)%3C%2Fscript%3E"
```

Generar el informe `.docx` desde el markdown de evidencias local:

```bash
python3 scripts/md_to_docx.py docs/evidence/Evaluacion.md docs/evidence/Evaluacion.docx
```

Ese script se usa en el entorno local de trabajo y puede no estar presente en todos los snapshots publicados del repositorio.

## Estado del laboratorio

El laboratorio ya cubre:

- pipeline funcional
- escaneo y parcheo de dependencias
- escaneo DAST con ZAP
- mitigacion de `SQL Injection` y `XSS`
- monitoreo con Prometheus y Grafana

## Referencias academicas

- Pauta base: `Docs/Parcial 3_OCY1102_Instrucciones y Pauta_Estudiante (4).docx`
- Plantilla de entrega: `Docs/Desarrollo EV3 (1).docx`
