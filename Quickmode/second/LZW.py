# Nombre del archivo "file.txt"
import lzma

archivo = open("file.txt", "rb")
data = archivo.read()
size = len(data)
archivo.close()
#print("File is", data)
print("Original size is", size)

enc = lzma.compress(data)
size2 = len(enc)
#print("Compressed file", enc)
print("Compressed size is", size2)

dec = lzma.decompress(enc)
size3 = len(dec)
print("Received fyle is", type(dec))
print("Received file size is", size3)
final= open("salida.txt", "wb")
final.write(dec)
final.close()