import requests
import xml.etree.ElementTree as ET
import json
import logging

# Loglama yapılandırması
logging.basicConfig(level=logging.INFO)

def fetch_line_data(hat_kodu):
    """
    Belirtilen hat kodu için GetHat_json metodunu çağırır.
    """
    url = "https://api.ibb.gov.tr/iett/UlasimAnaVeri/HatDurakGuzergah.asmx"
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://tempuri.org/GetHat_json"
    }
    
    # SOAP isteği (hat kodu ile)
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <GetHat_json xmlns="http://tempuri.org/">
      <HatKodu>{hat_kodu}</HatKodu>
    </GetHat_json>
  </soap:Body>
</soap:Envelope>"""

    try:
        response = requests.post(url, data=soap_body, headers=headers, timeout=10)
    except requests.RequestException as e:
        logging.error("HTTP isteği başarısız: %s", e)
        return None

    if response.status_code != 200:
        logging.error("SOAP isteği başarısız. HTTP kodu: %s", response.status_code)
        return None

    try:
        tree = ET.fromstring(response.content)
    except ET.ParseError as e:
        logging.error("XML ayrıştırma hatası: %s", e)
        return None

    ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/", "temp": "http://tempuri.org/"}
    result_elem = tree.find(".//temp:GetHat_jsonResult", ns)

    if result_elem is None:
        logging.error("SOAP yanıtında GetHat_jsonResult elementi bulunamadı.")
        return None

    try:
        data = json.loads(result_elem.text)
    except json.JSONDecodeError as e:
        logging.error("JSON ayrıştırma hatası: %s", e)
        return None

    return data

if __name__ == '__main__':
    hat_kodu = input("Lütfen bir hat kodu girin: ").strip()

    data = fetch_line_data(hat_kodu)
    if data is not None:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        logging.error("Veri alınamadı. Lütfen API'yi kontrol edin.")
