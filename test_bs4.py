from bs4 import BeautifulSoup

html = "<html><body><h1>Prueba bs4</h1></body></html>"
soup = BeautifulSoup(html, "html.parser")
print("✅ Extraído con bs4:", soup.h1.text)
