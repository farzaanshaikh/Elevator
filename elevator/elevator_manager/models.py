from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from elevator_manager.constants import (
    BUILDING_MAX_FLOORS,
    BUILDING_MIN_FLOORS,
    BUILDING_MAX_ELEVATORS,
    BUILDING_MIN_ELEVATORS,
    ELEVATOR_DOOR_OPEN,
    ELEVATOR_DOOR_CLOSED,
    GROUND_FLOOR,
    ELEVATOR_STOPPED,
    ELEVATOR_MOVE_UP,
    ELEVATOR_MOVE_DOWN
)


class Building(models.Model):
    name = models.CharField(max_length=128)
    floors = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(BUILDING_MIN_FLOORS), MaxValueValidator(BUILDING_MAX_FLOORS)])
    number_of_elevators = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(BUILDING_MIN_ELEVATORS), MaxValueValidator(BUILDING_MAX_ELEVATORS)])


class Elevator(models.Model):
    DOOR_CHOICES = (
        (ELEVATOR_DOOR_OPEN, 'Open'),
        (ELEVATOR_DOOR_CLOSED, 'Closed')
    )

    MOVEMENT_CHOICES = (
        (ELEVATOR_STOPPED, 'Stopped'),
        (ELEVATOR_MOVE_UP, 'Moving Up'),
        (ELEVATOR_MOVE_DOWN, 'Moving Down')
    )

    building = models.ForeignKey(Building, related_name="elevators", on_delete=models.CASCADE)
    door_status = models.BooleanField(default=ELEVATOR_DOOR_CLOSED, choices=DOOR_CHOICES)
    current_floor = models.PositiveSmallIntegerField(default=GROUND_FLOOR, validators=[MinValueValidator(GROUND_FLOOR), MaxValueValidator(BUILDING_MAX_FLOORS)])
    movement_status = models.PositiveSmallIntegerField(default=ELEVATOR_STOPPED, choices=MOVEMENT_CHOICES)
    is_operational = models.BooleanField(default=True)

    def is_busy(self, dest: int) -> bool:
        if self.movement_status == ELEVATOR_STOPPED:
            return False
        elif self.current_floor < dest and self.movement_status == ELEVATOR_MOVE_UP:
            return False
        elif self.current_floor > dest and self.movement_status == ELEVATOR_MOVE_DOWN:
            return False
        return True


class ElevatorLog(models.Model):
    elevator = models.ForeignKey(Elevator, related_name="logs", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    destination_floor = models.PositiveSmallIntegerField(validators=[MinValueValidator(GROUND_FLOOR), MaxValueValidator(BUILDING_MAX_FLOORS)])
    is_done = models.BooleanField(default=False)