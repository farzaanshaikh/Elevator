# Elevators
A backend server for a centralized elevator system.
## Build Instructions
### Dependencies
This is a packaged program and requires `docker` and `docker-compose` to be installed along with access to docker hub to pull images.

### Installation
Run the following commands in the directory with `Dockerfile` to build the server. It may take 3-5 mins on first run.
Depending on your operating system you may or may not need to use `sudo`.
```
sudo docker compose build
```
Run the following command to start the server.
```
sudo docker compose up
```
### Uninstall
After you are done run the following command to uninstall the built containers
```
docker compose down
```
Also check for any unwanted base images and remove them
```
sudo docker images

sudo docker rmi -f <image-id-here>
```

## API Documentation
In addition to the requested API's, I have added 2 new API's for added functionality. I may have also merged some requested API with similar objectives, while maintaining its intended purpose.
Please note, not passing the parameters may result in errors although most cases have validations.
Some parameters have hard limits and can be modifed in the `constants.py` file.

### Buildings
The program assumes there are buildings with a set amount of floors and elevators.
```
http://0.0.0.0:8080/elevator/building/
```
- `POST` Creates a building and it's elevators in the database. It requires the following parameters:

    - `name`: Name of the building. Duplicates are allowed
    - `floors`: Number of max floors in the building. Hard limit: 60.
    - `elevators`: Number of elevators to be created. Hard limit: 10.

- `GET` Fetch info about a building and it's elevators.

    -`id`: Id of the building.

### Elevators
Various elevator related operations make use of this api.
```
http://0.0.0.0:8080/elevator/elevator/
```
- `POST` Adds destination to an elevator. This API assumes the client has pushed the button on a floor, and has a destination floor in mind. When executed, the program will select an appropriate elevator, and that will have assumed to have arrived where the client called, with the clients destination added to its list of destinations. It will need to move using the move api discussed later.

    - `building_id`: Id of the building at which the client is at.
    - `called_at`: The floor at which the client is at.
    - `dest`: The destination floor of the client.

- `GET` Fetches the movement status (going up/down or stopped)of an elevator and the next floor it will arrive at.

    - `id`: The id of the elevator.

- `PUT` Updates an elevator's operational status (maintainence/malfunction) and its door (open/closed).

    - `id`: Id of the elevator
    - `operational`: (optional) 'yes' or 'no'
    - `door`: (optional) 'open' or 'close'.

### Move
Functionalities for elevator's movement
```
http://0.0.0.0:8080/elevator/move/
```
- `POST` Moves all the elevators by 1 step in a building.

    - `building_id`: Id of the building to simulate elevator movement

### Elevator Logs
Probably needed a better word, but here logs mean the list of destinations of an elevator.
```
http://0.0.0.0:8080/elevator/logs/
```
- `GET` Fetches all requests for a give elevator.

    - `id`: Id of the elevator.

## Extras: Introspection
For a closer view of what's happening, open a new window while the server is running. 
```
sudo docker ps
```
The above command will show two containers running, one of the main django app and the other of postgres. In order to access bash use the following command:
```
sudo docker exec -it <name-or-id-of-image> bash
```

In the postgres container use the following to access the database with password `postgres`:
```
psql -h db -U postgres
```