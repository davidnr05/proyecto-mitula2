import boto3
import requests
import datetime

def scrape_mitula(event, context):
    print("Ejecutando scrape_mitula...")

    base_url = "https://casas.mitula.com.co/find?operationType=sell&propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-0000014156&text=Bogotá%2C++%28Cundinamarca%29"
    
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    s3 = boto3.client('s3')
    bucket_name = "landing-casas-059"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.56"
    }

    for page in range(1, 11):
        url = f"{base_url}&page={page}"
        print(f"Descargando: {url}")

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            file_name = f"{fecha_hoy}-p{page}.html"
            file_path = f"/tmp/{file_name}"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"Subiendo {file_name} a S3...")

            try:
                s3.upload_file(file_path, bucket_name, f"{fecha_hoy}/{file_name}")
                print(f"✅ Guardado en S3: {bucket_name}/{fecha_hoy}/{file_name}")
            except Exception as e:
                print(f"❌ Error al subir {file_name} a S3: {e}")

        else:
            print(f"❌ Error {response.status_code} al descargar {url}")

    return {"status": "OK"}
