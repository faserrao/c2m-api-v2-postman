# After edits:
grep -nE '^\s*\.PHONY:\s*venv$|^venv:$' Makefile   # should show only 1 pair
echo "Command: grep -nE '^\s*\.PHONY:\s*venv$|^venv:$' Makefile   # should show only 1 pair"
echo "Enter anything to continue"
read x
grep -n 'postman-mock-create:' Makefile            # should show only 1 definition
echo "Command: grep -n 'postman-mock-create:' Makefile            # should show only 1 definition"
echo "Enter anything to continue"
read x
grep -n 'POSTMAN_APIS_URL' Makefile                # verify uses $(POSTMAN_Q_ID) where appropriate
echo "Command: grep -n 'POSTMAN_APIS_URL' Makefile                # verify uses $(POSTMAN_Q_ID) where appropriate"
echo "Enter anything to continue"
read x
grep -n 'POSTMAN_COLLECTIONS_URL' Makefile         # verify workspace= usage for collections
echo "Command: grep -n 'POSTMAN_COLLECTIONS_URL' Makefile         # verify workspace= usage for collections"
echo "Enter anything to continue"
read x
grep -nE 'C2MAPIV2_(OPENAPI_SPEC|MAIN_SPEC_PATH)' Makefile  # confirm correct order or '='
echo "Command: grep -nE 'C2MAPIV2_(OPENAPI_SPEC|MAIN_SPEC_PATH)' Makefile  # confirm correct order or '='"
echo "Enter anything to continue"
read x
