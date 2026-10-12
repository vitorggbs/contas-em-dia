from datetime import date
from calculos import situacao


class FinanceiroPresenter:
    def __init__(self, model):
        self.model = model
        self.tela = None

    def criar_tabelas(self):
        self.model.criar_tabelas()

    def listar_contatos(self):
        return self.model.listar_contatos()

    def salvar_contato(self, nome, tipo, telefone, email, codigo=None):
        self.model.salvar_contato(nome, tipo, telefone, email, codigo)

    def listar_contas(self):
        return self.model.listar_contas()

    def salvar_conta(self, contato, tipo, descricao, categoria, valor, data, parcelas):
        self.model.salvar_conta(contato, tipo, descricao, categoria, valor, data, parcelas)

    def salvar_pagamento(self, codigo, valor, data, observacao):
        self.model.salvar_pagamento(codigo, valor, data, observacao)

    def listar_pagamentos(self, codigo=None):
        return self.model.listar_pagamentos(codigo)

    def estornar_pagamento(self, codigo):
        self.model.estornar_pagamento(codigo)

    def excluir_conta(self, codigo):
        self.model.excluir_conta(codigo)

    def consultar_contas(self, tipo, estado, busca):
        contas_filtradas = []
        receber = 0
        pagar = 0
        vencidas = 0
        for registro in self.model.listar_contas():
            conta = dict(registro)
            conta['saldo'] = conta['valor'] - conta['pago']
            conta['situacao'] = situacao(conta['valor'], conta['pago'], conta['vencimento'])
            if conta['tipo'] == 'Receber':
                receber += conta['saldo']
            else:
                pagar += conta['saldo']
            if conta['situacao'] == 'Vencida':
                vencidas += conta['saldo']
            if tipo != 'Todas' and tipo != conta['tipo']:
                continue
            if estado != 'Todas' and estado != conta['situacao']:
                continue
            texto = conta['nome'] + ' ' + conta['descricao'] + ' ' + conta['categoria']
            if busca.lower() not in texto.lower():
                continue
            contas_filtradas.append(conta)
        return contas_filtradas, receber, pagar, vencidas

    def consultar_relatorio(self, mes):
        try:
            data = date.fromisoformat(mes.strip() + '-01')
        except ValueError:
            raise ValueError('Digite o mês no formato AAAA-MM.')
        prefixo = data.strftime('%Y-%m')
        pagamentos = []
        entradas = 0
        saidas = 0
        for pagamento in self.model.listar_pagamentos():
            if pagamento['data'][:7] != prefixo:
                continue
            pagamentos.append(pagamento)
            if pagamento['tipo'] == 'Receber':
                entradas += pagamento['valor']
            else:
                saidas += pagamento['valor']
        return pagamentos, entradas, saidas
