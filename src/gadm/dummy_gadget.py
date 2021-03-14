import sys

print(rf'''
python is run by {sys.executable}
''')

def EmptyPythonGadget(connection):
    try:
        index=0
        for acq in connection:
            print(rf'acq index {index}')
            index=index+1
    except:
        pass
    pass