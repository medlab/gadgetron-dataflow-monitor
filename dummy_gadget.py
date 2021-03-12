def EmptyPythonGadget(connection):
    try:
        index=0
        for acq in connection:
            print(rf'acq index {index}')
            index=index+1
    except:
        pass
    pass