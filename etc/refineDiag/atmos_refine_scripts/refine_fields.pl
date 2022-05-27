#!/usr/bin/perl
use strict;
use Cwd qw(abs_path);
use lib "$ENV{MODULESHOME}/init";
use perl qw(module);

# usage: 3 arguments
#  1) script  (either: plevel_mask, tasminmax, tracer_refine)
#  2) input file
#  3) output file

my %Opt = ( VERBOSE=>1 );

# input and output file names
die "ERROR: missing input and out file names" if (@ARGV < 3);
my ($script,$ifile,$ofile,$args) = @ARGV;

# script locations
my $package_location = substr(abs_path($0),0,rindex(abs_path($0),"/"));
my $nclscript = "$package_location/$script.ncl";

# load module NCL if needed (must be version 6.2.1 or greater)
if (!grep /^ncarg\/.*/, split/:/, $ENV{"LOADEDMODULES"}) {
  print STDOUT "NOTE: loading module ncarg/6.2.1\n" if $Opt{VERBOSE} > 0;
  module("load", "ncarg/6.2.1");
}
my $nclversion = `ncl -V`; chomp $nclversion;
die "ERROR: NCL version must be 6.2.1 or greater;" if ($nclversion lt "6.2.1");

# run the script
my $command = "ncl -Q \'ifile=\"$ifile\"\' \'ofile=\"$ofile\"\' $args verbose=True $nclscript";
print STDOUT "NCL Version $nclversion\n"   if $Opt{VERBOSE} > 0;
print STDOUT "$command\n"                  if $Opt{VERBOSE} > 0;
system ($command);
die "ERROR: ncl script failed" if $?;
