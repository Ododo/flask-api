#!/bin/bash

echo -e "\n\n***User list"
curl -i localhost:5000/user/
echo -e "\n\n***User 1 (not exists)"
curl -i localhost:5000/user/1
echo -e "\n\n***Create user"
curl -H "Content-Type: application/json" -X PUT -d '{"email":"test@test","username":"test","password":"1234"}' -i localhost:5000/user/
echo -e "\n\n***Get user"
curl -i localhost:5000/user/1/exercice/
echo -e "\n\n***User 1 exercice 1 (exists)"
curl -i localhost:5000/user/1/exercice/1
echo -e "\n\n***User 1 exercice 2 (not exists)"
curl -i localhost:5000/user/1/exercice/2
echo -e "\n\n***User 2 exercice 1 (not exists)"
curl -i localhost:5000/user/2/exercice/1

echo -e "\n\n***END TESTS"
