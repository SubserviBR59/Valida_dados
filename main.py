
import argparse
import csv
import re
from datetime import datetime
from pathlib import Path


PASTA_PROJETO = Path(__file__).resolve().parent
COLUNAS_OBRIGATORIAS = ("email", "cpf", "telefone", "data", "idade")
# re.ASCII limita \w e \d aos caracteres ASCII nesta atividade.
PADRAO_EMAIL = re.compile(
    r"^[\w]+(?:[.+-][\w]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*"
    r"[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$", re.ASCII
)
PADRAO_CPF = re.compile(r"^(?:\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$", re.ASCII)
PADRAO_TELEFONE = re.compile(
    r"^(?:\([1-9]\d\)\s?[2-9]\d{3,4}-\d{4}|[1-9]\d[2-9]\d{7,8})$",
    re.ASCII,
)
PADRAO_DATA = re.compile(r"^\d{2}/\d{2}/\d{4}$", re.ASCII)


class IdadeInvalidaError(Exception):
    """Idade numérica fora da faixa permitida pela regra de negócio."""


def validar_email(email):
    """Política simplificada de formato; não consulta existência do e-mail."""
    return PADRAO_EMAIL.fullmatch(email) is not None


def validar_cpf(cpf):
    """Valida apenas formato, sem calcular dígitos verificadores."""
    return PADRAO_CPF.fullmatch(cpf) is not None


def validar_telefone(telefone):
    """Aceita DDD + 8/9 dígitos, com ou sem a máscara documentada."""
    return PADRAO_TELEFONE.fullmatch(telefone) is not None


def validar_data(data):
    """Regex verifica a máscara; datetime verifica o calendário."""
    if PADRAO_DATA.fullmatch(data) is None:
        return False
    try:
        datetime.strptime(data, "%d/%m/%Y")
    except ValueError:
        return False
    else:
        return True


def validar_idade(texto):
    """int pode gerar ValueError; a faixa gera nossa exceção personalizada."""
    idade = int(texto)
    if not 0 <= idade <= 120:
        raise IdadeInvalidaError("idade fora da faixa de 0 a 120 anos")
    return idade


def analisar_csv(caminho):
    """Retorna registros analisados; erros de arquivo são tratados em main."""
    registros = []
    with open(caminho, "r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, strict=True)
        cabecalho = leitor.fieldnames
        if not cabecalho:
            raise KeyError("cabeçalho ausente")
        if len(cabecalho) != len(set(cabecalho)):
            raise ValueError("o cabeçalho contém colunas duplicadas")
        for coluna in COLUNAS_OBRIGATORIAS:
            if coluna not in cabecalho:
                raise KeyError(coluna)

        for numero_registro, linha in enumerate(leitor, start=1):
            erros = []
            dados = {}
            if None in linha:
                erros.append("há campos extras sem coluna no cabeçalho")
            for coluna in COLUNAS_OBRIGATORIAS:
                # DictReader usa None para campos ausentes em linhas curtas.
                valor = linha[coluna]
                dados[coluna] = valor.strip() if valor is not None else ""

            validadores = (
                ("email", validar_email),
                ("cpf", validar_cpf),
                ("telefone", validar_telefone),
                ("data", validar_data),
            )
            for campo, validador in validadores:
                if not validador(dados[campo]):
                    erros.append(f"{campo}: formato ou valor inválido")

            try:
                idade = validar_idade(dados["idade"])
            except ValueError:
                erros.append("idade: informe um número inteiro")
            except IdadeInvalidaError as erro:
                erros.append(f"idade: {erro}")
            else:
                dados["idade"] = str(idade)

            registros.append({
                "numero": numero_registro,
                "dados": dados,
                "erros": erros,
            })
    return registros


def formatar_registro(registro):
    dados = registro["dados"]
    # repr torna caracteres de controle visíveis, evitando quebrar o relatório.
    return (
        f"Registro {registro['numero']}: email={dados['email']!r} | "
        f"cpf={dados['cpf']!r} | telefone={dados['telefone']!r} | "
        f"data={dados['data']!r} | idade={dados['idade']!r}"
    )


def gerar_relatorio(registros):
    total = len(registros)
    validos = [registro for registro in registros if not registro["erros"]]
    invalidos = [registro for registro in registros if registro["erros"]]
    percentual = len(validos) / total * 100 if total else 0.0
    linhas = [
        f"RELATÓRIO DE ANÁLISE DE DADOS — SPRINT 5",
        f"{'=' * 60}",
        f"Validação didática: CPF e telefone são verificados por formato.",
        f"Total de registros: {total}",
        f"Registros válidos: {len(validos)}",
        f"Registros inválidos: {len(invalidos)}",
        f"Percentual de aprovação: {percentual:.2f}%",
        f"\nDADOS VÁLIDOS",
    ]
    linhas.extend(formatar_registro(registro) for registro in validos)
    if not validos:
        linhas.append(f"Nenhum registro válido.")
    linhas.append(f"\nDADOS INVÁLIDOS")
    for registro in invalidos:
        linhas.append(formatar_registro(registro))
        for erro in registro["erros"]:
            linhas.append(f"  - {erro}")
    if not invalidos:
        linhas.append(f"Nenhum registro inválido.")
    return "\n".join(linhas) + "\n"


def salvar_relatorio(caminho, relatorio):
    with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(relatorio)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "arquivo", nargs="?", type=Path,
        default=PASTA_PROJETO / "dados" / "exemplo.csv",
        help="CSV UTF-8 com cabeçalho; separador vírgula",
    )
    parser.add_argument(
        "--saida", type=Path,
        default=PASTA_PROJETO / "relatorios" / "relatorio.txt",
        help="arquivo TXT de saída; sua pasta deve existir",
    )
    argumentos = parser.parse_args(argv)
    codigo_saida = 1
    try:
        # Protege o CSV de ser sobrescrito com o relatório.
        mesma_rota = argumentos.arquivo.resolve() == argumentos.saida.resolve()
        mesmo_arquivo = (
            argumentos.arquivo.exists() and argumentos.saida.exists()
            and argumentos.arquivo.samefile(argumentos.saida)
        )
        if mesma_rota or mesmo_arquivo:
            raise ValueError("entrada e saída devem ser arquivos diferentes")
        registros = analisar_csv(argumentos.arquivo)
    except FileNotFoundError:
        print(f"Erro: arquivo de entrada não encontrado: {argumentos.arquivo}")
    except KeyError as erro:
        print(f"Erro no cabeçalho/coluna obrigatória: {erro.args[0]!r}.")
    except UnicodeError:
        print(f"Erro: o arquivo deve estar codificado em UTF-8.")
    except ValueError as erro:
        print(f"Erro nos dados: {erro}")
    except csv.Error as erro:
        print(f"Erro na estrutura do CSV: {erro}")
    except OSError as erro:
        print(f"Erro ao acessar a entrada: {erro}")
    else:
        # Erros levantados em else precisam de seu próprio tratamento.
        relatorio = gerar_relatorio(registros)
        print(f"{relatorio}", end="")
        try:
            salvar_relatorio(argumentos.saida, relatorio)
        except OSError as erro:
            print(f"Erro ao salvar relatório: {erro}")
        else:
            print(f"\nRelatório salvo em: {argumentos.saida}")
            codigo_saida = 0
    finally:
        # with já fecha os arquivos; finally sinaliza o término, mesmo com erro.
        print(f"Processamento finalizado.")
    return codigo_saida


if __name__ == "__main__":
    raise SystemExit(main())
