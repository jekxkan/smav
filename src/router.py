import json
import time

from src.schemas import Coordinates
from src.drone import Drone
from dronekit import APIException
from flask import Blueprint, render_template

routes = Blueprint('main', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.post("/post-coordinates")
def post_coordinates(coordinates: Coordinates):
    with open("src/coordinates.json", "a") as file:
        json.dump(coordinates.dict(), file)
        file.write("\n")
    return coordinates

@routes.get("/test")
def testing():
    try:
        with open("src/coordinates.json", "r") as file:
            data = [json.loads(line) for line in file][-1]
            drone = Drone()
            drone.arm()
            drone.takeoff(20)
            drone.goto(**data)
            while not drone.is_arrived(**data):
                time.sleep(3)
            drone.land()
            return {'status':'Успех'}
    except APIException:
        return {'status': f"Симулятор не запущен или не удалось подключиться к нему"}
