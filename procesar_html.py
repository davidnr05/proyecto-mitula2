import boto3
import csv
import datetime
import json
import re
from bs4 import BeautifulSoup
import bs4  # Asegurar que bs4 está disponible


def process_html(file_key):
    s3 = boto3.client("s3")
    input_bucket = "landing-casas-117"
    output_bucket = "casas-final-117"

    today = datetime.datetime.today().strftime("%Y-%m-%d")
    local_html_path = f"/tmp/{file_key}"
    local_csv_path = f"/tmp/{file_key.replace('.html', '.csv')}"

    # Descargar archivo HTML desde S3
    s3.download_file(input_bucket, file_key, local_html_path)

    with open(local_html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Extraer el JSON-LD del HTML
    script_tag = soup.find("script", type="application/ld+json")
    if not script_tag:
        print("No se encontró JSON-LD en el HTML.")
        return
    
    json_data = json.loads(script_tag.string)  # Convertir el JSON-LD en un diccionario
    
    # Buscar los precios dentro del HTML
    price_elements = soup.find_all("span", class_=True)  
    prices = [span.get_text(strip=True) for span in price_elements if re.match(r"\$\s?\d{1,3}(\.\d{3})*", span.get_text())]

    listings = []
    
    # Extraer los datos de cada propiedad
    for i, house in enumerate(json_data[0]["about"]):
        barrio = house["address"].get("addressLocality", "No disponible")
        habitaciones = house.get("numberOfBedrooms", "No disponible")
        banos = house.get("numberOfBathroomsTotal", "No disponible")
        mts2 = house.get("floorSize", {}).get("value", "No disponible")

        # Asignar precio desde la lista de precios
        valor = prices[i] if i < len(prices) else "No disponible"

        print(f"Extraído: Barrio={barrio}, Valor={valor}, Habitaciones={habitaciones}, Baños={banos}, Mts2={mts2}")

        listings.append([today, barrio, valor, habitaciones, banos, mts2])

    # Guardar CSV solo si hay datos
    if listings:
        with open(local_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["FechaDescarga", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"])
            writer.writerows(listings)

        # Subir CSV procesado a S3
        s3.upload_file(local_csv_path, output_bucket, file_key.replace(".html", ".csv"))
        print(f"Archivo CSV guardado: {file_key.replace('.html', '.csv')}")
    else:
        print(f"No se encontraron anuncios en {file_key}")

def lambda_handler(event, context):
    for record in event["Records"]:
        file_key = record["s3"]["object"]["key"]
        process_html(file_key)

    return {"statusCode": 200, "body": "Procesamiento completado"}
