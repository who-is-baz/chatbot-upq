# Inventario de fuentes UPQ para el chatbot

Revisión del ZIP `DOCUMENTOS UPQ.zip` (190 archivos) del 25 de noviembre de 2026. Los PDF originales van en `docs/fuentes/`, que **no se commitea** (está en `.gitignore`). Al repo solo van los CSV y las imágenes optimizadas.

## 1. Qué se usó y para qué

| Intención | Documento | Vigencia |
|---|---|---|
| admision | Convocatoria UPQ (20 ene 2026, queretaro.gob.mx) | Ingreso sep-dic 2026 |
| admision | Resultados 2do proceso SD2026 · Resultados e Inscripción MA2026 | 2026 |
| admision, oferta_educativa | Convocatoria posgrado ene-abr 2027 (3 ago 2026) | Ingreso ene-abr 2027 |
| oferta_educativa | 7 planes de estudio (mapas curriculares 2024) | Desde sep 2024 |
| oferta_educativa | Fichas de carrera y posgrado de upq.mx | 2026 |
| oferta_educativa | Convocatoria UPQ 2026 · Actores del Programa Dual (PFD) | 2026 |
| calendario_escolar | Calendario Escolar SEP 2026-AGO 2027 | Ciclo 2026-2027 |
| reinscripcion, costos_pagos | Convocatoria Reinscripción SD2026 | sep-dic 2026 |
| reinscripcion | Reglamento de Estudios de PA y Licenciatura (POGEQ 22 nov 2013) | Vigente |
| becas | Lineamientos de becas y exención de pago (POGEQ 24 sep 2021) · Resultados Becas SD2026 | Vigente / 2026 |
| becas, movilidad_intercambio | Becas y convocatorias internacionales · Movilidad · Internacionalización · Convenios | 2025 |
| costos_pagos | Reactivar o liberar pagos 2026 · Facturación · UMA 2026 (INEGI) | 2026 |
| estadias | Planes 2024 · Página Estancias y Estadías · Manual SII estancias | ver contradicción 1 |
| servicio_social | Reglamento (arts. 78-84) · Infografía Servicio Social · Preguntas frecuentes | Vigente |
| titulacion | Convocatoria de Titulación Licenciatura oct 2026 | oct 2026 |
| ingles_idiomas | Temario Inglés-Alemán SD2025 · Business English · Reubicación de inglés · Peace Corps | Precios 2025 |
| servicios_escolares | Kárdex-Comprobante de estudio · Reposición de credencial 2026 · Estacionamiento · Preguntas frecuentes | 2026 |
| ubicacion_transporte | Convocatoria transporte SD2026 · Rutas de transporte 2026 · Mapa de ubicación | 2026 |
| contacto_horarios | Directorio upq.mx · correos de las convocatorias · redes de los carteles 2026 | 2026 |
| biblioteca_actividades | Desarrollo Humano · Representativos · Catálogo de instalaciones | 2026 |
| contacto_horarios | Decreto de Creación (POGEQ 25 oct 2005) · Historia · Filosofía · Mascotas · Difusión de vacantes · Convocatorias PTC 2026 | — |

Los escaneados (preguntas frecuentes, servicio social, credencial, pagos, estacionamiento, dual, lineamientos de becas) se leyeron por OCR y se revisaron a mano contra la imagen.

## 2. Descartado

- **~55 leyes, códigos, constituciones y tratados** (IVA, ISR, Ley Federal del Trabajo, etc.): marco legal general, no responde preguntas de alumnos.
- **Protocolo sanitario 2021, comunicados COVID 2020, Periódico Oficial 18 y 19 mar 2020**: desactualizados.
- **Catálogo de ingresos 2021** (dos copias): sustituido por los montos en UMA de las convocatorias 2026, que coinciden con él (por ejemplo, admisión 15.93 UMA).
- **Finanzas, nómina, bienes muebles, condiciones de trabajo, minutas del comité de ética, SGC, estructura orgánica, consejos**: no sirven al chatbot.
- **Empresas y RSE** (Colabora con UPQ, ESR, CEMEFI, aliados, GTU): dirigido a empresas, no a alumnos.
- **UPQ en la Sierra 2024, credencialización de egresados 2023**: convocatorias vencidas.
- **Manual de Organización**: es un escaneo sin texto; no se usó.
- **Planes de estudio (7) a (11)**: no son planes, son 5 copias de la convocatoria de posgrado.
- **Tres archivos `.crdownload`**: descargas incompletas. Dos PDF sin estructura válida y una foto truncada. Hay que volver a bajarlos si importaban.

## 3. Contradicciones y datos dudosos (pendientes de decisión)

1. **Estancias vs. estadías.** La página `upq.mx/estancias-estadias` dice: Estancia 1 en 4.º (60 h), Estancia 2 en 7.º (120 h), Estadía en 10.º (600 h). Los planes 2024 dicen: estadía de TSU en 6.º y estadía de licenciatura en 10.º, ambas de 600 h, y las fichas de carrera dicen "2 estadías". Interpretación: la página web describe planes anteriores. El chatbot responde con el plan 2024 y avisa del esquema anterior.
2. **Inicio de enero 2027.** El calendario marca inicio de cuatrimestre el jueves 7 de enero, pero las reinscripciones ordinarias van hasta el 10 y las extemporáneas del 11 al 13. Se transcribió tal cual; conviene confirmarlo en Servicios Estudiantiles.
3. **Directorio.** Las extensiones de carrera usan nombres de programas que ya no se ofertan (Sistemas Computacionales, Redes y Telecomunicaciones, Negocios Internacionales, Administración y Gestión de PyMES).
4. **Modalidad mixta.** La convocatoria de admisión 2026 incluye mixta para 5 carreras (con Administración, Manufactura e ITIID); la de reinscripción solo lista mixta para Comercio y Mecatrónica, porque son las únicas con alumnos mixtos activos.
5. **TSU de ITIID.** La convocatoria lista TSU en Desarrollo de Software Multiplataforma; la reinscripción agrega Infraestructura de Redes Digitales y la ficha web menciona Entornos Virtuales y Negocios Digitales.
6. **Becas por excelencia.** Los lineamientos 2021 subieron el promedio mínimo de 9.0 a 9.5 (transitorio segundo). Se usa 9.5.
7. **Dominios de correo.** Conviven `@upq.edu.mx` (la mayoría) y `@upq.mx` (por ejemplo `unidad.transparencia@upq.mx`).
8. **Errores del sitio** (no se copiaron): el perfil de egreso de Administración trae texto de otro programa (física, química, inglés A1) y la ficha de Manufactura Avanzada repite el mismo párrafo en los 3 ciclos.

## 4. Pendientes (no hay fuente en el ZIP)

- Convocatoria de **admisión 2027** (licenciatura).
- **Catálogo de ingresos 2026** (está en *La Sombra de Arteaga* del 14 nov 2025, No. 91; no se pudo descargar). Faltan, por ejemplo, el costo de constancias, credencial y recursamiento.
- **Horarios** de biblioteca y de Servicios Estudiantiles.
- **Psicología, enfermería o servicio médico, papelería**: no aparecen en ningún documento. Orientación Educativa (ext. 365) existe, pero no hay descripción de sus servicios.
- Que **el deporte sea obligatorio** en los primeros cuatrimestres: no aparece en planes ni reglamento. Solo se confirma que hay actividades co-curriculares por la tarde el primer año.
- **Precios vigentes** de los cursos de idiomas (los que hay son de sep-dic 2025).
- **TikTok:** el handle `@upqoficial` sale de los carteles 2026; falta confirmar el link exacto.

## 5. Valor de la UMA usado

INEGI: $117.31 diarios, vigente del 1 de febrero de 2026 al 31 de enero de 2027. Desde el 1 de febrero de 2027 cambian todos los montos en pesos; los montos en UMA no.

## 6. Nombres de intención

Se alinearon con el README: `ingles_idiomas`, `movilidad_intercambio` y `biblioteca_actividades`. Los fragmentos de modalidades van en `oferta_educativa` y los institucionales en `contacto_horarios`.
