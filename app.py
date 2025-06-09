from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'banco.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

@app.route('/')
def index():
    usuarios = Usuario.query.all()
    return render_template('index.html', usuarios=usuarios)

# Função para adicionar um usuário
@app.route('/adicionar', methods=['POST'])
def add_usuario():
    try:
        id_user = int(request.form['id-user'])
        nome = request.form['nome-user']
        email = request.form['email-user']

        if id_user and nome and email:
            existe = Usuario.query.filter(
                (Usuario.id == id_user) | (Usuario.email == email)
            ).first()

            if existe:
                usuarios = Usuario.query.all()
                return render_template(
                    'index.html',
                    usuarios=usuarios,
                    mensagem_erro="ID ou e-mail já está cadastrado!"
                )

            novo_usuario = Usuario(id=id_user, nome=nome, email=email)
            db.session.add(novo_usuario)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return "Erro: Todos os campos são obrigatórios!"
    except ValueError:
        usuarios = Usuario.query.all()
        return render_template(
            'index.html',
            usuarios=usuarios,
            mensagem_erro="ID deve ser um número inteiro!"
        )

#Função para deletar um usuário
@app.route('/delete/<int:id>')
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('index'))

#Função para editar um usuário
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        novo_id = int(request.form['id-user'])
        nome = request.form['nome-user']
        email = request.form['email-user']

        # Verifica se já existe outro usuário com o mesmo ID ou Email (exceto o atual)
        conflito = Usuario.query.filter(
            ((Usuario.id == novo_id) | (Usuario.email == email)) & (Usuario.id != usuario.id)
        ).first()

        if conflito:
            erro = "Já existe um usuário com este ID ou email."
            return render_template('editar.html', usuario=usuario, erro=erro)

        # Atualiza dados
        usuario.id = novo_id
        usuario.nome = nome
        usuario.email = email
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('editar.html', usuario=usuario)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
