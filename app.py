"""Interfaz de chat del Asistente UPQ (Streamlit). La lógica vive en src/chatbot.py."""
import base64
import html
import re
from pathlib import Path

import streamlit as st

from src.chatbot import NIVEL_ACLARACION, ChatbotUPQ

RAIZ = Path(__file__).resolve().parent
LOGO = RAIZ / "assets" / "img" / "institucion" / "logo_upq.svg"
AVATARES = {"assistant": str(RAIZ / "assets" / "img" / "institucion" / "avatar_polo.png"),
            "user": ":material/person:"}
# Redes oficiales de la UPQ: (nombre, enlace, ícono de Font Awesome Free en assets/img/redes/).
REDES = [
    ("Facebook", "https://www.facebook.com/UPQoficial", "facebook-f"),
    ("X", "https://x.com/UPQoficial", "x-twitter"),
    ("Instagram", "https://www.instagram.com/soyupq", "instagram"),
    ("TikTok", "https://www.tiktok.com/@upqoficial", "tiktok"),
    ("LinkedIn", "https://www.linkedin.com/school/upq", "linkedin-in"),
]
AVISO = ("Proyecto escolar de Fundamentos de IA. No es un canal oficial de la UPQ; "
         "verifica la información en www.upq.mx.")
# Enlaces oficiales, iguales a los del pie de página de upq.mx.
ENLACES_PIE = {
    "Institución": [("Historia", "https://www.upq.mx/Institucion/Historia/"),
                    ("Filosofía", "https://www.upq.mx/Institucion/Filosofia/"),
                    ("Ubicación", "https://www.upq.mx/Institucion/Ubicacion/"),
                    ("Directorio", "https://www.upq.mx/Institucion/Directorio/")],
    "Comunidad": [("Servicios Estudiantiles", "https://www.upq.mx/ServiciosEstudiantiles/"),
                  ("Información Pública", "https://www.upq.mx/InformacionPublica/")],
}

st.set_page_config(page_title="Asistente UPQ", page_icon=str(LOGO))
st.logo(str(LOGO), size="large")
st.markdown(f"<style>{(RAIZ / 'assets' / 'estilos.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)


def iconos_redes() -> str:
    """Enlaces a las redes con su ícono SVG en línea (el color lo toma del CSS)."""
    enlaces = []
    for nombre, url, icono in REDES:
        svg = (RAIZ / "assets" / "img" / "redes" / f"{icono}.svg").read_text(encoding="utf-8")
        svg = svg.replace("<svg ", '<svg fill="currentColor" aria-hidden="true" ', 1)
        enlaces.append(f'<a href="{url}" target="_blank" rel="noopener" title="{nombre}" '
                       f'aria-label="{nombre} de la UPQ">{svg}</a>')
    return "".join(enlaces)


st.markdown(f'<nav class="upq-redes" aria-label="Redes sociales de la UPQ">{iconos_redes()}</nav>',
            unsafe_allow_html=True)


def contacto_upq() -> str:
    """Datos de contacto, enlaces oficiales y redes de la UPQ (versión compacta para el sidebar)."""
    secciones = "".join(
        f"<h5>{titulo}</h5><ul>"
        + "".join(f'<li><a href="{url}" target="_blank" rel="noopener">{texto}</a></li>' for texto, url in enlaces)
        + "</ul>"
        for titulo, enlaces in ENLACES_PIE.items()
    )
    return f"""<div class="upq-contacto">
<p>Carretera Estatal 420 SN, El Marqués, Querétaro, CP 76240</p>
<p>Tel. 442 101 9000 · comunicacion@upq.mx</p>
{secciones}
<h5>Redes sociales</h5><div class="upq-contacto-redes">{iconos_redes()}</div>
</div>"""


@st.cache_resource
def cargar_bot() -> ChatbotUPQ:
    return ChatbotUPQ()


bot = cargar_bot()
estado = st.session_state
estado.setdefault("mensajes", [])     # [{"rol", "texto", "resultado"}]
estado.setdefault("pendiente", None)  # pregunta o intención por responder en este ciclo
estado.setdefault("votos", {})        # índice del mensaje -> "👍" | "👎"
# Memoria corta: intención de la última respuesta. Vive en la sesión de cada usuario, no en el bot
# (el bot es compartido por todas las sesiones con st.cache_resource).
estado.setdefault("ultima_intencion", None)


# ---------------------------------------------------------------- barra lateral
with st.sidebar:
    st.header("Asistente UPQ")
    st.markdown(f'<div class="upq-aviso">{AVISO}</div>', unsafe_allow_html=True)
    st.caption("Respondo con información tomada de fuentes oficiales de la Universidad Politécnica de Querétaro. "
               "No proceses datos personales: no escribas tu matrícula, CURP ni teléfono.")
    tamano = st.segmented_control("Tamaño del texto", ["A−", "A", "A+"], default="A", key="tamano_texto",
                                  help="Accesibilidad: reduce o aumenta el texto de la página.")
    escala = {"A−": 90, "A": 100, "A+": 118}.get(tamano or "A", 100)
    st.markdown(f"<style>html {{ font-size: {escala}%; }}</style>", unsafe_allow_html=True)
    modo_tecnico = st.toggle("Modo técnico", help="Muestra intención, confianza, top-3, origen y latencia.")
    if modo_tecnico:
        m = bot.cache.metricas()
        st.caption(f"Caché: {m['aciertos']} aciertos de {m['aciertos'] + m['fallos']} consultas "
                   f"({m['tasa_aciertos']:.0%}) · {m['tamano']}/{m['capacidad']} guardadas")
    st.subheader("Preguntas sugeridas")
    with st.container(key="sugeridas_sidebar"):
        for i, pregunta in enumerate(bot.config["preguntas_sugeridas"]):
            if st.button(pregunta, key=f"sugerida_{i}", use_container_width=True):
                estado.pendiente = {"texto": pregunta}
    if st.button("Borrar conversación", type="secondary"):
        estado.mensajes, estado.votos, estado.pendiente, estado.ultima_intencion = [], {}, None, None
        st.rerun()
    with st.expander("Contacto y enlaces de la UPQ"):
        st.markdown(contacto_upq(), unsafe_allow_html=True)


# ---------------------------------------------------------------- render
def enlaces_fuente(fuente: str) -> list[tuple[str | None, str]]:
    """Convierte "url | nombre; url | nombre" en [(url, nombre), ...]."""
    partes = re.split(r"(https?://\S+)", fuente)
    if len(partes) == 1:
        return [(None, fuente.strip())]
    enlaces = []
    for i in range(1, len(partes), 2):
        url = partes[i]
        nombre = partes[i + 1].strip(" |;") if i + 1 < len(partes) else ""
        enlaces.append((url, nombre or url.split("/")[2]))
    return enlaces


def html_fuente(fuente: str, vigencia: str = "") -> str:
    enlaces = " · ".join(
        f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(nombre)}</a>' if url
        else html.escape(nombre)
        for url, nombre in enlaces_fuente(fuente)
    )
    extra = f'<span class="upq-vigencia">Vigencia: {html.escape(vigencia)}</span>' if vigencia else ""
    return f'<div class="upq-fuente"><strong>Fuente oficial:</strong> {enlaces}{extra}</div>'


def mostrar_tecnico(r: dict) -> None:
    with st.expander("Detalle técnico"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Confianza", f"{r['confianza']:.2f}")
        c2.metric("Origen", r["origen"])
        c3.metric("Latencia", f"{r['latencia_ms']} ms")
        st.write(f"**Intención:** `{r['intencion']}` · **Nivel:** `{r['nivel']}` · "
                 f"**Umbrales:** alto {bot.umbral_alto}, bajo {bot.umbral_bajo}")
        if r["top3"]:
            st.write("**Top-3:** " + " · ".join(f"`{i}` {p:.2f}" for i, p in r["top3"]))
        if r["fragmento"]:
            f = r["fragmento"]
            st.write(f"**Fragmento:** {f['id']} — {f['titulo']} (similitud {f['similitud']:.2f})")
        if r.get("herramienta"):
            st.write(f"**Herramienta:** `{r['herramienta']}`")
        if r.get("contexto_usado"):
            st.write("**Memoria corta:** se respondió con el tema de la pregunta anterior.")
        if r.get("motivo"):
            st.write(f"**Motivo del guardrail:** `{r['motivo']}`")


def mostrar_respuesta(idx: int, msg: dict) -> None:
    r = msg["resultado"]
    st.markdown(msg["texto"])
    f = r["fragmento"]
    if f and f["imagen"] and (RAIZ / f["imagen"]).exists():
        st.image(str(RAIZ / f["imagen"]), caption=f["titulo"])
    # Los saludos, despedidas y agradecimientos tienen fuente "interno": no se muestra como fuente oficial.
    if r["fuente"] and "http" in r["fuente"]:
        st.markdown(html_fuente(r["fuente"], f["vigencia"] if f else ""), unsafe_allow_html=True)

    if r["nivel"] == NIVEL_ACLARACION:
        columnas = st.columns(len(r["sugerencias"]))
        for col, intencion in zip(columnas, r["sugerencias"]):
            if col.button(bot.etiqueta(intencion), key=f"aclara_{idx}_{intencion}"):
                estado.pendiente = {"intencion": intencion, "texto": msg.get("pregunta", "")}

    if r["origen"] != "guardrail":
        voto = estado.votos.get(idx)
        if voto:
            st.caption(f"Gracias por tu opinión {voto}")
        else:
            c1, c2, _ = st.columns([1, 1, 8])
            if c1.button("👍", key=f"si_{idx}"):
                estado.votos[idx] = "👍"
                bot.registrar_voto(msg.get("pregunta", ""), r, util=True)
                st.rerun()
            if c2.button("👎", key=f"no_{idx}"):
                estado.votos[idx] = "👎"
                bot.registrar_voto(msg.get("pregunta", ""), r, util=False)
                st.rerun()

    if modo_tecnico:
        mostrar_tecnico(r)


logo_b64 = base64.b64encode(LOGO.read_bytes()).decode()
st.markdown(f"""
<div class="upq-encabezado">
  <img src="data:image/svg+xml;base64,{logo_b64}" alt="Logo UPQ">
  <div>
    <div class="upq-nombre">UNIVERSIDAD <span>POLITÉCNICA</span> DE QUERÉTARO</div>
    <div class="upq-titulo">Asistente <span>UPQ</span></div>
  </div>
</div>
""", unsafe_allow_html=True)
with st.chat_message("assistant", avatar=AVATARES["assistant"]):
    st.markdown(bot.config["bienvenida"])

# Con la conversación vacía, las preguntas sugeridas también salen como tarjetas en el centro.
if not estado.mensajes:
    with st.container(key="tarjetas"):
        st.markdown('<p class="upq-tarjetas-titulo">¿No sabes por dónde empezar?</p>', unsafe_allow_html=True)
        columnas = st.columns(2)
        for i, pregunta in enumerate(bot.config["preguntas_sugeridas"]):
            if columnas[i % 2].button(pregunta, key=f"tarjeta_{i}", use_container_width=True):
                estado.pendiente = {"texto": pregunta}

for idx, msg in enumerate(estado.mensajes):
    rol = "user" if msg["rol"] == "usuario" else "assistant"
    with st.chat_message(rol, avatar=AVATARES[rol]):
        if msg["rol"] == "usuario":
            st.markdown(msg["texto"])
        else:
            mostrar_respuesta(idx, msg)


# ---------------------------------------------------------------- entrada
escrito = st.chat_input("Escribe tu pregunta…")
if escrito:
    estado.pendiente = {"texto": escrito}

if estado.pendiente:
    pendiente, estado.pendiente = estado.pendiente, None
    if "intencion" in pendiente:
        resultado = bot.responder_intencion(pendiente["intencion"], pendiente["texto"])
        estado.mensajes.append({"rol": "usuario", "texto": bot.etiqueta(pendiente["intencion"])})
    else:
        resultado = bot.responder(pendiente["texto"], contexto=estado.ultima_intencion)
        estado.mensajes.append({"rol": "usuario", "texto": pendiente["texto"]})
    estado.mensajes.append({"rol": "asistente", "texto": resultado["respuesta"],
                            "resultado": resultado, "pregunta": pendiente["texto"]})
    if resultado["nivel"] == "respuesta" and resultado["origen"] in ("modelo", "cache"):
        estado.ultima_intencion = resultado["intencion"]
    st.rerun()
