# Contas em Dia

Aplicação desktop para controlar contas a pagar e a receber, desenvolvida em Python com interface gráfica e banco de dados local.

## Funcionalidades

- Cadastro e edição de clientes e fornecedores.
- Contas a pagar e a receber com parcelamento mensal.
- Registro de pagamentos parciais e estorno.
- Busca e filtros por tipo e situação da conta.
- Relatório mensal de entradas e saídas.
- Exportação das contas para CSV.

## Tecnologias

- Python
- Tkinter
- SQLite
- Padrão MVP (Model, View e Presenter)

## Como executar

Com Python 3.10 ou superior instalado, execute na pasta do projeto:

```bash
python main.py
```

No Windows, também é possível abrir pelo arquivo `iniciar.bat`. Não é necessário instalar bibliotecas externas. O banco de dados é criado automaticamente no primeiro uso.

## Organização

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Inicialização do programa |
| `model.py` | Regras e acesso ao banco de dados |
| `presenter.py` | Comunicação entre a interface e o Model |
| `view.py` | Interface gráfica |
| `calculos.py` | Cálculos de valores, parcelas e datas |
| `testes.py` | Testes das regras e do banco |

## Testes

```bash
python testes.py
```

## Tela do programa

![Tela principal do Contas em Dia](tela-principal.png)
