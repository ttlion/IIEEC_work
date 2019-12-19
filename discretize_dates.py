# -*- coding: utf-8 -*-
"""
File to discretize dates in datasets.
The file outputs the same dataset, but with dates discretized into 0, 1, 2, ...

@author: Tiago Leão
"""

###########################################################################
###########################################################################
# Imports

import csv
from datetime import datetime
import os
import sys                                                                              

###########################################################################
###########################################################################
# Defs

def months_appart(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def showUsage():
    print('usage: python discretize_dates.py inputFile.csv outputFile.csv deltaT option1 option2\n')
    print('inputFile.csv: Input dataset in table format')
    print('outputFile.csv: Output dataset in table format')
    print('deltaT: number of months of interval between two timesteps to be created')
    print('option1 (0 or 1): 0 does Last Obs Carried Forward, 1 fills with ?')
    print('option2 (0 or 1): 0 keeps existing intermeditate timesteps, 1 forces timeseries always with deltaT between consecutive timesteps)')
    print('\nRun python discretize_dates.py -e for an example of input')
    return

def printExample():
    print('Example of Input:\n')
    print('+-----+------------+----------+----------+')
    print('| REF | Date       | Feature1 | Feature2 |')
    print('+-----+------------+----------+----------+')
    print('| 1   | 10/02/2000 | a        | A        |')
    print('+-----+------------+----------+----------+')
    print('| 1   | 03/04/2000 | b        | B        |')
    print('+-----+------------+----------+----------+')
    print('| 1   | 05/05/2000 | c        | C        |')
    print('+-----+------------+----------+----------+')
    print('| 1   | 07/01/2001 | d        | D        |')
    print('+-----+------------+----------+----------+')
    print('| 2   | 03/03/1999 | e        | E        |')
    print('+-----+------------+----------+----------+')
    print('| 2   | 04/02/2000 | f        | F        |')
    print('+-----+------------+----------+----------+')
    print('| 2   | 05/04/2001 | g        | G        |')
    print('+-----+------------+----------+----------+')
    print('| 3   | 10/06/2018 | h        | H        |')
    print('+-----+------------+----------+----------+')
    print('| 3   | 04/07/2018 | i        | I        |')
    print('+-----+------------+----------+----------+')
    print('| 3   | 04/09/2018 | l        | L        |')
    print('+-----+------------+----------+----------+')
    return

###########################################################################
###########################################################################
# Check command line arguments validity

if len(sys.argv) == 2:
    if sys.argv[1] == '-h':
        showUsage()
        exit()
    elif sys.argv[1] == '-e':
        printExample()
        exit()


if len(sys.argv) != 6:
    print('Not all arguments inserted! Run with -h for usage')
    exit()

###########################################################################
###########################################################################
# Read input and output files

if sys.argv[1].find('.csv') == -1:
    print('Input file must be .csv format! Run with -h for usage')
    exit()

if sys.argv[2].find('.csv') == -1:
    print('Output file must be .csv format! Run with -h for usage')
    exit()

inputpath = sys.argv[1]
outputpath = sys.argv[2]

# Isto e ficheiro auxiliar por causa das ultimas linhas de codigo
auxiliarPath = "auxiliar.csv"
# cria-se ficheiro auxiliar porque o ficheiro de output nao e impresso logo
# no formato desejado para csv, logo cria-se auxiliar e depois faz-se prune

###########################################################################
###########################################################################
# Abrir os ficheiros e inicializar readers e writers

inputFile = open(inputpath, newline='', encoding='utf-8-sig')
auxiliarFile = open(auxiliarPath, 'w', newline='')
reader = csv.reader(inputFile)
writer = csv.writer(auxiliarFile)

###########################################################################
###########################################################################

# Tirar o header
header = next(reader)

# Substituir o campo da date por um campo de datestep
header.pop(1)
header.insert(1, 'dateStep')

# Escrever o header no ficheiro de output
writer.writerow(header)

# Array para fill com ? se user especificar esssa opcao
allUnknown = ['?'] * (len(header) - 2)

###########################################################################
###########################################################################
# Inicializacoes

# Estou a assumir que os ids de pacientes nao sao negativos
prevRef = -100
currRef = 0

if int(sys.argv[3]) < 1:
    print('deltaT must be positive! Run with -h for usage')
    exit()

# timeIntervals sao de meses
timeInterval = int(sys.argv[3])


# Opcoes dos modos de funcionamento do programa

if int(sys.argv[4]) != 0 and int(sys.argv[4]) != 1 :
    print('option 1 must be 0 or 1! Run with -h for usage')
    exit()

if int(sys.argv[5]) != 0 and int(sys.argv[5]) != 1 :
    print('option 2 must be 0 or 1! Run with -h for usage')
    exit()

option = int(sys.argv[4])
forceConstantInterval = int(sys.argv[5])

###########################################################################
###########################################################################

# Os casos de forceConstantInterval=1 e forceConstantInterval=0 sao explicitamente
# separados porque isso evita ter ifs dentro dos ciclos e, ainda que no codigo
# se tenha o ciclo for replicado, em ficheiros muito grandes com muitos dados
# ganha-se em termos de velocidade de programa por nao se fazer muitos ifs
# dentro dos ciclos for
# Como este script é pequeno, compensa replicar os ciclos para ganhar eficiencia

###########################################################################
###########################################################################
# Ciclo de leitura e escrita para caso em que se força time series com 
# intervalos de tempo constantes

if forceConstantInterval == 1:

    # Init de valores
    currTimestep = 0
    nextMandatory = timeInterval + 1 # para nao entrar no if na primeira iteracao do for
    
    # Estes dois nem e preciso fazer init, apenas faco para nao haver warnings em baixo
    timestepDiscretized = 0
    prevRow = 0 # Isto depois vai deixar de ser int para ser uma row

    for row in reader:
        # Ler o ref e a data da linha em analise
        currRef = row[0]
        date_curr = datetime.strptime(row[1], '%d/%m/%Y')
        
        # Tirar o ref e a data da lista porque depois vou imprimir
        row.pop(0)
        row.pop(0)
        
        # Caso em que se tem novo ref e se tem que reinicializar tudo
        if currRef != prevRef:
            
            # Para se escrever sempre o ultimo dado da ref anterior
            if currTimestep > nextMandatory - timeInterval:
                if option == 0: # Fazer last observation carried forward
                    writer.writerow([prevRef , timestepDiscretized, prevRow])
                elif option == 1: # Fazer ? fill
                    writer.writerow([prevRef , timestepDiscretized, allUnknown])
            
            date_init = date_curr
            currTimestep = 0
            nextMandatory = 0
            prevRow = row
            timestepDiscretized = 0
        
        # Ver qual o indice da linha atual
        currTimestep = months_appart(date_curr, date_init)
        
        # Caso ainda se tenha que escrever indices ate chegar ao atual
        while currTimestep > nextMandatory:
            if option == 0: # Fazer last observation carried forward
                writer.writerow([currRef , timestepDiscretized, prevRow])
            elif option == 1: # Fazer ? fill
                writer.writerow([currRef , timestepDiscretized, allUnknown])
            
            timestepDiscretized += 1
            nextMandatory += timeInterval
        
        # So se estiver no timestep exato e que se imprime no novo ficheiro
        if currTimestep == nextMandatory:
            writer.writerow( [currRef , timestepDiscretized, row] )
            timestepDiscretized += 1
            nextMandatory += timeInterval
        
        #Alterar os prevs
        prevRef = currRef
        prevRow = row
    
    # Para se escrever sempre o ultimo dado da ultima ref
    if currTimestep > nextMandatory - timeInterval:
        if option == 0: # Fazer last observation carried forward
            writer.writerow([currRef , timestepDiscretized, prevRow])
        elif option == 1: # Fazer ? fill
            writer.writerow([currRef , timestepDiscretized, allUnknown])

###########################################################################
###########################################################################
# Ciclo de leitura e escrita para caso em que se mantem os timesteps intermedios

else:
    for row in reader:
        # Ler o ref e a data da linha em analise
        currRef = row[0]
        date_curr = datetime.strptime(row[1], '%d/%m/%Y')
        
        #Tirar o ref e a data da lista porque depois vou imprimir
        row.pop(0)
        row.pop(0)
        
        #Caso em que se tem novo ref e se tem que reinicializar tudo
        if currRef != prevRef:
            date_init = date_curr
            currTimestep = 0
            nextMandatory = 0
            prevRow = row
        
        # Ver qual o indice da linha atual
        currTimestep = months_appart(date_curr, date_init)
        
        # Caso ainda se tenha que escrever indices ate chegar ao atual
        while currTimestep > nextMandatory:
            if option == 0: # Fazer last observation carried forward
                writer.writerow([currRef , nextMandatory, prevRow])
            elif option == 1: # Fazer ? fill
                writer.writerow([currRef , nextMandatory, allUnknown])
            
            nextMandatory += timeInterval
        
        # Se estiver no timestep exato tem que se incrementar nextMandatory
        if currTimestep == nextMandatory:
            nextMandatory += timeInterval
    
        # E depois escreve-se sempre, ao contrario de no outro ciclo for
        writer.writerow( [currRef , currTimestep, row] )
        
        #se quiser tambem imprimir a data dd/mm/yyyy:
        #writer.writerow([currRef , date_curr.strftime("%d/%m/%Y"), currTimestep, row] )
        
        #Alterar os prevs
        prevRef = currRef
        prevRow = row    

###########################################################################
###########################################################################
# Fechar os ficheiros
    
inputFile.close()
auxiliarFile.close()

###########################################################################
###########################################################################
# Eliminar chars [ ' " e ] do ficheiro de output

fileToPrune = open(auxiliarPath, newline='', encoding='utf-8-sig')
outputFile = open(outputpath, 'w', newline='')

data = fileToPrune.read()
data = data.replace("'", "")
data = data.replace("[", "")
data = data.replace("]", "")
data = data.replace('"', "")
data = data.replace(' ', "")
outputFile.write(data)

fileToPrune.close()
outputFile.close()

os.remove("auxiliar.csv")

###########################################################################
###########################################################################