import json
import textwrap
import re
from graphviz import Digraph

def visualize_thoughts_tree(json_path):
    '''Визуализация дерева мыслей'''

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Высокое качество и стиль оформления
    dot = Digraph(comment='Thoughts Tree', format='png')
    dot.attr(dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor="#636363", fontname='Times New Roman', fontsize='12')
    dot.attr('edge', fontname='Times New Roman', fontsize='10')

    # Общая информация в верхнем левом углу 
    gen_info = data.get('general_information', [{}])[0]
    info_text = (
        f"Total Thoughts: {gen_info.get('count_thoughts', 'N/A')}\\n"
        f"Total Time: {gen_info.get('total_time', 0)}s\\n"
        f"Total Tokens: {gen_info.get('total_tokens', 0)}"
    )
    dot.node('info_block', label=info_text, shape='plaintext', fontsize='14', fontname='Arial Bold', justify='l')

    # Проход по всем мыслям и формирование узлов с расширенной информацией
    for node in data['thoughts']:
        node_id = str(node['id'])
        role = node['role'].upper()
        score = node.get('score', 0)
    
        state_raw = node['state'].strip().replace('\n', ' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        feedback_raw = node.get('feedback', '').strip().replace('\n', ' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        state_wrapped = textwrap.fill(state_raw, width=60).replace('\n', '<BR/>')
        feedback_wrapped = textwrap.fill(feedback_raw, width=60).replace('\n', '<BR/>') if feedback_raw else "No feedback"
        
        label = f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                <TR><TD BGCOLOR="#E0E0E0"><B>{role}</B> (Score: {score})</TD></TR>
                <TR><TD ALIGN="LEFT"><B>Thought:</B><BR/>{state_wrapped}</TD></TR>
                <TR><TD ALIGN="LEFT" BGCOLOR="#F0F8FF"><B>Analysis &amp; Evaluation:</B><BR/><I>{feedback_wrapped}</I></TD></TR>
            </TABLE>
        >'''
        
        fillcolor = "#f9f9f9"
        if role == "ROOT": fillcolor = "#ffbc05"
        elif role == "FINAL_ANSWER": fillcolor = "#04ff04"
        
        dot.node(node_id, label=label, fillcolor=fillcolor)
        
        if node.get('parent'):
            dot.edge(str(node['parent']), node_id)
            
    filename = 'D:/Tree_of_Thoughts/logs/img/thoughts_tree_' + re.sub(r'^search_logs_|\.json$', '', json_path.split('/')[-1])
    dot.render(filename, cleanup=True)
