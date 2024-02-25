use Test2::V0;
use Test2::Tools::Exception qw/dies lives/;
use Test2::Plugin::DieOnFail;
use Test2::Plugin::ExitSummary;
use Test::File;

use FindBin qw($Bin);
use lib "$Bin/../lib";

my $text_file   = "$Bin/../t/data/random_text";
my $md_file     = "$Bin/../t/data/markdown_text.md";
my $output_dir  = "$Bin/../t/data";
my $output_file = "markdown_output.md";
my $file_path   = $output_dir . '/' . $output_file;

my $expected_broadcom_ver  = 'broadcom-sta 6.30.223.271-385';
my $expected_darktable_ver = 'darktable 4.6.0-77';

BEGIN {
   plan(6);
   use GetUniqueLines;
   pass('Module loads correctly.');
}

ok( GetUniqueLines::check_file_format($md_file), "Markdown file passes file check" );

like( dies { GetUniqueLines::check_file_format($text_file) }, qr/First line/, "Text file fails file check" );

# Make sure we get highest package versions from the result
my %packages = GetUniqueLines::get_unique_lines($md_file);
my $pkg_href = \%packages;

# Capture output of write_to_stdout
my $stdout_result;
open( my $outputFH, '>', \$stdout_result ) or die;
my $oldFH = select $outputFH;
GetUniqueLines::write_to_stdout($pkg_href);
select $oldFH;
close $outputFH;

my ( $broadcom_result, $darktable_result );

if ( $stdout_result =~ /\[(broadcom-sta \S+)\]/g ) {
   $broadcom_result = $1;
   like( "$broadcom_result", qr/$expected_broadcom_ver/, "Entry for package with 2 versions has highest value" );
} else {
   fail('Broadcom entry found in result');
}

if ( $stdout_result =~ /\[(darktable \S+)\]/g ) {
   $darktable_result = $1;
   like( "$darktable_result", qr/$expected_darktable_ver/, "Entry for package with 3 versions has highest version" );
} else {
   fail('Darktable entry found in result');
}

# Ensure module can write a file

GetUniqueLines::write_to_file( $file_path, $pkg_href );

print "test looking for $file_path\n";
# file_exists_ok( $file_path, 'Output file is written');
file_line_count_is( $file_path, 15, 'Output file is written and has expected number of packages');

END {
    # Remove test file
    unlink($file_path) or die "Can't delete $file_path: $!\n";
}
