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


import tkMessageBox
import tkFileDialog

from Tkinter import *
import ttk


# ========================================================================
# Info Dialog
# ========================================================================

class InfoDialog:

    def __init__( self, parent, nRows, nColumns, text ):

        self.top = Toplevel( parent, height=10*(nRows+2), width=10*nColumns )
        #self.top.geometry( '{}x{}'.format( 10*(nRows + 2), 10*nColumns ) )

        self.TextScrollbarY = Scrollbar(self.top, orient=VERTICAL)
        self.TextScrollbarX = Scrollbar(self.top, orient=HORIZONTAL)

        self.InfoText = Text( self.top, height=nRows, width=nColumns,
                              xscrollcommand=self.TextScrollbarX.set,
                              yscrollcommand=self.TextScrollbarY.set,
                              wrap=WORD )
        self.InfoText.pack(fill=BOTH, expand=1)

        self.InfoText.insert( 1.0, text )
        self.InfoText.config( state=DISABLED )

        self.TextScrollbarY['command'] = self.InfoText.xview
        self.TextScrollbarX['command'] = self.InfoText.yview

        self.okButton = Button( self.top, text="OK", command=self.OnOK )
        self.okButton.pack()

        

    def OnOK( self ):

        self.top.destroy()



# ========================================================================
# Dialog to select a subject
# ========================================================================

class DialogSelectSubject:

    def __init__( self, parent, ftGraph, instruction,
                  fnCallbackSelection, fnCallbackClear,
                  prependExtraLabels=None,
                  sexCriterion=None, idExclusionList=None,
                  subjects=None ):

        self.ftGraph = ftGraph
        self.instruction = instruction

        self.callback = fnCallbackSelection
        self.callbackClear = fnCallbackClear

        self.prependExtraLabels = prependExtraLabels
        self.sexCriterion = sexCriterion
        self.idExclusionList = idExclusionList
        self.subjects = subjects

        # Do we have any individuals to display?

        self.labels = self.GetLabels( )

        if ( len( self.labels ) == 0 ):
            fnCallbackSelection( None )
            return

        # Yes...

        self.top = Toplevel(parent)
        #self.top.geometry( '{}x{}'.format( 300, 900 ) )

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)

        #self.top.grid(row=0, column=0, sticky=N+S+E+W)

        nColumns = 2
        nRows = 20

        self.CreateSubjectListbox( nRows, nColumns )

        okButton = Button( self.top, text="OK", command=self.OnOK )
        okButton.grid( row=nRows+2, column=0, columnspan=nColumns+1, padx=5, pady=5, sticky=N+S+E+W )

        cancelButton = Button( self.top, text="CANCEL", command=self.OnCancel )
        cancelButton.grid( row=nRows+3, column=0, columnspan=nColumns+1, padx=5, pady=10, sticky=N+S+E+W )

        self.top.transient( parent )
        self.top.grab_set()
        parent.wait_window( self.top )

    def CreateSubjectListbox(self, nRows, nColumns):

        column = 0
        row = 0

        self.labelSubject = Label( self.top, text=self.instruction )
        self.labelSubject.grid(row=row, column=column,
                               padx=5, pady=2, columnspan=nColumns, sticky=N+S)

        self.SubjectScrollbarY = Scrollbar(self.top, orient=VERTICAL)
        self.SubjectScrollbarY.grid(row=row+1, column=column+nColumns,
                                    padx=2, pady=2, rowspan=nRows,
                                    sticky=N+S)

        self.SubjectScrollbarX = Scrollbar(self.top, orient=HORIZONTAL)
        self.SubjectScrollbarX.grid(row=row+nRows+1, column=column,
                                    padx=2, pady=2, columnspan=nColumns,
                                    sticky=E+W)

        self.SubjectListbox = \
            Listbox( self.top, selectmode=SINGLE,
                     xscrollcommand=self.SubjectScrollbarX.set,
                     yscrollcommand=self.SubjectScrollbarY.set,
                     exportselection=0 )

        self.SubjectListbox.grid( row=row+1, rowspan=nRows,
                                  padx=5, pady=2, column=column, columnspan=nColumns,
                                  sticky=N+S+E+W )

        self.UpdateSubjectListboxItems( )

        self.SubjectScrollbarX['command'] = self.SubjectListbox.xview
        self.SubjectScrollbarY['command'] = self.SubjectListbox.yview

        self.SubjectListbox.bind( '<<ListboxSelect>>', self.callback )

        for c in range( column, column + nColumns - 1 ):
            self.top.columnconfigure(c, weight=1)

        for r in range( row+1, row + nRows - 1 ):
            self.top.rowconfigure(r, weight=1)


    def GetLabels(self):

        labels = []

        if ( self.subjects is None ):
            self.subjects = self.ftGraph.GetIndividuals()

        for individual in self.subjects:

            idIndi = individual.attrib['id']

            if (  ( ( self.sexCriterion is None ) or
                    ( individual.findtext('SEX') is None ) or
                    ( len( individual.findtext('SEX') ) == 0 ) or
                    ( individual.findtext('SEX') == self.sexCriterion ) ) and
                  ( ( self.idExclusionList is None ) or
                    ( not idIndi in self.idExclusionList ) ) ):

                label = self.ftGraph.GetLabel( individual )

                labels.append( label )

        return labels


    def UpdateSubjectListboxItems(self):

        self.SubjectListbox.delete( 0, END )

        if ( not self.prependExtraLabels is None ):
            labels = self.prependExtraLabels + sorted( self.labels )
        else:
            labels = sorted( self.labels )

        for label in labels:
            self.SubjectListbox.insert( END, label )


    def OnOK( self ):

        self.top.destroy()

    def OnCancel( self ):

        self.callbackClear()
        self.top.destroy()

