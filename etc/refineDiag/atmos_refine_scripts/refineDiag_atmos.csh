###################################################################
#
#        Refine Atmospheric Diagnostics for CMIP6
#
###################################################################

set source_dir = $1     # CODE_DIRECTORY
set refineDiagDir = $2  # OUTPUT DIRECTORY

set refineAtmosErrors = 0

# find all files with 'plev*' dimension

set files_with_plev = ()
foreach atmos (`/bin/ls *.atmos*.tile1.nc`)
  if (`ncdump -h $atmos | perl -e '$n=0;while(<>){$n++ if(/\tplev\d* = \d+ ;/m)};print $n'`) then
    set files_with_plev = ($files_with_plev $atmos:r:r:e)
  endif
end

# find the pressure at the top model level (for possible masking)

set ptop_arg = ""
foreach atmos (`/bin/ls *.atmos*.tile1.nc`)
  set ptop = `$source_dir/check4ptop.pl $atmos`
  if ("$ptop" != "0") then
    set ptop_arg = 'ptop="'$ptop'"'
    break
  endif
end


# mask pressure levels below the surface (pressure)

foreach FILENAME ( $files_with_plev )
  set OFILENAME = `echo $FILENAME | sed -e 's/_cmip$//'`"_refined"
  foreach INFILE ( `ls *.$FILENAME.*` )
    if (-e $INFILE) then
      set OUTFILE = `echo $INFILE:t | sed -e "s/\.$FILENAME\./.$OFILENAME./"`
      $source_dir/refine_fields.pl plevel_mask $INFILE $OUTFILE $ptop_arg
      if ($?) @ refineAtmosErrors++
      mv -f $OUTFILE $refineDiagDir/$OUTFILE
    endif
  end
end

    
# compute monthly average of daily min/max near-surface temperature
# atmos_daily -> atmos_month_refined

set daily_files = `find  -name \*.atmos_daily_cmip.\* | sed -e "s/^\.\///"`
if ($#daily_files == 6) then
  foreach INFILE ( `ls *.atmos_daily_cmip.*` )
    set TMPFILE = $INFILE:t:s/.atmos_daily_cmip./.atmos_month_tmp./
    set OUTFILE = $refineDiagDir/$INFILE:t:s/.atmos_daily_cmip./.atmos_month_refined./
    if (-e $INFILE) then
      $source_dir/refine_fields.pl tasminmax $INFILE $TMPFILE
      if ($?) @ refineAtmosErrors++
      if (-e $OUTFILE) then
        # perform append in working directory to avoid long filenames
        cp $OUTFILE $OUTFILE:t
        echo "ncks -h -A $TMPFILE $OUTFILE:t"
        ncks -h -A $TMPFILE $OUTFILE:t
        if (! $?) then
          echo "cp -f $OUTFILE:t $OUTFILE"
          cp -f $OUTFILE:t $OUTFILE
          rm -f $OUTFILE:t
        else
          @ refineAtmosErrors++
        endif
        rm -f $TMPFILE
      else
        echo "mv $TMPFILE $OUTFILE"
        mv $TMPFILE $OUTFILE
      endif
    endif
  end
endif


# combining two aerosol/tracer variables into a single variable
# aerosol_month_cmip -> aerosol_month_refined

set tracer_files = `find  -name \*.aerosol_month_cmip.\* | sed -e "s/^\.\///"`
if ($#tracer_files == 6) then
  foreach INFILE ( $tracer_files )
    set OUTFILE = $INFILE:t:s/.aerosol_month_cmip./.aerosol_month_refined./
    $source_dir/refine_fields.pl tracer_refine $INFILE $OUTFILE
    if ($?) @ refineAtmosErrors++
    mv -f $OUTFILE $refineDiagDir/$OUTFILE
  end
endif


# find the atmos/aerosol file with SW up/down at surface

#set files_with_albedo = ()
#foreach atmos (`/bin/ls *.{atmos,aerosol}*.tile1.nc`)
#  if (`ncdump -h $atmos | perl -e '$n=0;while(<>){$n++ if(/(rsds|rsus)\(/)};print $n'` >= 2) then
#    set files_with_albedo = ($files_with_albedo $atmos:r:r:e)
#  endif
#end
set files_with_albedo = ( atmos_month_cmip atmos_daily_cmip atmos_8xdaily_cmip aerosol_month_cmip )


# compute surface albedo from shortwave up/down
foreach FILENAME ( $files_with_albedo )
  set albedo_files = `find  -name \*.$FILENAME.\* | sed -e "s/^\.\///"`
  if ($#albedo_files == 6) then
    foreach INFILE ( `ls *.$FILENAME.*` )
      if (-e $INFILE) then
        set OUTFILE = "$refineDiagDir/"`echo $INFILE:t | sed -e 's/_cmip\./_refined./'`
        set TMPFILE = `echo $INFILE:t | sed -e 's/_cmip\./_tmp./'`
        $source_dir/refine_fields.pl surface_albedo $INFILE $TMPFILE
        if ($?) @ refineAtmosErrors++
        if (-e $TMPFILE) then
          if (-e $OUTFILE) then
            # perform append in working directory to avoid long filenames
            cp $OUTFILE $OUTFILE:t
            echo "ncks -h -A $TMPFILE $OUTFILE:t"
            ncks -h -A $TMPFILE $OUTFILE:t
            if (! $?) then
              echo "cp -f $OUTFILE:t $OUTFILE"
              cp -f $OUTFILE:t $OUTFILE
              rm -f $OUTFILE:t
            else
              @ refineAtmosErrors++
            endif
            rm -f $TMPFILE
          else
            echo "mv $TMPFILE $OUTFILE"
            mv $TMPFILE $OUTFILE
          endif
        else
          echo "WARNING: $TMPFILE does not exist"
        endif
      endif
    end
  endif
end

# status returned is the number of errors
exit $refineAtmosErrors

