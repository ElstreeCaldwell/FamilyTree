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

import Dialogs
import FamilyTab

import pdb


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

        self.days = [ '' ] + [str(x) for x in range( 1, 31 )]

        self.months = [ '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]

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
        self.idSelectedFamilySpouse = None

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        if ( theIndividual is None ):

            theIndividual = self.ftGraph.CreateIndividual()

        self.idIndividual = self.ftGraph.GetIndividualID( theIndividual )

        self.varSelectedSubject = StringVar()
        self.varSelectedSubject.set( "" )

        self.varSelectedSearch = StringVar()

        self.varSelectedID = StringVar()
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

        iRow = 0
        iCol = 0

        nColumns = 2
        nRows = 22

        self.CreateSubjectListbox( nColumns, nRows, iRow, iCol )

        iRow = iRow + nRows + 2
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
        self.labelID.grid(row=iRow, column=iCol+1, columnspan=1, sticky=N+S)

        self.labelSelectedID = \
            Label(self, textvariable=self.varSelectedID, anchor=W, justify=LEFT)

        self.labelSelectedID.grid( row=iRow, rowspan=1, column=iCol+2, columnspan=1,
                                   sticky=N+S+E+W )

        iRow = iRow + 1

        # FamilyChild
        self.labelFamilyChildID = Label(self, text='Child of Family:', anchor=W, justify=LEFT)
        self.labelFamilyChildID.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.labelSelectedFamilyChildID = \
            Label(self, textvariable=self.varSelectedFamilyChildID, anchor=W, justify=LEFT)

        self.labelSelectedFamilyChildID.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1,
                                   sticky=N+S+E+W )

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

        # Empty
        self.labelEmpty1 = Label( self )
        self.labelEmpty1.grid( row=iRow, rowspan=1, column=iCol, columnspan=1 )

        iRow = iRow + 1

        # Birth Date
        self.labelBirth = Label(self, text='Born:', anchor=W, justify=LEFT)
        self.labelBirth.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedBirthDay = OptionMenu( self, self.varSelectedBirthDay, *self.days )
        self.optionSelectedBirthDay.bind( '<<ListboxSelect>>', self.OnBirthDayOptionSelect )

        self.optionSelectedBirthDay.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedBirthDay.trace( "w", self.OnBirthDayOptionSelect )

        self.optionSelectedBirthMonth = OptionMenu( self, self.varSelectedBirthMonth, *self.months )
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

        iRow = iRow + 2

        # Death Date
        self.labelDeath = Label(self, text='Died:', anchor=W, justify=LEFT)
        self.labelDeath.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedDeathDay = OptionMenu( self, self.varSelectedDeathDay, *self.days )
        self.optionSelectedDeathDay.bind( '<<ListboxSelect>>', self.OnDeathDayOptionSelect )

        self.optionSelectedDeathDay.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedDeathDay.trace( "w", self.OnDeathDayOptionSelect )

        self.optionSelectedDeathMonth = OptionMenu( self, self.varSelectedDeathMonth, *self.months )
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
                                          column=iCol+2, columnspan=4, sticky=N+S+E+W )
        self.varSelectedBurialPlace.trace( "w", self.OnBurialPlaceEdited )

        iRow = iRow + 1

        # Empty
        self.labelEmpty2 = Label( self )
        self.labelEmpty2.grid( row=iRow, rowspan=1, column=iCol, columnspan=1 )

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

        iRow = iRow + 1

        # Empty
        self.labelEmpty3 = Label( self )
        self.labelEmpty3.grid( row=iRow, rowspan=1, column=iCol, columnspan=1 )

        iRow = iRow + 1
 
        # Subject Notes

        nColumns = 8
        nRows = 4
        self.labelSubjectNote = Label(self, text='Subject Notes:', anchor=NW, justify=LEFT)
        self.labelSubjectNote.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.SubjectNoteScrollbarY = Scrollbar( self, orient=VERTICAL )
        self.SubjectNoteScrollbarY.grid( row=iRow, column=iCol+nColumns+1,
                                    padx=2, pady=2, rowspan=nRows,
                                    sticky=N+S )
        self.SubjectNoteScrollbarY.rowconfigure( iRow+1, weight=1 )

        self.SubjectNoteScrollbarX = Scrollbar(self, orient=HORIZONTAL)
        self.SubjectNoteScrollbarX.grid( row=iRow+nRows, column=iCol+1,
                                         padx=2, pady=2, columnspan=nColumns,
                                         sticky=E+W )

        self.textSubjectNote = Text( self, height=nRows, width=nColumns,
                                     xscrollcommand=self.SubjectNoteScrollbarX.set,
                                     yscrollcommand=self.SubjectNoteScrollbarY.set,
                                     wrap=WORD )
        self.textSubjectNote.grid( row=iRow, rowspan=nRows, column=iCol+1,
                                   columnspan=nColumns, sticky=N+S+E+W )



        iRow = iRow + nRows + 2

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

        iRow = iRow + 1

        # New Family
        self.buttonNewFamily = Button(self)
        self.buttonNewFamily['text'] = 'New Family'
        self.buttonNewFamily['command'] = self.OnNewFamily

        self.buttonNewFamily.grid(row=iRow, column=iCol+1, rowspan=1, columnspan=4, sticky=N+S+E+W)


        # The Family tabs

        self.familyColumn = iCol
        
        self.notebookFamilies = ttk.Notebook( self.master, name='families' )
        self.notebookFamilies.grid(row=0, column=iCol, sticky=N+S)

        self.notebookTabChangedFnID = self.notebookFamilies.bind_all( "<<NotebookTabChanged>>",
                                                                      self.OnFamilyChanged )
        
        self.style = ttk.Style()
        self.style.configure('.', foreground='black', background='white')


        
        #for column in range( iCol + 1 ):
        #    self.columnconfigure(column, weight=1)

        #for row in range( iRow ):
        #    self.rowconfigure(row, weight=1)


    # --------------------------------------------------------------------
    # CreateSubjectListbox
    # --------------------------------------------------------------------

    def CreateSubjectListbox(self, nColumns, nRows, row, column):

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
    # ChangeSubject
    # --------------------------------------------------------------------

    def ChangeSubject(self, idIndividual):

        self.CopySubjectNoteTextToXML()
        self.CopyFamilyNoteTextToXML()

        self.idIndividual = idIndividual
        self.idSelectedFamilySpouse = None
        
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
        d = Dialogs.DialogSelectSubject( self.master, self.ftGraph, 'Select a father',
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
        d = Dialogs.DialogSelectSubject( self.master, self.ftGraph, 'Select a mother',
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
    # OnRemoveFather
    # --------------------------------------------------------------------

    def OnRemoveParents(self):

        self.ftGraph.RemoveParents( self.idIndividual )
        self.UpdateSelectedSubject()


    # --------------------------------------------------------------------
    # InitialiseSelectedSubject
    # --------------------------------------------------------------------

    def InitialiseSelectedSubject(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        if ( self.idSelectedFamilySpouse is None ):
            self.idSelectedFamilySpouse = theIndividual.findtext('FAMILY_SPOUSE')

        self.varSelectedID.set( theIndividual.attrib['id'] )
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


    # --------------------------------------------------------------------
    # UpdateSelectedSubject
    # --------------------------------------------------------------------

    def UpdateSelectedSubject(self):

        print 'UpdateSelectedSubject()'

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        #ET.dump( theIndividual )

        self.InitialiseSelectedSubject()

        self.UpdateSubjectNote()

        self.UpdateFatherButtonAdd()
        self.UpdateMotherButtonAdd()

        self.UpdateFamily()


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
    # UpdateFamily
    # --------------------------------------------------------------------

    def UpdateFamily(self):

        #pdb.set_trace()

        selectedTab = None

        # Delete existing tabs

        for tab in self.notebookFamilies.tabs():

            self.notebookFamilies.forget( tab )

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        print '\nUpdateFamily()'
        ET.dump( theIndividual )

        # Create the family tabs for this individual

        if ( not theIndividual is None ):

            self.FamilyTabs = {}

            eFamilies = theIndividual.findall( 'FAMILY_SPOUSE' )

            print eFamilies

            if ( len( eFamilies ) == 0 ):

                self.ftGraph.CreateFamily( theIndividual )
                eFamilies = theIndividual.findall( 'FAMILY_SPOUSE' )

            for eFamily in eFamilies:

                ET.dump( eFamily )

                idFamily = eFamily.text

                print 'UpdateFamily()', idFamily

                familyTab = FamilyTab.FamilyTab( self.master, self.notebookFamilies,
                                                 self.ftGraph,
                                                 self.idIndividual, idFamily, self.familyColumn,
                                                 self.OnSubjectListboxSelect, self.GetNewIndividual )

                self.FamilyTabs[ idFamily ] = familyTab

                self.notebookFamilies.add( familyTab.familyFrame, text='Family: ' + idFamily )

                if ( self.idSelectedFamilySpouse == idFamily ):

                    selectedTab = familyTab


        if ( not selectedTab is None ):

            print 'self.idSelectedFamilySpouse:', self.idSelectedFamilySpouse

            self.notebookFamilies.select( selectedTab.familyFrame )

            selectedTab.UpdateChildrenListboxItems()
            selectedTab.UpdateSpouseButtonAdd()
            selectedTab.UpdateFamilyNote()

 
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

        note = self.FamilyTabs[ self.idSelectedFamilySpouse ].textFamilyNote.get(1.0, END)

        self.ftGraph.SetFamilyNote( self.idIndividual, self.idSelectedFamilySpouse, note )


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
    # OnFamilyChanged
    # --------------------------------------------------------------------

    def OnFamilyChanged(self, event):

        tabText = self.notebookFamilies.tab( self.notebookFamilies.index("current"), "text" )
        self.idSelectedFamilySpouse = re.search( 'F\d\d\d$', tabText ).group( 0 )
        
        print 'OnFamilyChanged()', self.idSelectedFamilySpouse

        self.FamilyTabs[ self.idSelectedFamilySpouse ].UpdateChildrenListboxItems()
        self.FamilyTabs[ self.idSelectedFamilySpouse ].UpdateSpouseButtonAdd()
        self.FamilyTabs[ self.idSelectedFamilySpouse ].UpdateFamilyNote()

        return "break"


    # --------------------------------------------------------------------
    # OnNewFamily
    # --------------------------------------------------------------------

    def OnNewFamily( self ):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        if ( not theIndividual is None ):

            print 'Creating new family'
            family = self.ftGraph.CreateFamily( theIndividual )
            self.idSelectedFamilySpouse = family.attrib['id']

            self.UpdateFamily()


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

        Dialogs.InfoDialog( self.master, 3, 30,
                            'Family Tree Editor\n' + \
                            'Copyright (C) 2015\n' + \
                            'Author: Elstree Caldwell\n' + \
                            'Email: Elstree.Caldwell@gmail.com' )


    # --------------------------------------------------------------------
    # OnHelpWarranty
    # --------------------------------------------------------------------

    def OnHelpWarranty( self ):

        Dialogs.InfoDialog( self.master, 21, 30,
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

        Dialogs.InfoDialog(self.master, 7, 30,
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

