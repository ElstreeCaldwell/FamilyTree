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

import tkMessageBox
import tkFileDialog

from lxml import etree as ET

from Tkinter import *
import ttk
# from ImageTk import PhotoImage

import FamilyTreeGraph as FTG


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

        self.top.transient(root)
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



# ========================================================================
# Main GUI Application
# ========================================================================

class Application( Frame ):

    # --------------------------------------------------------------------
    #  __init__
    # --------------------------------------------------------------------

    def __init__( self, master, fileInXML, fileOutXML ):

        """Initialise the application class"""

        self.master = master
        #Frame.__init__(self, self.master, bg='gray98')
        Frame.__init__(self, self.master)
    
        self.etXML = None
        self.ftXML = None

        self.fileInXML = fileInXML
        self.fileOutXML = fileOutXML

        self.ReadXML()

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        if ( not self.fileInXML is None ):
            self.master.title( self.fileInXML )

        self.grid(row=0, column=0, sticky=N+S+E+W)

        self.InitialiseMemberParameters()

        self.CreateMenuBar()
        self.CreateWidgets()
        self.UpdateSelectedSubject()
        self.UpdateSubjectListboxItems( True )

        master.bind("<Key>", self.OnKeypress)

        self.master.protocol("WM_DELETE_WINDOW", self.OnQuit)

        
    # --------------------------------------------------------------------
    #  SetHeader()
    # --------------------------------------------------------------------

    def SetHeader(self, fileOutXML):

        if ( self.ftXML is None ):
            self.ftXML = ET.Element( 'FamilyTree' )

        if ( self.etXML is None ):
            self.etXML = ET.ElementTree( self.ftXML )

        if ( self.ftXML.tag != 'FamilyTree' ):
            self.ftXML.tag = 'FamilyTree'

        eHeader = self.ftXML.find( 'HEADER' )

        if ( eHeader is None ):
            eHeader = ET.SubElement( self.ftXML, 'HEADER' )


        eDestination = eHeader.find( 'DESTINATION' )

        if ( not eDestination is None ):
            eHeader.remove( eDestination )

        eCharacter = eHeader.find( 'CHARACTER' )

        if ( not eCharacter is None ):
            eHeader.remove( eCharacter )

        eSource = eHeader.find( 'SOURCE' )

        if ( eSource is None ):
            eSource = ET.SubElement( eHeader, 'SOURCE' )

        eSource.text = 'RunFamilyTreeGUI.py'

        today = datetime.date.today()


        # Author

        eAuthor = eHeader.find( 'AUTHOR' )

        if ( eAuthor is None ):
            eAuthor = ET.SubElement( eHeader, 'AUTHOR' )

        eFirstName = eAuthor.find('forename')

        if ( eFirstName is None ):
            eFirstName = ET.SubElement( eAuthor, 'forename' )

        eFirstName.text = 'Elstree'

        eLastName = eAuthor.find('surname')

        if ( eLastName is None ):
            eLastName = ET.SubElement( eAuthor, 'surname' )

        eLastName.text = 'Caldwell'
        


        # Date

        eDate = eHeader.find( 'DATE' )

        if ( eDate is None ):
            eDate = ET.SubElement( eHeader, 'DATE' )

        eDateDay = eDate.find( 'day' )

        if ( eDateDay is None ):
            eDateDay = ET.SubElement( eDate, 'day' )

        eDateDay.text = str( today.day )
        
        eDateMonth = eDate.find( 'month' )

        if ( eDateMonth is None ):
            eDateMonth = ET.SubElement( eDate, 'month' )
            
        eDateMonth.text = str( today.month )

        eDateYear = eDate.find( 'year' )

        if ( eDateYear is None ):
            eDateYear = ET.SubElement( eDate, 'year' )

        eDateYear.text = str( today.year )


        # File

        if ( not fileOutXML is None ):
            eFile = eHeader.find( 'FILE' )

            if ( eFile is None ):
                eFile = ET.SubElement( eHeader, 'FILE' )

            eFile.text = fileOutXML


    # --------------------------------------------------------------------
    #  ReadXML()
    # --------------------------------------------------------------------

    def ReadXML(self):

        if ( self.fileInXML is not None ):

            self.etXML = ET.parse( self.fileInXML )
            self.ftXML = self.etXML.getroot()

        self.SetHeader( None )

        self.ftGraph = FTG.FamilyTreeGraph( self.ftXML )


    # --------------------------------------------------------------------
    #  OnQuit()
    # --------------------------------------------------------------------

    def OnQuit(self):

        if ( not tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?") ):
            return

        if ( self.fileOutXML is not None ):

            print 'Saving tree data to filename:', self.fileOutXML

            self.SetHeader( self.fileOutXML )
            self.etXML.write( self.fileOutXML, pretty_print=True )

        else:

            flgSaved = False

            if ( tkMessageBox.askokcancel("Save data?", "Would you like to save your data before quitting?") ):
               flgSaved = self.SaveAsTreeXML()

            if ( ( not flgSaved ) and
                 ( not tkMessageBox.askokcancel("Quit?",
                                                "Are you sure you want to quit without saving your data?") ) ):
                 return

        self.quit()

             
    # --------------------------------------------------------------------
    # InitialiseMemberParameters
    # --------------------------------------------------------------------

    def InitialiseMemberParameters(self):

        self.idIndividual = None

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        if ( theIndividual is None ):

            theIndividual = self.ftGraph.CreateIndividual()

        self.idIndividual = self.ftGraph.GetIndividualID( theIndividual )

        self.varSelectedSubject = StringVar()
        self.varSelectedSubject.set( "" )

        self.varSelectedSearch = StringVar()

        self.varSelectedID = StringVar()
        self.varSelectedFamilySpouseID = StringVar()
        self.varSelectedFamilyChildID = StringVar()

        self.varSelectedLastName = StringVar()
        self.varSelectedFirstName = StringVar()
        self.varSelectedAlias = StringVar()

        self.varSelectedSex = StringVar()

        self.varSelectedBirthDay   = StringVar()
        self.varSelectedBirthMonth = StringVar()
        self.varSelectedBirthYear  = StringVar()
        self.varSelectedBirthPlace = StringVar()

        self.varSelectedDeathDay   = StringVar()
        self.varSelectedDeathMonth = StringVar()
        self.varSelectedDeathYear  = StringVar()
        self.varSelectedDeathPlace = StringVar()

        self.varSelectedBurialPlace = StringVar()

        self.varSelectedMarriedDay   = StringVar()
        self.varSelectedMarriedMonth = StringVar()
        self.varSelectedMarriedYear  = StringVar()
        self.varSelectedMarriedPlace = StringVar()

        self.varSelectedDivorcedDay   = StringVar()
        self.varSelectedDivorcedMonth = StringVar()
        self.varSelectedDivorcedYear  = StringVar()

        self.varSelectedSpouse = StringVar()

        self.InitialiseSelectedSubject()


    # --------------------------------------------------------------------
    # CreateMenuBar
    # --------------------------------------------------------------------

    def CreateMenuBar(self):

        menubar = Menu( self.master )

        self.master.config( menu=menubar )

        # The File Menu

        fileMenu = Menu(menubar)

        fileMenu.add_command( label="Open", underline=0, command=self.OpenTreeXML )

        fileMenu.add_separator()

        fileMenu.add_command( label="Save", underline=0, command=self.SaveTreeXML )
        fileMenu.add_command( label="SaveAs", underline=0, command=self.SaveAsTreeXML )

        fileMenu.add_separator()

        fileMenu.add_command(label="Quit", underline=0, command=self.OnQuit)

        menubar.add_cascade(label="File", underline=0, menu=fileMenu)


        # The Plot Menu

        plotMenu = Menu(menubar)

        plotMenu.add_command( label="Plot Entire Tree",
                              underline=0, command=self.OnPlotEntireTree )

        plotMenu.add_command( label="Plot Subject's Immediate Family",
                              underline=0, command=self.OnPlotSubjectFamily )

        plotMenu.add_command( label="Plot Subject's Family Tree",
                              underline=0, command=self.OnPlotSubjectTree )

        plotMenu.add_command( label="Plot Tree of Subject's Ancestors",
                              underline=0, command=self.OnPlotAncestors )

        plotMenu.add_command( label="Plot Tree of Subject's Descendents",
                              underline=0, command=self.OnPlotDescendents )

        menubar.add_cascade(label="Plot", underline=0, menu=plotMenu)


        # The Help Menu

        helpMenu = Menu(menubar)

        helpMenu.add_command( label="About",
                              underline=0, command=self.OnHelpAbout )

        helpMenu.add_command( label="Warranty",
                              underline=0, command=self.OnHelpWarranty )

        helpMenu.add_command( label="License",
                              underline=0, command=self.OnHelpLicense )

        menubar.add_cascade(label="Help", underline=0, menu=helpMenu)


    # --------------------------------------------------------------------
    # CreateWidgets
    # --------------------------------------------------------------------

    def CreateWidgets(self):

        months = [ '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]

        days = [ '' ] + [str(x) for x in range( 1, 31 )]

        self.CreateSubjectListbox( 0, 0)

        iRow = 22
        iCol = 0

        # SearchSubjects
        self.labelSearch = Label(self, text='Subject Search')
        self.labelSearch.grid(row=iRow, column=iCol, columnspan=2, sticky=N+S)

        iRow = iRow + 1

        self.entrySelectedSearch = \
            Entry(self, textvariable=self.varSelectedSearch)

        self.entrySelectedSearch.grid( row=iRow, rowspan=1, column=iCol, columnspan=2,
                                         sticky=N+S+E+W )
        self.varSelectedSearch.trace( "w", self.OnSearchEdited )


        iRow = 0
        iCol = 4

        # Subject
        self.labelID = Label(self, text='Subject')
        self.labelID.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S)

        iRow = iRow + 1

        # ID
        self.labelID = Label(self, text='ID:', anchor=W, justify=LEFT)
        self.labelID.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.labelSelectedID = \
            Label(self, textvariable=self.varSelectedID, anchor=W, justify=LEFT)

        self.labelSelectedID.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1,
                                   sticky=N+S+E+W )

        iRow = iRow + 1

        # FamilySpouse
        self.labelFamilySpouseID = Label(self, text='Spouse Family:', anchor=W, justify=LEFT)
        self.labelFamilySpouseID.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.labelSelectedFamilySpouseID = \
            Label(self, textvariable=self.varSelectedFamilySpouseID, anchor=W, justify=LEFT)

        self.labelSelectedFamilySpouseID.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1,
                                   sticky=N+S+E+W )

        iRow = iRow + 1

       # FamilyChild
        self.labelFamilyChildID = Label(self, text='Child Family:', anchor=W, justify=LEFT)
        self.labelFamilyChildID.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.labelSelectedFamilyChildID = \
            Label(self, textvariable=self.varSelectedFamilyChildID, anchor=W, justify=LEFT)

        self.labelSelectedFamilyChildID.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1,
                                   sticky=N+S+E+W )

        iRow = iRow + 1

        # Last name
        self.labelLastName = Label(self, text='Last Name:', anchor=W, justify=LEFT)
        self.labelLastName.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.entrySelectedLastName = \
            Entry(self, textvariable=self.varSelectedLastName)

        self.entrySelectedLastName.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=4,
                                         sticky=N+S+E+W )
        self.varSelectedLastName.trace( "w", self.OnLastNameEdited )

        iRow = iRow + 1

        # First name
        self.labelFirstName = Label(self, text='First Name:', anchor=W, justify=LEFT)
        self.labelFirstName.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.entrySelectedFirstName = \
            Entry(self, textvariable=self.varSelectedFirstName)

        self.entrySelectedFirstName.grid( row=iRow, rowspan=1,
                                          column=iCol+1, columnspan=4, sticky=N+S+E+W )
        self.varSelectedFirstName.trace( "w", self.OnFirstNameEdited )

        iRow = iRow + 1

        # Alias
        self.labelAlias = Label(self, text='Alias:', anchor=W, justify=LEFT)
        self.labelAlias.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.entrySelectedAlias = \
            Entry(self, textvariable=self.varSelectedAlias)

        self.entrySelectedAlias.grid( row=iRow, rowspan=1,
                                          column=iCol+1, columnspan=4, sticky=N+S+E+W )
        self.varSelectedAlias.trace( "w", self.OnAliasEdited )

        iRow = iRow + 1

        # Sex
        self.labelSex = Label(self, text='Sex:', anchor=W, justify=LEFT)
        self.labelSex.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedSex = OptionMenu( self, self.varSelectedSex,
                                             ' ', 'M', 'F' )
        self.optionSelectedSex.bind( '<<ListboxSelect>>', self.OnSexOptionSelect )

        self.optionSelectedSex.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedSex.trace( "w", self.OnSexOptionSelect )

        iRow = iRow + 1

        # Birth Date
        self.labelBirth = Label(self, text='Born:', anchor=W, justify=LEFT)
        self.labelBirth.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedBirthDay = OptionMenu( self, self.varSelectedBirthDay, *days )
        self.optionSelectedBirthDay.bind( '<<ListboxSelect>>', self.OnBirthDayOptionSelect )

        self.optionSelectedBirthDay.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedBirthDay.trace( "w", self.OnBirthDayOptionSelect )

        self.optionSelectedBirthMonth = OptionMenu( self, self.varSelectedBirthMonth, *months )
        self.optionSelectedBirthMonth.bind( '<<ListboxSelect>>', self.OnBirthMonthOptionSelect )

        self.optionSelectedBirthMonth.grid( row=iRow, rowspan=1, column=iCol+2, columnspan=1, sticky=N+S+E+W )
        self.varSelectedBirthMonth.trace( "w", self.OnBirthMonthOptionSelect )

        self.entrySelectedBirthYear = \
            Entry(self, textvariable=self.varSelectedBirthYear, width=4)

        self.entrySelectedBirthYear.grid( row=iRow, rowspan=1,
                                          column=iCol+3, columnspan=2, sticky=N+S+E+W )
        self.varSelectedBirthYear.trace( "w", self.OnBirthYearEdited )

        iRow = iRow + 1

        self.labelBirthPlace = Label(self, text='Location:', anchor=W, justify=RIGHT)
        self.labelBirthPlace.grid(row=iRow, column=iCol+1, columnspan=1, sticky=W)

        self.entrySelectedBirthPlace = \
            Entry(self, textvariable=self.varSelectedBirthPlace)

        self.entrySelectedBirthPlace.grid( row=iRow, rowspan=1,
                                          column=iCol+2, columnspan=3, sticky=N+S+E+W )
        self.varSelectedBirthPlace.trace( "w", self.OnBirthPlaceEdited )

        iRow = iRow + 1

        # Death Date
        self.labelDeath = Label(self, text='Died:', anchor=W, justify=LEFT)
        self.labelDeath.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedDeathDay = OptionMenu( self, self.varSelectedDeathDay, *days )
        self.optionSelectedDeathDay.bind( '<<ListboxSelect>>', self.OnDeathDayOptionSelect )

        self.optionSelectedDeathDay.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedDeathDay.trace( "w", self.OnDeathDayOptionSelect )

        self.optionSelectedDeathMonth = OptionMenu( self, self.varSelectedDeathMonth, *months )
        self.optionSelectedDeathMonth.bind( '<<ListboxSelect>>', self.OnDeathMonthOptionSelect )

        self.optionSelectedDeathMonth.grid( row=iRow, rowspan=1, column=iCol+2, columnspan=1, sticky=N+S+E+W )
        self.varSelectedDeathMonth.trace( "w", self.OnDeathMonthOptionSelect )

        self.entrySelectedDeathYear = \
            Entry(self, textvariable=self.varSelectedDeathYear, width=4)

        self.entrySelectedDeathYear.grid( row=iRow, rowspan=1,
                                          column=iCol+3, columnspan=2, sticky=N+S+E+W )
        self.varSelectedDeathYear.trace( "w", self.OnDeathYearEdited )

        iRow = iRow + 1

        self.labelDeathPlace = Label(self, text='Location:', anchor=W, justify=RIGHT)
        self.labelDeathPlace.grid(row=iRow, column=iCol+1, columnspan=1, sticky=W)

        self.entrySelectedDeathPlace = \
            Entry(self, textvariable=self.varSelectedDeathPlace)

        self.entrySelectedDeathPlace.grid( row=iRow, rowspan=1,
                                          column=iCol+2, columnspan=3, sticky=N+S+E+W )
        self.varSelectedDeathPlace.trace( "w", self.OnDeathPlaceEdited )

        iRow = iRow + 1

        self.labelBurialPlace = Label(self, text='Buried:', anchor=W, justify=RIGHT)
        self.labelBurialPlace.grid(row=iRow, column=iCol+1, columnspan=1, sticky=W)

        self.entrySelectedBurialPlace = \
            Entry(self, textvariable=self.varSelectedBurialPlace)

        self.entrySelectedBurialPlace.grid( row=iRow, rowspan=1,
                                          column=iCol+2, columnspan=3, sticky=N+S+E+W )
        self.varSelectedBurialPlace.trace( "w", self.OnBurialPlaceEdited )

        iRow = iRow + 1

        # Subject Note

        nColumns = 3
        nRows = 5
        self.labelSubjectNote = Label(self, text='Subject Notes:', anchor=NW, justify=LEFT)
        self.labelSubjectNote.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.SubjectNoteScrollbarY = Scrollbar(self, orient=VERTICAL)
        self.SubjectNoteScrollbarY.grid(row=iRow, column=iCol+nColumns+1,
                                    padx=2, pady=2, rowspan=nRows,
                                    sticky=N+S)
        self.SubjectNoteScrollbarY.rowconfigure(iRow+1, weight=1)

        self.SubjectNoteScrollbarX = Scrollbar(self, orient=HORIZONTAL)
        self.SubjectNoteScrollbarX.grid(row=iRow+nRows, column=iCol+1,
                                        padx=2, pady=2, columnspan=nColumns,
                                        sticky=E+W)

        self.textSubjectNote = Text( self, height=nRows, width=nColumns,
                                     xscrollcommand=self.SubjectNoteScrollbarX.set,
                                     yscrollcommand=self.SubjectNoteScrollbarY.set,
                                     wrap=WORD )
        self.textSubjectNote.grid( row=iRow, column=iCol+1, columnspan=3, sticky=N+S+E+W )



        iRow = 22

        # New subject
        self.buttonNewSubject = Button(self)
        self.buttonNewSubject['text'] = 'New Subject'
        self.buttonNewSubject['command'] = self.OnNewSubject

        self.buttonNewSubject.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)

        iRow = iRow + 1

        # Delete subject
        self.buttonDeleteSubject = Button(self)
        self.buttonDeleteSubject['text'] = 'Delete Subject'
        self.buttonDeleteSubject['command'] = self.OnDeleteSubject

        self.buttonDeleteSubject.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)



        iRow = 0
        iCol = iCol + 5

        # Parents
        self.labelID = Label(self, text='Parents')
        self.labelID.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S)

        iRow = iRow + 1

        # Father
        self.labelFather = Label(self, text='Father:', anchor=W, justify=LEFT)
        self.labelFather.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.buttonAddFather = Button(self)
        self.buttonAddFather.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)

        self.UpdateFatherButtonAdd()

        iRow = iRow + 1

        # Mother
        self.labelMother = Label(self, text='Mother:', anchor=W, justify=LEFT)
        self.labelMother.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.buttonAddMother = Button(self)
        self.buttonAddMother.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)

        self.UpdateMotherButtonAdd()

        iRow = iRow + 1

        # Remove Parents
        self.buttonRemoveParents = Button(self)
        self.buttonRemoveParents['text'] = 'Remove Parents'
        self.buttonRemoveParents['command'] =  self.OnRemoveParents

        self.buttonRemoveParents.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)


        iRow = iRow + 2

        # Spouse
        self.labelID = Label(self, text='Spouse')
        self.labelID.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S)

        iRow = iRow + 1

        # Add Spouse
        self.buttonAddSpouse = Button(self)
        self.buttonAddSpouse.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)

        self.UpdateSpouseButtonAdd()

        iRow = iRow + 1

        # Married Date
        self.labelMarried = Label(self, text='Married:', anchor=W, justify=LEFT)
        self.labelMarried.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedMarriedDay = OptionMenu( self, self.varSelectedMarriedDay, *days )
        self.optionSelectedMarriedDay.bind( '<<ListboxSelect>>', self.OnMarriedDayOptionSelect )

        self.optionSelectedMarriedDay.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedMarriedDay.trace( "w", self.OnMarriedDayOptionSelect )

        self.optionSelectedMarriedMonth = OptionMenu( self, self.varSelectedMarriedMonth, *months )
        self.optionSelectedMarriedMonth.bind( '<<ListboxSelect>>', self.OnMarriedMonthOptionSelect )

        self.optionSelectedMarriedMonth.grid( row=iRow, rowspan=1, column=iCol+2, columnspan=1, sticky=N+S+E+W )
        self.varSelectedMarriedMonth.trace( "w", self.OnMarriedMonthOptionSelect )

        self.entrySelectedMarriedYear = \
            Entry(self, textvariable=self.varSelectedMarriedYear, width=4)

        self.entrySelectedMarriedYear.grid( row=iRow, rowspan=1,
                                          column=iCol+3, columnspan=2, sticky=N+S+E+W )
        self.varSelectedMarriedYear.trace( "w", self.OnMarriedYearEdited )

        iRow = iRow + 1

        self.labelMarriedPlace = Label(self, text='Location:', anchor=W, justify=RIGHT)
        self.labelMarriedPlace.grid(row=iRow, column=iCol+1, columnspan=1, sticky=W)

        self.entrySelectedMarriedPlace = \
            Entry(self, textvariable=self.varSelectedMarriedPlace)

        self.entrySelectedMarriedPlace.grid( row=iRow, rowspan=1,
                                          column=iCol+2, columnspan=3, sticky=N+S+E+W )
        self.varSelectedMarriedPlace.trace( "w", self.OnMarriedPlaceEdited )

        iRow = iRow + 1

        # Divorced Date
        self.labelDivorced = Label(self, text='Divorced:', anchor=W, justify=LEFT)
        self.labelDivorced.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedDivorcedDay = OptionMenu( self, self.varSelectedDivorcedDay, *days )
        self.optionSelectedDivorcedDay.bind( '<<ListboxSelect>>', self.OnDivorcedDayOptionSelect )

        self.optionSelectedDivorcedDay.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedDivorcedDay.trace( "w", self.OnDivorcedDayOptionSelect )

        self.optionSelectedDivorcedMonth = OptionMenu( self, self.varSelectedDivorcedMonth, *months )
        self.optionSelectedDivorcedMonth.bind( '<<ListboxSelect>>', self.OnDivorcedMonthOptionSelect )

        self.optionSelectedDivorcedMonth.grid( row=iRow, rowspan=1, column=iCol+2, columnspan=1, sticky=N+S+E+W )
        self.varSelectedDivorcedMonth.trace( "w", self.OnDivorcedMonthOptionSelect )

        self.entrySelectedDivorcedYear = \
            Entry(self, textvariable=self.varSelectedDivorcedYear, width=4)

        self.entrySelectedDivorcedYear.grid( row=iRow, rowspan=1,
                                             column=iCol+3, columnspan=2, sticky=N+S+E+W )
        self.varSelectedDivorcedYear.trace( "w", self.OnDivorcedYearEdited )

        iRow = iRow + 1

        # Remove Spouse
        self.buttonRemoveSpouse = Button(self)
        self.buttonRemoveSpouse['text'] = 'Remove Spouse'
        self.buttonRemoveSpouse['command'] =  self.OnRemoveSpouse

        self.buttonRemoveSpouse.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)

        iRow = iRow + 3

        # Family Note

        nColumns = 3
        nRows = 5
        self.labelFamilyNote = Label(self, text='Family Notes:', anchor=NW, justify=LEFT)
        self.labelFamilyNote.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.FamilyNoteScrollbarY = Scrollbar(self, orient=VERTICAL)
        self.FamilyNoteScrollbarY.grid(row=iRow, column=iCol+nColumns+1,
                                    padx=2, pady=2, rowspan=nRows,
                                    sticky=N+S)
        self.FamilyNoteScrollbarY.rowconfigure(iRow+1, weight=1)

        self.FamilyNoteScrollbarX = Scrollbar(self, orient=HORIZONTAL)
        self.FamilyNoteScrollbarX.grid(row=iRow+nRows, column=iCol+1,
                                        padx=2, pady=2, columnspan=nColumns,
                                        sticky=E+W)

        self.textFamilyNote = Text( self, height=nRows, width=nColumns,
                                    xscrollcommand=self.FamilyNoteScrollbarX.set,
                                    yscrollcommand=self.FamilyNoteScrollbarY.set,
                                    wrap=WORD )
        self.textFamilyNote.grid( row=iRow, column=iCol+1, columnspan=3, sticky=N+S+E+W )


        iRow = 0
        iCol = iCol + 5

        # Children
        self.CreateChildrenListbox( iCol, iRow )

        iRow = 22

        # Add child
        self.buttonAddChild = Button(self)
        self.buttonAddChild['text'] = 'Add Child'
        self.buttonAddChild['command'] = self.OnAddChild

        self.buttonAddChild.grid(row=iRow, column=iCol, columnspan=2, sticky=N+S+E+W)

        iRow = iRow + 1

        # Remove child
        self.buttonRemoveChild = Button(self)
        self.buttonRemoveChild['text'] = 'Remove Child'
        self.buttonRemoveChild['command'] = self.OnRemoveChild

        self.buttonRemoveChild.grid(row=iRow, column=iCol, columnspan=2, sticky=N+S+E+W)


        #for column in range( iCol + 1 ):
        #    self.columnconfigure(column, weight=1)

        #for row in range( iRow ):
        #    self.rowconfigure(row, weight=1)


    # --------------------------------------------------------------------
    # CreateSubjectListbox
    # --------------------------------------------------------------------

    def CreateSubjectListbox(self, column, row):

        nColumns = 2
        nRows = 20

        self.labelSubject = Label(self, text='Subjects')
        self.labelSubject.grid(row=row, column=column,
                               columnspan=nColumns, sticky=N+S)

        self.SubjectScrollbarY = Scrollbar(self, orient=VERTICAL)
        self.SubjectScrollbarY.grid(row=row+1, column=column+nColumns,
                                    padx=2, pady=2, rowspan=nRows,
                                    sticky=N+S)
        self.SubjectScrollbarY.rowconfigure(row+1, weight=1)

        self.SubjectScrollbarX = Scrollbar(self, orient=HORIZONTAL)
        self.SubjectScrollbarX.grid(row=row+nRows+1, column=column,
                                    padx=2, pady=2, columnspan=nColumns,
                                    sticky=E+W)

        self.SubjectListbox = \
            Listbox( self, selectmode=SINGLE,
                     xscrollcommand=self.SubjectScrollbarX.set,
                     yscrollcommand=self.SubjectScrollbarY.set,
                     exportselection=0 )

        self.UpdateSubjectListboxItems( False )

        self.SubjectListbox.grid(row=row+1, rowspan=nRows,
                                 padx=2, pady=2, column=column, columnspan=nColumns,
                                 sticky=N+S+E+W)
        self.SubjectListbox.columnconfigure(column, weight=1)
        self.SubjectListbox.rowconfigure(row+1, weight=1)

        self.SubjectScrollbarX['command'] = self.SubjectListbox.xview
        self.SubjectScrollbarY['command'] = self.SubjectListbox.yview

        self.SubjectListbox.bind( '<<ListboxSelect>>',
                                 self.OnSubjectListboxSelect )

        for c in range( column, column + nColumns - 1 ):
            self.columnconfigure(c, weight=1)


    # --------------------------------------------------------------------
    # CreateChildrenListbox
    # --------------------------------------------------------------------

    def CreateChildrenListbox(self, column, row):

        nColumns = 2
        nRows = 20

        self.labelChildren = Label(self, text='Children')
        self.labelChildren.grid(row=row, column=column,
                               columnspan=nColumns, sticky=N+S)

        self.ChildrenScrollbarY = Scrollbar(self, orient=VERTICAL)
        self.ChildrenScrollbarY.grid(row=row+1, column=column+nColumns,
                                     padx=2, pady=2, rowspan=nRows,
                                     sticky=N+S)
        self.ChildrenScrollbarY.rowconfigure(row+1, weight=1)

        self.ChildrenScrollbarX = Scrollbar(self, orient=HORIZONTAL)
        self.ChildrenScrollbarX.grid(row=row+nRows+1, column=column,
                                     padx=2, pady=2, columnspan=nColumns,
                                     sticky=E+W)

        self.ChildrenListbox = \
            Listbox( self, selectmode=SINGLE,
                     xscrollcommand=self.ChildrenScrollbarX.set,
                     yscrollcommand=self.ChildrenScrollbarY.set,
                     exportselection=0 )

        self.UpdateChildrenListboxItems()

        self.ChildrenListbox.grid(row=row+1, rowspan=nRows,
                                  padx=2, pady=2, column=column, columnspan=nColumns,
                                  sticky=N+S+E+W)
        self.ChildrenListbox.columnconfigure(column, weight=1)
        self.ChildrenListbox.rowconfigure(row+1, weight=1)

        self.ChildrenScrollbarX['command'] = self.ChildrenListbox.xview
        self.ChildrenScrollbarY['command'] = self.ChildrenListbox.yview

        self.ChildrenListbox.bind( '<<ListboxSelect>>',
                                 self.OnSubjectListboxSelect )

        for c in range( column, column + nColumns - 1 ):
            self.columnconfigure(c, weight=1)


    # --------------------------------------------------------------------
    # ChangeSubject
    # --------------------------------------------------------------------

    def ChangeSubject(self, idIndividual):

        self.CopySubjectNoteTextToXML()
        self.CopyFamilyNoteTextToXML()

        self.idIndividual = idIndividual

        self.UpdateSelectedSubject()
        

    # --------------------------------------------------------------------
    # OnSubjectListboxSelect
    # --------------------------------------------------------------------

    def OnSubjectListboxSelect(self, val):

        sender = val.widget

        idx = sender.curselection()
        value = sender.get(idx)

        self.ChangeSubject( re.search( 'I\d\d\d$', value ).group( 0 ) )


    # --------------------------------------------------------------------
    # OnAddFather
    # --------------------------------------------------------------------

    def OnAddFather(self):

        self.idSelectedFather = None
        d = DialogSelectSubject( self.master, self.ftGraph, 'Select a father',
                                 self.OnSelectedFather, self.OnSelectedFatherCancel,
                                 [ '***  New Individual ***' ],
                                 'M', [ self.idIndividual ] )

        # Create a new father?

        if ( self.idSelectedFather is None ):

            return

        elif ( self.idSelectedFather == '***  New Individual ***' ):

            self.idSelectedFather = self.GetNewIndividual()

        else:

            self.idSelectedFather = re.search( 'I\d\d\d$', self.idSelectedFather ).group( 0 )

        # Set the father

        self.ftGraph.SetSex( self.idSelectedFather, 'M' )
        self.ftGraph.SetFather( self.idIndividual, self.idSelectedFather )

        self.UpdateSelectedSubject()



    # --------------------------------------------------------------------
    # OnSelectedFather
    # --------------------------------------------------------------------

    def OnSelectedFather(self, val):

        # If val is None then this means there were non individuals to
        # choose from so a new one should be created

        if ( val is None ):
            self.idSelectedFather = '***  New Individual ***'

        else:
            sender = val.widget
            idx = sender.curselection()

            self.idSelectedFather = sender.get(idx)


    # --------------------------------------------------------------------
    # OnSelectedFatherCancel
    # --------------------------------------------------------------------

    def OnSelectedFatherCancel(self):

        self.idSelectedFather = None


    # --------------------------------------------------------------------
    # OnGoToFather
    # --------------------------------------------------------------------

    def OnGoToFather(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        mother, father, idFamilyChild = self.ftGraph.GetParents( theIndividual )

        if ( father is not None ):
            self.ChangeSubject( self.ftGraph.GetIndividualID( father ) )


    # --------------------------------------------------------------------
    # OnAddMother
    # --------------------------------------------------------------------

    def OnAddMother(self):

        self.idSelectedMother = None
        d = DialogSelectSubject( self.master, self.ftGraph, 'Select a mother',
                                 self.OnSelectedMother, self.OnSelectedMotherCancel,
                                 [ '***  New Individual ***' ],
                                 'F', [ self.idIndividual ] )

        # Create a new mother?

        if ( self.idSelectedMother is None ):

            return

        elif ( self.idSelectedMother == '***  New Individual ***' ):

            self.idSelectedMother = self.GetNewIndividual()

        else:

            self.idSelectedMother = re.search( 'I\d\d\d$', self.idSelectedMother ).group( 0 )

        # Set the mother

        self.ftGraph.SetSex( self.idSelectedMother, 'F' )
        self.ftGraph.SetMother( self.idIndividual, self.idSelectedMother )

        self.UpdateSelectedSubject()



    # --------------------------------------------------------------------
    # OnSelectedMother
    # --------------------------------------------------------------------

    def OnSelectedMother(self, val):

        # If val is None then this means there were non individuals to
        # choose from so a new one should be created

        if ( val is None ):
            self.idSelectedMother = '***  New Individual ***'

        else:
            sender = val.widget
            idx = sender.curselection()

            self.idSelectedMother = sender.get(idx)


    # --------------------------------------------------------------------
    # OnSelectedMotherCancel
    # --------------------------------------------------------------------

    def OnSelectedMotherCancel(self):

        self.idSelectedMother = None


    # --------------------------------------------------------------------
    # OnGoToMother
    # --------------------------------------------------------------------

    def OnGoToMother(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        mother, father, idFamilyChild = self.ftGraph.GetParents( theIndividual )

        if ( mother is not None ):
            self.ChangeSubject( self.ftGraph.GetIndividualID( mother ) )


    # --------------------------------------------------------------------
    # OnAddSpouse
    # --------------------------------------------------------------------

    def OnAddSpouse(self):

        idsExcluded = [ self.idIndividual ]

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        mother, father, idFamilyChild = self.ftGraph.GetParents( theIndividual )

        if ( not father is None ):
            idsExcluded.append( self.ftGraph.GetIndividualID( father ) )

        if ( not mother is None ):
            idsExcluded.append( self.ftGraph.GetIndividualID( mother ) )

        sex = theIndividual.findtext('SEX')

        self.idSelectedSpouse = None

        if ( sex == 'M' ):

            d = DialogSelectSubject( self.master, self.ftGraph, 'Select a spouse',
                                     self.OnSelectedSpouse, self.OnSelectedSpouseCancel,
                                     [ '***  New Individual ***' ],
                                     'F', idsExcluded )
        elif ( sex == 'F' ):

            d = DialogSelectSubject( self.master, self.ftGraph, 'Select a spouse',
                                     self.OnSelectedSpouse, self.OnSelectedSpouseCancel,
                                     [ '***  New Individual ***' ],
                                     'M', idsExcluded )
        else:

            tkMessageBox.showwarning( 'Warning',
                                      'Please set the gender of this subject before adding a spouse.' )
            return

        # Create a new spouse?

        if ( self.idSelectedSpouse is None ):

            return

        elif ( self.idSelectedSpouse == '***  New Individual ***' ):

            self.idSelectedSpouse = self.GetNewIndividual()

        else:

            self.idSelectedSpouse = re.search( 'I\d\d\d$', self.idSelectedSpouse ).group( 0 )

        # Set the spouse

        if ( sex == 'M' ):
            self.ftGraph.SetSex( self.idSelectedSpouse, 'F' )
        elif ( sex == 'F' ):
            self.ftGraph.SetSex( self.idSelectedSpouse, 'M' )

        self.ftGraph.SetSpouse( self.idIndividual, self.idSelectedSpouse )
        self.ftGraph.SetSpouse( self.idSelectedSpouse, self.idIndividual )

        self.UpdateSelectedSubject()



    # --------------------------------------------------------------------
    # OnSelectedSpouse
    # --------------------------------------------------------------------

    def OnSelectedSpouse(self, val):

        # If val is None then this means there were non individuals to
        # choose from so a new one should be created

        if ( val is None ):
            self.idSelectedSpouse = '***  New Individual ***'

        else:
            sender = val.widget
            idx = sender.curselection()

            self.idSelectedSpouse = sender.get(idx)


    # --------------------------------------------------------------------
    # OnSelectedSpouseCancel
    # --------------------------------------------------------------------

    def OnSelectedSpouseCancel(self):

        self.idSelectedSpouse = None


    # --------------------------------------------------------------------
    # OnGoToSpouse
    # --------------------------------------------------------------------

    def OnGoToSpouse(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        spouse, idFamilySpouse, dateMarriage, dateDivorced = self.ftGraph.GetSpouse( theIndividual )

        if ( spouse is not None ):
            self.ChangeSubject( self.ftGraph.GetIndividualID( spouse ) )


    # --------------------------------------------------------------------
    # OnRemoveFather
    # --------------------------------------------------------------------

    def OnRemoveParents(self):

        self.ftGraph.RemoveParents( self.idIndividual )
        self.UpdateSelectedSubject()


    # --------------------------------------------------------------------
    # OnRemoveSpouse
    # --------------------------------------------------------------------

    def OnRemoveSpouse(self):

        self.ftGraph.RemoveSpouse( self.idIndividual )
        self.UpdateSelectedSubject()


    # --------------------------------------------------------------------
    # OnAddChild
    # --------------------------------------------------------------------

    def OnAddChild(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        sex = theIndividual.findtext('SEX')
        surname = None

        if ( ( not ( sex == 'M' ) ) and ( not ( sex == 'F' ) ) ):

            tkMessageBox.showwarning( 'Warning',
                                      'Please set the gender of this subject before adding a child.' )
            return

        children, idFamily = self.ftGraph.GetChildren( theIndividual )
        idsChildren = []
        for child in children:
            idsChildren.append( child.attrib['id'] )


        self.idSelectedChild = None
        d = DialogSelectSubject( self.master, self.ftGraph, 'Select a child',
                                 self.OnSelectedChild, self.OnSelectedChildCancel,
                                 [ '***  New Individual ***' ],
                                 None, [ self.idIndividual ] + idsChildren )

        # Create a new child?

        if ( self.idSelectedChild is None ):

            return

        elif ( self.idSelectedChild == '***  New Individual ***' ):

            self.idSelectedChild = self.GetNewIndividual()

            if ( sex == 'M' ):
                surname = theIndividual.findtext('NAME/surname')
            else:
                spouse, idFamilySpouse, dateMarriage, dateDivorced = self.ftGraph.GetSpouse( theIndividual )

                if ( spouse is not None ):
                    surname = spouse.findtext('NAME/surname')
    
        else:

            self.idSelectedChild = re.search( 'I\d\d\d$', self.idSelectedChild ).group( 0 )

        # Set the child

        self.ftGraph.SetChild( self.idIndividual, self.idSelectedChild )

        if ( ( not surname is None ) and ( len( surname ) > 0 ) ):
            self.ftGraph.SetLastName( self.idSelectedChild, surname )

        self.UpdateSelectedSubject()



    # --------------------------------------------------------------------
    # OnSelectedChild
    # --------------------------------------------------------------------

    def OnSelectedChild(self, val):

        # If val is None then this means there were non individuals to
        # choose from so a new one should be created

        if ( val is None ):
            self.idSelectedChild = '***  New Individual ***'

        else:
            sender = val.widget
            idx = sender.curselection()

            self.idSelectedChild = sender.get(idx)


    # --------------------------------------------------------------------
    # OnSelectedChildCancel
    # --------------------------------------------------------------------

    def OnSelectedChildCancel(self):

        self.idSelectedChild = None


    # --------------------------------------------------------------------
    # OnRemoveChild
    # --------------------------------------------------------------------

    def OnRemoveChild(self):

        self.idSelectedChild = None

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        children, idFamily = self.ftGraph.GetChildren( theIndividual )

        d = DialogSelectSubject( self.master, self.ftGraph, 'Select a child to remove',
                                 self.OnSelectedRemoveChild, self.OnSelectedRemoveChildCancel,
                                 None, None, None, children )

        if ( not self.idSelectedChild is None ):
            self.ftGraph.RemoveChild( self.idIndividual, self.idSelectedChild )


        self.UpdateSelectedSubject()


    # --------------------------------------------------------------------
    # OnSelectedRemoveChild
    # --------------------------------------------------------------------

    def OnSelectedRemoveChild(self, val):

        if ( not val is None ):

            sender = val.widget
            idx = sender.curselection()
            selected = sender.get(idx)

            self.idSelectedChild = re.search( 'I\d\d\d$', selected ).group( 0 )


    # --------------------------------------------------------------------
    # OnSelectedRemoveChildCancel
    # --------------------------------------------------------------------

    def OnSelectedRemoveChildCancel(self):

        self.idSelectedChild = None


    # --------------------------------------------------------------------
    # InitialiseSelectedSubject
    # --------------------------------------------------------------------

    def InitialiseSelectedSubject(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        self.varSelectedID.set( theIndividual.attrib['id'] )
        self.varSelectedFamilySpouseID.set( theIndividual.findtext('FAMILY_SPOUSE') )
        self.varSelectedFamilyChildID.set( theIndividual.findtext('FAMILY_CHILD') )

        self.varSelectedLastName.set( theIndividual.findtext('NAME/surname') or '' )
        self.varSelectedFirstName.set( theIndividual.findtext('NAME/forename') or '' )
        self.varSelectedAlias.set( theIndividual.findtext('ALIAS') or '' )

        self.varSelectedSex.set( theIndividual.findtext('SEX') or '' )

        self.varSelectedBirthDay.set(   theIndividual.findtext('BIRTH/DATE/day') or '' )
        self.varSelectedBirthMonth.set( theIndividual.findtext('BIRTH/DATE/month') or '' )
        self.varSelectedBirthYear.set(  theIndividual.findtext('BIRTH/DATE/year') or '' )
        self.varSelectedBirthPlace.set( theIndividual.findtext('BIRTH/PLACE') or '' )

        self.varSelectedDeathDay.set(   theIndividual.findtext('DEATH/DATE/day') or '' )
        self.varSelectedDeathMonth.set( theIndividual.findtext('DEATH/DATE/month') or '' )
        self.varSelectedDeathYear.set(  theIndividual.findtext('DEATH/DATE/year') or '' )
        self.varSelectedDeathPlace.set( theIndividual.findtext('DEATH/PLACE') or '' )

        self.varSelectedBurialPlace.set( theIndividual.findtext('BURIAL/PLACE') or '' )

        marriageDay, marriageMonth, marriageYear = self.ftGraph.GetDateMarried( theIndividual )

        if ( marriageDay is None ):
            self.varSelectedMarriedDay.set( '' )
        else:
            self.varSelectedMarriedDay.set( marriageDay )

        if ( marriageMonth is None ):
            self.varSelectedMarriedMonth.set( '' )
        else:
            self.varSelectedMarriedMonth.set( marriageMonth )

        if ( marriageYear is None ):
            self.varSelectedMarriedYear.set( '' )
        else:
            self.varSelectedMarriedYear.set( marriageYear )

        theFamily = self.ftGraph.GetFamily( theIndividual )
        if ( theFamily is None ):
            self.varSelectedMarriedPlace.set( '' )
        else:
            self.varSelectedMarriedPlace.set( theFamily.findtext('MARRIAGE/PLACE') or '' )

        divorceDay, divorceMonth, divorceYear = self.ftGraph.GetDateDivorced( theIndividual )

        if ( divorceDay is None ):
            self.varSelectedDivorcedDay.set( '' )
        else:
            self.varSelectedDivorcedDay.set( divorceDay )

        if ( divorceMonth is None ):
            self.varSelectedDivorcedMonth.set( '' )
        else:
            self.varSelectedDivorcedMonth.set( divorceMonth )

        if ( divorceYear is None ):
            self.varSelectedDivorcedYear.set( '' )
        else:
            self.varSelectedDivorcedYear.set( divorceYear )

        self.varSelectedSpouse.set( theIndividual.findtext( 'FAMILY_SPOUSE' ) )


    # --------------------------------------------------------------------
    # UpdateSelectedSubject
    # --------------------------------------------------------------------

    def UpdateSelectedSubject(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        #ET.dump( theIndividual )

        self.InitialiseSelectedSubject()

        self.UpdateSubjectNote()
        self.UpdateFamilyNote()

        self.UpdateFatherButtonAdd()
        self.UpdateMotherButtonAdd()
        self.UpdateSpouseButtonAdd()

        self.UpdateChildrenListboxItems()


    # --------------------------------------------------------------------
    # UpdateSubjectNote
    # --------------------------------------------------------------------

    def UpdateSubjectNote(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        self.textSubjectNote.delete( 1.0, END )

        note = theIndividual.findtext('NOTE')

        if ( not note is None ):
            self.textSubjectNote.insert( 1.0, note.rstrip() )
            self.textSubjectNote.mark_set(INSERT, 1.0)


    # --------------------------------------------------------------------
    # UpdateFamilyNote
    # --------------------------------------------------------------------

    def UpdateFamilyNote(self):

        self.textFamilyNote.delete( 1.0, END )

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        theFamily = self.ftGraph.GetFamily( theIndividual )

        if ( not theFamily is None ):
            note = theFamily.findtext('NOTE')

            if ( not note is None ):
                self.textFamilyNote.insert( 1.0, note.rstrip() )
                self.textFamilyNote.mark_set(INSERT, 1.0)


    # --------------------------------------------------------------------
    # UpdateFatherButtonAdd
    # --------------------------------------------------------------------

    def UpdateFatherButtonAdd(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        mother, father, idFamilyChild = self.ftGraph.GetParents( theIndividual )

        if ( father is None ):

            self.buttonAddFather['text'] = 'Add Father'
            self.buttonAddFather['command'] = self.OnAddFather

        else:

            self.buttonAddFather['text'] = self.ftGraph.GetLabel( father )
            self.buttonAddFather['command'] = self.OnGoToFather


    # --------------------------------------------------------------------
    # UpdateMotherButtonAdd
    # --------------------------------------------------------------------

    def UpdateMotherButtonAdd(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        mother, father, idFamilyChild = self.ftGraph.GetParents( theIndividual )

        if ( mother is None ):

            self.buttonAddMother['text'] = 'Add Mother'
            self.buttonAddMother['command'] = self.OnAddMother

        else:

            self.buttonAddMother['text'] = self.ftGraph.GetLabel( mother )
            self.buttonAddMother['command'] = self.OnGoToMother


    # --------------------------------------------------------------------
    # UpdateSpouseButtonAdd
    # --------------------------------------------------------------------

    def UpdateSpouseButtonAdd(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        spouse, idFamilySpouse, dateMarriage, dateDivorce = self.ftGraph.GetSpouse( theIndividual )

        if ( spouse is None ):

            self.buttonAddSpouse['text'] = 'Add Spouse'
            self.buttonAddSpouse['command'] = self.OnAddSpouse

        else:

            self.buttonAddSpouse['text'] = self.ftGraph.GetLabel( spouse )
            self.buttonAddSpouse['command'] = self.OnGoToSpouse


    # --------------------------------------------------------------------
    # UpdateSubjectListboxItems
    # --------------------------------------------------------------------

    def UpdateSubjectListboxItems(self, flgActivateSelectedIndividual):

        strSearch = self.varSelectedSearch.get()

        self.SubjectListbox.delete( 0, END )

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        labels = []
        theLabel  = None
        for individual in self.ftGraph.GetIndividuals():

            label = self.ftGraph.GetLabel( individual )
            
            if ( len( strSearch ) != 0 ):
                flgFound = True

                for searchTerm in strSearch.split():
                    if ( not searchTerm.lower() in label.lower() ):
                        flgFound = False
            else:
                flgFound = True

            if ( flgFound ):
                labels.append( label )

            if ( individual == theIndividual ):
                theLabel = label

        labels = sorted( labels )

        index = None
        for label in labels:
            self.SubjectListbox.insert( END, label )

            if ( flgActivateSelectedIndividual and ( label == theLabel ) ):

                self.SubjectListbox.selection_clear( 0, END )
                self.SubjectListbox.selection_set( END )
                index = self.SubjectListbox.curselection()

        if ( index is not None ):
            self.SubjectListbox.activate( index )
            self.SubjectListbox.see( index )


        if ( False and flgActivateSelectedIndividual ):
            self.PlotIndividual( theIndividual, True, True, True, True )
            self.graph.write_gif( 'FamilyTree.gif' )

            imFamilyTree = PhotoImage( file='FamilyTree.gif' )


    # --------------------------------------------------------------------
    # UpdateChildrenListboxItems
    # --------------------------------------------------------------------

    def UpdateChildrenListboxItems(self):

        self.ChildrenListbox.delete( 0, END )

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        labels = []
        theLabel  = None

        children, idFamily = self.ftGraph.GetChildren( theIndividual )

        for child in children:

            label = child.attrib['id']

            forename = child.findtext('NAME/forename') or ''

            if ( not forename is None ):
                label = forename + ' ' + label

            labels.append( label )

        labels = sorted( labels )

        for label in labels:
            self.ChildrenListbox.insert( END, label )


    # --------------------------------------------------------------------
    # OnSearchEdited
    # --------------------------------------------------------------------

    def OnSearchEdited(self, *args):

        self.UpdateSubjectListboxItems( True )


    # --------------------------------------------------------------------
    # OnFirstNameEdited
    # --------------------------------------------------------------------

    def OnFirstNameEdited(self, *args):

        self.ftGraph.SetFirstName( self.idIndividual, self.varSelectedFirstName.get() )
        self.UpdateSubjectListboxItems( True )


    # --------------------------------------------------------------------
    # OnLastNameEdited
    # --------------------------------------------------------------------

    def OnLastNameEdited(self, *args):

        self.ftGraph.SetLastName( self.idIndividual, self.varSelectedLastName.get() )
        self.UpdateSubjectListboxItems( True )


    # --------------------------------------------------------------------
    # OnAliasEdited
    # --------------------------------------------------------------------

    def OnAliasEdited(self, *args):

        self.ftGraph.SetAlias( self.idIndividual, self.varSelectedAlias.get() )
        self.UpdateSubjectListboxItems( True )


    # --------------------------------------------------------------------
    # OnSexOptionSelect
    # --------------------------------------------------------------------

    def OnSexOptionSelect(self, *args):

        self.ftGraph.SetSex( self.idIndividual, self.varSelectedSex.get() )


    # --------------------------------------------------------------------
    # OnBirthDayOptionSelect
    # --------------------------------------------------------------------

    def OnBirthDayOptionSelect(self, *args):

        self.ftGraph.SetBirthDay( self.idIndividual, self.varSelectedBirthDay.get() )


    # --------------------------------------------------------------------
    # OnBirthMonthOptionSelect
    # --------------------------------------------------------------------

    def OnBirthMonthOptionSelect(self, *args):

        self.ftGraph.SetBirthMonth( self.idIndividual, self.varSelectedBirthMonth.get() )


    # --------------------------------------------------------------------
    # OnBirthYearEdited
    # --------------------------------------------------------------------

    def OnBirthYearEdited(self, *args):

        self.ftGraph.SetBirthYear( self.idIndividual, self.varSelectedBirthYear.get() )


    # --------------------------------------------------------------------
    # OnBirthPlaceEdited
    # --------------------------------------------------------------------

    def OnBirthPlaceEdited(self, *args):

        self.ftGraph.SetBirthPlace( self.idIndividual, self.varSelectedBirthPlace.get() )


    # --------------------------------------------------------------------
    # OnDeathDayOptionSelect
    # --------------------------------------------------------------------

    def OnDeathDayOptionSelect(self, *args):

        self.ftGraph.SetDeathDay( self.idIndividual, self.varSelectedDeathDay.get() )


    # --------------------------------------------------------------------
    # OnDeathMonthOptionSelect
    # --------------------------------------------------------------------

    def OnDeathMonthOptionSelect(self, *args):

        self.ftGraph.SetDeathMonth( self.idIndividual, self.varSelectedDeathMonth.get() )


    # --------------------------------------------------------------------
    # OnDeathYearEdited
    # --------------------------------------------------------------------

    def OnDeathYearEdited(self, *args):

        self.ftGraph.SetDeathYear( self.idIndividual, self.varSelectedDeathYear.get() )


    # --------------------------------------------------------------------
    # OnDeathPlaceEdited
    # --------------------------------------------------------------------

    def OnDeathPlaceEdited(self, *args):

        self.ftGraph.SetDeathPlace( self.idIndividual, self.varSelectedDeathPlace.get() )


    # --------------------------------------------------------------------
    # OnBurialPlaceEdited
    # --------------------------------------------------------------------

    def OnBurialPlaceEdited(self, *args):

        self.ftGraph.SetBurialPlace( self.idIndividual, self.varSelectedBurialPlace.get() )


    # --------------------------------------------------------------------
    # CopySubjectNoteTextToXML
    # --------------------------------------------------------------------

    def CopySubjectNoteTextToXML(self):

        note = self.textSubjectNote.get(1.0, END)

        self.ftGraph.SetSubjectNote( self.idIndividual, note )


    # --------------------------------------------------------------------
    # CopyFamilyNoteTextToXML
    # --------------------------------------------------------------------

    def CopyFamilyNoteTextToXML(self):

        note = self.textFamilyNote.get(1.0, END)

        self.ftGraph.SetFamilyNote( self.idIndividual, note )


    # --------------------------------------------------------------------
    # OnMarriedDayOptionSelect
    # --------------------------------------------------------------------

    def OnMarriedDayOptionSelect(self, *args):

        self.ftGraph.SetMarriedDay( self.idIndividual, self.varSelectedMarriedDay.get() )


    # --------------------------------------------------------------------
    # OnMarriedMonthOptionSelect
    # --------------------------------------------------------------------

    def OnMarriedMonthOptionSelect(self, *args):

        self.ftGraph.SetMarriedMonth( self.idIndividual, self.varSelectedMarriedMonth.get() )


    # --------------------------------------------------------------------
    # OnMarriedYearEdited
    # --------------------------------------------------------------------

    def OnMarriedYearEdited(self, *args):

        self.ftGraph.SetMarriedYear( self.idIndividual, self.varSelectedMarriedYear.get() )


    # --------------------------------------------------------------------
    # OnMarriedPlaceEdited
    # --------------------------------------------------------------------

    def OnMarriedPlaceEdited(self, *args):

        self.ftGraph.SetMarriedPlace( self.idIndividual, self.varSelectedMarriedPlace.get() )


    # --------------------------------------------------------------------
    # OnDivorcedDayOptionSelect
    # --------------------------------------------------------------------

    def OnDivorcedDayOptionSelect(self, *args):

        self.ftGraph.SetDivorcedDay( self.idIndividual, self.varSelectedDivorcedDay.get() )


    # --------------------------------------------------------------------
    # OnDivorcedMonthOptionSelect
    # --------------------------------------------------------------------

    def OnDivorcedMonthOptionSelect(self, *args):

        self.ftGraph.SetDivorcedMonth( self.idIndividual, self.varSelectedDivorcedMonth.get() )


    # --------------------------------------------------------------------
    # OnDivorcedYearEdited
    # --------------------------------------------------------------------

    def OnDivorcedYearEdited(self, *args):

        self.ftGraph.SetDivorcedYear( self.idIndividual, self.varSelectedDivorcedYear.get() )


    # --------------------------------------------------------------------
    # GetNewIndividual
    # --------------------------------------------------------------------

    def GetNewIndividual( self ):

        theIndividual = self.ftGraph.CreateIndividual( None, None )

        self.UpdateSelectedSubject()
        self.UpdateSubjectListboxItems( True )

        return self.ftGraph.GetIndividualID( theIndividual )


    # --------------------------------------------------------------------
    # OnNewSubject
    # --------------------------------------------------------------------

    def OnNewSubject( self ):

        self.CopySubjectNoteTextToXML()
        self.CopyFamilyNoteTextToXML()

        theIndividual = self.ftGraph.CreateIndividual( None, None )

        self.ChangeSubject( self.ftGraph.GetIndividualID( theIndividual ) )

        self.UpdateSubjectListboxItems( True )


    # --------------------------------------------------------------------
    # OnDeleteSubject
    # --------------------------------------------------------------------

    def OnDeleteSubject( self ):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        label = self.idIndividual

        forename = self.ftGraph.GetForename( theIndividual )
        surname = self.ftGraph.GetSurname( theIndividual )

        if ( not forename is None ):
            label = forename + ' ' + label

        if ( not surname is None ):
            label = surname + ' ' + label

        if ( tkMessageBox.askyesno( "Delete",
                                    "Delete subject: " + label + "?",
                                    default='yes' ) and
             tkMessageBox.askyesno( "Delete",
                                    "Are you sure you want to delete subject: "  + label + "?",
                                    default='no' ) ):

            self.ChangeSubject( self.ftGraph.DeleteIndividual( self.idIndividual ) )

            if ( self.idIndividual is None ):

                theIndividual = self.ftGraph.CreateIndividual()
                self.ChangeSubject( self.ftGraph.GetIndividualID( theIndividual ) )

            self.UpdateSelectedSubject()
            self.UpdateSubjectListboxItems( True )


    # --------------------------------------------------------------------
    # OpenTreeXML
    # --------------------------------------------------------------------

    def OpenTreeXML( self ):

        options = {}

        options['defaultextension'] = '.xml'
        options['filetypes'] = [('all files', '.*'), ('data files', '.xml')]
        options['parent'] = self
        options['title'] = 'Open Family Tree Data'

        self.fileInXML = tkFileDialog.askopenfilename( **options )

        print 'Opening tree data file:', self.fileInXML

        self.ftXML = ET.parse( self.fileInXML ).getroot()
        self.ftGraph = FTG.FamilyTreeGraph( self.ftXML )

        self.UpdateSelectedSubject()
        self.UpdateSubjectListboxItems( True )


    # --------------------------------------------------------------------
    # SaveTreeXML
    # --------------------------------------------------------------------

    def SaveTreeXML( self ):

        if ( not self.fileOutXML is None ):

            print 'Saving tree data to filename:', self.fileOutXML

            self.SetHeader( self.fileOutXML )

            self.etXML.write( self.fileOutXML, pretty_print=True )

        elif ( self.fileInXML is None ):

            self.SaveAsTreeXML()

        else:

            print 'Saving tree data to filename:', self.fileInXML

            self.SetHeader( self.fileInXML )

            self.etXML.write( self.fileInXML, pretty_print=True )


    # --------------------------------------------------------------------
    # SaveAsTreeXML
    # --------------------------------------------------------------------

    def SaveAsTreeXML( self ):

        options = {}

        today = datetime.date.today()

        defaultFilename = today.strftime('FamilyTree_%Y-%m-%d.xml')

        options['defaultextension'] = '.xml'
        options['filetypes'] = [('all files', '.*'), ('image files', '.xml')]
        options['initialfile'] = defaultFilename
        options['parent'] = self
        options['title'] = 'Save Family Tree Data'

        filename = tkFileDialog.asksaveasfilename( **options )

        if ( ( not filename is None ) and ( len( filename ) > 0 ) ):
            print 'Saving tree data to filename:', filename

            self.SetHeader( filename )

            self.etXML.write( filename, pretty_print=True )

            self.fileOutXML = filename
            
            self.master.title( self.fileOutXML )

            return True

        return False


    # --------------------------------------------------------------------
    # OnPlotEntireTree
    # --------------------------------------------------------------------

    def OnPlotEntireTree( self ):

        options = {}

        options['defaultextension'] = '.png'
        options['filetypes'] = [('all files', '.*'), ('image files', '.png')]
        options['initialfile'] = 'FamilyTree.png'
        options['parent'] = self
        options['title'] = 'Specify Family Tree Plot Output File'

        filename = tkFileDialog.asksaveasfilename( **options )

        print 'Saving entire tree plot to filename:', filename

        graph = self.ftGraph.PlotEntireTree()
        graph.write_png( filename )


    # --------------------------------------------------------------------
    # OnPlotSubjectFamily
    # --------------------------------------------------------------------

    def OnPlotSubjectFamily( self ):

        options = {}

        options['defaultextension'] = '.png'
        options['filetypes'] = [('all files', '.*'), ('image files', '.png')]
        options['initialfile'] = 'FamilyTree.png'
        options['parent'] = self
        options['title'] = "Specify Subject's Family Tree Plot File"

        filename = tkFileDialog.asksaveasfilename( **options )

        print "Saving subject's tree plot to filename:", filename

        self.ftGraph.SetIndividual( self.idIndividual )
        graph = self.ftGraph.PlotSubjectFamily()
        graph.write_png( filename )


    # --------------------------------------------------------------------
    # OnPlotSubjectTree
    # --------------------------------------------------------------------

    def OnPlotSubjectTree( self ):

        options = {}

        options['defaultextension'] = '.png'
        options['filetypes'] = [('all files', '.*'), ('image files', '.png')]
        options['initialfile'] = 'FamilyTree.png'
        options['parent'] = self
        options['title'] = "Specify Subject's Ancestors Tree Plot File"

        filename = tkFileDialog.asksaveasfilename( **options )

        print 'Saving ancestors tree plot to filename:', filename

        self.ftGraph.SetIndividual( self.idIndividual )
        graph = self.ftGraph.PlotSubjectTree()
        graph.write_png( filename )




    # --------------------------------------------------------------------
    # OnPlotAncestors
    # --------------------------------------------------------------------

    def OnPlotAncestors( self ):

        options = {}

        options['defaultextension'] = '.png'
        options['filetypes'] = [('all files', '.*'), ('image files', '.png')]
        options['initialfile'] = 'FamilyTree.png'
        options['parent'] = self
        options['title'] = "Specify Subject's Ancestors Tree Plot File"

        filename = tkFileDialog.asksaveasfilename( **options )

        print 'Saving ancestors tree plot to filename:', filename

        self.ftGraph.SetIndividual( self.idIndividual )
        graph = self.ftGraph.PlotAncestorsTree()
        graph.write_png( filename )


    # --------------------------------------------------------------------
    # OnPlotDescendents
    # --------------------------------------------------------------------

    def OnPlotDescendents( self ):

        options = {}

        options['defaultextension'] = '.png'
        options['filetypes'] = [('all files', '.*'), ('image files', '.png')]
        options['initialfile'] = 'FamilyTree.png'
        options['parent'] = self
        options['title'] = "Specify Subject's Descendents Tree Plot File"

        filename = tkFileDialog.asksaveasfilename( **options )

        print 'Saving descendents tree plot to filename:', filename

        self.ftGraph.SetIndividual( self.idIndividual )
        graph = self.ftGraph.PlotDescendentsTree()
        graph.write_png( filename )


    # --------------------------------------------------------------------
    # OnHelpAbout
    # --------------------------------------------------------------------

    def OnHelpAbout( self ):

        InfoDialog( self.master, 3, 30,
                    'Family Tree Editor\n' + \
                    'Copyright (C) 2015\n' + \
                    'Author: Elstree Caldwell\n' + \
                    'Email: Elstree.Caldwell@gmail.com' )


    # --------------------------------------------------------------------
    # OnHelpWarranty
    # --------------------------------------------------------------------

    def OnHelpWarranty( self ):

        InfoDialog( self.master, 21, 30,
                    'NO WARRANTY\n' + \
                    '\n' + \
                    '  BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY ' + \
                    'FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN ' + \
                    'OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES ' + \
                    'PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED ' + \
                    'OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF ' + \
                    'MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS ' + \
                    'TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE ' + \
                    'PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, ' + \
                    'REPAIR OR CORRECTION.\n' + \
                    '\n' + \
                    '  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING ' + \
                    'WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR ' + \
                    'REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, ' + \
                    'INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING ' + \
                    'OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED ' + \
                    'TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY ' + \
                    'YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER ' + \
                    'PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE ' + \
                    'POSSIBILITY OF SUCH DAMAGES.' )


    # --------------------------------------------------------------------
    # OnHelpLicense
    # --------------------------------------------------------------------

    def OnHelpLicense( self ):

        InfoDialog(self.master, 7, 30,
                   'GNU GENERAL PUBLIC LICENSE\n' + \
                   'Version 2, June 1991\n' + \
                   '\n' + \
                   'Copyright (C) 1989, 1991 Free Software Foundation, Inc., ' + \
                   '51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA ' + \
                   'Everyone is permitted to copy and distribute verbatim copies ' + \
                   'of this license document, but changing it is not allowed.' )
        

    # --------------------------------------------------------------------
    # OnKeypress
    # --------------------------------------------------------------------

    def OnKeypress( self, event ):

        #print "OnKeypress(): ", event.keysym
        key = event.keysym





# ========================================================================
# Main()
# ========================================================================

print '\nFamilyTree, Copyright (C) 2015 Elstree Caldwell\n\n' \
      'FamilyTree comes with ABSOLUTELY NO WARRANTY; for details see menu item Help->Warranty.\n' \
      'This is free software, and you are welcome to redistribute it\n' \
      'under certain conditions; see menu item Help->License for details.\n\n'


# Parse the command line
# ~~~~~~~~~~~~~~~~~~~~~~

parser = argparse.ArgumentParser(description='Family tree processing.')

parser.add_argument( '-i', dest='fileIn',  help='Input XML family tree file')
parser.add_argument( '-o', dest='fileOut', help='Output XML family tree file')

args = parser.parse_args()


print 'Input XML family tree file:', args.fileIn
print 'Output family tree image:', args.fileOut


root = Tk()

root.attributes("-topmost", True)
root.attributes("-topmost", False)

root.title( 'Family Tree Editor' )


#root.geometry('{}x{}'.format(1200, 900))

app = Application( root, args.fileIn, args.fileOut )
app.mainloop()
root.destroy()

