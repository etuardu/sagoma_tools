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
  child = subprocess.run(command, shell=True)
  return child.returncode

def tsv_reader(filename, header_only=False):
  with open(filename) as f:
    tsv = csv.reader(f, delimiter="\t")
    fieldnames = next(tsv)
    if header_only:
      yield fieldnames
    for line in tsv:
      yield line

def inject_fields(cmd, row_n, line, field_func):
  fields = [str(row_n), *[field_func(f) for f in line]]
  for (i, field) in enumerate(fields):
    cmd = cmd.replace(f"{{{i}}}", field)
  return cmd

def loop(filename, cmd, func, field_func):
  tsv = tsv_reader(filename)
  for row_n, line in enumerate(tsv, start=1):
    cmd_n = inject_fields(cmd, row_n, line, field_func)
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

  fields = next(tsv_reader(args.tsv_file, header_only=True))

  do_perform = args.yes

  field_func = safe_text if args.escape else lambda f: f

  if args.command == None:
    print(print_available_fields(fields))
    return 0

  if not do_perform:
    tsv = tsv_reader(args.tsv_file)
    for row_n, line in enumerate(tsv, start=1):
      cmd_n = inject_fields(args.command, row_n, line, field_func)
      print(cmd_n)
    print(print_available_fields(fields))
    do_perform = input("Perform (y/N)? ") in ['y', 'Y']

  if do_perform:
    tsv = tsv_reader(args.tsv_file)
    for row_n, line in enumerate(tsv, start=1):
      cmd_n = inject_fields(args.command, row_n, line, field_func)
      print(f"» {cmd_n}")
      retcode = run(cmd_n)
      if retcode != 0 and not args.force:
        print(f"tsvcmd: process returned code: {retcode}. Abort.", file=sys.stderr)
        return 1

  return 0

if __name__=='__main__':
  sys.exit(main())
