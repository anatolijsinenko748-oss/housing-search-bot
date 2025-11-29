import random
from typing import List, Dict

class FakeDataGenerator:
    @staticmethod
    def generate_apartments(city : str, min_price : int, max_price : int, count: int = 5 ) -> List[Dict]:

        '''Гененрируем список фейковых данных'''

        streets = ['Ленина', 'Пушкина', 'Гагарина', 'Советская', 'Мира', 'Центральная']
        dictricts = ['Центральная', 'Севреный', 'Южный', 'Западный', 'Восточный']

        appartments = []

        for i in range(count):
            price = random.randint(min_price, max_price)
            rooms = random.choice([1, 2, 3, 4])
            area = random.randint(30, 120)
            floor = random.randint(1, 25)
            total_floor = random.randint(5, 25)


            appartment = {
                'id' : i +1,
                'adress' : f"{city}, ул. {random.choice(streets)}, д. {random.randint(1, 100)}",
                'district' : random.choice(dictricts),
                'price' : price,
                'rooms' : rooms,
                'area' : area,
                'floor' : floor,
                'total_floor' : total_floor,
                'descriprions' : f"Прекрасная {rooms}- комнантная квартира в {random.choice(['спальном', 'центральном'])} районе",
                'source' : random.choice(['Авито', 'Циан']),
                'url' : f"https://example.com/appartments/{i+1}"
            }
            
            appartments.append(appartment)
        
        return appartments


        

