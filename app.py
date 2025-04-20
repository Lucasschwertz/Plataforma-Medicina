from warnings import filters
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash




app = Flask(__name__)

# Defina uma chave secreta para as sessões
app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória

# Função para criar o banco de dados e as tabelas
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Criar tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    # Criar tabela de consultas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medico TEXT NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            paciente TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Rota de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect(url_for('opcoes'))

    mensagem = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # sem hash aqui

        # Verifique o login no banco de dados
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # user[2] = senha
            session['usuario'] = user[1]  # email
            session['role'] = user[3]     # role do banco: 'paciente' ou 'medico'
        else:
            mensagem = 'Login falhou. Usuário ou senha inválidos!'

    return render_template('login.html', mensagem=mensagem)

# Rota de cadastro de novos usuários
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    mensagem = ''
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        role = request.form['role']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verifica se o email já está cadastrado
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        existente = cursor.fetchone()

        if existente:
            mensagem = 'E-mail já está cadastrado.'
        else:
            senha_hash = generate_password_hash(senha)
            cursor.execute('INSERT INTO users (email, password, role) VALUES (?, ?, ?)', (email, senha_hash, role))
            conn.commit()
            mensagem = 'Cadastro realizado com sucesso. Faça login.'

        conn.close()

    return render_template('cadastro.html', mensagem=mensagem)


# Rota de Excluir Conta
@app.route('/excluir_conta', methods=['POST'])
def excluir_conta():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    email = session['usuario']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE email = ?', (email,))
    conn.commit()
    conn.close()

    session.pop('usuario', None)  # Desloga o usuário
    return redirect(url_for('login'))

# Rota de Definir Senha
@app.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    mensagem = ''
    if request.method == 'POST':
        email = request.form['email']
        nova_senha = request.form['nova_senha']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if not user:
            mensagem = 'E-mail não encontrado no sistema.'
        else:
            nova_senha_hash = generate_password_hash(nova_senha)
            cursor.execute('UPDATE users SET password = ? WHERE email = ?', (nova_senha_hash, email))
            conn.commit()
            mensagem = 'Senha atualizada com sucesso. Faça login.'

        conn.close()

    return render_template('redefinir_senha.html', mensagem=mensagem)


# Rota de agendamento de consultas
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Verifica se o usuário está logado
    
    paciente_nome = session.get('usuario')
    
    if request.method == 'POST':
        medico = request.form['medico']
        tipo_consulta = request.form['tipo_consulta']  # Tipo de consulta
        data = request.form['data']
        horario = request.form['horario']
        paciente = request.form['paciente']
        observacoes = request.form['observacoes']  # Observações do paciente

        # Validação de data (não pode ser no passado)
        data_atual = datetime.now().date()
        data_selecionada = datetime.strptime(data, '%Y-%m-%d').date()

        if data_selecionada < data_atual:
            mensagem = 'A data do agendamento não pode ser no passado.'
            return render_template('agendar.html', mensagem=mensagem)

        # Verificar se já existe uma consulta agendada para o mesmo médico, data e horário
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments WHERE medico = ? AND data = ? AND horario = ?', 
                       (medico, data, horario))
        consulta_existente = cursor.fetchone()
        conn.close()

        if consulta_existente:
            mensagem = 'Já existe uma consulta agendada para este horário.'
            return render_template('agendar.html', mensagem=mensagem)

        # Inserir consulta no banco de dados
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO appointments (medico, tipo_consulta, data, horario, paciente, observacoes) VALUES (?, ?, ?, ?, ?, ?)', 
                       (medico, tipo_consulta, data, horario, paciente, observacoes))
        conn.commit()
        conn.close()

        # Redireciona para a página de sucesso após agendar a consulta
        return redirect(url_for('sucesso'))  # Redirecionamento para a página de sucesso após agendamento

    return render_template('agendar.html')


@app.route('/sucesso', methods=['GET'])
def sucesso():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Redireciona para o login caso o usuário não esteja logado
    
    return render_template('sucesso.html')  # Exibe a página de sucesso

# rota e a página de consulta virtual (só protótipo)
@app.route('/consulta_virtual', methods=['GET'])
def consulta_virtual():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Verifica se o usuário está logado

    return render_template('consulta_virtual.html')  # Exibe a página de consulta virtual (simulada)




# Rota de histórico de consultas
@app.route('/historico', methods=['GET'])
def historico():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Verifica se o usuário está logado

    paciente_nome = session.get('usuario')

    # Obtendo os parâmetros de filtro
    medico = request.args.get('medico', '')
    tipo_consulta = request.args.get('tipo_consulta', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Obter a lista de médicos e tipos de consulta para o filtro
    cursor.execute('SELECT DISTINCT medico FROM appointments')
    medicos = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT DISTINCT tipo_consulta FROM appointments')
    tipos_consulta = [row[0] for row in cursor.fetchall()]

    # Filtros para a consulta
    query = 'SELECT * FROM appointments WHERE paciente = ?'
    params = [paciente_nome]

    # Adicionando filtros à query
    if medico:
        query += ' AND medico LIKE ?'
        params.append(f'%{medico}%')
    if tipo_consulta:
        query += ' AND tipo_consulta LIKE ?'
        params.append(f'%{tipo_consulta}%')
    if data_inicio:
        query += ' AND data >= ?'
        params.append(data_inicio)
    if data_fim:
        query += ' AND data <= ?'
        params.append(data_fim)

    cursor.execute(query, params)
    consultas = cursor.fetchall()
    conn.close()

    # Passa os médicos e tipos de consulta para o template
    return render_template('historico.html', consultas=consultas, medicos=medicos, tipos_consulta=tipos_consulta, filtros={'medico': medico, 'tipo_consulta': tipo_consulta, 'data_inicio': data_inicio, 'data_fim': data_fim})

# Rota de perfil
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:  # Verifica se o usuário está logado
        return redirect(url_for('login'))  # Redireciona para o login
    
    paciente_nome = session.get('usuario')  # Nome do paciente logado

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Verifica os dados do usuário
    cursor.execute('SELECT email FROM users WHERE email = ?', (paciente_nome,))
    usuario = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        novo_email = request.form['email']
        nova_senha = generate_password_hash(request.form['senha'])
        
        # Atualiza os dados no banco de dados
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET email = ?, password = ? WHERE email = ?', 
                       (novo_email, nova_senha, paciente_nome))
        conn.commit()
        conn.close()

        session['usuario'] = novo_email  # Atualiza a sessão com o novo email

        mensagem = 'Dados atualizados com sucesso!'
        return render_template('perfil.html', mensagem=mensagem, usuario=novo_email)

    return render_template('perfil.html', usuario=usuario[0])

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)  # Remove a variável de sessão
    return redirect(url_for('login'))  # Redireciona para a página de login

# Rota de opções
@app.route('/opcoes', methods=['GET'])
def opcoes():
    if 'usuario' not in session:  # Verifica se o usuário está logado
        return redirect(url_for('login'))  # Redireciona para o login caso o usuário não esteja logado
    return render_template('opcoes.html')  # Exibe a página de opções


if __name__ == '__main__':
    init_db()  # 👉 isso garante que o banco seja criado
    app.run(debug=True)


def update_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''ALTER TABLE appointments ADD COLUMN tipo_consulta TEXT''')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('''ALTER TABLE appointments ADD COLUMN observacoes TEXT''')
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    update_db()
    app.run(debug=True)
