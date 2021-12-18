from bitarray import bitarray
from numpy.random import Generator, MT19937
import sys


def CRCFunc(filename: str, divisor: str, len_crc: int) -> int:
    """
    This function computes the CRC of a plain-text file 
    arguments:
    filename: the file containing the plain-text
    divisor: the generator polynomium
    len_crc: The number of redundant bits (r)
    """

    redundancy = len_crc * bitarray('0')
    A_bin = bitarray()
    p = bitarray(divisor)
    len_p = len(p)
    with open(filename, 'rb') as file:
        A_bin.fromfile(file)
    cw = A_bin + redundancy
    rem = cw[0 : len_p]
    end = len(cw)
    for i in range(len_p, end + 1):
        if rem[0]:
            rem ^= p
        if i < end:
            rem = rem << 1 
            rem[-1] = cw[i]
    #print(rem)
    return rem[len_p-len_crc : len_p] 

def codificador(filename: str, divisor: str, len_crc: int):
    #COdificamos el arreglo de caracteres, se agrega el CRC al final.

    crc = CRCFunc(filename, divisor, len_crc) #mandamos parmetros a CRCFunc "archivo", "divisor", "longitud_crc=4"
    A_bin = bitarray() #COnvertimos a binario
    with open(filename, 'rb') as f:
        A_bin.fromfile(f)
    cw = A_bin + crc
    return cw #REgresamos archivo binario + crc


def generador_de_errores(codigo : str, numR: int, semilla : int): 
    

    """
    Generar rafaga tamanio numR. De los bits que se miden vamos a invertir "aux".
    REgresamos cdigo modificado
    """
    valorA = 402515 #VAlor utilizado para dar aleatoriedad a generador y semilla.
    Array = []

    '''
    Mersenne TWister MT19937 provides a capsule containing function pointers that produce doubles, and unsigned 32 and 64- bit integers [1]. 
    These are not directly consumable in Python and must be consumed by a Generator or similar object that supports low-level access.
    '''
    Gen = Generator(MT19937(semilla + valorA))
    aux = int(Gen.integers(3, numR-1)) #num aleatroio de generador.
    
    codigo[semilla] = not codigo[semilla] #cambiar bit 0 -> 1 y 1 -> 0 
    codigo[semilla+numR-1] = not codigo[semilla+numR] #INvertimos codigo[semilla+numR-1]
    #Arreglo de nmeros a cambiar
    for i in range(0, aux):
        P = int(Gen.integers(1, numR-1))
        if P not in Array:
            Array.append(P)
    #MOdificamos
    for i in Array:   
        codigo[i+semilla] = not codigo [i+semilla]

    return codigo #regresamos codigo modificado




def descodificador(A_bin : str , divisor: str, len_crc: int):

    #decodificador usando division y agregando bits de crc al final
    #Similar a codificador

    p = bitarray(divisor)
    len_p = len(p)
    cw = A_bin
    rem = cw[0 : len_p]
    end = len(cw)
    for i in range(len_p, end + 1):
        if rem[0]:
            rem ^= p
        if i < end:
            rem = rem << 1 
            rem[-1] = cw[i]
    return rem[len_p-len_crc : len_p]


def validador(filename: str, divisor: str, len_crc: int, numR : int, semilla : int):
    
    # VAlidamos si el mensaje llega sin errores basado en CRC
  
    mensaje = False #MEnsaje con error
    redundancy = bitarray('0') * (len_crc)

    codigoCod = codificador(filename, divisor, len_crc) #COdificamos
    codigoMod = generador_de_errores(codigoCod, numR, semilla) #modificamos
    codigoDec = descodificador(codigoMod, divisor, len_crc) #decodificamos
    if(redundancy == codigoDec): mensaje = True #regresa verdadero si redundancy = bits de codigoDec
    return mensaje


def main():

    #Llamamos a validador para encontrar el nmero de errores.
    numR = int(sys.argv[1])
    errores = 0
    divisor = '10101'
    for i in range (0, 1000):
        aux =  validador('test.txt', divisor, 4, numR, i)
        if ( aux == False):
            errores=errores+1
    print ("\n\nErrores al momento de mandar 1000 = ", errores, "\n")



if __name__ == '__main__':
    main()