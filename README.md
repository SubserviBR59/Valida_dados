# ValidaDados

Sistema de análise e validação de dados desenvolvido em Python para o **Desafio Sprint 5 — Semana 05**.

O programa lê um arquivo CSV, verifica as informações de cada registro e gera um relatório com os dados válidos, inválidos e as estatísticas da análise.

## Funcionalidades

- Leitura de arquivos CSV com codificação UTF-8.
- Validação de e-mail, CPF, telefone e data com expressões regulares.
- Validação da idade com regra de negócio.
- Tratamento de erros de leitura, conversão e gravação.
- Relatório formatado com f-strings.
- Testes automatizados.

## Tecnologias

- Python 3.9 ou superior.
- Bibliotecas padrão: `csv`, `re`, `datetime`, `pathlib` e `argparse`.
- Testes com `unittest`.

Não é necessário instalar bibliotecas externas.

## Estrutura do projeto

| Arquivo | Descrição |
| --- | --- |
| `main.py` | Programa principal |
| `dados/exemplo.csv` | Dados fictícios para análise |
| `relatorios/relatorio.txt` | Relatório gerado pelo programa |
| `test_main.py` | Testes automatizados |
| `README.md` | Documentação do projeto |

## Como executar

1. Baixe ou clone o repositório.
2. Abra o terminal na pasta do projeto.
3. Execute:

```bash
python main.py
```

O programa lê `dados/exemplo.csv` e salva o resultado em `relatorios/relatorio.txt`.

Para informar outros caminhos:

```bash
python main.py dados/exemplo.csv --saida relatorios/outro_relatorio.txt
```

A pasta de saída deve existir. Se o arquivo de relatório já existir, seu conteúdo será substituído.

Em sistemas que utilizam esse comando, substitua `python` por `python3`.

## Arquivo de entrada

O CSV deve utilizar codificação **UTF-8**, separador **vírgula** e as seguintes colunas obrigatórias:

```csv
email,cpf,telefone,data,idade
ana@example.com,000.000.000-00,(11) 90000-0000,29/02/2024,28
bruno@example.org,11111111111,21900000000,15/08/2025,35
carla.example.com,123,(11) 90000-0000,31/02/2025,abc
davi@example.com,222.222.222-22,11900000000,10/10/2025,150
elisa@example.com,333.333.333-33,123,01/01/2025,22
fabio@example.net,44444444444,(31)90000-0000,01/12/2025,0
```

Todos os dados do exemplo são fictícios. Os registros inválidos foram incluídos propositalmente para demonstrar as validações.

## Regras de validação

| Campo | Regra aplicada |
| --- | --- |
| E-mail | Formato simplificado com usuário, `@` e domínio |
| CPF | Onze dígitos, com ou sem a máscara `000.000.000-00` |
| Telefone | DDD e número de oito ou nove dígitos, nos formatos aceitos |
| Data | Formato `DD/MM/AAAA` e existência da data no calendário |
| Idade | Número inteiro entre 0 e 120 anos |

### Expressões regulares

Os padrões são definidos com raw strings e verificados com o módulo `re`.

Exemplo de padrão para CPF:

```python
r"^(?:\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$"
```

Exemplo de padrão para data:

```python
r"^\d{2}/\d{2}/\d{4}$"
```

São utilizados recursos como:

- `^` e `$`: delimitam o início e o fim do texto.
- `\d`: representa dígitos.
- `\w`: representa caracteres de palavra.
- `\s`: representa espaços em branco.
- `{n}`: define a quantidade de repetições.
- `|`: permite alternativas de formato.

A função `fullmatch()` exige que todo o campo corresponda ao padrão.

### Limites das validações

O CPF é validado somente pelo formato, sem cálculo dos dígitos verificadores ou consulta cadastral.

E-mail e telefone não são consultados em serviços externos. Portanto, um formato válido não comprova que esses contatos existem.

A data também é verificada com `datetime.strptime()`, permitindo rejeitar valores como `31/02/2025`.

## Tratamento de exceções

| Exceção | Situação tratada |
| --- | --- |
| `FileNotFoundError` | Arquivo de entrada inexistente |
| `KeyError` | Coluna obrigatória ou cabeçalho ausente |
| `ValueError` | Conversão inválida da idade ou configuração inconsistente |
| `IdadeInvalidaError` | Idade fora da faixa permitida |
| `UnicodeError` | Codificação incompatível com UTF-8 |
| `csv.Error` | Estrutura inválida do CSV |
| `OSError` | Falha de acesso ou gravação |

A exceção personalizada herda de `Exception`:

```python
class IdadeInvalidaError(Exception):
    """Idade fora da faixa permitida."""
```

O programa utiliza:

- `try`: executa operações que podem falhar.
- `except`: trata as exceções previstas.
- `else`: executa quando o bloco `try` termina sem exceções.
- `finally`: informa o encerramento do processamento.

Os arquivos são abertos com `with open()`, garantindo seu fechamento automático.

Erros em campos tornam o registro inválido, mas permitem analisar os demais. Falhas na leitura ou no cabeçalho interrompem a análise com uma mensagem explicativa.

## Relatório de saída

Para o CSV completo de exemplo, o resumo gerado é:

```text
RELATÓRIO DE ANÁLISE DE DADOS — SPRINT 5
============================================================
Validação didática: CPF e telefone são verificados por formato.
Total de registros: 6
Registros válidos: 3
Registros inválidos: 3
Percentual de aprovação: 50.00%
```

O relatório também apresenta:

- Os campos de cada registro válido.
- Os campos de cada registro inválido.
- Os motivos de reprovação de cada registro.

A saída é exibida no terminal e gravada em um arquivo TXT.

## Testes automatizados

Execute na pasta do projeto:

```bash
python -m unittest -v
```

O projeto contém 15 testes que verificam as validações, as exceções, a leitura dos dados e a geração do relatório.

Entre os cenários estão arquivo inexistente, coluna ausente, data impossível, idade inválida, CSV malformado e proteção contra sobrescrever o arquivo de entrada.

## Objetivo acadêmico

Aplicar os conceitos de manipulação de arquivos, expressões regulares e tratamento de exceções em um sistema de análise de dados, com código organizado, nomes descritivos e documentação de uso.
