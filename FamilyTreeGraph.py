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

            families = individual.findall('FAMILY_SPOUSE')

            labelsMarried = []
            labelMarried = None
            
            for family in families:

                dateMarriage = self.ConvertDateTupleToLabel( self.GetDateMarried( individual,
                                                                                  family.text ) )
                dateDivorced = self.ConvertDateTupleToLabel( self.GetDateDivorced( individual,
                                                                                  family.text ) )

                if ( ( not dateMarriage is None ) and ( len( dateMarriage ) > 0 ) and
                     ( not dateDivorced is None ) and ( len( dateDivorced ) > 0 ) ):
                    labelMarried = 'm.' + dateMarriage + ', div.' + dateDivorced

                elif ( ( not dateMarriage is None ) and ( len( dateMarriage ) > 0 ) ):
                    labelMarried = 'm.' + dateMarriage

                elif ( ( not dateDivorced is None ) and ( len( dateDivorced ) > 0 ) ):
                    labelMarried = 'div.' + dateDivorced

                if ( not labelMarried is None ):
                    labelsMarried.append( labelMarried )

            label = name

            if ( ( not birthDate is None ) and ( len( birthDate ) > 0 ) ):
                label = label + '\nb. {:s}'.format( birthDate )

            #if ( len( labelsMarried ) > 0 ):
            #    label = label + '\n' + '\n'.join( labelsMarried )

            if ( ( not deathDate is None ) and ( len( deathDate ) > 0 ) ):
                label = label + '\nd. {:s}'.format( deathDate )

            #print idIndi, "Sex: {:s} '{:s}'".format( sex, label ), '\n'

            if ( sex == 'M' ):
                self.nodes[ idIndi ] = pydot.Node( name=label, shape='box')
            else:
                self.nodes[ idIndi ] = pydot.Node( name=label, shape='ellipse' )

            if ( self.idIndividual and ( self.idIndividual == idIndi ) ):
                self.theIndividual = individual

            nIndividuals = nIndividuals + 1

        print '\nNumber of individuals:', nIndividuals, '\n'


        if ( ( not self.idIndividual is None ) and ( self.theIndividual is None ) ):

            raise Exception( 'ERROR: Cannot find individual with id: {:s}'.format( idIndi ) )


    # --------------------------------------------------------------------
    #  GetGraph
    # --------------------------------------------------------------------

    def GetGraph( self ):


        # Plot ancestors and descendents for a specific individual
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        if ( not self.theIndividual is None ):

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

                self.PlotIndividual( individual, True, True, False, False, True  )

        except:
            print "ERROR: ", sys.exc_info()[0]
            raise


        return self.graph
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotSpouse( self, individual ):

        if ( individual is None ):
            return None

        spouses = []

        id = individual.attrib['id']
        sex = individual.findtext('SEX')

        spouseTuple = self.GetSpouses( individual )

        for spouseTuple in spouses:

            spouse, idFamilySpouse, dateMarriage, dateDivorce = spouseTuple

            if ( not spouse is None ):

                dateMarriage = self.ConvertDateTupleToLabel( dateMarriage )
                dateDivorced = self.ConvertDateTupleToLabel( dateDivorce )

                labelMarried = None

                if ( ( not dateMarriage is None ) and ( not dateDivorced is None ) ):
                    labelMarried = 'm' + dateMarriage + '\nd' + dateDivorced

                elif ( not dateMarriage is None ):
                    labelMarried = 'm' + dateMarriage

                elif ( not dateDivorced is None ):
                    labelMarried = 'd' + dateDivorced


                #couple = pydot.Subgraph(rank='same')
                couple = pydot.Subgraph()

                couple.add_node( self.nodes[ id ] )
                couple.add_node( self.nodes[ spouse.attrib['id'] ] )

                self.graph.add_subgraph( couple )

                if ( sex == 'M' ):

                    edge = pydot.Edge( self.nodes[ id ], self.nodes[ spouse.attrib['id'] ],
                                       dir='both', arrowhead='dot', arrowtail='dot', penwidth='3',
                                       label=labelMarried )

                    self.graph.add_edge( edge )

                spouses.append( spouse )

        return spouses

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotWife( self, individual ):

        id = individual.attrib['id']
        sex = individual.findtext('SEX')

        wives = []

        wifeTuples = self.GetWives( individual )

        for wifeTuple in wifeTuples:

            wife, idFamilyWife, dateMarriage, dateDivorce = wifeTuple

            if ( not wife is None ):

                dateMarriage = self.ConvertDateTupleToLabel( dateMarriage )
                dateDivorce = self.ConvertDateTupleToLabel( dateDivorce )

                labelMarried = None

                if ( ( not dateMarriage is None ) and ( len( dateMarriage ) > 0 ) and
                     ( not dateDivorce is None ) and ( len( dateDivorce ) > 0 ) ):
                    labelMarried = 'm.' + dateMarriage + ', div.' + dateDivorce

                elif ( ( not dateMarriage is None ) and ( len( dateMarriage ) > 0 ) ):
                    labelMarried = 'm.' + dateMarriage

                elif ( ( not dateDivorce is None ) and ( len( dateDivorce ) > 0 ) ):
                    labelMarried = 'div.' + dateDivorce

                #couple = pydot.Subgraph(rank='same')
                couple = pydot.Subgraph()

                couple.add_node( self.nodes[ id ] )
                couple.add_node( self.nodes[ wife.attrib['id'] ] )

                self.graph.add_subgraph( couple )

                if ( labelMarried is None ):
                    edge = pydot.Edge( self.nodes[ id ], self.nodes[ wife.attrib['id'] ],
                                       dir='both', arrowhead='dot', arrowtail='dot', penwidth='2' )
                else:
                    edge = pydot.Edge( self.nodes[ id ], self.nodes[ wife.attrib['id'] ],
                                       dir='both', arrowhead='dot', arrowtail='dot', penwidth='2', label=labelMarried )

                self.graph.add_edge( edge )

                wives.append( wife )

        return wives
    
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotChildren( self, individual ):

        if ( individual is None ):
            return []

        id = individual.attrib['id']
        sex = individual.findtext('SEX')

        if ( sex == 'M' ):
            for wife in self.PlotWife( individual ):

                if ( not wife is None ):
                    self.PlotChildren( wife )

            return

        children = self.GetChildren( individual )

        for child in children:

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

            self.PlotIndividual( sibling, False )

        return siblings

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotParents( self, individual ):

        id = individual.attrib['id']

        mother, father, idFamilyChild = self.GetParents( individual )

        if ( ( not mother is None ) and ( not father is None ) ):

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

        elif ( not mother is None ):

            self.graph.add_node( self.nodes[ mother.attrib['id'] ] )

            edge = pydot.Edge( self.nodes[ mother.attrib['id'] ], self.nodes[ id ] )
            self.graph.add_edge( edge )

        elif ( not father is None ):

            self.graph.add_node( self.nodes[ father.attrib['id'] ] )

            edge = pydot.Edge( self.nodes[ father.attrib['id'] ], self.nodes[ id ] )
            self.graph.add_edge( edge )

        return ( mother, father )

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotMother( self, individual ):

        id = individual.attrib['id']

        mother, father, idFamilyChild = self.GetParents( individual )

        if ( not mother is None ):

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

        # Spouse

        spouse = None

        if ( flgPlotSpouse ):
            spouses = self.PlotSpouse( individual )

            for spouse in spouses:
                self.PlotSpouse( spouse )

        #if ( spouse is None ):
        #    self.graph.add_node( self.nodes[ id ] )

        # Parents

        if ( flgPlotParents ):
            mother, father = self.PlotParents( individual )

        # Wife

        if ( flgPlotWife ):
            wives = self.PlotWife( individual )

            for wife in wives:
                
                if ( ( not wife is None ) and  flgPlotChildren ):

                    self.PlotChildren( wife )

                elif ( flgPlotChildren ):

                    self.PlotChildren( individual )

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

        if ( not individual is None ):

            mother, father = self.PlotIndividual( individual,
                                                  flgPlotSpouse,
                                                  flgPlotParents,
                                                  flgPlotChildren,
                                                  flgPlotSiblings,
                                                  flgPlotWife )

            if ( not mother is None ):
                self.PlotAncestors( mother,
                                    flgPlotSpouse,
                                    flgPlotParents,
                                    flgPlotChildren,
                                    flgPlotSiblings,
                                    flgPlotWife )

            if ( not father is None ):
                self.PlotAncestors( father,
                                    flgPlotSpouse,
                                    flgPlotParents,
                                    flgPlotChildren,
                                    flgPlotSiblings,
                                    flgPlotWife )

    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    def PlotDescendents( self, individual ):

        if ( not individual is None ):

            self.PlotChildren( individual )

            children = self.GetChildren( individual )

            for child in children:
                self.PlotDescendents( child )

    # ----------------------------------------------------------------------
