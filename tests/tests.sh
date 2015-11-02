#!/bin/bash

echo -e "\n\n***User list"
curl localhost:5000/user/
echo -e "\n\n*** User 1 (not exists)"
curl localhost:5000/user/1
echo -e "\n\n***Create user"
curl -H "Content-Type: application/json" -X POST -d '{"email":"test@test","username":"test","password":"1234"}' localhost:5000/user/
echo -e "\n\n***User 1 (exists)"
curl localhost:5000/user/1
echo -e "\n\n***User 2 (not exists)"
curl localhost:5000/user/2
echo -e "\n\n***Get user 1 exercise list"
curl localhost:5000/user/1/exercise/
echo -e "\n\n***User 1 exercice 1 (exists)"
curl localhost:5000/user/1/exercise/1
echo -e "\n\n***User 1 exercice 2 (not exists)"
curl localhost:5000/user/1/exercise/2
echo -e "\n\n***User 2 exercice 1 (not exists)"
curl localhost:5000/user/2/exercise/1

echo -e "\n\n***END TESTS"
