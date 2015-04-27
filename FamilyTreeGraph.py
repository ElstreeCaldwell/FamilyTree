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


import sys
import pydot
import xml.etree.ElementTree as ET

from FamilyTreeXML import FamilyTreeXML


# ========================================================================
# Class to build family tree graphs with pydot
# ========================================================================

class FamilyTreeGraph( FamilyTreeXML ):


    # --------------------------------------------------------------------
    #  __init__
    # --------------------------------------------------------------------

    def __init__( self,
                  xmlFamilyTree,
                  id=None,
                  ancestors=False,
                  descendents=False ):

        super( FamilyTreeGraph, self ).__init__( xmlFamilyTree )

        self.idIndividual = id
        self.ancestors = ancestors
        self.descendents = descendents

        self.nodes = {}
        self.theIndividual = None

 
    # --------------------------------------------------------------------
    #  SetIndividual
    # --------------------------------------------------------------------

    def SetIndividual( self, idIndividual ):

        self.idIndividual = idIndividual
        
 
    # --------------------------------------------------------------------
    #  InitialiseNodes
    # --------------------------------------------------------------------

    def InitialiseNodes( self ):

        # Make the nodes

        nIndividuals = 0

        self.nodes = {}
        self.theIndividual = None

        individuals = self.GetIndividuals()
        
        for individual in individuals:
        
            idIndi = individual.attrib['id']
            name = self.GetNameAndID( individual )
            sex = individual.findtext('SEX')
        
            birthDate = self.ConvertDateTupleToLabel( self.GetDate( individual.find('BIRTH') ) )
            deathDate = self.ConvertDateTupleToLabel( self.GetDate( individual.find('DEATH') ) )
        
            marriageDate = self.ConvertDateTupleToLabel( self.GetDateMarried( individual ) )
        
            label = name
            if ( birthDate is not None ):
                label = label + '\nb. {:s}'.format( birthDate )
            if ( marriageDate is not None ):
                label = label + '\nm. {:s}'.format( marriageDate )
            if ( deathDate is not None ):
                label = label + '\nd. {:s}'.format( deathDate )
        
            #print idIndi, "Sex: {:s} '{:s}'".format( sex, label ), '\n'
        
        
            if ( sex == 'M' ):
                self.nodes[ idIndi ] = pydot.Node( name=label, shape='box')
            else:
                self.nodes[ idIndi ] = pydot.Node( name=label, shape='ellipse' )
        
            if ( self.idIndividual and ( self.idIndividual == idIndi ) ):
                self.theIndividual = individual
        
            nIndividuals = nIndividuals + 1

        print '\nNumber of individuals:', nIndividuals, '\n\n'


        if ( ( self.idIndividual is not None ) and ( self.theIndividual is None ) ):

            raise Exception( 'ERROR: Cannot find individual with id: {:s}'.format( idIndi ) )


    # --------------------------------------------------------------------
    #  GetGraph
    # --------------------------------------------------------------------

    def GetGraph( self ):

        
        # Plot ancestors and descendents for a specific individual
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        if ( self.theIndividual is not None ):
        
             self.graph = self.PlotSubTree()

        
        # Plot the whole tree
        # ~~~~~~~~~~~~~~~~~~~
        
        else:
        
            self.graph = self.PlotEntireTree()


        return self.graph
            
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotSubTree( self ):

        self.InitialiseNodes()
        
        try:
            self.graph = pydot.Dot(graph_type='digraph', strict=True)
        
            if ( self.descendents ):
                self.PlotDescendents( self.theIndividual )
        
            if ( self.ancestors ):
                self.PlotAncestors( self.theIndividual )
                    
            if ( ( not self.ancestors ) and ( not self.descendents ) ):
                self.PlotIndividual( self.theIndividual, True, True, True, True )
         
         
        except:
            print "ERROR: ", sys.exc_info()[0]
            raise

        return self.graph

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotAncestorsTree( self ):

        self.InitialiseNodes()
        
        try:
            self.graph = pydot.Dot(graph_type='digraph', strict=True)
        
            self.PlotAncestors( self.theIndividual )
         
        except:
            print "ERROR: ", sys.exc_info()[0]
            raise

        return self.graph

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotDescendentsTree( self ):

        self.InitialiseNodes()
        
        try:
            self.graph = pydot.Dot(graph_type='digraph', strict=True)
        
            self.PlotDescendents( self.theIndividual )
         
        except:
            print "ERROR: ", sys.exc_info()[0]
            raise

        return self.graph

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotSubjectTree( self ):

        self.InitialiseNodes()
        
        try:
            self.graph = pydot.Dot(graph_type='digraph', strict=True)
        
            self.PlotAncestors( self.theIndividual, True, True, False, True, True )
            self.PlotDescendents( self.theIndividual )
         
        except:
            print "ERROR: ", sys.exc_info()[0]
            raise

        return self.graph

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotSubjectFamily( self ):

        self.InitialiseNodes()

        try:
        
            self.graph = pydot.Dot(graph_type='digraph', strict=True)

            flgPlotSpouse   = True
            flgPlotParents  = True
            flgPlotChildren = True
            flgPlotSiblings = True
            flgPlotWife     = True
        
            self.PlotIndividual( self.theIndividual,
                                 flgPlotSpouse,
                                 flgPlotParents,
                                 flgPlotChildren,
                                 flgPlotSiblings,
                                 flgPlotWife )
         
        except:
            print "ERROR: ", sys.exc_info()[0]
            raise

        return self.graph

    # ----------------------------------------------------------------------


   # ----------------------------------------------------------------------
    def PlotSubTree( self ):

        self.InitialiseNodes()
        
        try:
            self.graph = pydot.Dot(graph_type='digraph', strict=True)
        
            if ( self.descendents ):
                self.PlotDescendents( self.theIndividual )
        
            if ( self.ancestors ):
                self.PlotAncestors( self.theIndividual )
                    
            if ( ( not self.ancestors ) and ( not self.descendents ) ):
                self.PlotIndividual( self.theIndividual, True, True, True, True )
         
         
        except:
            print "ERROR: ", sys.exc_info()[0]
            raise

        return self.graph

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotEntireTree( self ):

        self.InitialiseNodes()

        try:
            self.graph = pydot.Dot(graph_type='digraph', strict=True)
        
            for individual in self.GetIndividuals():
            
                self.PlotIndividual( individual )
        
        except:
            print "ERROR: ", sys.exc_info()[0]
            raise


        return self.graph
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotSpouse( self, individual ):

        if ( individual is None ):
            return None
    
        id = individual.attrib['id']
        sex = individual.findtext('SEX')
    
        spouse, idFamilySpouse, dateMarriage, dateDivorce = self.GetSpouse( individual )
        
        if ( spouse is not None ):
    
            dateMarriage = self.ConvertDateTupleToLabel( dateMarriage )

            if ( dateMarriage is not None ):
                labelMarried = 'm' + dateMarriage
            else:
                labelMarried = 'm'
    
            print 'PlotSpouse Spouse:', self.GetNameAndID( spouse ), '( Family:', idFamilySpouse, \
                  'Married:', dateMarriage, ')'
        
            #couple = pydot.Subgraph(rank='same')
            couple = pydot.Subgraph()
    
            couple.add_node( self.nodes[ id ] )
            couple.add_node( self.nodes[ spouse.attrib['id'] ] )
    
            self.graph.add_subgraph( couple )
    
            if ( sex == 'M' ):
                #edge = pydot.Edge( self.nodes[ id ], self.nodes[ spouse.attrib['id'] ], label=labelMarried )
                edge = pydot.Edge( self.nodes[ id ], self.nodes[ spouse.attrib['id'] ],
                                   dir='both', arrowhead='dot', arrowtail='dot', penwidth='3' )
                self.graph.add_edge( edge )
        
        return spouse
     
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def PlotWife( self, individual ):
    
        id = individual.attrib['id']
        sex = individual.findtext('SEX')
    
        wife, idFamilyWife, dateMarriage, dateDivorce = self.GetWife( individual )
        
        if ( wife is not None ):

            dateMarriage = self.ConvertDateTupleToLabel( dateMarriage )
    
            if ( dateMarriage is not None ):
                labelMarried = 'm' + dateMarriage
            else:
                labelMarried = 'm'
    
            print 'PlotWife Wife:', self.GetNameAndID( wife ), '( Family:', idFamilyWife, 'Married:', dateMarriage, ')'
        
            #couple = pydot.Subgraph(rank='same')
            couple = pydot.Subgraph()
    
            couple.add_node( self.nodes[ id ] )
            couple.add_node( self.nodes[ wife.attrib['id'] ] )
    
            self.graph.add_subgraph( couple )
    
            #edge = pydot.Edge( self.nodes[ id ], self.nodes[ wife.attrib['id'] ], label=labelMarried )
            edge = pydot.Edge( self.nodes[ id ], self.nodes[ wife.attrib['id'] ],
                               dir='both', arrowhead='dot', arrowtail='dot', penwidth='2' )
            self.graph.add_edge( edge )
        
        return wife
     
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def PlotChildren( self, individual ):
    
        if ( individual is None ):
            return []
    
        id = individual.attrib['id']
        sex = individual.findtext('SEX')
    
        if ( sex == 'M' ):
            wife = self.PlotWife( individual )
    
            if ( wife is not None ):
                return self.PlotChildren( wife )            
    
        children, idFamilyChild = self.GetChildren( individual )
    
        for child in children:
    
            print 'PlotChildren Child:', self.GetNameAndID( child ), '( Family:', idFamilyChild, ')'
        
            self.graph.add_node( self.nodes[ id ] )
            self.graph.add_node( self.nodes[ child.attrib['id'] ] )
        
            edge = pydot.Edge( self.nodes[ id ], self.nodes[ child.attrib['id'] ] )
            self.graph.add_edge( edge )
        
        return children
     
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def PlotSiblings( self, individual ):
    
        id = individual.attrib['id']
    
        siblings, idFamilySibling = self.GetSiblings( individual )
    
        for sibling in siblings:
    
            print 'PlotSiblings Sibling:', self.GetNameAndID( sibling ), '( Family:', idFamilySibling, ')'
        
            self.PlotIndividual( sibling, False )
        
        return siblings
     
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def PlotParents( self, individual ):
    
        id = individual.attrib['id']
        
        mother, father, idFamilyChild = self.GetParents( individual )
        
        if ( ( mother is not None ) and ( father is not None ) ):
            print 'PlotParents Mother:', self.GetNameAndID( mother ), '( Family:', idFamilyChild, ')'
            print 'PlotParents Father:', self.GetNameAndID( father ), '( Family:', idFamilyChild, ')'
        
            #parents = pydot.Subgraph(rank='same')
            parents = pydot.Subgraph()
    
            parents.add_node( self.nodes[ mother.attrib['id'] ] )
            parents.add_node( self.nodes[ father.attrib['id'] ] )
    
            self.graph.add_subgraph( parents )       
        
            edge = pydot.Edge( self.nodes[ mother.attrib['id'] ], self.nodes[ id ] )
            self.graph.add_edge( edge )
        
            edge = pydot.Edge( self.nodes[ father.attrib['id'] ], self.nodes[ mother.attrib['id'] ],
                               dir='both', arrowhead='dot', arrowtail='dot', penwidth='2' )
            self.graph.add_edge( edge )

        elif ( mother is not None ):
            print 'PlotParents Mother:', self.GetNameAndID( mother ), '( Family:', idFamilyChild, ')'
    
            self.graph.add_node( self.nodes[ mother.attrib['id'] ] )
    
            edge = pydot.Edge( self.nodes[ mother.attrib['id'] ], self.nodes[ id ] )
            self.graph.add_edge( edge )
        
        elif ( father is not None ):
            print 'PlotParents Father:', self.GetNameAndID( father ), '( Family:', idFamilyChild, ')'
    
            self.graph.add_node( self.nodes[ father.attrib['id'] ] )
    
            edge = pydot.Edge( self.nodes[ father.attrib['id'] ], self.nodes[ id ] )
            self.graph.add_edge( edge )
    
        return ( mother, father )
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def PlotMother( self, individual ):
    
        id = individual.attrib['id']
        
        mother, father, idFamilyChild = self.GetParents( individual )
        
        if ( mother is not None ):
            print 'PlotMother Mother:', self.GetNameAndID( mother ), '( Family:', idFamilyChild, ')'
    
            self.graph.add_node( self.nodes[ mother.attrib['id'] ] )
    
            edge = pydot.Edge( self.nodes[ mother.attrib['id'] ], self.nodes[ id ] )
            self.graph.add_edge( edge )
        
        return mother
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def PlotIndividual( self, individual, flgPlotSpouse=True, flgPlotParents=True,
                        flgPlotChildren=False, flgPlotSiblings=False, flgPlotWife=False ):
    
        mother = None
        father = None
    
        if ( individual is None ):
            return ( mother, father )
    
        id = individual.attrib['id']
        name = self.GetNameAndID( individual )
        sex = individual.findtext('SEX')
        
        print 'PlotIndividual', ET.tostring( individual ), '\n', name
        
        # Spouse
    
        spouse = None
    
        if ( flgPlotSpouse ):
            spouse = self.PlotSpouse( individual )
            self.PlotSpouse( spouse )
    
        elif ( flgPlotWife ):
            wife = self.PlotWife( individual )
    
            if ( ( wife is not None ) and  flgPlotChildren ):
                self.PlotChildren( wife )
            elif ( flgPlotChildren ):
                self.PlotChildren( individual )        
    
        #if ( spouse is None ):
        #    self.graph.add_node( self.nodes[ id ] )
            
        # Parents
       
        if ( flgPlotParents ):
            mother, father = self.PlotParents( individual )
    
        # Wife
            
        if ( flgPlotWife ):
            wife = self.PlotWife( individual )
    
        # Children
    
        if ( flgPlotChildren ):
            self.PlotChildren( individual )
            
        # Siblings
    
        if ( flgPlotSiblings ):
            self.PlotSiblings( individual )
    
        return ( mother, father )
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def PlotAncestors( self, individual,
                       flgPlotSpouse=False,
                       flgPlotParents=True,
                       flgPlotChildren=False,
                       flgPlotSiblings=False,
                       flgPlotWife=False):
    
        if ( individual is not None ):
    
            mother, father = self.PlotIndividual( individual,
                                                  flgPlotSpouse,
                                                  flgPlotParents,
                                                  flgPlotChildren,
                                                  flgPlotSiblings,
                                                  flgPlotWife )
    
            if ( mother is not None ):
                self.PlotAncestors( mother,
                                    flgPlotSpouse,
                                    flgPlotParents,
                                    flgPlotChildren,
                                    flgPlotSiblings,
                                    flgPlotWife )
    
            if ( father is not None ):
                self.PlotAncestors( father,
                                    flgPlotSpouse,
                                    flgPlotParents,
                                    flgPlotChildren,
                                    flgPlotSiblings,
                                    flgPlotWife )
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def PlotDescendents( self, individual ):
    
        if ( individual is not None ):
    
            self.PlotChildren( individual )
    
            children, idFamily = self.GetChildren( individual )
            
            for child in children:
                print 'PlotDescendents child', ET.tostring( child )
                self.PlotDescendents( child )
    
    # ----------------------------------------------------------------------
