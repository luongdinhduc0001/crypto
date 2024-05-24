from ecpy.curves import Curve, Point
from ecpy.keys import ECPublicKey
import secrets

def modular_sqrt(a, p):
    if pow(a, (p - 1) // 2, p) == 1:
        return pow(a, (p + 1) // 4, p)
    return None

def mToP(m,cv):
    found = False
    p = cv.field
    for i in range(1000):
        X = 1000 * m + i
        y_square = (X**3 + cv.a * X + cv.b) % p
        y = modular_sqrt(y_square, p)
        if y is not None:
            point = Point(X, y, cv)
            found = True
            return point

    if not found:
        return None

def PTom(point):
    return point.x // 1000

import struct

def encode(string):
  """Encodes a string to a single integer."""
  return int.from_bytes(string.encode(), byteorder='big')

def decode(integer):
  """Decodes an integer to a string."""
  return integer.to_bytes((integer.bit_length() + 7) // 8, byteorder='big').decode()

cv = Curve.get_curve('secp256k1')
G = cv.generator
print("Generator point (Public key): \n\tG =", G)   # Public color

A = 2   # Alice's private color
B = 3   # Bob's private color
print("\nAlice's private key: \n\tA =", A)
print("Bob's private key: \n\tB =", B)

AG = A*G  # Alice's private color mix with Public color
BG = B*G  # Bob's private color mix with Public color 
print("\nAlice's mixed key: \n\tAG =", AG)
print("Bob's mixed key:   \n\tBG =", BG)

B_AG = B*AG
A_BG = A*BG
print("\nPrivate key of Alice and Bob (Calculated by Alice): \n\tA*(BG) =", A_BG)
print("Private key of Alice and Bob (Calculated by Bob): \n\tB*(AG) =", B_AG)

# Check
print("\nIs AG on the curve?", cv.is_on_curve(AG))
print("Is BG on the curve?", cv.is_on_curve(BG))
print("Is ABG on the curve?", cv.is_on_curve(A_BG))

# Check
message = "Hello, World!"
print("\nMessage:", message)
x = encode(message)
print("Encoded Message:", x)
Pm = mToP(x, cv)
print("\nPoint from integer m =", x, ":\n\tPm =", Pm)

# Encrypt
k = secrets.randbelow(cv.order - 1) + 1
print("\nRandom number k =", k)
C = (k*G, Pm + k*BG)
print("Ciphertext:\n\tC =", C)

# Decrypt
Pm_recovered = C[1] - B*C[0]
print("\nRecovered point from ciphertext:\n\tPm_recovered =", Pm_recovered)
print("Is Pm_recovered equal to Pm?", Pm_recovered == Pm)
m_recovered = PTom(Pm_recovered)
print("\nRecovered integer from point:\n\tm_recovered =", m_recovered)
print("Decode Message:", decode(m_recovered))



