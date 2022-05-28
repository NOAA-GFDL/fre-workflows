
if (! defined $ENV{MODULE_VERSION}) { 
  $ENV{MODULE_VERSION_STACK}="3.1.6";
  $ENV{MODULE_VERSION}="3.1.6";
} else {
  $ENV{MODULE_VERSION_STACK}=$ENV{MODULE_VERSION};
}

sub module {
  my $exec_prefix = "/usr/local/Modules/".$ENV{MODULE_VERSION};
  eval `$exec_prefix/bin/modulecmd perl @_`;
}

$ENV{MODULESHOME} = "/usr/local/Modules/".$ENV{MODULE_VERSION};

if (! defined $ENV{MODULEPATH} ) { 
  $ENV{MODULEPATH} = `sed 's/#.*$//' ${MODULESHOME}/init/.modulespath | awk 'NF==1{printf("%s:",$1)}'` 
}

if (! defined $ENV{LOADEDMODULES} ) { 
  $ENV{LOADEDMODULES} = ""; 
}

