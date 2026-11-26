"""Configuración común de pytest."""
import pytest

from src import registro


@pytest.fixture(autouse=True, scope="session")
def registro_temporal(tmp_path_factory):
    """Las pruebas escriben el registro en una carpeta temporal, nunca en logs/ del proyecto."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(registro, "RUTA_REGISTRO", tmp_path_factory.mktemp("logs") / "consultas.jsonl")
        yield
