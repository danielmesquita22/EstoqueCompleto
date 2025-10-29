from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

def conectar():
    return sqlite3.connect('banco.db')

def criar_tabela():
    con = conectar()
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            preco INTEGER,
            descricao TEXT,
            imagem TEXT
        )
    ''')
    con.commit()
    con.close()

criar_tabela()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/produtos', methods=['GET'])
def listar():
    con = conectar()
    cur = con.cursor()
    cur.execute('SELECT * FROM produtos')
    dados = cur.fetchall()
    con.close()

    produtos = [{"id": a[0], "nome": a[1], "preco": a[2], "descricao": a[3], "imagem": a[4]} for a in dados]
    return jsonify(produtos)


@app.route('/produtos', methods=['POST'])
def adicionar():
    novo = request.get_json()
    nome = novo.get('nome')
    preco = novo.get('preco')
    descricao = novo.get('descricao')
    imagem = novo.get('imagem')

    con = conectar()
    cur = con.cursor()
    cur.execute('INSERT INTO produtos (nome, preco, descricao, imagem) VALUES (?, ?, ?, ?)', (nome, preco, descricao, imagem))
    con.commit()
    con.close()

    return jsonify({'mensagem': "Produto adicionado com sucesso!"})

@app.route('/produtos/<int:id>', methods=['DELETE'])
def deletar(id):
    con = conectar()
    cur = con.cursor()
    cur.execute('DELETE FROM produtos WHERE id=?', (id,))
    con.commit()
    con.close()

    return jsonify({'mensagem': f"Produto {id} deletado com sucesso!"})

@app.route('/produtos/<int:id>', methods=['PUT'])
def atualizar(id):
    dados = request.get_json()
    nome = dados.get('nome')
    preco = dados.get('preco')
    descricao = dados.get('descricao')
    imagem = dados.get('imagem')

    con = conectar()
    cur = con.cursor()
    cur.execute('UPDATE produtos SET nome=?, preco=?, descricao=?, imagem=? WHERE id=?', (nome, preco, descricao, imagem, id))
    con.commit()
    con.close()
    
    return jsonify({'mensagem': "Produto atualizado com sucesso"})

@app.route('/produtos/pesquisar')
def pesquisar():
    con = conectar()
    cur = con.cursor()

    termo = request.args.get('termo')
    preco_min = request.args.get('preco_min')
    preco_max = request.args.get('preco_max')

    query = 'SELECT * FROM produtos WHERE 1=1'
    params = []

    if termo:
        query += ' AND (nome LIKE ? OR descricao LIKE ?)'
        params.extend([f'%{termo}%', f'%{termo}%'])

    if preco_min:
        query += ' AND preco >= ?'
        params.append(preco_min)

    if preco_max:
        query += ' AND preco <= ?'
        params.append(preco_max)

    cur.execute(query, params)
    dados = cur.fetchall()
    con.close()

    resultado = [{"id": a[0], "nome": a[1], "preco": a[2], "descricao": a[3], "imagem": a[4]} for a in dados]
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)

