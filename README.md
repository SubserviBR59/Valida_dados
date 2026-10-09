Sistema de Análise de Dados — Sprint 5
Projeto didático em Python para ler um CSV, validar campos com expressões
regulares, tratar exceções e salvar um relatório de registros válidos e inválidos.
Requisitos e execução
Python 3.9 ou superior. Usa somente a biblioteca padrão; não é necessário pip install.
No terminal, dentro da pasta do projeto:
python main.py
O comando usa dados/exemplo.csv e salva relatorios/relatorio.txt.
Para outros arquivos:
python main.py dados/exemplo.csv --saida relatorios/outro_relatorio.txt
Use python3 se esse for o comando disponível no seu computador. As pastas de
saída devem existir. Um relatório existente será substituído; a entrada nunca pode
ser usada como saída. O processamento mantém os registros em memória.
Arquivos
Arquivo	Finalidade
main.py	Leitura, funções regex, exceções, análise e escrita do relatório
dados/exemplo.csv	Seis registros inteiramente fictícios
relatorios/relatorio.txt	Saída real gerada pelo exemplo
test_main.py	Quinze testes automatizados
.gitignore	Exclui cache Python e ambientes virtuais do versionamento


Formato de entrada
CSV em UTF-8, sem BOM, separado por vírgula, com os nomes de colunas exatamente
como abaixo. A ordem das colunas pode variar. data é uma data genérica de
registro; não representa nascimento e não é comparada com a idade.
email,cpf,telefone,data,idade
ana@example.com,000.000.000-00,(11) 90000-0000,29/02/2024,28
bruno@example.org,11111111111,21900000000,15/08/2025,35
carla.example.com,123,(11) 90000-0000,31/02/2025,abc
Espaços no início e fim dos valores são removidos. Colunas adicionais nomeadas
são ignoradas. Linhas curtas são analisadas como campos vazios; campos extras
sem cabeçalho tornam o registro inválido. Linhas totalmente vazias são ignoradas
pelo leitor CSV. A numeração no relatório conta registros, não linhas físicas.
Arquivo com apenas cabeçalho gera relatório com zero registros; arquivo sem
cabeçalho gera erro.
Validações e justificativas
Campo	Regra	Motivo e limite
E-mail	Usuário, @ e domínio com sufixo alfabético de ao menos duas letras	Regra didática simplificada; não cobre todos os e-mails permitidos pelos padrões da internet nem verifica existência
CPF	Onze dígitos ou máscara 000.000.000-00	Valida exclusivamente formato; não calcula dígitos verificadores nem consulta cadastro
Telefone	DDD de dois dígitos, iniciado de 1 a 9; número de oito ou nove dígitos, iniciado de 2 a 9	Aceita (11) 90000-0000, (11)90000-0000 e 11900000000; não verifica DDD real, operadora ou existência; não aceita +55
Data	DD/MM/AAAA e data existente no calendário	Regex confere a máscara; datetime.strptime() rejeita datas como 31/02/2025 e considera anos bissextos
Idade	Conversível em inteiro e entre 0 e 120, inclusive	Conversão demonstra ValueError; faixa demonstra a exceção personalizada


Os CPFs repetidos do exemplo são propositalmente artificiais. Um registro
classificado como válido atende às regras acima, não significa identidade real.
Expressões regulares
Os padrões usam raw strings, como:
r"^(?:\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$"  # CPF
r"^\d{2}/\d{2}/\d{4}$"  # Data
- ^ e $: limites do texto; fullmatch() exige correspondência completa.
- \d: dígito; \w: caractere de palavra; \s: espaço em branco.
- \.: ponto literal; {n}: quantidade exata; {m,n}: faixa de repetições.
- ?: trecho opcional; |: alternativa; (?:...): agrupamento sem captura.
- re.ASCII restringe \d e \w ao alfabeto ASCII nos padrões aplicáveis.
A validação é feita com o motor re do próprio Python, coberto pelos testes.
Não foi utilizada uma ferramenta online de regex.
Exceções tratadas
Exceção	Quando ocorre	Comportamento
FileNotFoundError	CSV não existe	Mensagem clara; não cria relatório
KeyError	Coluna obrigatória ou cabeçalho ausente	Interrompe a análise, informando o problema
ValueError	Idade não inteira	Marca o registro como inválido e continua
ValueError	Data impossível	Função retorna False; registro fica inválido
ValueError	Cabeçalho duplicado ou entrada igual à saída	Interrompe sem sobrescrever a entrada
IdadeInvalidaError	Idade menor que 0 ou maior que 120	Marca o registro como inválido e continua
UnicodeError	Arquivo não decodificável em UTF-8	Informa a codificação exigida
csv.Error	CSV estruturalmente malformado	Interrompe sem gerar relatório parcial
OSError	Falta de permissão, pasta ausente ou falha de escrita	Informa o erro de acesso ou gravação


IdadeInvalidaError herda diretamente de Exception. O programa demonstra
try/except/else/finally: try tenta ler e analisar; except trata a falha;
else gera o relatório quando a análise termina; finally informa o término
nos caminhos de sucesso e erro tratados. A escrita no else tem seu próprio
try, pois erros dentro de else não são capturados pelos except anteriores.
O fechamento automático dos arquivos é responsabilidade de with open().
O código de saída é 0 quando a análise e a gravação terminam e 1 em falhas
tratadas de arquivo/configuração. Ter registros inválidos não é falha de execução:
eles são parte do resultado esperado da análise. Erros de argumentos da linha de
comando são tratados pelo argparse, antes do processamento.
Exemplo de saída
O CSV completo fornecido tem seis registros. A saída começa assim:
RELATÓRIO DE ANÁLISE DE DADOS — SPRINT 5
============================================================
Validação didática: CPF e telefone são verificados por formato.
Total de registros: 6
Registros válidos: 3
Registros inválidos: 3
Percentual de aprovação: 50.00%
A seguir são listados todos os dados válidos e inválidos, com cada motivo de
reprovação. O registro 3 possui erros de e-mail, CPF, data e conversão da idade;
o registro 4 tem idade fora da faixa; o registro 5 tem telefone inválido.
Consulte relatorios/relatorio.txt para a saída integral. O relatório utiliza
f-strings, inclusive para formatar o percentual com duas casas decimais.
Testes
Dentro da pasta do projeto:
python -m unittest -v
Quinze testes verificam máscaras, datas impossíveis, ano bissexto, limites da
idade, exceções, arquivo ausente, coluna ausente, cabeçalho duplicado, CSV vazio,
linhas incompletas, campos extras, UTF-8 inválido, CSV malformado, relatório,
falha de saída e proteção contra sobrescrever a entrada. Todos passaram na
verificação da entrega.