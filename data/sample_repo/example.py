def add(a, b):
    return a + b

def multiply(a, b):
    result = add(a, b)
    return result

def calculate(a, b):
    x = multiply(a, b)
    y = add(a, b)
    return x + y