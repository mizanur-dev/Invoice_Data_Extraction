import json
from django.test import TestCase
from unittest.mock import patch, MagicMock
from .models import Invoice


class InvoiceProcessorTestCase(TestCase):
    @patch('invoice_processor.views.requests.get')
    @patch('invoice_processor.views.anthropic.Anthropic')
    def test_invoice_extraction_with_url(self, mock_anthropic_class, mock_requests_get):
        """Test full extraction flow: JSON URL input -> image fetch -> AI extraction."""
        # Mock the image download
        mock_response = MagicMock()
        mock_response.content = b'\x89PNG\r\n\x1a\n\x00\x00'  # fake PNG bytes
        mock_response.headers = {'Content-Type': 'image/png'}
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        # Mock the Claude API response with the new field structure
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response_text = json.dumps([
            {
                "name": "Labour",
                "description": None,
                "quantity": 23.75,
                "unit": "hours",
                "unit_price": 40.00,
                "total_cost": 950.00
            },
            {
                "name": "Concrete Mix",
                "description": "High-strength concrete mix for foundation work",
                "quantity": 10,
                "unit": "bags",
                "unit_price": 12.50,
                "total_cost": 125.00
            }
        ])
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=mock_response_text)]
        mock_message.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_message

        # POST a JSON payload with image_url
        payload = {"image_url": "https://example.com/invoice.png"}
        response = self.client.post(
            '/api/invoice_processor/extract-invoice/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Verify response
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('extracted_data', data)
        self.assertEqual(data['image_url'], "https://example.com/invoice.png")

        extracted = data['extracted_data']
        self.assertEqual(len(extracted), 2)

        # Item 1: name only, no description, has quantity/unit/unit_price/total_cost
        item1 = extracted[0]
        self.assertEqual(item1['name'], "Labour")
        self.assertIsNone(item1['description'])
        self.assertEqual(item1['quantity'], 23.75)
        self.assertEqual(item1['unit'], "hours")
        self.assertEqual(item1['unit_price'], 40.00)
        self.assertEqual(item1['total_cost'], 950.00)

        # Item 2: name + description, has all fields
        item2 = extracted[1]
        self.assertEqual(item2['name'], "Concrete Mix")
        self.assertEqual(item2['description'], "High-strength concrete mix for foundation work")
        self.assertEqual(item2['quantity'], 10)
        self.assertEqual(item2['unit'], "bags")
        self.assertEqual(item2['unit_price'], 12.50)
        self.assertEqual(item2['total_cost'], 125.00)

        # Verify the image was fetched from the correct URL
        mock_requests_get.assert_called_once_with("https://example.com/invoice.png", timeout=30)

    @patch('invoice_processor.views.requests.get')
    @patch('invoice_processor.views.anthropic.Anthropic')
    def test_invoice_extraction_null_fields(self, mock_anthropic_class, mock_requests_get):
        """Test that null values are correctly handled for optional fields."""
        # Mock the image download
        mock_response = MagicMock()
        mock_response.content = b'\xff\xd8\xff\xe0'  # fake JPEG bytes
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        # Mock Claude response with null fields
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response_text = json.dumps([
            {
                "name": "Cheese Curds",
                "description": None,
                "quantity": None,
                "unit": None,
                "unit_price": None,
                "total_cost": 11.50
            }
        ])
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=mock_response_text)]
        mock_message.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_message

        payload = {"image_url": "https://example.com/menu.jpg"}
        response = self.client.post(
            '/api/invoice_processor/extract-invoice/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        extracted = response.json()['extracted_data']
        self.assertEqual(len(extracted), 1)

        item = extracted[0]
        self.assertEqual(item['name'], "Cheese Curds")
        self.assertIsNone(item['description'])
        self.assertIsNone(item['quantity'])
        self.assertIsNone(item['unit'])
        self.assertIsNone(item['unit_price'])
        self.assertEqual(item['total_cost'], 11.50)

    def test_missing_image_url_returns_400(self):
        """Test that submitting without image_url returns a validation error."""
        response = self.client.post(
            '/api/invoice_processor/extract-invoice/',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
