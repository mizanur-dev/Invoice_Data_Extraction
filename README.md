# Restaurant Invoice Processor

A Django REST API application that extracts line items from restaurant invoices using Claude AI's vision capabilities. Supports PDF and image formats (JPG, PNG, WebP, GIF).

## ✨ Features

- **Invoice Upload**: Upload invoices in PDF or image format
- **AI-Powered Extraction**: Uses Claude Haiku 4.5 Vision API to extract line items
- **Multi-Page Support**: Automatically handles multi-page PDFs by converting them to images
- **Structured Data Output**: Returns extracted data in JSON format with item details
- **RESTful API**: Built with Django REST Framework
- **Error Handling**: Comprehensive error messages and validation

## 📋 Prerequisites

- Python 3.10+
- pip package manager
- Anthropic API Key (get one at [console.anthropic.com](https://console.anthropic.com))
- Poppler (for PDF processing) - see [Installation](#installation) section

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Restaurant_Manager
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Poppler (Required for PDF Processing)

**Windows:**
```bash
# Using Chocolatey
choco install poppler

# Or download from: https://github.com/oschwartz10612/poppler-windows/releases
```

**macOS:**
```bash
brew install poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install poppler-utils
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
```

**Note**: Replace `sk-ant-your-actual-api-key-here` with your actual Anthropic API key.

### 6. Run Database Migrations

```bash
python manage.py migrate
```

### 7. Start the Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

---

## 📁 Project Structure

```
Restaurant_Manager/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── db.sqlite3               # SQLite database
├── core/                    # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   ├── asgi.py
│   └── wsgi.py
├── invoice_processor/       # Main app
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # App URL routing
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/          # Database migrations
└── README.md               # This file
```

---

## 🔌 API Endpoints

### Extract Invoice

**Endpoint:** `POST /api/invoice_processor/extract-invoice/`

**Description:** Upload an invoice and extract line items using AI

**Request Body (JSON):**
```json
{
  "image_url": "https://example.com/invoice.jpg"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "image_url": "https://example.com/invoice.jpg",
  "extracted_data": [
    {
      "name": "Grilled Salmon",
      "description": "Atlantic salmon with lemon butter sauce",
      "quantity": 2,
      "unit": "pcs",
      "unit_price": 45.50,
      "total_cost": 91.00
    },
    {
      "name": "Caesar Salad",
      "description": null,
      "quantity": 1,
      "unit": "pcs",
      "unit_price": 12.99,
      "total_cost": 12.99
    }
  ],
  "created_at": "2026-06-13T14:59:36.123456Z"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "ANTHROPIC_API_KEY not found in environment variables"
}
```

---

## 📝 Usage Examples

### Using Postman

1. **Create a new POST request**
2. **URL:** `http://localhost:8000/api/invoice_processor/extract-invoice/`
3. **Headers:**
   - `Content-Type: application/json`
4. **Body (raw JSON):**
   ```json
   {
     "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Invoices.png/440px-Invoices.png"
   }
   ```
5. **Click Send**

### Using cURL

```bash
curl -X POST http://localhost:8000/api/invoice_processor/extract-invoice/ \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/invoice.jpg"
  }'
```

### Using Python

```python
import requests
import json

url = "http://localhost:8000/api/invoice_processor/extract-invoice/"
payload = {
    "image_url": "https://example.com/invoice.jpg"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(response.status_code)
print(json.dumps(response.json(), indent=2))
```

### Using JavaScript/Fetch

```javascript
const url = "http://localhost:8000/api/invoice_processor/extract-invoice/";
const payload = {
  image_url: "https://example.com/invoice.jpg"
};

fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Error:", error));
```

---

## 📊 Database Models

### Invoice Model

The `Invoice` model stores invoice records and extracted data.

**Fields:**
- `id` (Integer, Primary Key) - Unique identifier
- `image_url` (URL Field) - URL of the invoice image
- `extracted_data` (JSON Field) - Extracted line items in JSON format
- `created_at` (DateTime) - Creation timestamp (auto-set)

**Example:**
```python
{
  "id": 1,
  "image_url": "https://example.com/invoice.jpg",
  "extracted_data": [
    {
      "name": "Item Name",
      "description": "Item Description",
      "quantity": 2,
      "unit": "pcs",
      "unit_price": 10.50,
      "total_cost": 21.00
    }
  ],
  "created_at": "2026-06-13T14:59:36.123456Z"
}
```

---

## 🔧 Configuration

### Django Settings

Key settings in `core/settings.py`:

```python
# Debug Mode (set to False in production)
DEBUG = True

# Allowed Hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Media Files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Installed Apps
INSTALLED_APPS = [
    ...
    'rest_framework',
    'invoice_processor',
]
```

### API Key Management

The API key is stored in `.env` and loaded by the application:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

The application reads this in `invoice_processor/views.py`:

```python
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'dotenv'`

**Solution:**
```bash
pip install python-dotenv
```

### Issue: `ANTHROPIC_API_KEY not found in environment variables`

**Solution:**
1. Create a `.env` file in the project root
2. Add your API key: `ANTHROPIC_API_KEY=sk-ant-your-key-here`
3. Restart the server

### Issue: `pdf2image` not working / Poppler not found

**Solution:**
- Windows: Install via Chocolatey or download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
- macOS: `brew install poppler`
- Linux: `sudo apt-get install poppler-utils`

### Issue: 500 Internal Server Error

**Solution:**
1. Check Django logs for detailed error messages
2. Verify `.env` file exists and has `ANTHROPIC_API_KEY`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Try restarting the server

### Issue: Image URL is invalid or unreachable

**Solution:**
- Ensure the `image_url` is publicly accessible
- Check that the URL doesn't require authentication
- Try with a different invoice image URL

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 5.2.14+ | Web framework |
| djangorestframework | 3.17.1+ | REST API framework |
| anthropic | 0.109.1+ | Claude AI API client |
| pdf2image | 1.17.0+ | PDF to image conversion |
| Pillow | 12.2.0+ | Image processing |
| python-dotenv | 1.2.2+ | Environment variable management |
| requests | 2.31.0+ | HTTP library |

See `requirements.txt` for complete list.

---

## 🚀 Performance Tips

1. **Use smaller image sizes** - Larger images take longer to process
2. **Batch requests carefully** - API has rate limits
3. **Cache results** - Store extracted data to avoid re-processing
4. **Use PDF format when possible** - Better OCR accuracy for documents

---

## 📚 API Documentation

### Claude Haiku 4.5 Vision API

This project uses Claude Haiku 4.5 for invoice analysis. Key features:

- Vision capabilities for image understanding
- JSON output support
- Multi-page document handling
- Structured data extraction

For more information: [Anthropic Documentation](https://docs.anthropic.com)

---

## 🔐 Security Notes

⚠️ **Important for Production:**

1. Change `DEBUG = False` in settings
2. Set a strong `SECRET_KEY`
3. Use environment variables for sensitive data
4. Add HTTPS/SSL
5. Implement authentication and authorization
6. Use a production WSGI server (Gunicorn, uWSGI)
7. Add rate limiting
8. Never commit `.env` file to version control

Add to `.gitignore`:
```
.env
*.pyc
__pycache__/
db.sqlite3
media/
venv/
```

---

## 📞 Support & Contributing

For issues or improvements:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review error messages in Django logs
3. Check [Anthropic Documentation](https://docs.anthropic.com)

---

## 📄 License

This project is part of the Restaurant Manager suite. See LICENSE file for details.

---

## 🎯 Roadmap

- [ ] User authentication
- [ ] Invoice history and search
- [ ] Batch processing
- [ ] Webhook notifications
- [ ] Data export (CSV, Excel)
- [ ] Mobile app integration
- [ ] Advanced analytics

---

## ✅ Checklist Before Deployment

- [ ] Create `.env` file with valid `ANTHROPIC_API_KEY`
- [ ] Run `python manage.py migrate`
- [ ] Test API with sample invoice
- [ ] Set `DEBUG = False` in production
- [ ] Configure allowed hosts
- [ ] Set up proper logging
- [ ] Test error handling
- [ ] Set up monitoring/alerting

---

**Last Updated:** June 13, 2026  
**Version:** 1.0.0
