#!/usr/bin/env python3
"""
Execute a shell command for each line in a tsv file.
Edoardo Nannotti 2023 - Public domain CC0
"""
import csv
import sys
import argparse
import re
import subprocess
import textwrap

def print_available_fields(fields):
  """Return the field summary as string
  Input: ['Name', 'Surname']
  Output: "{0}=(line number) {1}=Name {2}=Surname"
  """
  return "Fields: " + " ".join([
    f"{{{i}}}={field}" for (i, field) in enumerate(['(line number)', *fields])
  ])

def escape_text(txt):
  return re.sub('[^a-zA-Z0-9-_]', '_', txt)

def run(command):
  """Run a shell command, return its return code"""
  child = subprocess.run(command, shell=True)
  return child.returncode

def tsv_reader(filename, header_only=False):
  """Yield a list of fields for each tsv line"""
  with open(filename) as f:
    tsv = csv.reader(f, delimiter="\t")
    fieldnames = next(tsv)
    if header_only:
      yield fieldnames
    for line in tsv:
      yield line

def inject_fields(cmd, row_n, line, field_func=None):
  """Replace the placeholders in cmd with the fields in the list line
  E.g.:
  >>> inject_fields('mv {0}.pdf {1}-{2}.pdf', 5, ['John', 'Al Bano'], escape_text)
  "mv 5.pdf John-Al_Bano.pdf"
  """
  if field_func:
    line = [field_func(f) for f in line]
  fields = [str(row_n), *line]
  for (i, field) in enumerate(fields):
    cmd = cmd.replace(f"{{{i}}}", field)
  return cmd

def loop(filename, cmd, field_func=None):
  tsv = tsv_reader(filename)
  for row_n, line in enumerate(tsv, start=1):
    cmd_n = inject_fields(cmd, row_n, line, field_func)
    yield cmd_n

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

  if args.command == None:
    # only tsv provided: print the fields summary
    print(print_available_fields(fields))
    return 0

  loop_args = dict(
    filename=args.tsv_file,
    cmd=args.command,
    field_func=escape_text if args.escape else None
  )

  confirm = False
  if not args.yes:
    for cmd in loop(**loop_args):
      print(cmd)
    print(print_available_fields(fields))
    confirm = input("Perform (y/N)? ") in ['y', 'Y']

  if confirm or args.yes:
    for cmd in loop(**loop_args):
      print(f"» {cmd}")
      retcode = run(cmd)
      if retcode != 0 and not args.force:
        print(f"tsvcmd: process returned code: {retcode}. Abort.", file=sys.stderr)
        return 1

  return 0

if __name__=='__main__':
  sys.exit(main())
