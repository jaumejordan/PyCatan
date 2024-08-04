from Classes.Constants import BuildConstants, MaterialConstants
from Classes.Materials import *


class TestMaterials:
    def test_add_materials(self):
        materials = Materials(0, 0, 0, 0, 0)

        materials = materials.add_cereal(1)
        assert materials.cereal == 1

        materials = materials.add_mineral(2)
        assert materials.mineral == 2

        materials = materials.add_clay(3)
        assert materials.clay == 3

        materials = materials.add_wood(4)
        assert materials.wood == 4

        materials = materials.add_wool(5)
        assert materials.wool == 5

        mc = [MaterialConstants.CEREAL, MaterialConstants.MINERAL, MaterialConstants.CLAY,
              MaterialConstants.WOOD, MaterialConstants.WOOL]
        for i in range(5):
            assert materials.get_from_id(mc[i]) == i + 1

    def test_has_more_materials_than_build_values(self):
        # Comprobamos que el mínimo funciona correctamente
        materials_for_town = Materials(1, 0, 1, 1, 1)
        assert materials_for_town.has_this_more_materials(BuildConstants.TOWN)

        materials_for_city = Materials(2, 3, 0, 0, 0)
        assert materials_for_city.has_this_more_materials(BuildConstants.CITY)

        materials_for_road = Materials(0, 0, 1, 1, 0)
        assert materials_for_road.has_this_more_materials(BuildConstants.ROAD)

        materials_for_card = Materials(1, 1, 0, 0, 1)
        assert materials_for_card.has_this_more_materials(BuildConstants.CARD)

        # Comprobamos que falla correctamente también
        assert not materials_for_town.has_this_more_materials(BuildConstants.CITY)

        # Y también que funciona si se tiene materiales suficientes
        assert materials_for_town.has_this_more_materials(BuildConstants.ROAD)

        # Y debería de tener materiales suficientes
        materials = Materials(1, 0, 4, 2, 7)
        assert materials.has_this_more_materials(BuildConstants.TOWN)

        # Nos aseguramos de que no acepta valores negativos
        materials = Materials(1, 0, 4, 2, 7)
        assert not materials.has_this_more_materials(Materials(1, 0, -1, 1, 1))


if __name__ == '__main__':
    test = TestMaterials()
    test.test_add_materials()
    test.test_has_more_materials_than_build_values()