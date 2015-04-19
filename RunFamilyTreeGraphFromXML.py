#!/usr/bin/env python

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
