#!/bin/bash

if [ -z $1 ]; then
    echo "You must specify an user"
    exit 1
fi

# Get user data
record_name=$(dscl . -read /Users/$1 RecordName | sed 's/RecordName: //g')
unique_id=$(dscl . -read /Users/$1 UniqueID | sed 's/UniqueID: //g')
primary_group_id=$(dscl . -read /Users/$1 PrimaryGroupID | sed 's/PrimaryGroupID: //g')
real_name=$(dscl . -read /Users/$1 RealName | sed -e 's/RealName://g' -e 's/^ //g' | awk '{printf("%s", $0 (NR==1 ? "" : ""))}')
user_shell=$(dscl . -read /Users/$1 UserShell | sed 's/UserShell: //g')

# Print user data
echo "${record_name}:*:${unique_id}:${primary_group_id}:${real_name}:/Users/$1:${user_shell}"

exit 0

# This simulates the Linux `getent password` on a Mac using `dscl`.
