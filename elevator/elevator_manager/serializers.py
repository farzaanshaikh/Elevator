from rest_framework import serializers
from elevator_manager.models import (
    Building,
    Elevator,
    ElevatorLog
)

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["id", "name", "floors", "number_of_elevators"]

class ElevatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elevator
        fields = ["id", "current_floor", "is_operational"]


class ElevatorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElevatorLog
        fields = ['timestamp', 'destination_floor']
