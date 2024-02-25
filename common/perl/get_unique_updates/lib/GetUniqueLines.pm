package GetUniqueLines;

use Modern::Perl;
use List::Util;

use Data::Dumper;

use Pod::Usage;

sub check_file_format {
   my $file = shift;
   my $is_markdown;

   # Make sure file is in the right format
   # This is a very simple check to avoid needing to have more perl modules installed

   open( my $fh, "<", $file )
     or die "Can't open '$file': $!";
   my @rows = <$fh>;
   chomp @rows;

   # Line one should be a number of builds
   unless ( $rows[0] =~ /\d+\sbuilds/i ) {
      die( "First line of the filed does not appear to show the number of builds. Got:\n'" . $rows[0] . "'\n" );
   }

   # Line two should be an unordered list item which is a package name and link
   unless ( $rows[1] =~ /^-\s\[[^\s]+\s\d+[^\s]+\]\(https:\/\/[^\s]+\)/ ) {
      die( "Second line of the file is not in expected markdown format. Got:\n'" . $rows[1] . "'\n" );
   }
   $is_markdown = 1;

   close($fh) or die $!;

   return $is_markdown;
}

sub get_unique_lines {

   # Take input file
   my $input_file = shift;
   my %packages;

   open( my $fh, "<", $input_file )
     or die "Can't open file '$input_file': $!";
   my @lines = <$fh>;
   chomp @lines;

   # iterate through lines and parse out package names
   # Create a hash of packages, package names are the keys
   # Each update of each key will write in the line with the highest version
   # Skip first line since that is the package count
   for my $i ( 1 .. $#lines ) {
      my $line = $lines[$i];

      # Get package name
      if ( $line =~ /^-\s\[([^\s]+)\s/ ) {
         my $pkg_name = $1;

         #  say "Got package name $1";
         $packages{$pkg_name} = $line;
      } else {
         next;
      }
   }

   # return the hash of unique package lines
   return %packages;
}

sub write_to_stdout {
   my $package_href = shift;
   my %package_list = %{$package_href};

   foreach my $name ( sort( keys %package_list ) ) {
      print $package_list{$name} . "\n";
   }

   return;
}

sub write_to_file {
   my ( $file_path, $package_href ) = @_;
   my %package_list = %{$package_href};

   open( my $fh, ">", $file_path )
     or die "Can't open '$file_path': $!";

   foreach my $name ( sort( keys %package_list ) ) {
      print $fh $package_list{$name} . "\n";
   }

   close($fh) or die $!;

   return;

}

1;
