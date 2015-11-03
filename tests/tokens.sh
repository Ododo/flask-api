#!/bin/bash

echo -e "\n\n*** User List"
curl localhost:5000/user/

echo -e "\n\n*** Get token for user \"test\""
curl -H "Content-Type: application/json" -X POST -d '{"username":"test","password":"1234"}' localhost:5000/token/


echo -e "\n\n***END TESTS"
