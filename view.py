import csv
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from calculos import mostrar_valor

class FinanceiroView:

    def aviso_erro(self, erro):
        messagebox.showerror('Verifique os dados', str(erro))

    def criar_tabela(self, pai, colunas):
        quadro = ttk.Frame(pai)
        quadro.pack(fill='both', expand=True, pady=10)
        tabela = ttk.Treeview(quadro, columns=colunas, show='headings', selectmode='browse')
        for coluna in colunas:
            tabela.heading(coluna, text=coluna)
            tabela.column(coluna, width=120, minwidth=60)
        barra = ttk.Scrollbar(quadro, orient='vertical', command=tabela.yview)
        horizontal = ttk.Scrollbar(quadro, orient='horizontal', command=tabela.xview)
        tabela.configure(yscrollcommand=barra.set, xscrollcommand=horizontal.set)
        tabela.grid(row=0, column=0, sticky='nsew')
        barra.grid(row=0, column=1, sticky='ns')
        horizontal.grid(row=1, column=0, sticky='ew')
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)
        return tabela

    def limpar_tabela(self, tabela):
        for linha in tabela.get_children():
            tabela.delete(linha)

    def selecionado(self, tabela):
        linhas = tabela.selection()
        if not linhas:
            messagebox.showwarning('Selecione', 'Selecione uma linha na tabela.')
            return None
        return int(linhas[0])

    def nova_janela(self, titulo):
        janela = tk.Toplevel(self.raiz)
        janela.title(titulo)
        janela.transient(self.raiz)
        janela.grab_set()
        quadro = ttk.Frame(janela, padding=15)
        quadro.pack(fill='both', expand=True)
        return (janela, quadro)

    def campo(self, quadro, rotulo, valor='', opcoes=None):
        ttk.Label(quadro, text=rotulo).pack(anchor='w', pady=(8, 2))
        if opcoes is None:
            entrada = ttk.Entry(quadro, width=45)
            entrada.insert(0, valor)
        else:
            entrada = ttk.Combobox(quadro, values=opcoes, state='readonly', width=42)
            entrada.set(valor)
        entrada.pack(fill='x')
        return entrada

    def atualizar(self):
        self.limpar_tabela(self.tabela_contatos)
        for contato in self.presenter.listar_contatos():
            self.tabela_contatos.insert('', 'end', iid=contato['id'], values=(contato['id'], contato['nome'], contato['tipo'], contato['telefone'], contato['email']))
        self.limpar_tabela(self.tabela_contas)
        contas, receber, pagar, vencidas = self.presenter.consultar_contas(self.filtro_tipo.get(), self.filtro_estado.get(), self.busca.get())
        for conta in contas:
            vencimento = date.fromisoformat(conta['vencimento']).strftime('%d/%m/%Y')
            parcela = str(conta['parcela']) + '/' + str(conta['quantidade'])
            self.tabela_contas.insert('', 'end', iid=conta['id'], values=(conta['id'], conta['tipo'], conta['nome'], conta['descricao'], conta['categoria'], parcela, vencimento, mostrar_valor(conta['valor']), mostrar_valor(conta['pago']), mostrar_valor(conta['saldo']), conta['situacao']))
        self.resumo.config(text='A receber: ' + mostrar_valor(receber) + '   |   A pagar: ' + mostrar_valor(pagar) + '   |   Vencidas: ' + mostrar_valor(vencidas))

    def contato_formulario(self, editar=False):
        codigo = None
        nome_inicial = ''
        tipo_inicial = 'Cliente'
        telefone_inicial = ''
        email_inicial = ''
        if editar:
            codigo = self.selecionado(self.tabela_contatos)
            if codigo is None:
                return
            for contato in self.presenter.listar_contatos():
                if contato['id'] == codigo:
                    nome_inicial = contato['nome']
                    tipo_inicial = contato['tipo']
                    telefone_inicial = contato['telefone']
                    email_inicial = contato['email']
        janela, quadro = self.nova_janela('Contato')
        nome = self.campo(quadro, 'Nome', nome_inicial)
        tipo = self.campo(quadro, 'Tipo', tipo_inicial, ['Cliente', 'Fornecedor', 'Ambos'])
        telefone = self.campo(quadro, 'Telefone', telefone_inicial)
        email = self.campo(quadro, 'E-mail', email_inicial)

        def salvar():
            try:
                self.presenter.salvar_contato(nome.get(), tipo.get(), telefone.get(), email.get(), codigo)
                self.atualizar()
                janela.destroy()
            except (ValueError, sqlite3.Error) as erro:
                self.aviso_erro(erro)
        ttk.Button(quadro, text='Salvar contato', command=salvar).pack(pady=12)

    def conta_formulario(self):
        contatos = self.presenter.listar_contatos()
        if not contatos:
            messagebox.showwarning('Contato', 'Cadastre um contato primeiro.')
            return
        nomes = []
        for contato in contatos:
            nomes.append(str(contato['id']) + ' - ' + contato['nome'])
        janela, quadro = self.nova_janela('Nova conta')
        contato = self.campo(quadro, 'Contato', nomes[0], nomes)
        tipo = self.campo(quadro, 'Tipo', 'Receber', ['Receber', 'Pagar'])
        descricao = self.campo(quadro, 'Descrição')
        categoria = self.campo(quadro, 'Categoria', 'Serviços')
        valor = self.campo(quadro, 'Valor TOTAL (exemplo: 150,00)')
        vencimento = self.campo(quadro, 'Primeiro vencimento (DD/MM/AAAA)', date.today().strftime('%d/%m/%Y'))
        parcelas = self.campo(quadro, 'Quantidade de parcelas mensais', '1')

        def salvar():
            try:
                codigo = contatos[nomes.index(contato.get())]['id']
                self.presenter.salvar_conta(codigo, tipo.get(), descricao.get(), categoria.get(), valor.get(), vencimento.get(), parcelas.get())
                self.atualizar()
                janela.destroy()
            except (ValueError, sqlite3.Error) as erro:
                self.aviso_erro(erro)
        ttk.Button(quadro, text='Salvar conta', command=salvar).pack(pady=12)

    def pagamento_formulario(self):
        codigo = self.selecionado(self.tabela_contas)
        if codigo is None:
            return
        for conta in self.presenter.listar_contas():
            if conta['id'] == codigo:
                saldo = conta['valor'] - conta['pago']
        if saldo == 0:
            messagebox.showinfo('Quitada', 'Esta conta já está quitada.')
            return
        janela, quadro = self.nova_janela('Registrar pagamento')
        ttk.Label(quadro, text='Saldo: ' + mostrar_valor(saldo)).pack()
        valor = self.campo(quadro, 'Valor pago', str(saldo // 100) + ',' + str(saldo % 100).zfill(2))
        data = self.campo(quadro, 'Data (DD/MM/AAAA)', date.today().strftime('%d/%m/%Y'))
        observacao = self.campo(quadro, 'Observação')

        def salvar():
            try:
                self.presenter.salvar_pagamento(codigo, valor.get(), data.get(), observacao.get())
                self.atualizar()
                janela.destroy()
            except (ValueError, sqlite3.Error) as erro:
                self.aviso_erro(erro)
        ttk.Button(quadro, text='Salvar pagamento', command=salvar).pack(pady=12)

    def historico(self):
        codigo = self.selecionado(self.tabela_contas)
        if codigo is None:
            return
        janela, quadro = self.nova_janela('Histórico de pagamentos')
        janela.geometry('700x350')
        tabela = self.criar_tabela(quadro, ['ID', 'Data', 'Valor', 'Observação'])

        def carregar():
            self.limpar_tabela(tabela)
            for pagamento in self.presenter.listar_pagamentos(codigo):
                data = date.fromisoformat(pagamento['data']).strftime('%d/%m/%Y')
                tabela.insert('', 'end', iid=pagamento['id'], values=(pagamento['id'], data, mostrar_valor(pagamento['valor']), pagamento['observacao']))

        def estornar():
            pagamento_id = self.selecionado(tabela)
            if pagamento_id is None:
                return
            if messagebox.askyesno('Estornar', 'Remover o pagamento e devolver o valor ao saldo?', parent=janela):
                try:
                    self.presenter.estornar_pagamento(pagamento_id)
                    carregar()
                    self.atualizar()
                except sqlite3.Error as erro:
                    self.aviso_erro(erro)
        ttk.Button(quadro, text='Estornar selecionado', command=estornar).pack()
        carregar()

    def excluir(self):
        codigo = self.selecionado(self.tabela_contas)
        if codigo is None:
            return
        if messagebox.askyesno('Excluir', 'Excluir somente a parcela selecionada?'):
            try:
                self.presenter.excluir_conta(codigo)
                self.atualizar()
            except (ValueError, sqlite3.Error) as erro:
                self.aviso_erro(erro)

    def exportar(self):
        caminho = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')], initialfile='contas.csv')
        if not caminho:
            return
        try:
            with open(caminho, 'w', encoding='utf-8-sig', newline='') as arquivo:
                escritor = csv.writer(arquivo, delimiter=';')
                escritor.writerow(self.tabela_contas['columns'])
                for linha in self.tabela_contas.get_children():
                    valores = []
                    for valor in self.tabela_contas.item(linha)['values']:
                        texto = str(valor)
                        if texto.lstrip().startswith(('=', '+', '-', '@')):
                            texto = "'" + texto
                        valores.append(texto)
                    escritor.writerow(valores)
            messagebox.showinfo('Exportação', 'Arquivo CSV salvo.')
        except OSError as erro:
            self.aviso_erro(erro)

    def relatorio(self):
        try:
            pagamentos, entradas, saidas = self.presenter.consultar_relatorio(self.mes.get())
        except (ValueError, sqlite3.Error) as erro:
            self.aviso_erro(erro)
            return
        self.limpar_tabela(self.tabela_relatorio)
        for pagamento in pagamentos:
            dia = date.fromisoformat(pagamento['data']).strftime('%d/%m/%Y')
            self.tabela_relatorio.insert('', 'end', values=(dia, pagamento['tipo'], pagamento['nome'], pagamento['descricao'], mostrar_valor(pagamento['valor'])))
        self.resumo_mes.config(text='Entradas: ' + mostrar_valor(entradas) + '   |   Saídas: ' + mostrar_valor(saidas) + '   |   Saldo: ' + mostrar_valor(entradas - saidas))

    def __init__(self, presenter):
        self.presenter = presenter
        self.presenter.tela = self
        self.raiz = tk.Tk()
        self.raiz.title('Contas em Dia')
        self.raiz.geometry('1150x700')
        self.raiz.minsize(900, 550)
        try:
            self.presenter.criar_tabelas()
        except sqlite3.Error as erro:
            self.aviso_erro(erro)
            self.raiz.destroy()
            return
        ttk.Label(self.raiz, text='Contas em Dia', font=('Arial', 20, 'bold')).pack(anchor='w', padx=15, pady=10)
        self.resumo = ttk.Label(self.raiz, font=('Arial', 12))
        self.resumo.pack(anchor='w', padx=15, pady=5)
        abas = ttk.Notebook(self.raiz)
        abas.pack(fill='both', expand=True, padx=15, pady=15)
        aba_contas = ttk.Frame(abas, padding=10)
        aba_contatos = ttk.Frame(abas, padding=10)
        aba_relatorio = ttk.Frame(abas, padding=10)
        abas.add(aba_contas, text='Contas')
        abas.add(aba_contatos, text='Contatos')
        abas.add(aba_relatorio, text='Relatório mensal')
        botoes = ttk.Frame(aba_contas)
        botoes.pack(fill='x')
        ttk.Button(botoes, text='Nova conta', command=self.conta_formulario).pack(side='left', padx=3)
        ttk.Button(botoes, text='Pagamento', command=self.pagamento_formulario).pack(side='left', padx=3)
        ttk.Button(botoes, text='Histórico / estorno', command=self.historico).pack(side='left', padx=3)
        ttk.Button(botoes, text='Excluir', command=self.excluir).pack(side='left', padx=3)
        ttk.Button(botoes, text='Exportar CSV', command=self.exportar).pack(side='left', padx=3)
        filtros = ttk.Frame(aba_contas)
        filtros.pack(fill='x', pady=10)
        self.filtro_tipo = ttk.Combobox(filtros, values=['Todas', 'Receber', 'Pagar'], state='readonly', width=12)
        self.filtro_tipo.set('Todas')
        self.filtro_tipo.pack(side='left', padx=3)
        self.filtro_estado = ttk.Combobox(filtros, values=['Todas', 'Aberta', 'Parcial', 'Vencida', 'Quitada'], state='readonly', width=12)
        self.filtro_estado.set('Todas')
        self.filtro_estado.pack(side='left', padx=3)
        ttk.Label(filtros, text='Buscar:').pack(side='left', padx=5)
        self.busca = ttk.Entry(filtros, width=35)
        self.busca.pack(side='left')
        ttk.Button(filtros, text='Atualizar', command=self.atualizar).pack(side='left', padx=5)
        self.tabela_contas = self.criar_tabela(aba_contas, ['ID', 'Tipo', 'Contato', 'Descrição', 'Categoria', 'Parcela', 'Vencimento', 'Valor', 'Pago', 'Saldo', 'Situação'])
        self.filtro_tipo.bind('<<ComboboxSelected>>', lambda evento: self.atualizar())
        self.filtro_estado.bind('<<ComboboxSelected>>', lambda evento: self.atualizar())
        self.busca.bind('<KeyRelease>', lambda evento: self.atualizar())
        botoes_contatos = ttk.Frame(aba_contatos)
        botoes_contatos.pack(fill='x')
        ttk.Button(botoes_contatos, text='Novo contato', command=self.contato_formulario).pack(side='left', padx=3)
        ttk.Button(botoes_contatos, text='Editar contato', command=lambda: self.contato_formulario(True)).pack(side='left', padx=3)
        self.tabela_contatos = self.criar_tabela(aba_contatos, ['ID', 'Nome', 'Tipo', 'Telefone', 'E-mail'])
        topo_relatorio = ttk.Frame(aba_relatorio)
        topo_relatorio.pack(fill='x')
        ttk.Label(topo_relatorio, text='Mês (AAAA-MM):').pack(side='left')
        self.mes = ttk.Entry(topo_relatorio, width=12)
        self.mes.insert(0, date.today().strftime('%Y-%m'))
        self.mes.pack(side='left', padx=8)
        ttk.Button(topo_relatorio, text='Atualizar relatório', command=self.relatorio).pack(side='left')
        self.resumo_mes = ttk.Label(aba_relatorio, text='Clique em Atualizar relatório para consultar os pagamentos.')
        self.resumo_mes.pack(anchor='w', pady=12)
        self.tabela_relatorio = self.criar_tabela(aba_relatorio, ['Data', 'Tipo', 'Contato', 'Descrição', 'Valor'])
        self.atualizar()
        self.raiz.mainloop()
