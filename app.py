# app.py - Backend para Sistema de Chamada
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # Permitir requisições cross-origin

# Simulando um banco de dados com arquivo JSON
DB_FILE = 'database.json'

def init_db():
    if not os.path.exists(DB_FILE):
        data = {
            'alunos': [
                {'id': 1, 'nome': 'Ana Silva', 'matricula': '2024001'},
                {'id': 2, 'nome': 'Bruno Souza', 'matricula': '2024002'},
                {'id': 3, 'nome': 'Carla Mendes', 'matricula': '2024003'},
                {'id': 4, 'nome': 'Daniel Costa', 'matricula': '2024004'},
                {'id': 5, 'nome': 'Eduarda Santos', 'matricula': '2024005'}
            ],
            'aulas': [],
            'presencas': []
        }
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)

def get_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    db = get_db()
    return jsonify(db['alunos'])

@app.route('/api/aulas', methods=['POST'])
def criar_aula():
    db = get_db()
    dados = request.json
    
    nova_aula = {
        'id': len(db['aulas']) + 1,
        'data': datetime.now().strftime('%Y-%m-%d'),
        'titulo': dados['titulo'],
        'professor': dados['professor'],
        'horario': dados['horario']
    }
    
    db['aulas'].append(nova_aula)
    save_db(db)
    
    return jsonify(nova_aula), 201

@app.route('/api/presenca', methods=['POST'])
def registrar_presenca():
    db = get_db()
    dados = request.json
    
    # Validações básicas
    if 'aula_id' not in dados or 'aluno_id' not in dados:
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    # Verificar se o aluno existe
    aluno_existe = any(aluno['id'] == dados['aluno_id'] for aluno in db['alunos'])
    if not aluno_existe:
        return jsonify({'erro': 'Aluno não encontrado'}), 404
    
    # Registrar presença
    nova_presenca = {
        'id': len(db['presencas']) + 1,
        'aula_id': dados['aula_id'],
        'aluno_id': dados['aluno_id'],
        'horario': datetime.now().strftime('%H:%M:%S'),
        'status': dados.get('status', 'presente')
    }
    
    db['presencas'].append(nova_presenca)
    save_db(db)
    
    return jsonify(nova_presenca), 201

@app.route('/api/relatorio/<int:aula_id>', methods=['GET'])
def gerar_relatorio(aula_id):
    db = get_db()
    
    # Verificar se a aula existe
    aula = next((a for a in db['aulas'] if a['id'] == aula_id), None)
    if not aula:
        return jsonify({'erro': 'Aula não encontrada'}), 404
    
    # Buscar presença para a aula específica
    presencas = [p for p in db['presencas'] if p['aula_id'] == aula_id]
    
    # Criar relatório com detalhes de alunos
    relatorio = {
        'aula': aula,
        'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'presentes': [],
        'ausentes': []
    }
    
    # Identificar alunos presentes e ausentes
    alunos_presentes_ids = [p['aluno_id'] for p in presencas]
    
    for aluno in db['alunos']:
        if aluno['id'] in alunos_presentes_ids:
            relatorio['presentes'].append(aluno)
        else:
            relatorio['ausentes'].append(aluno)
    
    # Estatísticas
    total_alunos = len(db['alunos'])
    total_presentes = len(relatorio['presentes'])
    
    relatorio['estatisticas'] = {
        'total_alunos': total_alunos,
        'total_presentes': total_presentes,
        'total_ausentes': total_alunos - total_presentes,
        'percentual_presenca': (total_presentes / total_alunos) * 100 if total_alunos > 0 else 0
    }
    
    return jsonify(relatorio)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)