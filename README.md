# Basic usage

```
svgsagoma --separator "\t" --header -pdf prelegoj.tsv sxablono_baza.svg ./out/
```

- Will create the pdfs `./out/<1-N>.pdf`
- In each pdf the placeholders `{Nomo}` and `{Prelego}` will be replaced with the
  corresponding fields in the tsv.

# Preprocessing (fixing the "long name" problem)

Let's say we want the field `Name` to be displayed with a smaller font when its
length exceeds 15 charaters.

Since svgsagoma doesn't support conditions, we need some preprocessing:

- In the svg: create two overlapping placeholders, e.g. `{nomo_longa}` and
  `{nomo_mallonga}`, styled accordingly (see `sxablono_longa_mallonga.svg`).
- Generate a new tsv including the two fields (see `adjust_tsv.awk`, but you
  can do that in python or any other mean):
  - `nomo_mallonga`: containing the field value if it's short, empty otherwise
  - `nomo_longa`: containing the field value if it's long, empty otherwise

```
./adjust_tsv.awk -F "\t" prelegoj.tsv > prelegoj_prilaborita.tsv
svgsagoma --separator "\t" --header -pdf prelegoj_prilaborita.tsv sxablono_longa_mallonga.svg ./out/
```

# Bulk renaming

To rename the generated pdf files from `<1-N>.pdf` using fields from the tsv, can be used `tsvcmd.py`.
It supports field placeholders in the form `{1}` - `{N}` (`{0}` for line number).
Example:

```
$ ls out
10.pdf  1.pdf  2.pdf  3.pdf  4.pdf  5.pdf  6.pdf  7.pdf  8.pdf  9.pdf
$ ./tsvcmd.py prelegoj.tsv 'mv out/{0}.pdf out/atestilo_{1}.pdf' --escape
mv out/1.pdf out/atestilo_Maria_Paulina_Sanchez_de_la_Fuente.pdf
mv out/2.pdf out/atestilo_Marco_Rossi.pdf
mv out/3.pdf out/atestilo_Xu_Lee.pdf
mv out/4.pdf out/atestilo_Carlos_Pereira_do_Nascimento.pdf
mv out/5.pdf out/atestilo_Anna_Nguyen.pdf
mv out/6.pdf out/atestilo_John_Smith.pdf
mv out/7.pdf out/atestilo_Hiroshi_Tanaka.pdf
mv out/8.pdf out/atestilo_Laura_Garcia.pdf
mv out/9.pdf out/atestilo_Anton_Petrov.pdf
mv out/10.pdf out/atestilo_Sarah_Johnson.pdf
Fields: {0}=(line number) {1}=Nomo {2}=Prelego
Perform (y/N)? y
```
