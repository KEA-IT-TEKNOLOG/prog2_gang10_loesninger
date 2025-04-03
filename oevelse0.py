"""
Øvelse 0

Kravspecifikation:

    Lav en klasse kaldet BitwiseOperations.

    Klassen skal have en konstruktør, der tager to heltal som parametre.​

    Klassen skal have metoder til at udføre følgende bitwise operationer:​

    AND

    OR

    XOR

    NOT

    Venstreskift (left shift)

    Højreskift (right shift)

    Hver metode skal returnere resultatet af operationen.

Eksempel på brug af klassen:

bitwise = BitwiseOperations(12, 25)
print("AND:", bitwise.bitwise_and())
print("OR:", bitwise.bitwise_or())
print("XOR:", bitwise.bitwise_xor())
print("NOT:", bitwise.bitwise_not())
print("Left Shift:", bitwise.left_shift(2))
print("Right Shift:", bitwise.right_shift(2))
"""

class BitwiseOperations:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def bitwise_and(self):
        return self.a & self.b

    def bitwise_or(self):
        return self.a | self.b

    def bitwise_xor(self):
        return self.a ^ self.b

    def bitwise_not(self):
        return ~self.a, ~self.b

    def left_shift(self, shift):
        return self.a << shift, self.b << shift

    def right_shift(self, shift):
        return self.a >> shift, self.b >> shift

# Test
bitwise = BitwiseOperations(12, 25)
print("AND:", bitwise.bitwise_and())
print("OR:", bitwise.bitwise_or())
print("XOR:", bitwise.bitwise_xor())
print("NOT:", bitwise.bitwise_not())
print("Left Shift:", bitwise.left_shift(2))
print("Right Shift:", bitwise.right_shift(2))