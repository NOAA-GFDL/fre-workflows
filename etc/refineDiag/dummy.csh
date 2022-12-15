# refineDiag test script
# This script acts like a refineDiag script, producing a spoofed history file
# that FRE will accept to include in the history_refineDiag directory
# This script can be included in test workflows to demonstrate refineDiag capability.
echo This is a dummy script
ls
cd $refineDiagDir
ls
touch dummy.nc
exit 0
