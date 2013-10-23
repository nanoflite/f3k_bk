#!/usr/bin/perl

<>;
print "Rank,Name,Score\n";
while (<>) {
  @fields = split /,/;
  $score = $fields[-5];
  $score =~ s/%//;
  print join( ",", $fields[0], $fields[1], $score ) . "\n" if $fields[1] !~ /dummy/i;
}
