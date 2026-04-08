import unittest

from pydantic import ValidationError

from app.pets.schemas import SPetCreate, SPetListParams


class PetSchemasTests(unittest.TestCase):
    def test_pet_create_normalizes_searchable_fields(self):
        pet = SPetCreate(
            type=" Dog ",
            breed=" Corgi ",
            name=" Lucky ",
            color=" Black ",
            sex=" Male ",
            age=" 2 years ",
            chip_number=" 123 ",
            brand_number=" 456 ",
            found_date="2026-03-24",
            found_time="11:20:00",
            address=" Moscow Kremlin ",
            description=" Friendly dog seen near the main square. ",
            status="lost",
        )

        self.assertEqual(pet.type, "dog")
        self.assertEqual(pet.color, "black")
        self.assertEqual(pet.sex, "male")
        self.assertEqual(pet.breed, "Corgi")
        self.assertEqual(pet.address, "Moscow Kremlin")

    def test_pet_list_params_reject_invalid_page(self):
        with self.assertRaises(ValidationError):
            SPetListParams(page=0)


if __name__ == "__main__":
    unittest.main()
