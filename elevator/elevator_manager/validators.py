from django.core.exceptions import ObjectDoesNotExist

from elevator_manager.models import Building, Elevator, ElevatorLog
from elevator_manager.constants import (
    VALIDATE_SUCCESS,
    VALID,
    INVALID,
    BUILDING_MIN_FLOORS,
    BUILDING_MAX_FLOORS,
    BUILDING_MIN_ELEVATORS,
    BUILDING_MAX_ELEVATORS,
    BUILDING_NAME_MAX_LEN,
    GROUND_FLOOR
)


def validate_building(data: dict) -> tuple[int, str]:
    '''
    '''
    if not (data['name'] and data['floors'] and data['elevators']):
        return (INVALID, "Please fill all 3 fields: name, floors, elevators.")
    if len(data['name']) >= BUILDING_NAME_MAX_LEN:
        return (INVALID, f"Max length for name of the building is {BUILDING_NAME_MAX_LEN}")
    
    try:
        floors = int(data['floors'])
        elevators = int(data['elevators'])
    except ValueError:
        return (INVALID, "Floors and elevators are integer types")

    if floors > BUILDING_MAX_FLOORS or floors < BUILDING_MIN_FLOORS:
        return (INVALID, f"Number of floors in building must be between {BUILDING_MIN_FLOORS} and {BUILDING_MAX_FLOORS}")
    if elevators > BUILDING_MAX_ELEVATORS or elevators < BUILDING_MIN_ELEVATORS:
        return (INVALID, f"Number of elevators in the building must be between {BUILDING_MIN_ELEVATORS} and {BUILDING_MAX_ELEVATORS}")
    return (VALID, VALIDATE_SUCCESS)

def validate_elevator(data: dict) -> tuple[int, str]:
    '''
    '''
    if not (data['called_at'] and data['dest'] and data['building_id']):
        return (INVALID, "Please fill all fields: called_at, dest, building_id")
    try:
        data['called_at'] = int(data['called_at'])
        data['dest'] = int(data['dest'])
        data['building_id'] = int(data['building_id'])
    except ValueError:
        return (INVALID, "All fields are integer types")
    
    try:
        building = Building.objects.get(pk=data['building_id'])
    except ObjectDoesNotExist:
        return (INVALID, f"Building with id {data['building_id']} does not exist")

    if any(var < GROUND_FLOOR for var in (data['called_at'], data['dest'])):
        return (INVALID, "Cannot go to negative floors. Ground floor is 0")
    if any(var > building.floors for var in (data['called_at'], data['dest'])):
        return (INVALID, f"Max floor for building '{building.name}' is {building.floors}.")
    if data['called_at'] == data['dest']:
        return (INVALID, "Called and destinations floors cannot be the same")

    return(VALID, VALIDATE_SUCCESS)

def validate_elevator_move(data: dict) -> tuple[int, str]:
    if not data['building_id']:
        return (INVALID, "Please enter the id of the building")
    return (VALID, VALIDATE_SUCCESS)