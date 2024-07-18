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

function get_formula_terms(fi[1]:file,dim[1]:string)
local OUT,i
begin
  OUT = 0
  terms = str_split(fi->$dim$@formula_terms," ")
  do i = 0, dimsizes(terms)-1
    if (.not.isStrSubset(terms(i),":")) then
      if (isfilevar(fi,terms(i))) then
        if (.not.isatt(OUT,terms(i))) then
          OUT = OUT+1
          OUT@$terms(i)$ = 0
        end if
      end if
    end if
  end do
  return OUT
end

undef("additional_variables_needed")
procedure additional_variables_needed(fi[1]:file,var[1]:string,LIST[1]:integer)
local BNDS,TERMS,dims,bvar,bvars,atts,ib,id,i,it
begin
  BNDS = 0
  TERMS = 0
  dims = getfilevardims(fi,var)
  do id = 0, dimsizes(dims)-1
    ; 1) check for bounds
    if (isfilevaratt(fi,dims(id),"bounds")) then
      bvar = fi->$dims(id)$@bounds
      if (isfilevar(fi,bvar)) then
        if (.not.isatt(BNDS,bvar)) then
          BNDS = BNDS+1
          BNDS@$bvar$ = 0
        end if
      end if
    end if
    ; 2) check for formula terms
    if (isfilevaratt(fi,dims(id),"formula_terms")) then
      TERMS = get_formula_terms(fi,dims(id))
    end if
  end do

  ; 3) check bounds variables for formula terms
  if (BNDS .gt. 0) then
    bvars = getvaratts(BNDS)
    do ib = 0, dimsizes(bvars)-1
      if (isfilevaratt(fi,bvars(ib),"formula_terms")) then
        NTERMS = get_formula_terms(fi,bvars(ib))
        if (NTERMS .gt. 0) then
          atts = getvaratts(NTERMS)
          do it = 0, dimsizes(atts)-1
            if (.not.isatt(TERMS,atts(it))) then
              TERMS = TERMS+1
              TERMS@$atts(it)$ = 0
            end if
          end do
          delete(atts)
        end if
      end if
    end do
  end if

  ; combine BNDS and TERMS into LIST
  if (BNDS .gt. 0) then
    atts = getvaratts(BNDS)
    do it = 0, dimsizes(atts)-1
      if (.not.isatt(LIST,atts(it))) then
        LIST = LIST+1
        LIST@$atts(it)$ = 0
      end if
    end do
    delete(atts)
  end if
  if (TERMS .gt. 0) then
    atts = getvaratts(TERMS)
    do it = 0, dimsizes(atts)-1
      if (.not.isatt(LIST,atts(it))) then
        LIST = LIST+1
        LIST@$atts(it)$ = 0
      end if
    end do
    delete(atts)
  end if

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
  REQUIRED = 0
  REQUIRED@emioa = (/"emipoa","chepsoa"/)
  REQUIRED@emiaoa = (/"emiapoa","chepasoa"/)
  REQUIRED@dryoa = (/"drypoa","drysoa"/)
  REQUIRED@wetoa = (/"wetpoa","wetsoa"/)
  REQUIRED@cheaqpso4 = (/"pso4_aq_kg_m2_s","pso4_aq_so2_reevap_ls"/)

  EXTRA_VARS = 0 ; stores additional bounds and formula term variables needed

  ; count numbers of variables to process (if they have 4 dimensions and dim 1 is pressure)
  ; quit if there are no variable (this will avoid error messages)
  nfound = 0
  outvars = getvaratts(REQUIRED)
  do vo = 0, dimsizes(outvars)-1
    ; only process if output var is not in file
    if (.not.isfilevar(fi,outvars(vo))) then
      invars = REQUIRED@$outvars(vo)$
      allpresent = True
      do vi = 0, dimsizes(invars)-1
        if (.not.isfilevar(fi,invars(vi))) then
          print(invars(vi)+" not found in input file (outvar="+outvars(vo)+")")
          allpresent = False
        end if
      end do
      if (allpresent) then
        nfound = nfound + 1
        additional_variables_needed(fi,invars(0),EXTRA_VARS)
      else
        delete(REQUIRED@$outvars(vo)$)
      end if
      delete(invars)
    else
      print("outvar="+outvars(vo)+" was found in the input file: no processing needed")
    end if
  end do
  if (nfound .eq. 0) then
    print("No fields to process, output file not created")
    exit
  end if
  ; update output variable list
  delete(outvars)
  outvars = getvaratts(REQUIRED)

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
  ; define time dimension
  invars = REQUIRED@$outvars(0)$
 ;print("invars(0) = "+invars(0))
  vardims = getfilevardims(fi,invars(0))
  timename = vardims(0)
  print("Time dimension: "+timename)
  filedimdef(fo,timename,-1,True)
  delete(invars)

  ; copy time: bounds
 ;if (isfilevaratt(fi,vardims(0),"bounds")) then
 ;  bndsname = fi->$vardims(0)$@bounds
 ;  fo->$bndsname$ = fi->$bndsname$
 ;end if
  xvars = getvaratts(EXTRA_VARS)
  do i = 0, dimsizes(xvars)-1
    print("Copying extra variable: "+xvars(i))
    fo->$xvars(i)$ = fi->$xvars(i)$
  end do

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

  if (tavginfo) then
    if (isfilevar(fi,"average_T1") .and. isfilevar(fi,"average_T2") .and. isfilevar(fi,"average_DT")) then
    else
      tavginfo = False
    end if
  end if
  

  ; loop thru all variables

  do vo = 0, dimsizes(outvars)-1
    if (isfilevar(fi,outvars(vo))) then
      continue
    end if
    invars = REQUIRED@$outvars(vo)$
    if (outvars(vo) .eq. "emioa") then
      data = fi->$invars(0)$
      data = data + fi->$invars(1)$
     ;copy_VarMeta(fi->$invars(0)$,data)
      data@long_name = "Rate of Emission and Production of Dry Aerosol Total Organic Matter"
      data@units = "kg m-2 s-1"
      data@standard_name = "tendency_of_atmosphere_mass_content_of_particulate_organic_matter_dry_aerosol_due_to_net_chemical_production_and_emission"
    else if (outvars(vo) .eq. "emiaoa") then
      data = fi->$invars(0)$
      data = data + fi->$invars(1)$
      data@long_name = "total emission of anthropogenic organic aerosol"
      data@units = "kg m-2 s-1"
      data@standard_name = "tendency_of_atmosphere_mass_content_of_particulate_organic_matter_dry_aerosol_particles_due_to_net_chemical_production_and_emission"
    else if (outvars(vo) .eq. "dryoa") then
      data = fi->$invars(0)$
      data = data + fi->$invars(1)$
      data@long_name = "Dry Deposition Rate of Dry Aerosol Total Organic Matter"
      data@units = "kg m-2 s-1"
      data@standard_name = "tendency_of_atmosphere_mass_content_of_particulate_organic_matter_dry_aerosol_due_to_dry_deposition"
    else if (outvars(vo) .eq. "wetoa") then
      data = fi->$invars(0)$
      data = data + fi->$invars(1)$
      data@long_name = "Wet Deposition Rate of Dry Aerosol Total Organic Matter"
      data@units = "kg m-2 s-1"
      data@standard_name = "tendency_of_atmosphere_mass_content_of_particulate_organic_matter_dry_aerosol_due_to_wet_deposition"
    else if (outvars(vo) .eq. "cheaqpso4") then
      data = fi->$invars(0)$
      data = data + fi->$invars(1)$
      data@long_name = "Aqueous-phase Production Rate of Sulfate Aerosol"
      data@units = "kg m-2 s-1"
      data@standard_name = "tendency_of_atmosphere_mass_content_of_sulfate_dry_aerosol_particles_due_to_aqueous_phase_net_chemical_production"
    else
      continue
    end if
    end if
    end if
    end if
    end if
    if (.not.tavginfo .and. isatt(data,"time_avg_info")) then
      delete(data@time_avg_info)
    end if
    comment = invars(0)+"+"+invars(1)
    print("output: "+outvars(vo)+" = "+comment)
    fo->$outvars(vo)$ = data
    fo->$outvars(vo)$@comment = comment
    delete([/data,invars/])
  end do

  if (tavginfo) then
    fo->average_T1 = fi->average_T1
    fo->average_T2 = fi->average_T2
    fo->average_DT = fi->average_DT
  end if

  delete(fi)
  delete(fo)

; if (ndone .gt. 0) then
;   print(ndone+" fields processed")
; else
;   ; this check done earily and should not be needed here
;   print("No fields processed, output file not created")
;   if (isfilepresent(ofile)) then
;     system("/bin/rm -f "+ofile)
;   end if
; end if
end
