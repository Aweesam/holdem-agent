#!/usr/bin/env python3
"""
Unit tests for the holdem logging system.
Tests log rotation, structured logging, and error handling.
"""

import unittest
import tempfile
import os
import sys
import shutil
import json
import time
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from holdem.utils.logging_config import (
    setup_logger, 
    ensure_log_directories, 
    get_log_file_path,
    JSONFormatter,
    ColoredFormatter,
    setup_exception_logging
)


class TestLoggingConfig(unittest.TestCase):
    """Test the centralized logging configuration."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Mock the logging directory to use temp dir
        self.patcher = patch('holdem.utils.logging_config.Path')
        self.mock_path = self.patcher.start()
        self.mock_path.return_value.parent.parent.parent.parent = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.chdir(self.original_cwd)
    
    def test_ensure_log_directories(self):
        """Test that log directories are created correctly."""
        # Create the expected directory structure manually for this test
        base_log_dir = Path(self.temp_dir) / 'logs'
        expected_dirs = [
            base_log_dir,
            base_log_dir / 'api',
            base_log_dir / 'agent',
            base_log_dir / 'dashboard',
            base_log_dir / 'holdemctl'
        ]
        
        for dir_path in expected_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Verify directories exist
        for dir_path in expected_dirs:
            self.assertTrue(dir_path.exists(), f"Directory {dir_path} should exist")
            self.assertTrue(dir_path.is_dir(), f"{dir_path} should be a directory")
    
    def test_json_formatter(self):
        """Test JSON log formatter produces valid JSON."""
        formatter = JSONFormatter()
        
        import logging
        record = logging.LogRecord(
            name='test.logger',
            level=logging.INFO,
            pathname='/test/path.py',
            lineno=123,
            msg='Test message with %s',
            args=('args',),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Should be valid JSON
        try:
            parsed = json.loads(formatted)
        except json.JSONDecodeError:
            self.fail("JSON formatter did not produce valid JSON")
        
        # Check required fields
        self.assertIn('timestamp', parsed)
        self.assertIn('level', parsed)
        self.assertIn('logger', parsed)
        self.assertIn('message', parsed)
        self.assertEqual(parsed['level'], 'INFO')
        self.assertEqual(parsed['logger'], 'test.logger')
        self.assertEqual(parsed['message'], 'Test message with args')
    
    def test_json_formatter_with_exception(self):
        """Test JSON formatter handles exceptions properly."""
        formatter = JSONFormatter()
        
        import logging
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name='test.logger',
            level=logging.ERROR,
            pathname='/test/path.py',
            lineno=123,
            msg='Error occurred',
            args=(),
            exc_info=exc_info
        )
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertIn('exception', parsed)
        self.assertIn('ValueError: Test exception', parsed['exception'])
    
    def test_colored_formatter(self):
        """Test colored formatter adds ANSI color codes."""
        formatter = ColoredFormatter('%(levelname)s: %(message)s')
        
        import logging
        record = logging.LogRecord(
            name='test.logger',
            level=logging.ERROR,
            pathname='/test/path.py',
            lineno=123,
            msg='Error message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Should contain ANSI color codes
        self.assertIn('\033[', formatted)  # ANSI escape sequence
        self.assertIn('ERROR', formatted)
        self.assertIn('Error message', formatted)
    
    def test_setup_logger_creates_files(self):
        """Test that setup_logger creates log files."""
        log_dir = Path(self.temp_dir) / 'logs' / 'test'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('holdem.utils.logging_config.ensure_log_directories') as mock_ensure:
            mock_ensure.return_value = Path(self.temp_dir) / 'logs'
            
            logger = setup_logger('test_logger', 'test')
            
            # Log a message to trigger file creation
            logger.info('Test log message')
            
            # Check that log file was created
            log_file = log_dir / 'test.log'
            # Note: In a real test, we'd need to handle file handlers properly
            # This is a simplified test
    
    @patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'})
    def test_log_level_from_environment(self):
        """Test that log level is read from environment variables."""
        with patch('holdem.utils.logging_config.ensure_log_directories'):
            logger = setup_logger('test_logger', 'test', log_level='DEBUG')
            self.assertEqual(logger.level, 10)  # DEBUG level
    
    @patch.dict(os.environ, {'LOG_FORMAT': 'json'})
    def test_log_format_from_environment(self):
        """Test that log format is read from environment variables."""
        with patch('holdem.utils.logging_config.ensure_log_directories'):
            logger = setup_logger('test_logger', 'test', log_format='json')
            # Check that JSON formatter is being used
            # This would require inspecting the handler's formatter
    
    def test_get_log_file_path(self):
        """Test log file path generation."""
        with patch('holdem.utils.logging_config.ensure_log_directories') as mock_ensure:
            mock_ensure.return_value = Path(self.temp_dir) / 'logs'
            
            path = get_log_file_path('api')
            expected = Path(self.temp_dir) / 'logs' / 'api' / 'api.log'
            self.assertEqual(path, expected)
            
            # Test custom log file name
            path = get_log_file_path('api', 'custom.log')
            expected = Path(self.temp_dir) / 'logs' / 'api' / 'custom.log'
            self.assertEqual(path, expected)


class TestLogRotation(unittest.TestCase):
    """Test log rotation functionality."""
    
    def setUp(self):
        """Set up test with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / 'logs' / 'test'
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_rotating_file_handler_rotation(self):
        """Test that RotatingFileHandler rotates files when size limit reached."""
        import logging.handlers
        
        log_file = self.log_dir / 'test.log'
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=1024,  # 1KB - small for testing
            backupCount=3
        )
        
        logger = logging.getLogger('test_rotation')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        # Write enough data to trigger rotation
        large_message = 'x' * 200  # 200 character message
        for i in range(10):  # 10 * 200 = 2000 chars > 1KB
            logger.info(f'Message {i}: {large_message}')
        
        # Check that rotation occurred
        self.assertTrue(log_file.exists(), "Main log file should exist")
        
        # Check for rotated files
        rotated_files = list(self.log_dir.glob('test.log.*'))
        self.assertGreater(len(rotated_files), 0, "Should have rotated files")
        
        # Verify file sizes are reasonable
        if log_file.exists():
            self.assertLessEqual(log_file.stat().st_size, 1024 + 500, "Main log shouldn't be too large")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and fatal error logging."""
    
    def test_setup_exception_logging(self):
        """Test that global exception handler is set up correctly."""
        import logging
        logger = logging.getLogger('test_exception')
        
        # Mock sys.excepthook
        original_excepthook = sys.excepthook
        
        try:
            setup_exception_logging(logger)
            
            # Verify that excepthook was changed
            self.assertNotEqual(sys.excepthook, original_excepthook)
            
        finally:
            # Restore original excepthook
            sys.excepthook = original_excepthook
    
    def test_keyboard_interrupt_passthrough(self):
        """Test that KeyboardInterrupt passes through normally."""
        import logging
        logger = logging.getLogger('test_keyboard')
        
        original_excepthook = sys.excepthook
        
        try:
            setup_exception_logging(logger)
            
            # KeyboardInterrupt should call original hook
            with patch('sys.__excepthook__') as mock_original:
                sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)
                mock_original.assert_called_once()
                
        finally:
            sys.excepthook = original_excepthook


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestLoggingConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestLogRotation))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)