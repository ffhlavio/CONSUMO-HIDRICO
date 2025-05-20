from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Caminho do banco de dados
db_path = 'database/banco.db'
if not os.path.exists(db_path):
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Criar tabela de usuários
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cep TEXT NOT NULL,
            cidade TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Criar tabela de histórico
    cur.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            data TEXT NOT NULL,
            consumo INTEGER NOT NULL,
            comentario TEXT,
            valor_conta REAL
        )
    ''')

    conn.commit()
    conn.close()

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Página Sobre
@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

# Cadastro de usuário
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        dados = (
            request.form['full_name'],
            request.form['email'],
            request.form['telefone'],
            request.form['cep'],
            request.form['cidade'],
            request.form['username'],
            request.form['password']
        )

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO usuarios (full_name, email, telefone, cep, cidade, username, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', dados)
            conn.commit()
            conn.close()

            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('historico'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')

    return render_template('login.html')

# Histórico de consumo
@app.route('/historico')
def historico():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, data, consumo, comentario, valor_conta FROM historico WHERE username=?", (username,))
    registros = cur.fetchall()
    conn.close()

    return render_template('historico.html', registros=registros)

# Adicionar novo registro
@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    data = request.form['data']
    consumo = request.form['consumo']
    comentario = request.form.get('comentario')
    valor_conta = request.form.get('valor_conta')

    if not valor_conta:
        valor_conta = 0

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO historico (username, data, consumo, comentario, valor_conta)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, data, consumo, comentario, valor_conta))
    conn.commit()
    conn.close()

    return redirect(url_for('historico'))

# Editar registro
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_registro(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    if request.method == 'POST':
        data = request.form['data']
        consumo = request.form['consumo']
        comentario = request.form.get('comentario')
        valor_conta = request.form.get('valor_conta') or 0

        cur.execute('''
            UPDATE historico
            SET data=?, consumo=?, comentario=?, valor_conta=?
            WHERE id=? AND username=?
        ''', (data, consumo, comentario, valor_conta, id, session['username']))
        conn.commit()
        conn.close()
        flash('Registro atualizado com sucesso.', 'success')
        return redirect(url_for('historico'))

    # Aqui pegamos todos os campos que o template espera
    cur.execute("SELECT id, username, data, consumo, comentario, valor_conta FROM historico WHERE id=? AND username=?", (id, session['username']))
    registro = cur.fetchone()
    conn.close()

    if not registro:
        flash('Registro não encontrado.', 'danger')
        return redirect(url_for('historico'))

    return render_template('editar.html', registro=registro)

# Deletar registro
@app.route('/deletar/<int:id>')
def deletar_registro(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico WHERE id=? AND username=?", (id, session['username']))
    conn.commit()
    conn.close()
    flash('Registro excluído com sucesso.', 'success')
    return redirect(url_for('historico'))

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Você saiu da conta.', 'success')
    return redirect(url_for('index'))

# Gráficos e estatísticas de consumo
@app.route('/graficos')
def graficos():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT strftime('%Y-%m-%d', data) as data_formatada, consumo 
            FROM historico 
            WHERE username=? 
            ORDER BY data
            """, (username,))
        
        registros = cur.fetchall()
        datas = [registro[0] for registro in registros]
        consumos = [registro[1] for registro in registros]
        
        return render_template('graficos.html', 
                            datas=datas, 
                            consumos=consumos)
    
    except sqlite3.Error as e:
        flash(f"Erro ao acessar dados: {str(e)}", 'danger')
        return redirect(url_for('historico'))
    
    finally:
        if conn:
            conn.close()

# Executar o app
if __name__ == '__main__':
    app.run(debug=True)
    
