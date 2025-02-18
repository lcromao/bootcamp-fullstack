from flask import Flask, request, send_from_directory, render_template
from sqlalchemy.exc import IntegrityError

from model import Session, Produto
from model.comentario import Comentario


app = Flask(__name__)


@app.route('/')
def home():
    frutas = ['banana', 'maçã', 'uva']	
    return render_template("home.html",
                           frutas=frutas), 200 # Tente trocar para pretty_home


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/x-icon')


@app.route('/add_produto', methods=['POST'])
def add_produto():
    session = Session()
    produto = Produto(
        nome=request.form.get("nome"),
        quantidade=request.form.get("quantidade"),
        valor=request.form.get("valor")
    )
    try:
        # adicionando produto
        session.add(produto)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        return render_template("produto.html", produto=produto), 200
    except IntegrityError as e:
        error_msg = "Produto de mesmo nome já salvo na base :/"
        return render_template("error.html", error_code=409, 
                               error_msg=error_msg), 409
    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/"
        print(str(e))
        return render_template("error.html", error_code=400, 
                               error_msg=error_msg), 400


@app.route('/get_produto/<produto_id>', methods=['GET'])
def get_produto(produto_id):
    session = Session()
    produto = session.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        error_msg = "Produto não encontrado na base :/"
        return render_template("error.html", error_code= 404, 
                               error_msg=error_msg), 404
    else:
        return render_template("produto.html", produto=produto), 200
    

@app.route('/update_produto/<produto_id>', methods=['POST', 'PUT'])
def update_produto(produto_id):
    session = Session()
    
    # Buscando o produto pelo id
    produto = session.query(Produto).filter(Produto.id == produto_id).first()
    
    # Checando se o produto existe
    if not produto:
        error_msg = "Produto não encontrado na base :/"
        return render_template("error.html", error_code=404, 
                               error_msg=error_msg), 404

    # Recebendo os novos valores do produto
    nome = request.form.get("nome")
    quantidade = request.form.get("quantidade")
    valor = request.form.get("valor")
    
    # Checando se os valores são válidos
    try:
        quantidade = int(quantidade)
        valor = float(valor)
    except ValueError:
        error_msg = "Quantidade ou valor inválidos :/"
        return render_template("error.html", error_code=400, 
                               error_msg=error_msg), 400

    # Atualizando os valores do produto
    if nome and quantidade and valor:
        produto.nome = nome
        produto.quantidade = quantidade
        produto.valor = valor

    try:
        session.commit()
        return render_template("produto.html", produto=produto), 200
    except IntegrityError:
        session.rollback()
        error_msg = "Produto com o mesmo nome já existe :/"
        return render_template("error.html", error_code=409, 
                               error_msg=error_msg), 409
    except Exception as e:
        session.rollback()
        error_msg = "Não foi possível atualizar o produto :/"
        print(str(e))
        return render_template("error.html", error_code=400, 
                               error_msg=error_msg), 400


@app.route('/del_produto/<produto_id>', methods=['DELETE'])
def del_produto(produto_id):
    session = Session()
    # Deletando o produto pelo id
    count = session.query(Produto).filter(Produto.id == produto_id).delete()
    session.commit()
    if count ==1:
        return render_template("deletado.html", produto_id=produto_id), 200
    else: 
        error_msg = "Produto não encontrado na base :/"
        return render_template("error.html", error_code=404, 
                               error_msg=error_msg), 404


@app.route('/add_comentario/<produto_id>', methods=['POST'])
def add_comentario(produto_id):
    session = Session()
    # Buscando o produto pelo id
    produto = session.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        error_msg = "Produto não encontrado na base :/"
        return render_template("error.html", error_code= 404, 
                               error_msg=error_msg), 404

    # Recebendo os valores do comentário
    autor = request.form.get("autor")
    texto = request.form.get("texto")
    n_estrelas = request.form.get("n_estrela")
    if n_estrelas:
        n_estrelas = int(n_estrelas)

    # Criando o comentário
    comentario = Comentario(autor, texto, n_estrelas)
    # Adicionando o comentário ao produto
    produto.adiciona_comentario(comentario)
    session.commit()
    return render_template("produto.html", produto=produto), 200
