def parseFloat(fileName,r):
    
    file = open(fileName,'r')
    datas = []
    
    for i in range(0,r):
        line = file.readline()
        datas.append([float(x) for x in line.split()])

    return datas