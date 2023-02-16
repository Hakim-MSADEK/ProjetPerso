
import wincertstore
import base64 
import ssl
import socket
import os
import array
import json
from json2html import *
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import ExtensionOID

# Certificate Name & Thumbprint to look for
hostname = socket.gethostname()
certName = hostname

def hex_string_readable(bytes):
    return ["{:02X}".format(x) for x in bytes]
#("ROOT", "CA", "MY")

def GetCertificates(input_store):
    final_list = []
    if os.name == 'nt':
        with wincertstore.CertSystemStore(input_store) as store:
            for cert in store.itercerts(usage=wincertstore.SERVER_AUTH):
                if cert.get_name() == certName:
                    line = {}
                    
                    pem = cert.get_pem()
                    encodedDer = ''.join(pem.split("\n")[1:-2])

                    cert_bytes = base64.b64decode(encodedDer)
                    cert_pem = ssl.DER_cert_to_PEM_cert(cert_bytes)
                    cert_details = x509.load_pem_x509_certificate(cert_pem.encode('utf-8'), default_backend())

                    fingerprint = hex_string_readable(cert_details.fingerprint(hashes.SHA1()))
                    fingerprint_string = ''.join(fingerprint)
                    line["subject"]=cert.get_name().upper()
                    line["thumbprint"]=fingerprint_string.lower()
                    line["expiry"]=str(cert_details.not_valid_after)

                    final_list.append(line)
                    # print(cert.get_name())
                    # print("     Issuer: ", cert_details.issuer.rfc4514_string())
                    # print("     Thumbprint: ", fingerprint_string.lower())
                    # print("     Subject: ", cert_details.subject.rfc4514_string())
                    # print("     Serial Number: ", hex(cert_details.serial_number).replace("0x",""))
                    # print("     Issued (UTC): ", cert_details.not_valid_before)
                    # print("     Expiry (UTC): ", cert_details.not_valid_after)
        return final_list
    else:
        print("This only works on a Windows System.")


final_result={}
final_result["certificates"] = GetCertificates("CA")

build_direction = "LEFT_TO_RIGHT"
table_attributes = {"style": "width:100%"}
html_result = json2html.convert(json = final_result)

print(html_result)
with open('certificate.json', 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=4)

with open('certificate.html', 'w', encoding='utf-8') as f:
    f.write(html_result)