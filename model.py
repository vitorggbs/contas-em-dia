import sqlite3
from pathlib import Path
from datetime import date
from calculos import ler_valor, ler_data, dividir_parcelas, vencimento_parcela
PASTA = Path(__file__).resolve().parent

class FinanceiroModel:

    def conectar(self):
        conexao = sqlite3.connect(PASTA / 'financeiro.db')
        conexao.row_factory = sqlite3.Row
        conexao.execute('PRAGMA foreign_keys = ON')
        return conexao

    def criar_tabelas(self):
        conexao = self.conectar()
        with conexao:
            conexao.execute("""CREATE TABLE IF NOT EXISTS contatos (
            id INTEGER PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL,
            telefone TEXT NOT NULL, email TEXT NOT NULL)""")
            conexao.execute("""CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY, contato_id INTEGER NOT NULL REFERENCES contatos(id),
            tipo TEXT NOT NULL, descricao TEXT NOT NULL, categoria TEXT NOT NULL,
            valor INTEGER NOT NULL CHECK(valor > 0), vencimento TEXT NOT NULL,
            parcela INTEGER NOT NULL, quantidade INTEGER NOT NULL)""")
            conexao.execute("""CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY, conta_id INTEGER NOT NULL REFERENCES contas(id),
            valor INTEGER NOT NULL CHECK(valor > 0), data TEXT NOT NULL, observacao TEXT NOT NULL)""")
        conexao.close()

    def salvar_contato(self, nome, tipo, telefone, email, codigo=None):
        if not nome.strip():
            raise ValueError('Digite o nome do contato.')
        if tipo not in ['Cliente', 'Fornecedor', 'Ambos']:
            raise ValueError('Escolha o tipo do contato.')
        conexao = self.conectar()
        with conexao:
            if codigo is None:
                conexao.execute('INSERT INTO contatos (nome,tipo,telefone,email) VALUES (?,?,?,?)', (nome.strip(), tipo, telefone.strip(), email.strip()))
            else:
                conexao.execute('UPDATE contatos SET nome=?,tipo=?,telefone=?,email=? WHERE id=?', (nome.strip(), tipo, telefone.strip(), email.strip(), codigo))
        conexao.close()

    def listar_contatos(self):
        conexao = self.conectar()
        contatos = conexao.execute('SELECT * FROM contatos ORDER BY nome').fetchall()
        conexao.close()
        return contatos

    def salvar_conta(self, contato_id, tipo, descricao, categoria, texto_valor, texto_data, texto_parcelas):
        if not descricao.strip() or not categoria.strip():
            raise ValueError('Preencha descrição e categoria.')
        if tipo not in ['Receber', 'Pagar']:
            raise ValueError('Escolha o tipo da conta.')
        try:
            quantidade = int(texto_parcelas)
        except ValueError:
            raise ValueError('Digite um número inteiro para as parcelas.')
        valor = ler_valor(texto_valor)
        primeira_data = ler_data(texto_data)
        parcelas = dividir_parcelas(valor, quantidade)
        registros = []
        for numero in range(quantidade):
            data = vencimento_parcela(primeira_data, numero)
            registros.append((contato_id, tipo, descricao.strip(), categoria.strip(), parcelas[numero], data.isoformat(), numero + 1, quantidade))
        conexao = self.conectar()
        try:
            with conexao:
                contato = conexao.execute('SELECT id FROM contatos WHERE id=?', (contato_id,)).fetchone()
                if contato is None:
                    raise ValueError('Selecione um contato cadastrado.')
                conexao.executemany("""INSERT INTO contas
                (contato_id,tipo,descricao,categoria,valor,vencimento,parcela,quantidade)
                VALUES (?,?,?,?,?,?,?,?)""", registros)
        finally:
            conexao.close()

    def listar_contas(self):
        conexao = self.conectar()
        contas = conexao.execute("""SELECT contas.*, contatos.nome,
        COALESCE(SUM(pagamentos.valor),0) AS pago
        FROM contas JOIN contatos ON contatos.id=contas.contato_id
        LEFT JOIN pagamentos ON pagamentos.conta_id=contas.id
        GROUP BY contas.id ORDER BY contas.vencimento, contas.id""").fetchall()
        conexao.close()
        return contas

    def salvar_pagamento(self, codigo, texto_valor, texto_data, observacao):
        valor = ler_valor(texto_valor)
        data = ler_data(texto_data)
        if data > date.today():
            raise ValueError('O pagamento não pode ter data futura.')
        conexao = self.conectar()
        try:
            conexao.execute('BEGIN IMMEDIATE')
            conta = conexao.execute('SELECT valor FROM contas WHERE id=?', (codigo,)).fetchone()
            if conta is None:
                raise ValueError('Conta não encontrada.')
            pago = conexao.execute('SELECT COALESCE(SUM(valor),0) FROM pagamentos WHERE conta_id=?', (codigo,)).fetchone()[0]
            saldo = conta['valor'] - pago
            if valor > saldo:
                raise ValueError('O pagamento é maior que o saldo da conta.')
            conexao.execute('INSERT INTO pagamentos (conta_id,valor,data,observacao) VALUES (?,?,?,?)', (codigo, valor, data.isoformat(), observacao.strip()))
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    def listar_pagamentos(self, codigo=None):
        conexao = self.conectar()
        consulta = """SELECT pagamentos.*, contas.tipo, contas.descricao, contatos.nome
        FROM pagamentos JOIN contas ON contas.id=pagamentos.conta_id
        JOIN contatos ON contatos.id=contas.contato_id"""
        if codigo is None:
            pagamentos = conexao.execute(consulta + ' ORDER BY pagamentos.data').fetchall()
        else:
            pagamentos = conexao.execute(consulta + ' WHERE conta_id=? ORDER BY pagamentos.data', (codigo,)).fetchall()
        conexao.close()
        return pagamentos

    def estornar_pagamento(self, codigo):
        conexao = self.conectar()
        with conexao:
            conexao.execute('DELETE FROM pagamentos WHERE id=?', (codigo,))
        conexao.close()

    def excluir_conta(self, codigo):
        conexao = self.conectar()
        try:
            with conexao:
                pagamento = conexao.execute('SELECT id FROM pagamentos WHERE conta_id=?', (codigo,)).fetchone()
                if pagamento is not None:
                    raise ValueError('Esta conta tem pagamentos. Estorne antes de excluir.')
                conexao.execute('DELETE FROM contas WHERE id=?', (codigo,))
        finally:
            conexao.close()
