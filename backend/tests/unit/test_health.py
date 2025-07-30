"""Unit tests for health check functionality."""
import unittest
from unittest.mock import patch, MagicMock
from http import HTTPStatus
from fastapi.testclient import TestClient

# Import the FastAPI app
from automation_stack.health import app

class TestHealthCheck(unittest.TestCase):
    """Test health check endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
        
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()["status"], "ok")
        
    def test_ready_endpoint(self):
        """Test the readiness check endpoint."""
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()["status"], "ready")
        
    def test_live_endpoint(self):
        """Test the liveness check endpoint."""
        response = self.client.get("/live")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()["status"], "alive")
        
    @patch('psycopg2.connect')
    def test_database_health(self, mock_connect):
        """Test database health check."""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        
        response = self.client.get("/health")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()["database"])
        
    @patch('psycopg2.connect')
    def test_database_health_failure(self, mock_connect):
        """Test database health check failure."""
        # Mock database connection failure
        mock_connect.side_effect = Exception("Connection failed")
        
        response = self.client.get("/health")
        self.assertEqual(response.status_code, HTTPStatus.SERVICE_UNAVAILABLE)
        self.assertFalse(response.json()["database"])

if __name__ == "__main__":
    unittest.main()
