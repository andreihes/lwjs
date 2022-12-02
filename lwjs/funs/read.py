'''
Reads the whole file as text using given encoding
'''

def read(path: str, enc: str = 'utf-8'):
  with open(path, encoding = enc) as f:
    return f.read()
