from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from psycopg2 import IntegrityError
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


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
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute('''
                INSERT INTO usuarios
                (full_name, email, telefone, cep, cidade, username, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', dados)

            conn.commit()
            conn.close()

            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('login'))

        except IntegrityError:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return redirect(url_for('cadastro'))

    return render_template('cadastro.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM usuarios WHERE username=%s AND password=%s",
            (username, password)
        )

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

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, data, consumo, comentario, valor_conta FROM historico WHERE username=%s",
        (username,)
    )

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

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO historico
        (username, data, consumo, comentario, valor_conta)
        VALUES (%s, %s, %s, %s, %s)
    ''', (username, data, consumo, comentario, valor_conta))

    conn.commit()
    conn.close()

    return redirect(url_for('historico'))


# Editar registro
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_registro(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        data = request.form['data']
        consumo = request.form['consumo']
        comentario = request.form.get('comentario')
        valor_conta = request.form.get('valor_conta') or 0

        cur.execute('''
            UPDATE historico
            SET data=%s, consumo=%s, comentario=%s, valor_conta=%s
            WHERE id=%s AND username=%s
        ''', (data, consumo, comentario, valor_conta, id, session['username']))

        conn.commit()
        conn.close()

        flash('Registro atualizado com sucesso.', 'success')
        return redirect(url_for('historico'))

    cur.execute('''
        SELECT id, username, data, consumo, comentario, valor_conta
        FROM historico
        WHERE id=%s AND username=%s
    ''', (id, session['username']))

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

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM historico WHERE id=%s AND username=%s",
        (id, session['username'])
    )

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


# Executar o app
if __name__ == '__main__':
    app.run(debug=True)