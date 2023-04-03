#!/usr/bin/env python3
import csv
import sys
import argparse
import re
import subprocess
import textwrap

def print_available_fields(fields):
  return "Fields: " + " ".join([
    f"{{{i}}}={field}" for (i, field) in enumerate(['(line number)', *fields])
  ])

def safe_text(txt):
  return re.sub('[^a-zA-Z0-9-_]', '_', txt)

def run(command):
  print(f"» {command}")
  child = subprocess.run(command, shell=True)
  return child.returncode

def tsv_reader(filename):
  with open(filename) as f:
    tsv = csv.reader(f, delimiter="\t")
    for line in tsv:
      yield line

def get_fieldnames(filename):
  tsv = tsv_reader(filename)
  return next(tsv)

def loop(filename, cmd, func, field_func):
  tsv = tsv_reader(filename)
  next(tsv) # skip header line
  for row_n, line in enumerate(tsv, start=1):
    cmd_n = cmd
    for (i, field) in enumerate([str(row_n), *line]):
      cmd_n = cmd_n.replace(f"{{{i}}}", field_func(field))
    func(cmd_n)

def main():

  pargs = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Execute a shell command for each line in a tsv",
    epilog=textwrap.dedent("""\
      examples:
        tsvcmd table.tsv                       print the available fields
        tsvcmd table.tsv 'mv {0}.pdf {1}.pdf'  rename pdf files
      """
    )
  )
  pargs.add_argument("tsv_file", help="input text file in tsv format")
  pargs.add_argument("command", help="shell command to perform", nargs="?")
  pargs.add_argument("--yes", action="store_true", help="assume yes: perform the commands without confirm")
  pargs.add_argument("--force", action="store_true", help="keep looping if a command fails")
  pargs.add_argument("--escape", action="store_true", help="adjust the fields so it's safe to use them as paths (replace spaces with _ etc.)")
  args = pargs.parse_args()

  fields = get_fieldnames(args.tsv_file)
  do_perform = args.yes

  field_func = safe_text if args.escape else lambda f: f

  if args.command == None:
    print(print_available_fields(fields))
    return 0

  if not do_perform:
    loop(args.tsv_file, args.command, print, field_func)
    print(print_available_fields(fields))
    do_perform = input("Perform (y/N)? ") in ['y', 'Y']

  run_func = run
  if not args.force:
    def deco(f):
      def inner(cmd):
        ret = f(cmd)
        if ret != 0:
          raise ValueError(f"Command returned code: {ret}")
        return ret
      return inner
    run_func = deco(run_func)

  if do_perform:
    try:
      loop(args.tsv_file, args.command, run_func, field_func)
    except ValueError as e:
      print(f"tsvcmd: {e}. Abort.", file=sys.stderr)
      return 1

  return 0

if __name__=='__main__':
  sys.exit(main())
