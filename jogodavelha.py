from flask import Flask, render_template_string, request, redirect, url_for  # importa as funções necessárias do Flask

app = Flask(__name__)  # cria a aplicação Flask e define um nome para ela

# --- Estado do jogo (variáveis globais simples) ---
board = [""] * 9  # representa as 9 casas do tabuleiro como uma lista vazia inicialmente
current_player = "X"  # jogador que começa (X) — alternamos entre "X" e "O"
score = {"X": 0, "O": 0}  # placar dos jogadores: X e O

# --- Template HTML embutido (string) ---
template = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Jogo da Velha - Flask</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 30px; }
        .board { display: grid; grid-template-columns: repeat(3, 120px); gap: 5px; justify-content: center; }
        .cell { width: 120px; height: 120px; font-size: 48px; display:flex; align-items:center; justify-content:center; border:2px solid #333; background:#fff; }
        .controls { margin-top: 20px; }
        button.reset { padding:10px 16px; margin: 6px; font-size:16px; }
        .info { margin-bottom: 12px; font-size:18px; }
        form { display:inline-block; margin:0; padding:0; }
    </style>
</head>
<body>
    <h1>Jogo da Velha</h1>

    <div class="info">
        Jogador atual: <strong>{{ current_player }}</strong><br>
        Placar — X: <strong>{{ score['X'] }}</strong> | O: <strong>{{ score['O'] }}</strong>
    </div>

    <div class="board">
        {% for i in range(9) %}
            <form method="POST" action="/play/{{ i }}">  <!-- cada célula é um formulário que faz POST para /play/<indice> -->
                <button class="cell" type="submit">{{ board[i] if board[i] else '&nbsp;' }}</button> <!-- mostra X, O ou espaço -->
            </form>
        {% endfor %}
    </div>

    <div class="controls">
        <form method="POST" action="/reset_game" style="display:inline-block;">
            <button class="reset" type="submit">Reiniciar Jogo</button> <!-- apenas reinicia o tabuleiro, sem zerar placar -->
        </form>

        <form method="POST" action="/reset_score" style="display:inline-block;">
            <button class="reset" type="submit">Resetar Placar</button> <!-- zera o placar dos dois jogadores -->
        </form>
    </div>

</body>
</html>
"""  # fim do template HTML

# --- Função para verificar se há vencedor ou empate ---
def check_winner(b):  # recebe a lista 'b' representando o tabuleiro
    wins = [  # combinações de índices que definem vitória
        (0,1,2), (3,4,5), (6,7,8),  # linhas
        (0,3,6), (1,4,7), (2,5,8),  # colunas
        (0,4,8), (2,4,6)            # diagonais
    ]
    for a, c, d in wins:  # percorre cada tripla vencedora
        if b[a] != "" and b[a] == b[c] and b[c] == b[d]:  # se as três posições têm mesma marca e não estão vazias
            return b[a]  # retorna "X" ou "O" — o vencedor
    if "" not in b:  # se não há casas vazias e ninguém venceu
        return "Empate"  # resultado de empate
    return None  # jogo continua (nenhum vencedor ainda)

# --- Rota principal: mostra o tabuleiro e o placar ---
@app.route("/")  # rota raiz
def index():
    return render_template_string(template, board=board, score=score, current_player=current_player)  # renderiza o HTML com variáveis

# --- Rota para jogar em uma célula específica ---
@app.route("/play/<int:cell>", methods=["POST"])  # rota que recebe qual célula foi clicada (índice 0..8)
def play(cell):
    global current_player, board, score  # indica que vamos modificar essas variáveis globais
    # somente jogue se a célula estiver vazia
    if board[cell] == "":
        board[cell] = current_player  # marca a célula com o jogador atual (X ou O)

        winner = check_winner(board)  # checa se após a jogada apareceu um vencedor ou empate

        if winner == "X" or winner == "O":  # se há vencedor
            score[winner] += 1  # incrementa o placar do vencedor
            board = [""] * 9  # reinicia o tabuleiro para começar nova partida
            current_player = "X"  # opcional: define X para iniciar próxima partida
        elif winner == "Empate":  # se deu empate
            board = [""] * 9  # reinicia o tabuleiro
            current_player = "X"  # define X para iniciar próxima partida
        else:
            # se ninguém venceu ainda, troca o jogador atual
            current_player = "O" if current_player == "X" else "X"

    return redirect(url_for("index"))  # após a jogada, redireciona de volta para a página principal

# --- Rota para reiniciar APENAS o tabuleiro (nova partida) ---
@app.route("/reset_game", methods=["POST"])
def reset_game():
    global board, current_player  # vamos alterar essas variáveis
    board = [""] * 9  # limpa o tabuleiro
    current_player = "X"  # define X para iniciar
    return redirect(url_for("index"))  # volta para a página principal

# --- Rota para resetar o placar (zerar X e O) ---
@app.route("/reset_score", methods=["POST"])
def reset_score():
    global score  # vamos alterar o placar global
    score = {"X": 0, "O": 0}  # zera os pontos
    return redirect(url_for("index"))  # volta para a página principal

# --- ponto de entrada ---
if __name__ == "__main__":
    app.run(debug=True)  # executa a aplicação em modo debug (recarrega automaticamente em alterações)
