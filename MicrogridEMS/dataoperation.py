import numpy as np

def get_data_from_file(path, line_numbers=1):
    
    file = open(path,'r')
    data = []
    
    for i in range(0,line_numbers):
        line = file.readline()
        data.append([float(x) for x in line.split()])

    file.close()

    if line_numbers == 1:
        return data[0]
    else:
        return data


def printcolumn(array):
    i = 0
    for item in array:
        i += 1
        print('{:>2} : {:.4f}'.format(i,item))


def get_paths(config):
    paths = dict()

    folder = get_folder_path(config)

    with open(config) as file:
        lines = [line.rstrip('\n').split(': ') for line in file]

    for line in lines:
        paths[line[0]] = folder + line[1]
    
    return paths

def get_folder_path(full_path):
    separate = full_path.split('/')
    return "/".join(separate[:-1]) + "/"
 
def save_to_file(file_path, data):
    np.savetxt(file_path, data, fmt='%.3f', delimiter=' ', newline='\r\n')