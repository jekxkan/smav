import math
import time
import logging

from dronekit import connect, VehicleMode, LocationGlobalRelative

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Drone:
    """Класс для управления дроном"""

    def __init__(self):
        """Инициализация дрона и подключение к нему по адресу"""
        self.vehicle = connect('udpin:0.0.0.0:14550', wait_ready=True)

    def arm(self):
        """Запуск моторов дрона"""
        while not self.vehicle.is_armable:
            logger.info("Ждем коптер...")
            time.sleep(1)

        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        while not self.vehicle.armed:
            logger.info("Ждем моторы...")
            time.sleep(1)
            break

    def takeoff(self, height: int):
        """
        Взлет дрона на заданную высоту

        Args:
            hight (int): Целевая высота для взлета в метрах
        """
        logger.info('Моторы работают')

        self.vehicle.simple_takeoff(height)

        while True:
            logger.info(f"Текущая высота: {self.vehicle.location.global_relative_frame.alt}")
            #При проверке текущей высоты допускаем погрешность в 5%
            if self.vehicle.location.global_relative_frame.alt >= height * 0.95:
                logger.info(f"Поднялись на {self.vehicle.location.global_relative_frame.alt} метров")
                break
            time.sleep(1)

    def goto(self, **kwargs):
        """
        Перемещение дрона к заданным координатам и высоте

        Args:
            **kwargs: Широта, долгота и высота для перемещения
        """
        lat = kwargs['latitude']
        lon = kwargs['longitude']
        alt = kwargs['height']

        location = LocationGlobalRelative(lat, lon, alt)
        self.vehicle.simple_goto(location)
        self.vehicle.groundspeed = 7.5

    def land(self):
        """Посадка дрона"""

        logger.info('Садимся')
        self.vehicle.mode = VehicleMode("LAND")
        while self.vehicle.location.global_relative_frame.alt > 1:
            logger.info(f'Текущая высота {self.vehicle.location.global_relative_frame.alt}')
            time.sleep(1)
        logger.info('Сели')

    def is_arrived(self, precision=1, **kwargs) -> bool:
        """Проверка, достиг ли дрон заданной точки.

        Args:
            **kwargs: Широта, долгота и высота целевой точки
            precision (float): Допустимая погрешность в метрах

        Returns:
            bool: True, если дрон заданной точки, иначе False
        """
        drone_loc = self.vehicle.location.global_relative_frame

        lat = kwargs['latitude']
        lon = kwargs['longitude']
        alt = kwargs['height']

        # Переводим разницу для широты и долготы из градусов в метры
        diff_lat_m = (lat - drone_loc.lat) * 1.113195e5
        diff_lon_m = (lon - drone_loc.lon) * 1.113195e5
        diff_alt_m = alt - drone_loc.alt

        dist_xyz = math.sqrt(diff_lat_m ** 2 + diff_lon_m ** 2 + diff_alt_m ** 2)

        if dist_xyz < precision:
            logger.info("Прибыли на место")
            return True
        else:
            logger.info("Еще не долетели")
            return False