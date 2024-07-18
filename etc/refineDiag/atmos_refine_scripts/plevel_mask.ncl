
undef("isPressureDimension")
function isPressureDimension (fi:file, dimName:string)
local result
begin
  result = False
  if (isfilevaratt(fi,dimName,"long_name")) then
    if (fi->$dimName$@long_name .eq. "pressure") then
      result = True
    end if
  end if
  return result
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; remove "_suffix" from string variable

undef("remove_suffix")
function remove_suffix (str:string)
local result,index
begin
  result = str
  index = str_index_of_substr(result,"_",-1)
  if (.not.ismissing(index)) then
    result = str_get_cols(result,0,index-1)
  end if
  return result
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; find the file name (tailname) from a path name

undef("tailname")
function tailname (str:string)
local result,index
begin
  result = str
  index = str_index_of_substr(result,"/",-1)
  if (.not.ismissing(index)) then
    result = str_get_cols(result,index+1,-1)
  end if
  return result
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

begin
  if (.not.isvar("ifile") .or. .not.isvar("ofile")) then
    print("ERROR: must supply input and output file names")
    status_exit(1)
  end if

  ; is the input file present?
  if (.not.isfilepresent(ifile)) then
    print("ERROR: input file does not exist")
    status_exit(1)
  end if

  if (.not.isvar("verbose")) then
    verbose = False
  end if

  if (.not.isvar("tavginfo")) then
    tavginfo = True
  end if

  ; open the input file
  fi = addfile(ifile,"r")

  ; get variable names in this file
  varnames = getfilevarnames(fi)

  ; count numbers of variables to process (if they have 4 dimensions and dim 1 is pressure)
  ; quit if there are no variable (this will avoid error messages)
  nfound = 0
  do iv = 0, dimsizes(varnames)-1
    dimnames = getfilevardims(fi,varnames(iv))
    if (dimsizes(dimnames) .eq. 4) then
      if (isPressureDimension(fi,dimnames(1))) then
        nfound = nfound + 1
      end if
    end if
    delete(dimnames)
  end do
  if (nfound .eq. 0) then
    print("No fields processed, output file not created")
    exit
  end if

  ; surface pressure (ps) must be present in the input file
  if (.not.isfilevar(fi,"ps")) then
    print("ERROR: input file does not have surface pressure (ps), output file not created")
    status_exit(1)
  end if

  ; read surf press
  ps = fi->ps

  ; if format not specified - format of the output file same as input file
  if (.not.isvar("format")) then
    format = systemfunc("ncdump -k "+ifile)
    format = str_sub_str(str_sub_str(str_capital(str_sub_str(format,"-"," "))," ",""),"Model","")
  end if
  ; check format
  if (all(format .ne. (/"Classic","64BitOffset","NetCDF4Classic","NetCDF4"/))) then
    print ("ERROR: invalid output netcdf format")
    status_exit(1)
  end if

  ; set the output format and increase header space
  setfileoption("nc","Format",format)
  setfileoption("nc","HeaderReserveSpace",16384)

  ; open the output file
  if (isfilepresent(ofile)) then
    system("/bin/rm -f "+ofile)
  end if
  fo = addfile(ofile,"c")
  filedimdef(fo,ps!0,-1,True)

  ; copy time: bounds
  if (isatt(ps&$ps!0$,"bounds")) then
    bnds = ps&$ps!0$@bounds
    fo->$bnds$ = fi->$bnds$
  end if

  ; is ptop defined?
  if (isvar("ptop")) then
    print("Masking will be applied using ptop = "+ptop)
  end if

  ; copy the global attributes
  ; change the filename
  global_attnames = getvaratts(fi)
  do i = 0, dimsizes(global_attnames)-1
    if (.not.ismissing(global_attnames(i))) then
      if (global_attnames(i) .ne. "filename") then
        fo@$global_attnames(i)$ = fi@$global_attnames(i)$
      else
        fo@$global_attnames(i)$ = tailname(ofile)
      end if
    end if
  end do

  ; loop thru all variables
  ndone = 0
  do iv = 0, dimsizes(varnames)-1
    dimnames = getfilevardims(fi,varnames(iv))

    ; process if they have 4 dimensions and
    ; first dimension has long_name = "pressure"
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    if (dimsizes(dimnames) .eq. 4) then
      if (isPressureDimension(fi,dimnames(1))) then
        data = fi->$varnames(iv)$
        plev = data&$dimnames(1)$
        do k = 0, dimsizes(plev)-1
          data(:,k,:,:) = where(plev(k) .gt. ps, data@_FillValue, data(:,k,:,:))
          ; masking at top of model if ptop is defined
          if (isvar("ptop")) then
            if (plev(k) .lt. ptop) then
              data(:,k,:,:) = data@_FillValue
            end if
          end if
        end do
        if (.not.tavginfo .and. isatt(data,"time_avg_info")) then
          delete(data@time_avg_info)
        end if
        ; output names should differ from input names
        ; if the input name has a "_string" suffix then remove it
        outname = remove_suffix(varnames(iv))
        if (verbose) then
          print(varnames(iv)+" ---> "+outname)
        end if
        fo->$outname$ = data
        ndone = ndone+1
        delete([/data,plev/])
      end if

    ; also process if there are 3 dimensions and the following conditions are met:
    ;    1) variable has coordinates attribute
    ;    2) coordinates variable exists in the file
    ;    3) coordinates variable is a scalar
    ;    4) coordinates variable has units = "Pa"
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    else if (dimsizes(dimnames) .eq. 3 .and. .not. any(varnames(iv) .eq. (/"cll","clm","clh"/))) then
      if (any(getfilevaratts(fi,varnames(iv)) .eq. "coordinates")) then
        coord = fi->$varnames(iv)$@coordinates
        if (isfilevar(fi,coord)) then ; multiple names will fail
          plev = fi->$coord$
          if (sum(dimsizes(plev)) .eq. 1) then
            if (isatt(plev,"units")) then
              if (plev@units .eq. "Pa" .and. plev .gt. 50000.) then
                data = fi->$varnames(iv)$
                data = where(plev .gt. ps, data@_FillValue, data)
                if (.not.tavginfo .and. isatt(data,"time_avg_info")) then
                  delete(data@time_avg_info)
                end if
                outname = remove_suffix(varnames(iv))
                if (verbose) then
                  print(varnames(iv)+" ---> "+outname)
                end if
                fo->$outname$ = data
                fo->$coord$ = fi->$coord$ ; also copy the coordinate variable
                ndone = ndone+1
                delete(data)
              end if
            end if
          end if
          delete(plev)
        end if
      end if

    else if (tavginfo .and. any(varnames(iv) .eq. (/"average_T1","average_T2","average_DT"/))) then
      fo->$varnames(iv)$ = fi->$varnames(iv)$
    end if
    end if
    end if
    delete(dimnames)
  end do

  delete(fi)
  delete(fo)

  if (ndone .gt. 0) then
    print(ndone+" fields processed")
  else
    ; this check done earily and should not be needed here
    print("No fields processed, output file not created")
    if (isfilepresent(ofile)) then
      system("/bin/rm -f "+ofile)
    end if
  end if
end
