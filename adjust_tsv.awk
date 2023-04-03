#!/usr/bin/awk -f

{
  sub("\r",""); /* remove "\r" from google sheets exported tsv */
}
(NR == 1) {
  for(i=1;i<=NF;i++) f[$i]=i; /* ^ so we can use named fields: $f["Name"]: */
}

/* - - - */

(NR == 1) {
  print "nomo_mallonga" FS "nomo_longa" FS "prelego";
}
(NR > 1) {
  prelego = $f["Prelego"];
  nomo_mallonga = "";
  nomo_longa = "";
  if (length($f["Nomo"]) > 15) {
    nomo_longa = $f["Nomo"];
  } else {
    nomo_mallonga = $f["Nomo"];
  }
  print nomo_mallonga FS nomo_longa FS prelego;
}
