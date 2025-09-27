import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from fpdf import FPDF
from PIL import Image

# Inicialização do Flask. Esta linha é crucial para o seu aplicativo.
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Classe PDF Personalizada com cabeçalho e rodapé
class PDFPersonalizado(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logo_path = os.path.join(app.static_folder, 'img', 'logo.png')
        self.cliente = ""
        self.data = ""

    def header(self):
        # Logo no canto superior esquerdo
        if os.path.exists(self.logo_path):
            self.image(self.logo_path, 10, 8, 33)
        
        # Título do relatório
        self.set_font('Arial', 'B', 15)
        self.cell(80)  # Move para a direita
        self.cell(30, 10, 'Relatório de Vistoria', 0, 0, 'C')
        self.ln(10)
        
        # Informações do cliente e data abaixo do título
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'Cliente: {self.cliente}', 0, 1, 'C')
        self.cell(0, 5, f'Data: {self.data}', 0, 1, 'C')
        
        # Linha separadora
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        # Rodapé com número da página
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

# Rota para exibir o formulário
@app.route('/')
def formulario():
    return render_template('formulario.html')

# Rota para processar o formulário e gerar o relatório
@app.route('/enviar-vistoria', methods=['POST'])
def enviar_vistoria():
    # Coletar todos os dados do formulário
    id_container = request.form.get('id_container')
    tipo_container = request.form.get('tipo_container')
    data_vistoria = request.form.get('data_vistoria')
    dia_semana = request.form.get('dia_semana')
    nome_cliente = request.form.get('nome_cliente')
    setor = request.form.get('setor')
    local = request.form.get('local')
    contratante = request.form.get('contratante')
    responsavel = request.form.get('responsavel')
    funcao = request.form.get('funcao')
    turno = request.form.get('turno')
    hora_inicio = request.form.get('hora_inicio')
    hora_fim = request.form.get('hora_fim')
    pausas = request.form.get('pausas')
    atividade = request.form.get('atividade')
    status_container = request.form.get('status_container')
    qtd_volumes = request.form.get('qtd_volumes')
    avarias_volumes = request.form.get('avarias_volumes')
    qtd_asp = request.form.get('qtd_asp')
    qtd_empilhadores = request.form.get('qtd_empilhadores')
    observacoes = request.form.get('observacoes')
    
    fotos_salvas = []
    for foto in request.files.getlist('fotos'):
        if foto.filename:
            caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            foto.save(caminho_foto)
            fotos_salvas.append(caminho_foto)
            
    pdf = PDFPersonalizado()
    pdf.alias_nb_pages()
    pdf.cliente = nome_cliente
    pdf.data = data_vistoria
    pdf.add_page()
    
    # Adicionar todas as informações do formulário no PDF
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Detalhes da Vistoria', 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 7, f'ID do Container: {id_container or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Tipo de Container: {tipo_container or "N/A"}"', 0, 1)
    pdf.cell(0, 7, f'Data da Vistoria: {data_vistoria or "N/A"} ({dia_semana or "N/A"})', 0, 1)
    pdf.cell(0, 7, f'Cliente: {nome_cliente or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Setor: {setor or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Local: {local or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Contratante: {contratante or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Responsável: {responsavel or "N/A"} ({funcao or "N/A"})', 0, 1)
    pdf.cell(0, 7, f'Turno: {turno or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Horário: {hora_inicio or "N/A"} - {hora_fim or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Houve pausas?: {pausas or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Atividade: {atividade or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Status do Container: {status_container or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Volumes/Pallets: {qtd_volumes or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Avarias nos volumes?: {avarias_volumes or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Quantidade de ASP: {qtd_asp or "N/A"}', 0, 1)
    pdf.cell(0, 7, f'Quantidade de Empilhadores: {qtd_empilhadores or "N/A"}', 0, 1)

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Observações', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, observacoes or "Nenhuma")
    pdf.ln(5)

    # Lógica para adicionar fotos em grade (4 por página)
    if fotos_salvas:
        # Adiciona uma nova página para as imagens
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Imagens da Vistoria', 0, 1, 'L')
        pdf.ln(5)

        margem = 15
        espacamento = 5
        largura_foto = (210 - 2 * margem - espacamento) / 2
        altura_foto = largura_foto * 3/4
        
        for i in range(0, len(fotos_salvas), 4):
            # Adicionar nova página apenas se não for o primeiro lote de fotos
            if i > 0:
                pdf.add_page()
            
            lote_fotos = fotos_salvas[i:i+4]
            y_atual = pdf.get_y()
            
            for j, caminho_foto in enumerate(lote_fotos):
                posicao_coluna = j % 2
                posicao_linha = j // 2
                
                x_pos = margem + posicao_coluna * (largura_foto + espacamento)
                y_pos = y_atual + posicao_linha * (altura_foto + espacamento + 10)
                
                pdf.set_xy(x_pos, y_pos)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(largura_foto, 10, f'Foto {i+j+1}', 0, 1, 'C')
                
                try:
                    pdf.image(caminho_foto, x=x_pos, y=y_pos + 10, w=largura_foto, h=altura_foto)
                except Exception as e:
                    print(f"Erro ao carregar imagem: {e}")
            
            pdf.set_y(y_atual + 2 * (altura_foto + espacamento + 10) + 10)
            
    nome_arquivo_pdf = f'vistoria_{id_container}_{nome_cliente}.pdf'.replace(' ', '_').replace('/', '_')
    caminho_relatorio = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo_pdf)
    pdf.output(caminho_relatorio)
    
    return redirect(url_for('download_relatorio', filename=nome_arquivo_pdf))

# Rota para baixar o PDF
@app.route('/download/<filename>')
def download_relatorio(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except FileNotFoundError:
        return "Relatório não encontrado.", 404

if __name__ == '__main__':
    app.run(debug=True)
