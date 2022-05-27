
; given time the corresponding date is returned
;   time[*] must have the 'units' and 'calendar' attributes
;   date[*][3] is an integer where the last dimension
;   corresponds to [year,month,day]

undef("get_day")
function get_day(time[*]:numeric)
local ymd,dates
begin
   ymd = cd_calendar(time,-2)
   dates = new((/dimsizes(time),3/),integer)
   dates(:,0) = toint(ymd/10000)
   dates(:,1) = toint((ymd-dates(:,0)*10000)/100)
   dates(:,2) = ymd - (dates(:,0)*10000 + dates(:,1)*100)
   return dates
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; given integer date[3] a formatted string is returned
;   if fmt > 0  then out = "2000jan01"
;   if fmt <= 0 then out = "2000/01/01"

undef("format_date")
function format_date(date[3]:integer,fmt[1]:integer)
local year,mon,dy,mlabs,out
begin
  mlabs = (/"jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"/)
  year = sprinti("%4.4i",date(0))
  dy   = sprinti("%2.2i",date(2))
  if (fmt .gt. 0) then
    mon = mlabs(date(1)-1)
    delim = ""
  else
    mon = sprinti("%2.2i",date(1))
    delim = "/" 
  end if
  out = year+delim+mon+delim+dy
  return out
end

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; changes the 'cell_methods' attribute from 'time: XXX' to
;  'time: XXX within days time: mean over days'
;   where 'XXX' = 'min' or 'max'

undef("modify_cell_methods")
procedure modify_cell_methods (x:numeric)
local dim
begin
  dim = x!0
  if (isatt(x,"cell_methods")) then
    if (x@cell_methods .eq. dim+": min") then
      x@cell_methods = dim+": min within days "+dim+": mean over days"
    else if (x@cell_methods .eq. dim+": max") then
      x@cell_methods = dim+": max within days "+dim+": mean over days"
    end if
    end if
  end if
end
   
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

begin
  if (.not.isvar("ifile") .and. .not.isvar("ofile")) then
    print("ERROR: must supply input and output file names")
    status_exit(1)
  end if

  if (.not.isvar("var")) then
    var = "tas"
  end if

  ; is the input file present?
  if (.not.isfilepresent(ifile)) then
    print("ERROR: input file does not exist")
    status_exit(1)
  end if

  if (.not.isvar("verbose")) then
    verbose = False
  end if

  DEBUG = False

  ; open the input file
  fi = addfile(ifile,"r")

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
  
  ; mapping to gfdl names
  GFDLNAME = 0
  GFDLNAME@tas = "t_ref"
  GFDLNAME@uas = "u_ref"
  GFDLNAME@rhs = "rh_ref"  ; append _cmip?

  ; variable names (cmip & gfdl)
  varmin = var+"min"
  varmax = var+"max"
  gvar = var
  if (isatt(GFDLNAME,var)) then
    gvar = GFDLNAME@$var$
  end if
  gvar_min = gvar + "_min"
  gvar_max = gvar + "_max"
  
  ; read min/max (temperature) data
  if (isfilevar(fi,varmin) .and. isfilevar(fi,varmax)) then
    dmin = fi->$varmin$
    dmax = fi->$varmax$
    tempName = var
  else if (isfilevar(fi,"t_ref_min") .and. isfilevar(fi,"t_ref_max")) then
    dmin = fi->t_ref_min
    dmax = fi->t_ref_max
    tempName = gvar+"_"
  else
    print("ERROR: could not find min/max for "+var+"/"+gvar)
    status_exit(1)
  end if
  end if

  ; time dimension
  time = dmin&$dmin!0$
  ntime = dimsizes(time)
  if (isatt(time,"bounds")) then
    boundsName = time@bounds
    bounds = fi->$boundsName$
  else
    bounds = new((/ntime,2/),typeof(time))
    if (isatt(time,"units")) then
      if (str_get_cols(time@units,0,4) .eq. "days") then
        hdel = 0.5
      else if (str_get_cols(time@units,0,4) .eq. "hours") then
        hdel = 12.
      else
        print("ERROR: could not determine time bounds without the correct units")
        status_exit(1)
      end if
      end if
      do n = 0, ntime-1
        bounds(n,1) = time(n)+hdel
        bounds(n+1,0) = bounds(n,1)
      end do
      bounds(0,0) = time(0)-hdel
      bounds(ntime-1,1) = time(ntime-1)+hdel
    else
      print("ERROR: could not determine time bounds without units")
      status_exit(1)
    end if
  end if


  ; dates(:,3)  yr,mo,dy
  dates = get_day(time)

  if (DEBUG) then
    cnt = -1
    do n = 0, dimsizes(time)-1
      if (dates(n,2) .eq. 1) then
        cnt = cnt + 1
        count = " <--- " + cnt
      else
        count = " "
      end if
      print("n: "+sprinti("%3i",n)+"  year mo dy:"+sprinti("%4i",dates(n,0))+" "+sprinti("%2.2i",dates(n,1))+" "+sprinti("%2.2i",dates(n,2))+count)
    end do
  end if

  ; equal weight at all time axis points
  wt = new(ntime,float)
  wt = 1.0

  ; starting and ending day for each month
  sday = ind(dates(:,2).eq.1)
  npts = dimsizes(sday)
  print("num months = "+npts)
  eday = new(npts,typeof(sday))
  do n = 0, npts-2
    eday(n) = sday(n+1)-1
  end do
  eday(npts-1) = dimsizes(time)-1

  ; define new (output) time axis/bounds variable
  otime = new(npts,typeof(time))
  btime = new((/npts,2/),typeof(time))
  do n = 0, npts-1
    ks = sday(n)
    ke = eday(n)
   ;otime(n) = (time(ks)+time(ke))*0.5
    btime(n,0) = (/bounds(ks,0)/)
    btime(n,1) = (/bounds(ke,1)/)
    otime(n) = (btime(n,0)+btime(n,1))*0.5
  end do
  copy_VarAtts(time,otime)
  if (.not.isatt(time,"bounds")) then
    boundsName = "time_bounds"
    otime@bounds = boundsName
    btime@units = otime@units
    btime@long_name = otime@long_name
  else
    copy_VarAtts(fi->$boundsName$,btime)
  end if

  ; new GFDL-style average_* fields (if they exist)
  if (isatt(dmin,"time_avg_info")) then
    if (isfilevar(fi,"average_T1")) then
      avg1 = fi->average_T1
      avg2 = fi->average_T2
      avgd = fi->average_DT
      oavg1 = avg1(sday)
      oavg2 = avg2(eday)
      oavgd = oavg1
      do n = 0, npts-1
        oavgd(n) = sum(avgd(sday(n):eday(n)))
      end do
      copy_VarAtts(avgd,oavgd)
      delete(oavg1@missing_value)
      delete(oavg2@missing_value)
      delete(oavgd@missing_value)
      delete(oavg1@_FillValue)
      delete(oavg2@_FillValue)
      delete(oavgd@_FillValue)
    else
      delete(dmin@time_avg_info)
      delete(dmax@time_avg_info)
    end if
  end if

  if (isatt(otime,"_FillValue")) then
    delete(otime@_FillValue)
  end if
  

  otime!0 = time!0
  otime&$otime!0$ = otime
  btime!0 = time!0
  btime&$btime!0$ = otime
  btime!1 = "nv"
  if (isvar("oavg1")) then
    oavg1!0 = time!0
    oavg1&$oavg1!0$ = otime
    oavg2!0 = time!0
    oavg2&$oavg2!0$ = otime
    oavgd!0 = time!0
    oavgd&$oavgd!0$ = otime
  end if

  ; define new monthly time average variables (with on npts time values)
  dims = dimsizes(dmin)
  dims(0) = npts
  dminavg = new(dims,typeof(dmin))
  dmaxavg = new(dims,typeof(dmax))

  dminavg!0 = time!0
  dminavg&$dminavg!0$ = otime
  dmaxavg!0 = time!0
  dmaxavg&$dmaxavg!0$ = otime

  ; open the output file
  if (isfilepresent(ofile)) then
    system("/bin/rm -f "+ofile)
  end if
  fo = addfile(ofile,"c")
  filedimdef(fo,time!0,-1,True)

  ; save variables reference by coordinates attribute
  if (isatt(dmin,"coordinates")) then
    fo->$dmin@coordinates$ = fi->$dmin@coordinates$
  end if
  if (isatt(dmax,"coordinates")) then
    if (.not.isfilevar(fo,dmax@coordinates)) then
      fo->$dmax@coordinates$ = fi->$dmax@coordinates$
    end if
  end if

  ; loop through months and compute average
  do n = 0, npts-1
    ks = sday(n)
    ke = eday(n)
    ndys = ke-ks+1
    an = sprinti("%3i",n)
    adys = sprinti("%2.2i",ndys)
    print("n: "+an+"   ndys: "+adys+"   dates: "+format_date(dates(ks,:),1)+" to "+format_date(dates(ke,:),1)+"   ks,ke="+ks+", "+ke)
    dminavg(n,:,:) = dim_avg_wgt_n_Wrap(dmin(ks:ke,:,:), wt(ks:ke), (ke-ks+1)/3, 0)
    dmaxavg(n,:,:) = dim_avg_wgt_n_Wrap(dmax(ks:ke,:,:), wt(ks:ke), (ke-ks+1)/3, 0)
  end do
  if (isatt(dminavg,"average_op_ncl")) then
    delete(dminavg@average_op_ncl)
    delete(dmaxavg@average_op_ncl)
  end if
  modify_cell_methods(dminavg)
  modify_cell_methods(dmaxavg)

  fo->$boundsName$ = btime
  tempNameMin = tempName+"min"
  fo->$tempNameMin$ = dminavg
  tempNameMax = tempName+"max"
  fo->$tempNameMax$ = dmaxavg
  
  if (isvar("oavg1")) then
    fo->average_T1 = oavg1
    fo->average_T2 = oavg2
    fo->average_DT = oavgd
  end if

end
  
  
