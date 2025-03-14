import pytest
import json
import requests
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from procesar_html import process_html
from app import download_html_pages

@pytest.fixture
def sample_html():
    """ Simula un HTML de prueba con estructura de un anuncio """
    return """
    <html>
    <head><script type="application/ld+json">
    [{"about": [{"address": {"addressLocality": "Bogotá, Chapinero"},
                 "numberOfBedrooms": 1,
                 "numberOfBathroomsTotal": 1,
                 "floorSize": {"value": 39}
    }]}]
    </script></head>
    <body>
        <span>$ 315.000.000</span>
    </body>
    </html>
    """

def test_process_html(mocker, sample_html):
    """ Prueba el procesamiento de HTML para extraer datos correctamente """
    mock_s3 = mocker.patch("boto3.client")
    mock_s3.return_value.download_file.side_effect = lambda bucket, key, filename: open(filename, "w").write(sample_html)
    
    process_html("test.html")

    mock_s3.return_value.upload_file.assert_called_once()

def test_price_extraction(sample_html):
    """ Verifica que el precio se extrae correctamente del HTML """
    soup = BeautifulSoup(sample_html, "html.parser")
    price_element = soup.find("span")
    assert price_element is not None
    assert price_element.text.strip() == "$ 315.000.000"

@patch("requests.get")
def test_download_html(mock_get):
    """ Prueba la función de descarga de HTML con un mock """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<html><body>Mock Page</body></html>"

    download_html_pages()
    
    mock_get.assert_called()
