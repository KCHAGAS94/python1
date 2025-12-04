from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB = "estudo.db"


# ------------------------------------
# CRIAR BANCO DE DADOS AUTOMATICAMENTE
# ------------------------------------
def criar_banco():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE estudos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio TEXT NOT NULL,
                fim TEXT NOT NULL,
                materia TEXT NOT NULL,
                anotacoes TEXT
            )
        """)
        conn.commit()
        conn.close()


criar_banco()


# ------------------------------------
# FUNÇÕES AUXILIARES DE BANCO
# ------------------------------------
def obter_estudos():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, inicio, fim, materia, anotacoes FROM estudos")
    dados = cursor.fetchall()
    conn.close()
    return dados


def obter_estudo_por_id(estudo_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, inicio, fim, materia, anotacoes FROM estudos WHERE id = ?", (estudo_id,))
    dado = cursor.fetchone()
    conn.close()
    return dado


def salvar_estudo(inicio, fim, materia, anotacoes):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO estudos (inicio, fim, materia, anotacoes)
        VALUES (?, ?, ?, ?)
    """, (inicio, fim, materia, anotacoes))
    conn.commit()
    conn.close()


def atualizar_estudo(estudo_id, inicio, fim, materia, anotacoes):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE estudos
        SET inicio = ?, fim = ?, materia = ?, anotacoes = ?
        WHERE id = ?
    """, (inicio, fim, materia, anotacoes, estudo_id))
    conn.commit()
    conn.close()


# ------------------------------------
# TEMPLATE BASE (Bootstrap 5)
# ------------------------------------
template = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Controle de Estudo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        body { background: #eef3ff; }
        .card { border-radius: 14px; }
        textarea { resize: vertical; }
    </style>
</head>
<body>

<div class="container py-5">

    <h1 class="text-center mb-4">📘 Controle de Estudo</h1>

    <!-- FORMULÁRIO PRINCIPAL -->
    <div class="card shadow p-4 mb-5">
        <h4 class="mb-3">Registrar Estudo</h4>

        <form method="POST" action="/">
            <div class="mb-3">
                <label class="form-label">Horário que iniciou</label>
                <input type="time" name="inicio" required class="form-control">
            </div>

            <div class="mb-3">
                <label class="form-label">Horário que parou</label>
                <input type="time" name="fim" required class="form-control">
            </div>

            <div class="mb-3">
                <label class="form-label">Matéria estudada</label>
                <input type="text" name="materia" required class="form-control" placeholder="Ex: Python, Matemática...">
            </div>

            <div class="mb-3">
                <label class="form-label">Anotações</label>
                <textarea name="anotacoes" class="form-control" placeholder="Digite suas anotações"></textarea>
            </div>

            <button type="submit" class="btn btn-primary w-100">Salvar Estudo</button>
        </form>
    </div>


    <h3>📋 Registros</h3>
    <div class="card shadow mt-3">
        <table class="table table-striped table-hover mb-0">
            <thead class="table-primary">
                <tr>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Matéria</th>
                    <th>Anotações</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                {% for id, inicio, fim, materia, anotacoes in estudos %}
                <tr>
                    <td>{{ inicio }}</td>
                    <td>{{ fim }}</td>
                    <td>{{ materia }}</td>
                    <td style="white-space: pre-wrap;">{{ anotacoes }}</td>
                    <td>
                        <a href="/editar/{{ id }}" class="btn btn-sm btn-warning">Editar</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

</div>

</body>
</html>
"""


# ---------------------------
# ROTA PRINCIPAL
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        salvar_estudo(
            request.form["inicio"],
            request.form["fim"],
            request.form["materia"],
            request.form["anotacoes"],
        )
        return redirect("/")

    estudos = obter_estudos()
    return render_template_string(template, estudos=estudos)


# ---------------------------
# TELA DE EDITAR ESTUDO
# ---------------------------
editar_template = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Editar Estudo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        body { background: #eef3ff; }
        .card { border-radius: 14px; }
    </style>
</head>
<body>

<div class="container py-5">

    <h2 class="text-center mb-4">✏ Editar Estudo</h2>

    <div class="card shadow p-4">

        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Horário de início</label>
                <input type="time" name="inicio" value="{{ inicio }}" required class="form-control">
            </div>

            <div class="mb-3">
                <label class="form-label">Horário de fim</label>
                <input type="time" name="fim" value="{{ fim }}" required class="form-control">
            </div>

            <div class="mb-3">
                <label class="form-label">Matéria</label>
                <input type="text" name="materia" value="{{ materia }}" required class="form-control">
            </div>

            <div class="mb-3">
                <label class="form-label">Anotações</label>
                <textarea name="anotacoes" class="form-control">{{ anotacoes }}</textarea>
            </div>

            <button type="submit" class="btn btn-success w-100">Salvar Alterações</button>
        </form>

        <a href="/" class="btn btn-secondary w-100 mt-3">Voltar</a>

    </div>

</div>

</body>
</html>
"""


@app.route("/editar/<int:estudo_id>", methods=["GET", "POST"])
def editar(estudo_id):
    estudo = obter_estudo_por_id(estudo_id)

    if not estudo:
        return "Registro não encontrado", 404

    if request.method == "POST":
        atualizar_estudo(
            estudo_id,
            request.form["inicio"],
            request.form["fim"],
            request.form["materia"],
            request.form["anotacoes"],
        )
        return redirect("/")

    return render_template_string(
        editar_template,
        id=estudo[0],
        inicio=estudo[1],
        fim=estudo[2],
        materia=estudo[3],
        anotacoes=estudo[4],
    )


# ---------------------------
# EXECUTAR
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
