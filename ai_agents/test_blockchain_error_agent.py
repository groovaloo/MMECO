#!/usr/bin/env python3
"""
Testes para o Blockchain Error Agent
"""

import sys
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

import unittest
from blockchain_memory import BlockchainMemory
from rust_error_patterns import (
    get_solution_for_error,
    identify_error_category,
    parse_cargo_error,
    RUST_ERROR_PATTERNS,
)
from blockchain_error_agent import BlockchainErrorAgent


class TestBlockchainMemory(unittest.TestCase):
    """Testes para BlockchainMemory."""
    
    def setUp(self):
        self.memory = BlockchainMemory()
        # Limpar memória para testes
        self.memory.errors_db = {}
    
    def test_learn_and_search_error(self):
        """Teste de aprendizado e pesquisa de erros."""
        error = "error[E0277]: the trait bound `u32: Encode` is not satisfied"
        solution = "Add #[derive(Encode, Decode)] to the struct"
        
        self.memory.learn_error(error, solution, "test")
        
        # Deve encontrar pelo código
        result = self.memory.search_solution(error)
        self.assertIsNotNone(result)
        self.assertEqual(result['solution'], solution)
    
    def test_extract_error_code(self):
        """Teste de extração de código de erro."""
        test_cases = [
            ("error[E0277]: message", "E0277"),
            ("error[E0308]: mismatched types", "E0308"),
            ("error[E0432]: unresolved import", "E0432"),
            ("no error code here", None),
        ]
        
        for msg, expected in test_cases:
            result = self.memory._extract_error_code(msg)
            self.assertEqual(result, expected)
    
    def test_error_stats(self):
        """Teste de estatísticas."""
        self.memory.learn_error("error[E0001]", "solution1", "")
        self.memory.learn_error("error[E0002]", "solution2", "")
        self.memory.learn_error("error[E0001]", "solution1", "")  # Duplicado
        
        stats = self.memory.get_error_stats()
        self.assertEqual(stats['total_errors'], 2)
        self.assertEqual(stats['total_occurrences'], 3)


class TestRustErrorPatterns(unittest.TestCase):
    """Testes para rust_error_patterns."""
    
    def test_get_solution_for_known_error(self):
        """Teste de solução para erro conhecido."""
        error = "error[E0277]: the trait bound `Foo: Encode` is not satisfied"
        result = get_solution_for_error(error)
        self.assertIsNotNone(result)
        self.assertEqual(result.code, "E0277")
    
    def test_identify_category(self):
        """Teste de identificação de categoria."""
        error = "error[E0432]: unresolved import `foo`"
        categories = identify_error_category(error)
        self.assertIn("Imports e Módulos", categories)
    
    def test_parse_cargo_output(self):
        """Teste de parsing de output do cargo."""
        cargo_output = """
error[E0308]: mismatched types
 --> src/lib.rs:5:8
  |
5 |     let x: u32 = "string";
  |                 ^^^^^^^^ expected u32, found `&str`

error[E0277]: the trait bound
 --> src/lib.rs:10:5
  |
10 | fn test<T: Encode>() {}
  |                  ^^^^^ the trait `Encode` is not implemented for `T`
"""
        errors = parse_cargo_error(cargo_output)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['code'], 'E0308')
        self.assertEqual(errors[1]['code'], 'E0277')


class TestBlockchainErrorAgent(unittest.TestCase):
    """Testes para BlockchainErrorAgent."""
    
    def setUp(self):
        self.agent = BlockchainErrorAgent()
    
    def test_analyze_known_error(self):
        """Teste de análise de erro conhecido."""
        error = "error[E0432]: unresolved import `frame_support`"
        result = self.agent.analyze_error(error)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['code'], 'E0432')
        self.assertIn('Imports e Módulos', result['categories'])
    
    def test_analyze_unknown_error(self):
        """Teste de análise de erro desconhecido."""
        error = "some random error that doesn't match patterns"
        result = self.agent.analyze_error(error)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['confidence'], 0)


class TestIntegration(unittest.TestCase):
    """Testes de integração."""
    
    def test_full_workflow(self):
        """Teste de fluxo completo: erro -> análise -> memória."""
        agent = BlockchainErrorAgent()
        
        # Criar erro de teste
        test_error = "error[E0277]: the trait bound `MyType: MaxEncodedLen` is not satisfied"
        
        # Analisar
        result = agent.analyze_error(test_error)
        self.assertIsNotNone(result)
        
        # Deve ter encontrado solução
        self.assertGreater(result['confidence'], 0)


def run_tests():
    """Executa todos os testes."""
    # Carregar testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar testes
    suite.addTests(loader.loadTestsFromTestCase(TestBlockchainMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestRustErrorPatterns))
    suite.addTests(loader.loadTestsFromTestCase(TestBlockchainErrorAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Executar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
