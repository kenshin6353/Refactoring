import unittest
from unittest.mock import Mock, patch
import requests
from bs4 import BeautifulSoup
import threading
import time
import sys
import os

# Add path to the tested module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from programminglanguage2023 import NewsScraping


class TestNoneTypeExceptions(unittest.TestCase):
    """
    Testing Issue #1: Lack of NoneType Exception Handling
    Using focused testing techniques from Code Complete
    """
    
    def setUp(self):
        self.scraper = NewsScraping("https://test.com", 60)
    
    def test_equivalence_class_valid_html(self):
        """
        Technique: Equivalence-class partitioning
        Valid HTML with all required elements (valid equivalence class)
        """
        html_content = """
        <html>
            <head><title>Test Site</title></head>
            <body>
                <div class="headline--main__wrapper">
                    <h1 class="headline--main__title">Test Title</h1>
                    <p class="headline--main__short-desc">Test Description</p>
                    <time class="timeago" datetime="2023-01-01T12:00:00">Time</time>
                </div>
            </body>
        </html>
        """
        
        result = self.scraper.scrapenews1(html_content)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test Title')
    
    def test_equivalence_class_invalid_html(self):
        """
        Technique: Equivalence-class partitioning
        Invalid HTML missing required elements (invalid equivalence class)
        """
        html_content = """
        <html>
            <head><title>Test Site</title></head>
            <body>
                <div class="headline--main__wrapper">
                    <!-- Missing required elements -->
                </div>
            </body>
        </html>
        """
        
        with self.assertRaises(AttributeError):
            self.scraper.scrapenews1(html_content)
    
    def test_boundary_value_empty_html(self):
        """
        Technique: Boundary-value analysis
        Testing boundary condition: completely empty HTML
        """
        html_content = "<html></html>"
        
        result = self.scraper.scrapenews1(html_content)
        self.assertEqual(result, [])
    
    def test_boundary_value_minimal_html(self):
        """
        Technique: Boundary-value analysis
        Testing boundary condition: minimal valid HTML structure
        """
        html_content = """
        <html>
            <head><title>Minimal</title></head>
            <body></body>
        </html>
        """
        
        result = self.scraper.scrapenews1(html_content)
        self.assertEqual(result, [])
    
    def test_error_guessing_none_elements(self):
        """
        Technique: Error guessing
        Guessing common error: accessing .text on None elements
        """
        html_content = """
        <html>
            <head><title>Test Site</title></head>
            <body>
                <div class="headline--main__wrapper">
                    <p class="headline--main__short-desc">Description</p>
                    <time class="timeago" datetime="2023-01-01">Time</time>
                    <!-- Missing h1 title element -->
                </div>
            </body>
        </html>
        """
        
        # Error guessing: this will likely cause AttributeError on None.text
        with self.assertRaises(AttributeError):
            self.scraper.scrapenews1(html_content)
    
    def test_statement_branch_coverage_scrapenews2(self):
        """
        Technique: Statement & branch coverage
        Testing different code paths in scrapenews2 method
        """
        # Test valid path
        valid_html = """
        <html>
            <head><title>Test Site</title></head>
            <body>
                <li class="big style2">
                    <div class="channel"><div class="date">2023-01-01</div></div>
                    <h2><a class="bigteks" title="Test Title">Title</a></h2>
                    <div class="description">Description</div>
                </li>
            </body>
        </html>
        """
        
        result = self.scraper.scrapenews2(valid_html)
        self.assertEqual(len(result), 1)
        
        # Test error path
        invalid_html = """
        <html>
            <head><title>Test Site</title></head>
            <body>
                <li class="big style2">
                    <div class="channel"></div>
                    <!-- Missing nested elements -->
                </li>
            </body>
        </html>
        """
        
        with self.assertRaises(AttributeError):
            self.scraper.scrapenews2(invalid_html)
    
    def test_path_condition_coverage_scrape_site(self):
        """
        Technique: Path/condition coverage
        Testing all conditional paths in scrape_site method
        """
        # Test first condition: liputan6.com
        self.scraper.news_site = "https://www.liputan6.com/"
        html = "<html><head><title>Test</title></head><body></body></html>"
        result = self.scraper.scrape_site(html)
        self.assertEqual(result, [])
        
        # Test second condition: bisnis.com
        self.scraper.news_site = "https://www.bisnis.com/"
        result = self.scraper.scrape_site(html)
        self.assertEqual(result, [])
        
        # Test third condition: abc.net.au
        self.scraper.news_site = "https://www.abc.net.au/news/indonesian"
        result = self.scraper.scrape_site(html)
        self.assertEqual(result, [])
        
        # Test else condition: unsupported site
        self.scraper.news_site = "https://unsupported.com/"
        with self.assertRaises(ValueError):
            self.scraper.scrape_site(html)
    
    def test_data_flow_state_based_news_queue(self):
        """
        Technique: Data-flow or state-based
        Testing data flow through news_queue
        """
        # Initial state: empty queue
        self.assertTrue(self.scraper.news_queue.empty())
        
        # Add data to queue
        test_news = {'name': 'Test', 'title': 'Title', 'desc': 'Desc', 'timestamp': '2023-01-01'}
        self.scraper.news_queue.put(test_news)
        
        # State change: queue has data
        self.assertFalse(self.scraper.news_queue.empty())
        
        # Data flow: retrieve data
        retrieved_news = self.scraper.news_queue.get()
        self.assertEqual(retrieved_news, test_news)
        
        # Final state: queue empty again
        self.assertTrue(self.scraper.news_queue.empty())


class TestHTTPTimeoutHandling(unittest.TestCase):
    """
    Testing Issue #4: Lack of HTTP Request Timeouts
    Using focused testing techniques from Code Complete
    """
    
    def setUp(self):
        self.scraper = NewsScraping("https://test.com", 60)
    
    @patch('requests.get')
    def test_equivalence_class_successful_request(self, mock_get):
        """
        Technique: Equivalence-class partitioning
        Successful HTTP request (valid equivalence class)
        """
        mock_response = Mock()
        mock_response.text = "<html>Success</html>"
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch()
        self.assertEqual(result, "<html>Success</html>")
    
    @patch('requests.get')
    def test_equivalence_class_failed_request(self, mock_get):
        """
        Technique: Equivalence-class partitioning
        Failed HTTP request (invalid equivalence class)
        """
        mock_get.side_effect = requests.exceptions.RequestException("Error")
        
        result = self.scraper.fetch()
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_boundary_value_timeout_edge(self, mock_get):
        """
        Technique: Boundary-value analysis
        Testing at the edge of timeout conditions
        """
        mock_get.side_effect = requests.exceptions.Timeout("Timeout at boundary")
        
        result = self.scraper.fetch()
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_error_guessing_common_network_issues(self, mock_get):
        """
        Technique: Error guessing
        Guessing common network errors that might occur
        """
        # Common error 1: Connection refused
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        result = self.scraper.fetch()
        self.assertIsNone(result)
        
        # Common error 2: DNS resolution failure
        mock_get.side_effect = requests.exceptions.ConnectionError("DNS resolution failed")
        result = self.scraper.fetch()
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_statement_branch_coverage_fetch(self, mock_get):
        """
        Technique: Statement & branch coverage
        Testing both success and exception branches in fetch method
        """
        # Success branch
        mock_response = Mock()
        mock_response.text = "Success"
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch()
        self.assertEqual(result, "Success")
        
        # Exception branch
        mock_get.side_effect = requests.exceptions.RequestException("Error")
        result = self.scraper.fetch()
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_path_condition_coverage_fetch_flow(self, mock_get):
        """
        Technique: Path/condition coverage
        Testing different execution paths in fetch method
        """
        # Path 1: Successful response with raise_for_status passing
        mock_response = Mock()
        mock_response.text = "Success Path"
        mock_response.raise_for_status.return_value = None  # No exception
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch()
        self.assertEqual(result, "Success Path")
        mock_response.raise_for_status.assert_called_once()
        
        # Path 2: raise_for_status throws HTTPError
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
        result = self.scraper.fetch()
        self.assertIsNone(result)
        
        # Path 3: requests.get throws RequestException
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        result = self.scraper.fetch()
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_stress_performance_multiple_requests(self, mock_get):
        """
        Technique: Stress/performance
        Testing performance under multiple rapid requests
        """
        mock_response = Mock()
        mock_response.text = "Response"
        mock_get.return_value = mock_response
        
        start_time = time.time()
        
        # Simulate stress: multiple rapid requests
        for i in range(10):
            result = self.scraper.fetch()
            self.assertEqual(result, "Response")
        
        end_time = time.time()
        
        # Performance check: should complete reasonably fast
        self.assertLess(end_time - start_time, 1.0)  # Should take less than 1 second
        self.assertEqual(mock_get.call_count, 10)
    
    @patch('requests.get')
    def test_regression_fetch_behavior_consistency(self, mock_get):
        """
        Technique: Regression
        Ensuring fetch behavior remains consistent across calls
        """
        mock_response = Mock()
        mock_response.text = "Consistent Response"
        mock_get.return_value = mock_response
        
        # First call
        result1 = self.scraper.fetch()
        
        # Second call - should behave identically
        result2 = self.scraper.fetch()
        
        # Third call - should still behave identically
        result3 = self.scraper.fetch()
        
        # Regression check: all results should be identical
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        self.assertEqual(result1, "Consistent Response")
        
        # Verify consistent call pattern
        self.assertEqual(mock_get.call_count, 3)
        for call in mock_get.call_args_list:
            self.assertEqual(call[0][0], "https://test.com")


if __name__ == '__main__':
    unittest.main(verbosity=2) 