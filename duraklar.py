import requests
import xml.etree.ElementTree as ET
import json
import logging

# Loglama yapılandırması
logging.basicConfig(level=logging.INFO)

def fetch_stop_data(durak_kodu):
    """
    Belirtilen durak kodu için GetDurak_json metodunu çağırır.
    """
    url = "https://api.ibb.gov.tr/iett/UlasimAnaVeri/HatDurakGuzergah.asmx"
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://tempuri.org/GetDurak_json"
    }
    
    # SOAP isteği (Durak kodu ile)
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <GetDurak_json xmlns="http://tempuri.org/">
      <DurakKodu>{durak_kodu}</DurakKodu>
    </GetDurak_json>
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
    result_elem = tree.find(".//temp:GetDurak_jsonResult", ns)

    if result_elem is None:
        logging.error("SOAP yanıtında GetDurak_jsonResult elementi bulunamadı.")
        return None

    try:
        data = json.loads(result_elem.text)
    except json.JSONDecodeError as e:
        logging.error("JSON ayrıştırma hatası: %s", e)
        return None

    return data

if __name__ == '__main__':
    durak_kodu = input("Lütfen bir durak kodu girin: ").strip()

    data = fetch_stop_data(durak_kodu)
    if data is not None:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        logging.error("Veri alınamadı. Lütfen API'yi kontrol edin.")
