import tempfile
from pathlib import Path
from datetime import date
import model
from model import FinanceiroModel
from calculos import ler_valor, dividir_parcelas, vencimento_parcela, situacao
from presenter import FinanceiroPresenter

banco = FinanceiroModel()

def deve_recusar(funcao, *argumentos):
    try:
        funcao(*argumentos)
    except ValueError:
        return
    raise AssertionError('A entrada inválida foi aceita.')

def testar():
    assert ler_valor('1.250,50') == 125050
    assert ler_valor('25.50') == 2550
    for texto in ['0', '-1', 'abc', 'NaN', 'Infinity', '1,234']:
        deve_recusar(ler_valor, texto)
    assert dividir_parcelas(10000, 3) == [3334, 3333, 3333]
    deve_recusar(dividir_parcelas, 100, 0)
    deve_recusar(dividir_parcelas, 2, 3)
    assert vencimento_parcela(date(2024, 1, 31), 1) == date(2024, 2, 29)
    assert vencimento_parcela(date(2024, 1, 31), 2) == date(2024, 3, 31)
    assert situacao(100, 100, '2020-01-01') == 'Quitada'
    assert situacao(100, 10, '2020-01-01') == 'Vencida'
    pasta_original = model.PASTA
    try:
        with tempfile.TemporaryDirectory() as pasta:
            model.PASTA = Path(pasta)
            banco.criar_tabelas()
            banco.criar_tabelas()
            banco.salvar_contato('Ana', 'Cliente', '', '')
            contato = banco.listar_contatos()[0]['id']
            hoje = date.today().strftime('%d/%m/%Y')
            banco.salvar_conta(contato, 'Receber', 'Venda', 'Serviços', '100', hoje, '3')
            contas = banco.listar_contas()
            assert len(contas) == 3
            presenter = FinanceiroPresenter(banco)
            filtradas, receber, pagar, vencidas = presenter.consultar_contas('Receber', 'Todas', 'venda')
            assert len(filtradas) == 3
            assert receber == 10000
            assert pagar == 0
            assert sum((conta['valor'] for conta in contas)) == 10000
            codigo = contas[0]['id']
            banco.salvar_pagamento(codigo, '10', hoje, '')
            assert banco.listar_contas()[0]['pago'] == 1000
            pagamentos, entradas, saidas = presenter.consultar_relatorio(date.today().strftime('%Y-%m'))
            assert len(pagamentos) == 1
            assert entradas == 1000
            assert saidas == 0
            deve_recusar(presenter.consultar_relatorio, '2026-13')
            deve_recusar(banco.salvar_pagamento, codigo, '24', hoje, '')
            assert len(banco.listar_pagamentos(codigo)) == 1
            deve_recusar(banco.excluir_conta, codigo)
            banco.estornar_pagamento(banco.listar_pagamentos(codigo)[0]['id'])
            assert banco.listar_contas()[0]['pago'] == 0
            banco.salvar_pagamento(codigo, '33,34', hoje, '')
            assert situacao(3334, banco.listar_contas()[0]['pago'], contas[0]['vencimento']) == 'Quitada'
            deve_recusar(banco.salvar_conta, contato, 'Pagar', 'x', 'x', '10', '31/12/9999', '2')
            assert len(banco.listar_contas()) == 3
            banco.excluir_conta(contas[1]['id'])
            assert len(banco.listar_contas()) == 2
    finally:
        model.PASTA = pasta_original
    print('Todos os testes passaram. Nenhum dado real foi alterado.')
if __name__ == '__main__':
    testar()
