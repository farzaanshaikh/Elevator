from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist

from elevator_manager.validators import (
    validate_building,
    validate_elevator,
    validate_elevator_move
)
from elevator_manager.models import (
    Building,
    Elevator,
    ElevatorLog
)
from elevator_manager.constants import (
    CREATION_SUCCESS,
    FETCH_SUCCESS,
    UPDATE_SUCCESS,
    PROCESS_SUCCESS,
    INVALID,
    ELEVATOR_MOVE_UP,
    ELEVATOR_MOVE_DOWN,
    ELEVATOR_STOPPED,
    ELEVATOR_DOOR_OPEN,
    ELEVATOR_DOOR_CLOSED
)
from elevator_manager.serializers import (
    BuildingSerializer,
    ElevatorSerializer,
    ElevatorLogSerializer
)


class BuildingView(APIView):

    def get(self, request, *args, **kwargs):
        '''
        Get info about a building and it's elevators
        '''
        building_id = request.data.get('id')
        try:
            building_id = int(building_id)
        except ValueError:
            return Response({'msg':"Invalid Type, id must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            building = Building.objects.get(pk=building_id)
        except ObjectDoesNotExist:
            return Response({'msg': "Error, no such building exists."}, status=status.HTTP_404_NOT_FOUND)

        building_res = BuildingSerializer(building).data
        elevator_res = ElevatorSerializer(building.elevators.all(), many=True).data
        response_data = {
            'msg': FETCH_SUCCESS,
            'data': {
                'building': building_res,
                'elevators': elevator_res
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        '''
        Create a new building and define it's features
        '''
        data = {
            'name': request.data.get("name"),
            'floors': request.data.get("floors"),
            'elevators': request.data.get("elevators")
        }

        # Validate data
        verdict, msg = validate_building(data)
        if verdict == INVALID:
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

        # Create building
        new_building = Building(name = data['name'], floors = int(data['floors']),
                                    number_of_elevators=int(data['elevators']))
        new_building.save()

        # Create the elevators in the building
        new_elevators = [Elevator(building = new_building) for idx in range(int(data['elevators']))]
        new_elevators = Elevator.objects.bulk_create(new_elevators)

        # Serialize json response
        building_res = BuildingSerializer(new_building).data
        elevator_res = ElevatorSerializer(new_elevators, many=True).data
        response_data = {
            'msg': CREATION_SUCCESS,
            'data': {
                'building': building_res,
                'elevators': elevator_res
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class ElevatorView(APIView):

    def get(self, request, *args, **kwargs):
        '''
        '''
        elevator_id = request.data.get('id')

        try:
            elevator_id = int(elevator_id)
        except ValueError:
            return Response({'msg':"Elevator id must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            elevator = Elevator.objects.get(pk=elevator_id)
        except ObjectDoesNotExist:
            return Response({'msg':"The elevator does not exist."}, status=status.HTTP_404_NOT_FOUND)

        ordering = "destination_floor" if elevator.movement_status == ELEVATOR_MOVE_UP else "-destination_floor"
        next_floor = elevator.logs.filter(is_done=False).order_by(ordering)
        if next_floor.exists():
            next_floor = next_floor.first().destination_floor
        else:
            next_floor = "No outstanding move requests."

        move = "Stopped"
        if elevator.movement_status == ELEVATOR_MOVE_UP:
            move = "Moving up"
        elif elevator.movement_status == ELEVATOR_MOVE_DOWN:
            move = "Moving down"

        res = {
            'next_floor': next_floor,
            'movement_status': move,
            'msg': FETCH_SUCCESS
        }

        return Response(res, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        '''
        Adds destination to an elevator. This API assumes the client has pushed the button on a floor,
        and has a destination floor in mind.
        '''
        data = {
            'building_id': request.data.get('building_id'),
            'called_at': request.data.get('called_at'),
            'dest': request.data.get('dest'),
        }

        # Validate data
        verdict, msg = validate_elevator(data)
        if verdict == INVALID:
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

        data['move_status'] = ELEVATOR_MOVE_UP if data['dest'] > data['called_at'] else ELEVATOR_MOVE_DOWN
        data['called_at'] = int(data['called_at'])
        data['dest'] = int(data['dest'])
        data['building_id'] = int(data['building_id'])
        all_elevators = Elevator.objects.filter(building_id=data['building_id'], is_operational=True)
        found = False
        for elevator in all_elevators:
            if elevator.available(data['called_at']):
                found = True
                break

        if not found or (elevator.movement_status != data['move_status'] and elevator.movement_status != ELEVATOR_STOPPED):
            return Response({'msg': "All elevators are busy. Please try later"}, status=status.HTTP_408_REQUEST_TIMEOUT)

        move_path = elevator.logs.filter(is_done=False).order_by('destination_floor')
        if move_path.exists():
            first_move = move_path.first().destination_floor
            if (data['move_status']==ELEVATOR_MOVE_UP and data['called_at'] > first_move) or \
                    (data['move_status']==ELEVATOR_MOVE_DOWN and data['called_at'] < first_move):
                return Response({'msg': "Anomaly detected: Called at floor exceeds elevators current destination. Please move the elevators first!"}, status=status.HTTP_403_FORBIDDEN)

        elevator.current_floor = data['called_at']
        elevator.door_status = ELEVATOR_DOOR_OPEN
        elevator.movement_status = data['move_status']
        elevator.save()

        if not move_path.filter(destination_floor=data['dest']).exists():
            client_req = ElevatorLog(elevator=elevator, destination_floor=data['dest'])
            client_req.save()
        res = dict()
        res['assigned'] = f"Elevator assigned with id '{elevator.pk}'"
        res['msg'] = PROCESS_SUCCESS
        return Response(res, status=status.HTTP_201_CREATED)


    def put(self, request, *args, **kwargs):
        '''
        '''
        elevator_id = request.data.get('id')
        operational = request.data.get('operational')
        door = request.data.get('door')

        if door:
            door = door.lower()

        if operational:
            operational = operational.lower()

        if operational and operational not in ["yes", "no"]:
            return Response({'msg': "operational parameter requires value 'yes' or 'no'"}, status=status.HTTP_400_BAD_REQUEST)

        if door and door not in ["open", "close"]:
            return Response({'msg': "door parameter requires value 'open' or 'close'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            elevator_id = int(elevator_id)
        except ValueError:
            return Response({'msg':"Elevator id must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            elevator = Elevator.objects.get(pk=elevator_id)
        except ObjectDoesNotExist:
            return Response({'msg':"The elevator does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if operational:
            elevator.is_operational = True if operational == 'yes' else False

        if door:
            elevator.door_status = ELEVATOR_DOOR_OPEN if door == "open" else ELEVATOR_DOOR_CLOSED

        elevator.save()

        serializer = ElevatorSerializer(elevator)
        res = {
            'msg': UPDATE_SUCCESS,
            'data': serializer.data
        }
        res['data']['door'] = "open" if elevator.door_status == ELEVATOR_DOOR_OPEN else "closed"

        return Response(res, status=status.HTTP_200_OK)


class ElevatorMoveView(APIView):

    def post(self, request, *args, **kwargs):
        '''
        '''
        data = {
            'building_id': request.data.get('building_id')
        }

        verdict, msg = validate_elevator_move(data)
        if verdict == INVALID:
            return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

        res = dict()
        all_elevator = Elevator.objects.filter(building_id=data['building_id'], is_operational=True)
        for elevator in all_elevator:
            ordering = "destination_floor" if elevator.movement_status == ELEVATOR_MOVE_UP else "-destination_floor"
            moves = elevator.logs.filter(is_done=False).order_by(ordering)
            next_move = moves.first()
            if next_move:
                next_move.is_done = True
                elevator.current_floor = next_move.destination_floor
                elevator.door_status = ELEVATOR_DOOR_CLOSED
                if len(moves) <=1:
                    elevator.movement_status = ELEVATOR_STOPPED
                next_move.save()
                elevator.save()
                res[elevator.pk] = f"Moved to floor {next_move.destination_floor}"
            else:
                res[elevator.pk] = "No moves"

        res['msg'] = PROCESS_SUCCESS
        return Response(res, status=status.HTTP_202_ACCEPTED)


class ElevatorLogsView(APIView):

    def get(self, request, *args, **kwargs):
        '''
        Get elevator data. Expects elevator id.
        '''
        elevator_id = request.data.get('id')

        try:
            elevator_id = int(elevator_id)
        except ValueError:
            return Response({'msg':"Elevator id must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            elevator = Elevator.objects.get(pk=elevator_id)
        except ObjectDoesNotExist:
            return Response({'msg':"The elevator does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ElevatorLogSerializer(elevator.logs.filter(is_done=False), many=True)
        if serializer.data:
            res = {
                'msg': FETCH_SUCCESS,
                'data': serializer.data
            }
            return Response(res, status=status.HTTP_200_OK)

        return Response({'msg': "No outstanding move requests."}, status=status.HTTP_200_OK)