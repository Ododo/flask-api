#!/bin/bash

echo -e "\n\n***User list"
curl localhost:5000/user/
echo -e "\n\n*** User 1 (not exists)"
curl localhost:5000/user/1
echo -e "\n\n***Create user"
curl -H "Content-Type: application/json" -X POST -d '{"email":"test@test","username":"test","password":"1234"}' localhost:5000/user/
echo -e "\n\n***User 1 (not exists)"
curl localhost:5000/user/1
echo -e "\n\n***User 2 (exists)"
curl localhost:5000/user/2
echo -e "\n\n***Exercise list (global)"
curl localhost:5000/exercise/
echo -e "\n\n***Get user 1 exercise list (none)"
curl localhost:5000/user/1/exercise/
echo -e "\n\n***Get User 2 exercise list (exists)"
curl localhost:5000/user/2/exercise/
echo -e "\n\n***User 2 exercice 1 (exists)"
curl localhost:5000/user/2/exercise/1
echo -e "\n\n***User 2 exercice 8 (not exists)"
curl localhost:5000/user/2/exercise/8
echo -e "\n\n***Delete user 1"
curl -X DELETE localhost:5000/user/1


echo -e "\n\n***END TESTS"
