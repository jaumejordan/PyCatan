from typing import NamedTuple
from Classes.Constants import MaterialConstants as mc
from Classes.Constants import BuildConstants as bc

class Materials(NamedTuple):
    """
    Clase que representa los materiales. Se usa tanto en la mano de los jugadores como en las ofertas
    """
    cereal: int
    mineral: int
    clay: int
    wood: int
    wool: int
    
    def get_from_id(self, material_constant):
        return self[material_constant]
    
    def add_from_id(self, material_constant, amount):
        return Materials(*[self[i] + amount if i == material_constant else self[i] for i in range(5)])
    
    def remove_from_id(self, material_constant, amount):
        return self.add_from_id(material_constant, -amount)

    # adders #####
    def add_cereal(self, amount):
        return self.add_from_id(mc.CEREAL, amount)

    def add_mineral(self, amount):
        return self.add_from_id(mc.MINERAL, amount)

    def add_clay(self, amount):
        return self.add_from_id(mc.CLAY, amount)

    def add_wood(self, amount):
        return self.add_from_id(mc.WOOD, amount)

    def add_wool(self, amount):
        return self.add_from_id(mc.WOOL, amount)
    
    def has_this_more_materials(self, materials):
        """
        Si le llega otra clase Materials() comprobará si hay más o igual materiales que los que hay en el parámetro y
        si le llega un string con lo que se quiere construir comprobará si tiene suficiente material para hacerlo.
        :param materials: (str o Materials()) Nombre de lo que se quiere construir o materiales.
        :return: bool
        """
        # todo: esto se puede mejorar bastante con un diccionario de costes de construcción en la clase constants
        if isinstance(materials, str):
            if materials == 'town':
                materials = Materials(1, 0, 1, 1, 1)
            elif materials == 'city':
                materials = Materials(2, 3, 0, 0, 0)
            elif materials == 'road':
                materials = Materials(0, 0, 1, 1, 0)
            elif materials == 'card':
                materials = Materials(1, 1, 0, 0, 1)
            else:
                return False

        if isinstance(materials, Materials):
            if (0 <= materials.cereal <= self.cereal and 0 <= materials.mineral <= self.mineral and
                    0 <= materials.clay <= self.clay and 0 <= materials.wood <= self.wood and
                    0 <= materials.wool <= self.wool):

                return True

            return False
        else:
            return False
        
    def __sub__(self, other):
        return Materials(*[self[i] - other[i] for i in range(5)])
    
    def __add__(self, other):
        return Materials(*[self[i] + other[i] for i in range(5)])
    
    def __mul__(self, other):
        return Materials(*[self[i] * other for i in range(5)])
    
    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        material_icons = ["🥖", "🪨", "🧱", "🪵", "🧶"]
        material_tuples = list(zip(self, material_icons))
        mls = [str(t[0]).rjust(2)+t[1] for t in material_tuples]
        return " ".join(mls)

    def __to_object__(self):
        return {'cereal': str(self.cereal), 'mineral': str(self.mineral), 'clay': str(self.clay),
                'wood': str(self.wood), 'wool': str(self.wool)}

    def __repr__(self):
        return 'Materials()'