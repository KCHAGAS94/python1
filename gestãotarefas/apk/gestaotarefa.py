import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Define o caminho do banco de dados relativo ao local do script
script_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(script_dir, 'gestaoTarefa.db')

# --- Configuração do Banco de Dados ---

def get_db_connection():
    """Cria uma conexão com o banco de dados que retorna linhas como dicionários."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados e cria a tabela se ela não existir."""
    if os.path.exists(DATABASE):
        return  # O banco de dados já existe.

    print("Criando e populando o banco de dados inicial...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                column TEXT NOT NULL,
                priority TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                notes TEXT
            )
        ''')
        # Adiciona dados iniciais apenas na primeira vez
        initial_tasks = [
            ("Configurar ambiente", "Fazer", "urgente", "2025-12-03", "2025-12-04", "Instalar Python e Flask."),
            ("Criar layout inicial", "Em Progresso", "emergente", "2025-12-04", "2025-12-05", "Estrutura básica em HTML/CSS."),
            ("Implementar back-end", "Feito", "necessário", "2025-12-05", "2025-12-06", "Lógica com Flask e DB.")
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, column, priority, start_date, end_date, notes) VALUES (?, ?, ?, ?, ?, ?)",
            initial_tasks
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
    finally:
        if conn:
            conn.close()

# --- Rotas da Aplicação ---

columns = ["Fazer", "Em Progresso", "Feito"]
priorities = ["urgente", "emergente", "necessário", "delegavel"]

@app.route('/')
def index():
    conn = get_db_connection()
    all_tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()

    tasks_by_column = {col: [] for col in columns}
    for task in all_tasks:
        task_dict = dict(task)
        if task_dict['column'] in tasks_by_column:
            tasks_by_column[task_dict['column']].append(task_dict)

    # Ordena a coluna "Fazer" por prioridade
    if "Fazer" in tasks_by_column:
        priority_map = {priority: index for index, priority in enumerate(priorities)}
        tasks_by_column["Fazer"].sort(key=lambda t: priority_map.get(t['priority'], 999))

    return render_template('index.html', tasks_by_column=tasks_by_column, columns=columns, priorities=priorities)

@app.route('/add', methods=['POST'])
def add_task():
    if request.form.get('title'):
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO tasks (title, notes, priority, start_date, end_date, column) VALUES (?, ?, ?, ?, ?, ?)',
            (
                request.form.get('title'),
                request.form.get('notes'),
                request.form.get('priority'),
                request.form.get('start_date'),
                request.form.get('end_date'),
                'Fazer'  # Coluna padrão
            )
        )
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

def get_task(task_id):
    """Busca uma única tarefa pelo ID."""
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    return task

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = get_task(task_id)
    if not task:
        return "Tarefa não encontrada", 404

    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute(
            'UPDATE tasks SET title=?, notes=?, priority=?, start_date=?, end_date=?, column=? WHERE id = ?',
            (
                request.form.get('title'),
                request.form.get('notes'),
                request.form.get('priority'),
                request.form.get('start_date'),
                request.form.get('end_date'),
                request.form.get('column'),
                task_id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task, priorities=priorities, columns=columns)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/move/<int:task_id>/<string:new_column>', methods=['POST'])
def move_task(task_id, new_column):
    if new_column not in columns:
        return "Coluna inválida", 400

    conn = get_db_connection()
    conn.execute(
        'UPDATE tasks SET column = ? WHERE id = ?',
        (new_column, task_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # Garante que o DB e a tabela existam
    app.run(debug=True)