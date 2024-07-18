#!/usr/bin/perl
use strict;
use lib "$ENV{MODULESHOME}/init";
use perl qw(module);

# gcp /archive/h1g/awg/warsaw/c96L33_am4p0_cmip6Diag/gfdl.ncrc4-intel-prod-openmp/history/tmp/19800101.atmos*.tile1.nc .

my ($ifile,$opt) = @ARGV;

# load NCL if needed
if (!grep /^ncl\/.*/, split/:/, $ENV{"LOADEDMODULES"}) {
  module ("load", "ncl");
}

my $flag = "False"; $flag = "True" if $opt;
my $ncl = create_script_file($ifile,$flag);
my $answer = `ncl -Qn \'ifile=\"$ifile\"\' <<EOF$ncl`;
print "$answer";

################################

sub create_script_file {
  my ($file,$opt) = @_;
  my $src = "
begin
  gfdl = $opt
  fi = addfile(\"$file\",\"r\")
  if (isfilevar(fi,\"ap\")) then
    nlev = filevardimsizes(fi,\"ap\")
    ptop = fi->ap(nlev-1)
    print(\"\"+ptop)
  else if (isfilevar(fi,\"pk\") .and. gfdl ) then
    nlev = filevardimsizes(fi,\"pfull\")
    if (dimsizes(nlev) .eq. 1) then
      ptop = fi->pfull(0)*100.
      print(\"\"+ptop)
    end if  
  else
    print(\"0\")
  end if  
  end if  
end
EOF";
  return $src;
}

