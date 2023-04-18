import socketserver
import urllib.request
import http.server as http
from urllib.request import urlopen
import hashlib
import shutil 
import os
import sys


# Aplicación clásica de proxy con cache
# Uso : $python3 proxy.py
# Navegador actua como cliente: 127.0.0.1:PORT/(dirección a la que se quiere acceder)

# Coge el puerto por linea de comandos
PORT = int(input("Port: ")) 

# Servidor HTTP
handler = http.SimpleHTTPRequestHandler


class proxy(handler):
    
  def do_GET(self):
    # Se obtiene la url a la que se quiere acceder
    url =self.path[1:] #url sin /

    # Se codifica la url para crear el nombre único para el archivo de cache 
    m = hashlib.md5()
    m.update(self.path.encode("utf-8"))
    cache_filename = m.hexdigest() + ".cached"

    # Páginas no cacheadas 
    if not os.path.exists(cache_filename + ".temp"):
      print("cache miss")
      print("------------------------------------")

      # Se crea el archivo y se añaden las cabeceras del navegador   
      with open(cache_filename + ".temp", "wb") as output:
        req = urllib.request.Request("http://" + url) #self.path 
        for k in self.headers:
            if k not in ["Host"]:
                req.add_header(k, self.headers[k])
        
        self.send_response(200)
        self.end_headers()
        
        # Se abre la url (petición al servidor) y se guarda la información en cache
        try:
            self.copyfile(urlopen(url), output)
            self.copyfile(urlopen(url), self.wfile)
            print("\n")
        
        except ValueError:
            
            print(" - This request couldn't be resolved\n") 
            return

        print(" - Request done an cached\n")

    # Páginas cacheadas
    else:
        print("cache hit")
        print("------------------------------------")
        file = cache_filename + ".temp"

        # Se abre y lee el archivo 
        with open(file, "rb") as cached:
            self.send_response(200)
            self.end_headers()
            shutil.copyfileobj(cached, self.wfile)

        print("\n - Request resolved from cache\n")

        
# Servidor TCP
with socketserver.TCPServer(("", PORT), proxy) as httpd:
    try:
        print("___________________________________")
        print("Listening 127.0.0.1:" + str(PORT))
        print("___________________________________")
        print("\n")
        
        httpd.serve_forever()

    # Para que no salgan errores al terminar la conexión
    except KeyboardInterrupt:
      print(" Shutting down...\n")
      sys.exit(0)