import boto3
import requests
import datetime

def download_html_pages():
    s3 = boto3.client('s3')
    bucket_name = "landing-casas-117"
    base_url = "https://casas.mitula.com.co/find?operationType=sell&propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-0000014156&text=Bogot%C3%A1%2C++%28Cundinamarca%29"

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    for i in range(1, 11):  # Descargar las primeras 10 páginas
        if i == 1:
            url = base_url  # Primera página sin `page=`
        else:
            url = f"{base_url}&page={i}"  # Agregar el número de página a la URL

        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        if response.status_code == 200:
            file_name = f"{today}-{i}.html"
            file_path = f"/tmp/{file_name}"

            with open(file_path, "w", encoding='utf-8') as f:
                f.write(response.text)

            try:
                s3.upload_file(file_path, bucket_name, file_name)
                print(f"Subido {file_name} a {bucket_name}")
            except Exception as e:
                print(f"Error al subir {file_name}: {e}")
        else:
            print(f"Error al descargar {url}: {response.status_code}")

def lambda_handler(event, context):
    download_html_pages()
    return {"statusCode": 200, "body": "Descarga completada y subida a S3"}
