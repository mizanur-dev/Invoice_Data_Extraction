import base64
import json
import re
import io
import os
import anthropic
import requests
from dotenv import load_dotenv
from pdf2image import convert_from_path
from rest_framework import generics, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import Invoice
from .serializers import InvoiceSerializer

load_dotenv()

IMAGE_EXTENSIONS = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.gif': 'image/gif',
}


class InvoiceCreateAPIView(generics.CreateAPIView):
    """
    API endpoint that accepts a JSON payload with an image URL,
    fetches the image, and extracts line items using Claude Vision API.

    Expected payload: {"image_url": "https://example.com/invoice.jpg"}
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    parser_classes = [JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        try:
            self._extract_data_with_ai(instance)

            response_serializer = self.get_serializer(instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _fetch_image(self, image_url):
        """
        Download the image from the given URL and return the raw bytes
        along with the detected content type.
        """
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '').lower()
        image_bytes = response.content

        return image_bytes, content_type

    def _build_content_blocks(self, image_bytes, content_type):
        """
        Build the content blocks for the Claude API request.
        Handles both PDF (multi-page conversion) and direct image formats.
        """
        content_blocks = []

        if 'pdf' in content_type:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name

            try:
                images = convert_from_path(tmp_path)
                for img in images:
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG")
                    base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

                    content_blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_str
                        }
                    })
            finally:
                os.unlink(tmp_path)
        else:
            media_type = "image/jpeg"
            if 'png' in content_type:
                media_type = "image/png"
            elif 'webp' in content_type:
                media_type = "image/webp"
            elif 'gif' in content_type:
                media_type = "image/gif"
            elif 'jpeg' in content_type or 'jpg' in content_type:
                media_type = "image/jpeg"

            base64_str = base64.b64encode(image_bytes).decode("utf-8")

            content_blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_str
                }
            })

        return content_blocks

    def _extract_data_with_ai(self, instance):
        """
        Private method to handle the AI extraction logic.
        1. Fetches the image from the stored URL.
        2. Builds image content blocks for Claude.
        3. Sends the extraction prompt and parses the JSON response.
        """
        image_bytes, content_type = self._fetch_image(instance.image_url)
        content_blocks = self._build_content_blocks(image_bytes, content_type)

        prompt = """
        Analyze the provided invoice image(s). This invoice might have multiple pages.
        Extract all the line items across all pages.
        Return ONLY a JSON array of objects without any markdown formatting (do not include ```json), explanations, or extra text.
        Each object must contain exactly these keys: 
        "name" (string), "description" (string or null), "quantity" (number or null), "unit" (string or null), "unit_price" (number or null), "total_cost" (number or null).
        
        Strict extraction rules:
        1. "name": The primary name or title of the item.
        2. "description": Detailed description or explanation of the item. If both a name and a description are present on the invoice, extract both. If only a name is present (no detailed description), put that value into the "name" field and strictly set "description" to null.
        3. "quantity": The quantity of the item. If not found, use null.
        4. "unit": The unit of measurement for the item (e.g., "hours", "kg", "each"). If not found, use null.
        5. "unit_price": The price per single unit of the item. If not found, use null.
        6. "total_cost": The total cost for that line item (typically quantity * unit_price). If not found, use null.
        """
        content_blocks.append({"type": "text", "text": prompt})

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=8192,
            messages=[
                {
                    "role": "user",
                    "content": content_blocks
                }
            ]
        )

        if response.stop_reason == "max_tokens":
            raise ValueError(
                "AI response was truncated due to token limit. "
                "The invoice may contain too many items for a single request."
            )

        extracted_text = response.content[0].text

        json_match = re.search(r'\[\s*\{.*\}\s*\]', extracted_text, re.DOTALL)
        if json_match:
            clean_json_string = json_match.group(0)
        else:
            clean_json_string = extracted_text

        extracted_json = json.loads(clean_json_string)

        instance.extracted_data = extracted_json
        instance.save(update_fields=['extracted_data'])