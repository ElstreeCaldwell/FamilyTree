#!/usr/bin/env python

#   FamilyTree
#   Copyright (C) 2015 Elstree Caldwell
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import os                               # Operating system
import time                             # Time functions
import sys                              # System functions
import glob                             # Filename globbing
import re                               # Regular expressions
import csv                              # Easy way to parse files
import datetime
import argparse
import pydot
import xml.etree.ElementTree as ET
import FamilyTreeGraph as FTG



# Parse the command line
# ~~~~~~~~~~~~~~~~~~~~~~

parser = argparse.ArgumentParser(description='Family tree processing.')

parser.add_argument('-id', dest='idIndividual', help='A specific ID to plot ancestors and descendents for')

parser.add_argument( '-i', dest='fileIn',       help='Input XML family tree file')
parser.add_argument( '-o', dest='fileOut',      help='Output family tree image')

parser.add_argument( '-ancestors', dest='ancestors',
                     help='Plot ancestors of an individual', action='store_true')
parser.add_argument( '-descendents', dest='descendents',
                     help='Plot descendents of an individual', action='store_true')

parser.set_defaults( descendents=False )
parser.set_defaults( ancestors=False )

args = parser.parse_args()

print 'Individual ID:', args.idIndividual

print 'Input XML family tree file:', args.fileIn
print 'Output family tree image:', args.fileOut

print 'Ancestors?:', args.ancestors
print 'Descendents?:', args.descendents


ft = ET.parse( args.fileIn ).getroot()


ftGraph = FTG.FamilyTreeGraph( ft,
                               args.idIndividual,
                               args.ancestors,
                               args.descendents )

graph = ftGraph.GetGraph()


if ( args.fileOut is not None ):
      
    graph.write_gif( args.fileOut + '.gif' )
    graph.write( args.fileOut + '.dot' )
