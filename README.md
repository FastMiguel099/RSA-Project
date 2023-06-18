# Projeto Final: Redes e Sistemas Autónomos
## Description
Boats scout maritime area without passing through previously explored places

## Repository Structure
- Script being run by boats, necessary message formats and Docker file are in boat/
- Tracking system API and its Dockerfile are in frontend/ 
- Class presentations and final report are in reports/
- File to start the simulation is docker-compose.yml in root

## Usage
Must have a Docker Network and Docker Compose:
```
docker network create vanetzalan0 --subnet 192.168.98.0/24
docker-compose up
```

## Boat Tracking
Tracking available at: http://127.0.0.1:5000/

## Author
[Nuno Fahla](https://github.com/broth2) - 2023