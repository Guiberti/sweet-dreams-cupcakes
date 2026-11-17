"""Model FeedbackTeste - laudos dos testadores (Situação-Problema 3)."""
from ..db import get_db


class FeedbackTeste:
    @staticmethod
    def validar(dados: dict) -> list[str]:
        erros = []
        if len((dados.get("nome_testador") or "").strip()) < 3:
            erros.append("Informe seu nome.")
        if not dados.get("data_teste"):
            erros.append("Informe a data do teste.")
        if not any((dados.get(c) or "").strip() for c in ("funcionou", "nao_funcionou", "sugestoes")):
            erros.append("Descreva pelo menos o que funcionou, o que não funcionou ou uma sugestão.")
        nota = dados.get("nota")
        if nota and (not str(nota).isdigit() or not 1 <= int(nota) <= 5):
            erros.append("A nota deve ser de 1 a 5.")
        return erros

    @staticmethod
    def criar(dados: dict, print_arquivo: str | None = None) -> int:
        db = get_db()
        cur = db.execute(
            "INSERT INTO feedback_teste (nome_testador, perfil_testador, data_teste, funcionou, nao_funcionou, "
            "nao_testado, sugestoes, nota, print_arquivo) VALUES (?,?,?,?,?,?,?,?,?)",
            tuple((dados.get(c) or "").strip() or None for c in
                  ("nome_testador", "perfil_testador", "data_teste", "funcionou", "nao_funcionou",
                   "nao_testado", "sugestoes")) + (int(dados["nota"]) if dados.get("nota") else None, print_arquivo))
        db.commit()
        return cur.lastrowid

    @staticmethod
    def listar():
        return get_db().execute("SELECT * FROM feedback_teste ORDER BY id").fetchall()
