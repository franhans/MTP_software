#Open the file and get the data as a byte array

def file_to_bytearray(filename):
    file = open(filename, mode='rb', buffering=0)
    data = bytearray()
    while(True):
        d = file.read(32)
        if(d == b''):
            break
        data += d
    file.close()

    return data

def bytearray_to_file(data, filename):
    file = open(filename, mode="wb")


if __name__ == "__main__":
    filename = "test.txt"
    data = file_to_bytearray(filename)

    for d in range(len(data)):
        print(data[d])
