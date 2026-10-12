import calendar
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

def ler_valor(texto):
    texto = texto.strip().replace('R$', '').strip()
    if ',' in texto:
        texto = texto.replace('.', '').replace(',', '.')
    try:
        valor = Decimal(texto)
        if not valor.is_finite() or valor <= 0 or valor > 999999999:
            raise ValueError('Digite um valor positivo de até R$ 999.999.999,00.')
        centavos = valor * 100
        if centavos != centavos.to_integral_value():
            raise ValueError('Use no máximo duas casas decimais.')
        return int(centavos)
    except InvalidOperation:
        raise ValueError('Digite um valor como 150,00 ou 1.250,50.')

def mostrar_valor(centavos):
    reais = abs(centavos) // 100
    resto = abs(centavos) % 100
    texto = f'{reais:,}'.replace(',', '.')
    sinal = '-' if centavos < 0 else ''
    return f'{sinal}R$ {texto},{resto:02d}'

def ler_data(texto):
    try:
        return datetime.strptime(texto.strip(), '%d/%m/%Y').date()
    except ValueError:
        raise ValueError('Digite uma data válida: DD/MM/AAAA.')

def dividir_parcelas(total, quantidade):
    if quantidade < 1 or quantidade > 120:
        raise ValueError('Use de 1 a 120 parcelas.')
    if total < quantidade:
        raise ValueError('Cada parcela precisa ter pelo menos um centavo.')
    valor = total // quantidade
    sobra = total % quantidade
    parcelas = []
    for numero in range(quantidade):
        if numero < sobra:
            parcelas.append(valor + 1)
        else:
            parcelas.append(valor)
    return parcelas

def vencimento_parcela(primeira_data, numero):
    mes = primeira_data.month + numero
    ano = primeira_data.year
    while mes > 12:
        mes = mes - 12
        ano = ano + 1
    if ano > 9999:
        raise ValueError('As parcelas ultrapassam o limite de datas.')
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    dia = min(primeira_data.day, ultimo_dia)
    return date(ano, mes, dia)

def situacao(valor, pago, vencimento):
    if pago == valor:
        return 'Quitada'
    if date.fromisoformat(vencimento) < date.today():
        return 'Vencida'
    if pago > 0:
        return 'Parcial'
    return 'Aberta'
