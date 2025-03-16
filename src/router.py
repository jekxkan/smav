import json
import time

from pydantic import ValidationError

from drone import Drone
from dronekit import APIException
from flask import Blueprint, render_template, request

from schemas import Coordinates

routes = Blueprint('main', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route("/post-coordinates", methods=['POST'])
def post_coordinates() -> json:
    coordinates = request.json
    try:
        with open("src/coordinates.json", "a") as file:
            coordinates = Coordinates(**coordinates)
            json.dump(dict(coordinates), file)
            file.write("\n")
            return {'status': 'Данные успешно отправлены'}
    except ValidationError as e:
        e = e.errors()[0]['loc'][0]
        return {'status': f'Не заполнено поле {e}'}
@routes.route("/test", methods=['GET'])
def test() -> json:
    try:
        with open("src/coordinates.json", "r") as file:
            data = [json.loads(line) for line in file][-1]
            drone = Drone()
            drone.arm()
            drone.takeoff(10)
            drone.goto(**data)
            while not drone.is_arrived(**data):
                time.sleep(3)
            drone.land()
            return {'status':'Успех'}
    except APIException:
        return {'status': f"Симулятор не запущен или не удалось подключиться к нему"}
