from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Dados de exemplo em memória
tasks = [
    {
        "id": 1,
        "title": "Configurar ambiente de desenvolvimento",
        "column": "Fazer",
        "priority": "urgente",
        "start_date": "2025-12-03",
        "end_date": "2025-12-04",
        "notes": "Instalar Python, Flask e outras dependências."
    },
    {
        "id": 2,
        "title": "Criar layout inicial",
        "column": "Em Progresso",
        "priority": "emergente",
        "start_date": "2025-12-04",
        "end_date": "2025-12-05",
        "notes": "Usar HTML e CSS para a estrutura básica."
    },
    {
        "id": 3,
        "title": "Implementar back-end",
        "column": "Feito",
        "priority": "necessário",
        "start_date": "2025-12-05",
        "end_date": "2025-12-06",
        "notes": "Desenvolver a lógica com Flask."
    }
]
next_id = 4

# Definição das colunas e prioridades
columns = ["Fazer", "Em Progresso", "Feito"]
priorities = ["urgente", "emergente", "necessário", "delegavel"]

@app.route('/')
def index():
    # Organiza as tarefas por coluna para exibição
    tasks_by_column = {col: [] for col in columns}
    for task in tasks:
        if task['column'] in tasks_by_column:
            tasks_by_column[task['column']].append(task)
    return render_template('index.html', tasks_by_column=tasks_by_column, columns=columns, priorities=priorities)

@app.route('/add', methods=['POST'])
def add_task():
    global next_id
    title = request.form.get('title')
    notes = request.form.get('notes')
    priority = request.form.get('priority')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if title:
        new_task = {
            "id": next_id,
            "title": title,
            "column": "Fazer",  # Coluna padrão para novas tarefas
            "priority": priority,
            "start_date": start_date,
            "end_date": end_date,
            "notes": notes
        }
        tasks.append(new_task)
        next_id += 1
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return "Tarefa não encontrada", 404

    if request.method == 'POST':
        task['title'] = request.form.get('title', task['title'])
        task['priority'] = request.form.get('priority', task['priority'])
        task['start_date'] = request.form.get('start_date', task['start_date'])
        task['end_date'] = request.form.get('end_date', task['end_date'])
        task['notes'] = request.form.get('notes', task['notes'])
        task['column'] = request.form.get('column', task['column'])
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task, priorities=priorities, columns=columns)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Garante que a pasta de templates exista
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
