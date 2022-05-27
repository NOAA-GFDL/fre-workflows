###################################################################
#
#        Refine Atmospheric Diagnostics for CMIP6
#
###################################################################
#  required files -> output file
#  -----------------------------
#  *.atmos_month_cmip.tile?.nc  -> *.atmos_month_refined.tile?.nc
#  *.atmos_daily_cmip.tile?.nc  -> *.atmos_month_refined.tile?.nc
#  *.atmos_daily_cmip.tile?.nc  -> *.atmos_daily_refined.tile?.nc
#  *.atmos_tracer_cmip.tile?.nc -> *.atmos_tracer_refined.tile?.nc
#
#  require variables (set outside this script)
#  -----------------
#  set refineDiagDir = ???   # output directory
#                            # input directory = `cwd`
###################################################################

set CODE_DIRECTORY = $CYLC_WORKFLOW_RUN_DIR/etc/refineDiag/atmos_refine_scripts

#set xmlDir = $rtsxml:h
#set refineDiagScriptDir = $xmlDir/awg_include/refineDiag
#cp -r $refineDiagScriptDir/$CODE_DIRECTORY $CODE_DIRECTORY
#chmod +x $CODE_DIRECTORY/refineDiag_atmos.csh
#chmod +x $CODE_DIRECTORY/refine_fields.pl
#chmod +x $CODE_DIRECTORY/check4ptop.pl
#chmod +x $CODE_DIRECTORY/module_init_3_1_6.pl


# check that output directory is defined

if ($?refineDiagDir) then

# run script to create refined fields

   $CODE_DIRECTORY/refineDiag_atmos.csh $CODE_DIRECTORY $refineDiagDir
   set return_status = $?

else
   echo "ERROR: refineDiagDir is not defined - can run refineDiag scripts"
   set return_status = 1
endif

# set the status for frepp wrapper script to access

set status = $return_status

