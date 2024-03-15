# IdleOpenLine
Python IDLE extension to open a specific line in a file

[![Tests](https://github.com/CoolCat467/idleopenline/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/CoolCat467/idleopenline/actions/workflows/tests.yml)
<!-- BADGIE TIME -->

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/CoolCat467/idleopenline/main.svg)](https://results.pre-commit.ci/latest/github/CoolCat467/idleopenline/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![code style: black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- END BADGIE TIME -->

## What does this extension do?
This IDLE extension allows you to open a specific line and column from
a terminal launch command, such as `idle-python3.12 my_file.py:32:4`
and jump to line 32 column 4. This line indexing syntax is very common
in error/warning messages in many systems such as [Ruff](https://github.com/astral-sh/ruff).

## Installation (Without root permissions)
1) Go to terminal and install with `pip install idleopenline[user]`.
2) Run command `idleuserextend; idleopenline`. You should see the following
output: `Config should be good! Config should be good!`.
3) Open IDLE, go to `Options` -> `Configure IDLE` -> `Extensions`.
If everything went well, alongside `ZzDummy` there should be and
option called `idleopenline`. This is where you can configure how
idleopenline works.

## Installation (Legacy, needs root permission)
1) Go to terminal and install with `pip install idleopenline`.
2) Run command `idleopenline`. You will likely see a message saying
`idleopenline not in system registered extensions!`. Run the command
given to add idleopenline to your system's IDLE extension config file.
3) Again run command `idleopenline`. This time, you should see the
following output: `Config should be good!`.
4) Open IDLE, go to `Options` -> `Configure IDLE` -> `Extensions`.
If everything went well, alongside `ZzDummy` there should be and
option called `idleopenline`. This is where you can configure how
idleopenline works.
