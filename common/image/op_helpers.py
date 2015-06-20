#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  op-helpers.py
#  
#  Copyright 2015 Ikey Doherty <ikey@solus-project.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#

import sys

class OpItem:
    ''' Operationable item '''

    safety = True
    component = False
    target = None
    repo = False
    repo_name = None

    def __init__(self, line, lineno):
        line = line.strip()
        if line.startswith("#"):
            raise RuntimeError("Initialised OpItem from comment")

        if len(line) == 0:
            raise RuntimeError("Passed empty line")

        if len(line) >= 2:
            for i in line[:2]:
                if i == '@':
                    self.component = True
                elif i == '~':
                    self.safety = False

        if "=" in line:
            spl = line.split("=")
            if len(spl) != 2:
                raise RuntimeError("[L%d] Repo list must be NAME = URL format" % lineno)

            self.repo = True
            self.repo_name = spl[0].strip()
            self.target = spl[1].strip()

            if len(self.target) == 0 or len(self.repo_name) == 0:
                raise RuntimeError("[L%d] Repo list must be NAME = URL format" % lineno)
        else:
            self.target = line.replace("@", "").replace("~", "").strip()
            if len(self.target.split()) > 1:
                raise RuntimeError("[L%d] Invalid split in line" % lineno)

        if len(self.target) == 0:
            raise RuntimeError("[L%d] Empty target operation" % lineno)

    def get_execute(self, targetDirectory):
        if not self.target:
            raise RuntimeError("Cannot execute without a target!")
        cmd = "eopkg "
        if self.repo:
            cmd += "add-repo \"%s\" \"%s\"" % (self.repo_name, self.target)
        else:
            cmd += "install "
            if self.component:
                cmd += "-c "
            cmd += self.target + " --ignore-comar "
            if not self.safety:
                cmd += " --ignore-safety "
            cmd = cmd.replace("  ", " ")
        cmd += " -D \"%s\" -y" % targetDirectory
        return cmd

    def batch(self, targetDirectory, args):
        lines = []
        if not self.target:
            raise RuntimeError("Cannot execute without a target!")
        argSet = list()

        # Split into multiple invocations if we have an enormous amount to deal with.
        upperLimit = 150
        if self.component:
            upperLimit = 75
        if len(args) > upperLimit:
            added = 0
            while added < len(args):
                mad = upperLimit if upperLimit + added < len(args) else len(args) - added
                arg = args[added:added+mad]
                added += len(arg)
                argSet.append(arg)
        else:
            argSet.append(args)

        for arg in argSet:
            cmd = "eopkg "
            cmd += "install "
            if self.component:
                opts = " ".join(["-c %s" % x.target for x in arg])
            else:
                opts = " ".join([x.target for x in arg])
            cmd += opts
            if not self.safety:
                cmd += " --ignore-safety "
            cmd = cmd.replace("  ", " ") + " -D \"%s\" --ignore-comar -y" % targetDirectory
            lines.append(cmd)
        return lines

def get_op_items(filename):
    currentStack = list()
    lastItem = None
    stacks = list()
    op_list = list()

    no = 1
    with open(filename, "r") as inp:
        for line in inp.readlines():
            line = line.replace("\n", "").replace("\r", "").strip()
            if line.startswith("#"):
                no += 1
                continue
            if len(line) == 0:
                no += 1
                continue

            op = OpItem(line, no)

            if lastItem is not None:
                if lastItem.component != op.component or lastItem.safety != op.safety or lastItem.repo:
                    if len(currentStack) != 0:
                        op_list.append(currentStack)
                    currentStack = list()
                    currentStack.append(op)
                else:
                    currentStack.append(op)
            else:
                currentStack.append(op)
            lastItem = op
            no += 1

    if currentStack not in op_list:
        op_list.append(currentStack)

    return op_list
