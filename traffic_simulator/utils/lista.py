class NodoLista:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class Lista:
    def __init__(self):
        self.primero = None
        self.ultimo = None
        self.tamano = 0

    def agregar(self, dato):
        nuevo = NodoLista(dato)
        if not self.primero:
            self.primero = nuevo
            self.ultimo = nuevo
        else:
            self.ultimo.siguiente = nuevo
            self.ultimo = nuevo
        self.tamano += 1

    def obtener(self, indice):
        actual = self.primero
        for _ in range(indice):
            if actual is not None:
                actual = actual.siguiente
        return actual.dato if actual else None

    def __iter__(self):
        actual = self.primero
        while actual:
            yield actual.dato
            actual = actual.siguiente

    def __len__(self):
        return self.tamano
