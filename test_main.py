"""Testes da Sprint 5, usando apenas unittest da biblioteca por padrão."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from main import (
    IdadeInvalidaError,
    PASTA_PROJETO,
    analisar_csv,
    gerar_relatorio,
    main,
    validar_cpf,
    validar_data,
    validar_email,
    validar_idade,
    validar_telefone,
)


class TestValidacoes(unittest.TestCase):
    def test_email(self):
        self.assertTrue(validar_email("aluna.teste+curso@example.com"))
        for valor in ("sem-arroba.com", "a@-example.com", "a..b@example.com", "a@b", "a@b.com\n"):
            with self.subTest(valor=valor):
                self.assertFalse(validar_email(valor))

    def test_cpf_apenas_formato(self):
        self.assertTrue(validar_cpf("000.000.000-00"))
        self.assertTrue(validar_cpf("00000000000"))
        for valor in ("123", "000.000000-00", "٠٠٠٠٠٠٠٠٠٠٠"):
            self.assertFalse(validar_cpf(valor))

    def test_telefone(self):
        for valor in ("(11) 90000-0000", "11900000000", "(11)3000-0000"):
            self.assertTrue(validar_telefone(valor))
        for valor in ("123", "(01) 90000-0000", "+5511900000000"):
            self.assertFalse(validar_telefone(valor))

    def test_data_calendario(self):
        self.assertTrue(validar_data("29/02/2024"))
        for valor in ("29/02/2025", "31/04/2025", "1/1/2025", "01/01/0000"):
            self.assertFalse(validar_data(valor))

    def test_idade(self):
        for idade in ("0", "120"):
            self.assertEqual(validar_idade(idade), int(idade))
        with self.assertRaises(ValueError):
            validar_idade("vinte")
        with self.assertRaises(ValueError):
            validar_idade("20.5")
        for idade in ("-1", "121"):
            with self.assertRaises(IdadeInvalidaError):
                validar_idade(idade)


class TestArquivos(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        self.pasta = Path(self.temporario.name)
        self.entrada = self.pasta / "entrada.csv"
        self.saida = self.pasta / "relatorio.txt"

    def executar(self, entrada=None, saida=None):
        with contextlib.redirect_stdout(io.StringIO()) as captura:
            codigo = main([str(entrada or self.entrada), "--saida", str(saida or self.saida)])
        self.assertIn("Processamento finalizado.", captura.getvalue())
        return codigo, captura.getvalue()

    def test_exemplo_e_escrita(self):
        exemplo = PASTA_PROJETO / "dados" / "exemplo.csv"
        registros = analisar_csv(exemplo)
        self.assertEqual(len(registros), 6)
        self.assertEqual(sum(not r["erros"] for r in registros), 3)
        self.assertEqual(len(registros[2]["erros"]), 4)
        codigo, texto = self.executar(exemplo)
        self.assertEqual(codigo, 0)
        self.assertIn("Percentual de aprovação: 50.00%", texto)
        self.assertEqual(self.saida.read_text(encoding="utf-8"), gerar_relatorio(registros))

    def test_arquivo_inexistente(self):
        codigo, texto = self.executar()
        self.assertEqual(codigo, 1)
        self.assertIn("não encontrado", texto)
        self.assertFalse(self.saida.exists())

    def test_coluna_ausente(self):
        self.entrada.write_text("email,idade\na@example.com,20\n", encoding="utf-8")
        codigo, texto = self.executar()
        self.assertEqual(codigo, 1)
        self.assertIn("cpf", texto)

    def test_apenas_cabecalho(self):
        self.entrada.write_text("email,cpf,telefone,data,idade\n", encoding="utf-8")
        codigo, texto = self.executar()
        self.assertEqual(codigo, 0)
        self.assertIn("Total de registros: 0", texto)
        self.assertIn("0.00%", texto)

    def test_vazio_e_cabecalho_duplicado(self):
        for conteudo in ("", "email,cpf,telefone,data,idade,idade\n"):
            self.entrada.write_text(conteudo, encoding="utf-8")
            self.assertEqual(self.executar()[0], 1)

    def test_linhas_incompletas_e_campos_extras(self):
        self.entrada.write_text(
            'email,cpf,telefone,data,idade\n'
            'a@example.com\n'
            'b@example.com,00000000000,11900000000,01/01/2025,20,extra\n',
            encoding="utf-8",
        )
        registros = analisar_csv(self.entrada)
        self.assertEqual(len(registros), 2)
        self.assertEqual(len(registros[0]["erros"]), 4)
        self.assertEqual(len(registros[1]["erros"]), 1)

    def test_codificacao_invalida(self):
        self.entrada.write_bytes(b"\xff\xfe")
        codigo, texto = self.executar()
        self.assertEqual(codigo, 1)
        self.assertIn("UTF-8", texto)

    def test_csv_malformado(self):
        self.entrada.write_text('email,cpf,telefone,data,idade\n"sem fechamento', encoding="utf-8")
        codigo, texto = self.executar()
        self.assertEqual(codigo, 1)
        self.assertIn("estrutura do CSV", texto)

    def test_saida_invalida(self):
        codigo, texto = self.executar(
            PASTA_PROJETO / "dados" / "exemplo.csv",
            self.pasta / "nao_existe" / "saida.txt",
        )
        self.assertEqual(codigo, 1)
        self.assertIn("Erro ao salvar", texto)

    def test_nao_sobrescrever_entrada(self):
        conteudo = "email,cpf,telefone,data,idade\n"
        self.entrada.write_text(conteudo, encoding="utf-8")
        self.assertEqual(self.executar(saida=self.entrada)[0], 1)
        self.assertEqual(self.entrada.read_text(), conteudo)


if __name__ == "__main__":
    unittest.main()
