from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime, timedelta

def extrair_data_formatada(data_string):
    # Tratamento para valores indicando que a data não está definida
    if 'Adicionar data/hora' in data_string:
        return 'Data não definida'
    
    # Tratamento para datas como Hoje, Amanhã, Ontem
    if data_string.lower() == 'hoje':
        return datetime.now().strftime('%d/%m/%Y')
    elif data_string.lower() == 'amanhã':
        return (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
    elif data_string.lower() == 'ontem':
        return (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
    
    # Tratamento para X dias atrás, X semanas atrás
    dias_atras = re.match(r'(\d+) (dia|semana)s? atrás', data_string)
    if dias_atras:
        if dias_atras.group(2) == 'dia':
            return (datetime.now() - timedelta(days=int(dias_atras.group(1)))).strftime('%d/%m/%Y')
        elif dias_atras.group(2) == 'semana':
            return (datetime.now() - timedelta(weeks=int(dias_atras.group(1)))).strftime('%d/%m/%Y')
    
    # Tratamento para datas no formato "ter., 12 de mar., 11:30"
    match_data = re.match(r'(\w{3}.\s*),\s*(\d{1,2})\s*de\s*(\w+).,\s*(\d{1,2}:\d{2})', data_string)
    if match_data:
        mes_map = {
            'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
            'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
            'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
        }
        mes = mes_map.get(match_data.group(3).lower(), '01')
        data_completa = f"{match_data.group(2)}/{mes}/{datetime.now().year} {match_data.group(4)}"
        return datetime.strptime(data_completa, '%d/%m/%Y %H:%M').strftime('%d/%m/%Y')
    
    # Tratamento para datas no formato "dom., 17 de mar."
    match_data = re.match(r'(\w{3}.\s*),\s*(\d{1,2})\s*de\s*(\w+).', data_string)
    if match_data:
        mes_map = {
            'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
            'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
            'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
        }
        mes = mes_map.get(match_data.group(3).lower(), '01')
        return f"{match_data.group(2)}/{mes}/{datetime.now().year}"
    
    # Se nenhuma correspondência for encontrada, retorna a string original
    return data_string

def extrair_informacoes(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    tarefas = []
    # Definindo um contador para o ID
    id_contador = 1
    for div in soup.find_all('div', class_='xEfhu'):
        # Verifica se a div está dentro da classe PwTVze
        if div.find_parent(class_='PwTVze'):
            concluida = True
        else:
            concluida = False
        
        titulo_element = div.find('div', {'role': 'group'})
        if titulo_element:
            titulo = titulo_element.text.strip()
        else:
            titulo = 'Não encontrado'
        
        descricao_element = div.find('div', {'data-placeholder': 'Detalhes'})
        if descricao_element:
            descricao = descricao_element.text.strip()
            # Separar campos adicionais
            detalhes = descricao.split('\n')
            dificuldade = None
            entregavel = None
            outros_detalhes = []
            for detalhe in detalhes:
                if 'Dificuldade(Em horas)' in detalhe:
                    dificuldade = detalhe.split(':')[-1].strip()
                elif 'Entregável' in detalhe:
                    entregavel = detalhe.split(':')[-1].strip()
                else:
                    outros_detalhes.append(detalhe)
            descricao = '\n'.join(outros_detalhes)
        else:
            descricao = 'Não encontrado'
        
        data_element = div.find('div', {'role': 'button'})
        if data_element:
            data = data_element.text.strip()
            # Aqui você chama a função para formatar a data
            data_formatada = extrair_data_formatada(data)
        else:
            data = 'Não encontrado'
            data_formatada = data
        
        atribuido_para_element = div.find('span', {'title': True})
        if atribuido_para_element:
            atribuido_para = atribuido_para_element['title']
        else:
            atribuido_para = 'Não atribuído'
        
        # Criando o ID único para a tarefa
        id_tarefa = id_contador
        id_contador += 1
        
        tarefa = {
            'ID': id_tarefa,  # Adicionando o ID à tarefa
            'Título': titulo,
            'Descrição': descricao,
            'Dificuldade': dificuldade,
            'Entregável': entregavel,
            'Detalhamento': outros_detalhes,
            'Data': data_formatada,  # Usar a data formatada aqui
            'Atribuído Para': atribuido_para,
            'Tarefa Concluída': concluida
        }
        tarefas.append(tarefa)
    
    return tarefas

# Lendo o conteúdo do arquivo HTML
nome_arquivo_html = 'arquivo.html'
with open(nome_arquivo_html, 'r', encoding='utf-8') as arquivo_html:
    html = arquivo_html.read()

informacoes = extrair_informacoes(html)

# Escrever as informações em um arquivo CSV
nome_arquivo_csv = 'informacoes_tarefas.csv'
with open(nome_arquivo_csv, 'w', newline='', encoding='utf-8') as arquivo_csv:
    colunas = ['ID', 'Título', 'Descrição', 'Dificuldade', 'Entregável', 'Detalhamento', 'Data', 'Atribuído Para', 'Tarefa Concluída']
    escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=colunas)
    
    escritor_csv.writeheader()
    for tarefa in informacoes:
        escritor_csv.writerow(tarefa)

print(f'As informações foram escritas no arquivo "{nome_arquivo_csv}" com sucesso.')
