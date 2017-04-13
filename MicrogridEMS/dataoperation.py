def parsefloat(path, line_numbers=1):
    
    file = open(path,'r')
    data = []
    
    for i in range(0,line_numbers):
        line = file.readline()
        data.append([float(x) for x in line.split()])

    if line_numbers == 1:
        return data[0]
    else:
        return data

def printcolumn(array):
    i = 0
    for item in array:
        i += 1
        print('{:>2} : {:.4f}'.format(i,item))