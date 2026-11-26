import importlib.util
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("unir_corpus", RAIZ / "scripts" / "unir_corpus.py")
unir_corpus = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unir_corpus)

ENCABEZADO = '"texto","intencion","respuesta","fuente"\n'


def preparar(tmp_path, monkeypatch, filas):
    carpeta = tmp_path / "data" / "intenciones"
    carpeta.mkdir(parents=True)
    (carpeta / "corpus_prueba.csv").write_text(ENCABEZADO + "".join(filas), encoding="utf-8")
    monkeypatch.setattr(unir_corpus, "RAIZ", tmp_path)
    monkeypatch.setattr(unir_corpus, "SALIDA", tmp_path / "data" / "corpus_upq.csv")


def test_une_y_quita_duplicados_tras_limpiar(tmp_path, monkeypatch):
    preparar(tmp_path, monkeypatch, [
        '"¿Hay becas?","becas","r","f"\n',
        '"hay becas","becas","r","f"\n',
        '"hola","saludo","r2","f2"\n',
    ])
    unir_corpus.main()
    salida = pd.read_csv(tmp_path / "data" / "corpus_upq.csv")
    assert len(salida) == 2
    assert set(salida.intencion) == {"becas", "saludo"}


def test_falla_si_un_texto_tiene_dos_intenciones(tmp_path, monkeypatch):
    preparar(tmp_path, monkeypatch, [
        '"hola","saludo","r","f"\n',
        '"hola","becas","r2","f2"\n',
    ])
    with pytest.raises(SystemExit) as error:
        unir_corpus.main()
    assert error.value.code == 1
