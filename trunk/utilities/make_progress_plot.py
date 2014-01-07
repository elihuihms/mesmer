#!/usr/bin/perl

#
# Author: Elihu Ihms (c) 2012
#

use File::Basename;
use File::Spec;

#
# default options for settings
#

$gnuplot = '/usr/bin/gnuplot';
$terminal = 'aqua';
$plotargs = ();

#
# get any specified vars
#

if( $#ARGV == -1 )
{
	print "Usage: progress_plot [-t/-term <terminal>] [-out/-o <file>] [-arg 'arg'] <mesmer_log.txt>\n";
	exit;
}

while ( $argcounter <= $#ARGV )
{
	if ( $ARGV[ $argcounter ] eq "-term" || $ARGV[ $argcounter ] eq "-t" )
	{
		$terminal = $ARGV[ $argcounter +1 ];
		$argcounter++;
	}
	elsif ( $ARGV[ $argcounter ] eq "-out" || $ARGV[ $argcounter ] eq "-o" )
	{
		$output = $ARGV[ $argcounter +1 ];
		$argcounter++;
	}
	elsif ( $ARGV[ $argcounter ] eq "-arg" )
	{
		push( @plotargs, $ARGV[ $argcounter +1 ] );
		$argcounter++;
	}
	else
	{
		$path = $ARGV[ $argcounter ];
		$path = File::Spec->rel2abs( $path );
		
		if( ! -f $path)
		{
			print "Bad mesmer log file specified: \"$ARGV[ $argcounter ]\"\n";
			exit;
		}
	}
	$argcounter++;
}

#
# done with argument parsing
#

# parse the file and convert it to gnuplot format
open FILE , "<$path" or die $!;
@lines = <FILE>;
close FILE;
s{^\s+|\s+$}{}g foreach @lines;

@scores_b = ();
@scores_a = ();
@scores_d = ();

open FILE, ">progress_plot.tmp" or die $!;

$generation = 0;
for ($i = 0; $i <=$#lines; $i++)
{
	@a = split(/\|/,$lines[$i]);
	s{^\s+|\s+$}{}g foreach @a;
	
	if( $a[0] eq 'Best Score' )
	{
		@b = split(/\|/,$lines[$i+2]);
		s{^\s+|\s+$}{}g foreach @b;	
		
		print FILE "$generation\t$b[0]\t$b[1]\t$b[2]\n";
		$generation++;
	}
}
close FILE;

$title = basename( $path );
$title =~ s/\_/\\\_/g;

# open the pipe to GNUPLOT and make it hot
open( GNUPLOT, "| $gnuplot");
select GNUPLOT;
$| = 1;
select STDOUT;

print GNUPLOT <<EOPLOT;
	set terminal $terminal enhanced
EOPLOT
if( $output ne '' ){
	print GNUPLOT "set output \"$output\"\n";
}

print GNUPLOT <<EOPLOT;
reset
set encoding iso_8859_1
set title '$title'

unset key
set tic scale 0
set xlabel "Generation"
set ylabel "Fitness"

set logscale y

plot 'progress_plot.tmp' using 1:2 with lines lc rgb "red", 'progress_plot.tmp' using 1:3:4 with yerrorbars lc rgb "black", 'progress_plot.tmp' using 1:3 with circles ps 6 lc rgb "black"

EOPLOT

close( GNUPLOT );






