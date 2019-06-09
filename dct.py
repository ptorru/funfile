#################################################################################
#  Copyright (c) 2019 Pedro Torruella
#
# Author: Pedro Torruella
#
# Description: Direct Cosine Transform. Just a very quick function to
#              implement DCT on the elements of a list.
#
#
# Resources
# Consulted:
#              [1] https://en.wikipedia.org/wiki/Discrete_cosine_transform
#################################################################################


from math import cos
from math import pi

# From wikipedia, implementing DCT-II
def dct(data):
    N = len(data)
    C = pi / N
    dct_out = []
    for k in range(N):
        sum_partial = 0
        for n in range(N):
            sum_partial += data[n] * cos(C * (n + 0.5) * k)
        dct_out.append(sum_partial)

    return dct_out


# Just a quick self-contained unit-test
if __name__ == '__main__':
    data = [10,0,10,0,10,0,10,0,10,0,10,0]

    new_data = dct(data)

    print("Lenght of input:", len(data), " Length of Output:", len(new_data))
    print(new_data)

    data = [0, 0, 0, 100, 0, 0, 0, 0]

    new_data = dct(data)

    print("Lenght of input:", len(data), " Length of Output:", len(new_data))
    print(new_data)

    data = []
    freq = 2
    N = 32
    for i in range(N):
        data.append(cos((2*pi/N)*i*freq))
        new_data = dct(data)
    print("Lenght of input:", len(data), " Length of Output:", len(new_data))
    print(new_data)
