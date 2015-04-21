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

import tkMessageBox
import tkFileDialog

import xml.etree.ElementTree as ET

from Tkinter import *
import ttk
# from ImageTk import PhotoImage

import FamilyTreeGraph as FTG


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

        self.CreateSubjectListbox()

        okButton = Button( self.top, text="OK", command=self.OnOK )
        okButton.pack()

        cancelButton = Button( self.top, text="CANCEL", command=self.OnCancel )
        cancelButton.pack()

        self.top.transient(root)
        self.top.grab_set()
        parent.wait_window( self.top )

    def CreateSubjectListbox(self):

        column = 0
        nColumns = 2

        row = 1
        nRows = 20

        self.labelSubject = Label( self.top, text=self.instruction )
        self.labelSubject.pack()

        self.SubjectScrollbarY = Scrollbar(self.top, orient=VERTICAL)
        self.SubjectScrollbarX = Scrollbar(self.top, orient=HORIZONTAL)

        self.SubjectListbox = \
            Listbox( self.top, selectmode=SINGLE,
                     xscrollcommand=self.SubjectScrollbarX.set,
                     yscrollcommand=self.SubjectScrollbarY.set,
                     exportselection=0 )
        self.SubjectListbox.pack(fill=BOTH, expand=1)

        self.UpdateSubjectListboxItems( )

        self.SubjectScrollbarX['command'] = self.SubjectListbox.xview
        self.SubjectScrollbarY['command'] = self.SubjectListbox.yview

        self.SubjectListbox.bind( '<<ListboxSelect>>',
                                  self.callback )


    def GetLabels(self):

        labels = []

        if ( self.subjects is None ):
            self.subjects = self.ftGraph.GetIndividuals()

        for individual in self.subjects:

            idIndi = individual.attrib['id']

            if (  ( ( self.sexCriterion is None ) or
                    ( individual.findtext('SEX') == self.sexCriterion ) ) and
                  ( ( self.idExclusionList is None ) or
                    ( not idIndi in self.idExclusionList ) ) ):

                forename = individual.findtext('NAME/forename') or ''
                surname  = individual.findtext('NAME/surname') or ''

                label = ', '.join( [ surname, forename, idIndi,  ] )
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
        Frame.__init__(self, self.master)

        self.fileInXML = fileInXML
        self.fileOutXML = fileOutXML

        self.ReadXML()

        self.grid()

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        self.InitialiseMemberParameters()

        self.CreateMenuBar()
        self.CreateWidgets()
        self.UpdateSelectedSubject()
        self.UpdateSubjectListboxItems( True )

        master.bind("<Key>", self.OnKeypress)


    # --------------------------------------------------------------------
    #  ReadXML()
    # --------------------------------------------------------------------

    def ReadXML(self):

        if ( self.fileInXML is not None ):

            self.ftXML = ET.parse( self.fileInXML ).getroot()

        else:

            self.ftXML = ET.Element( 'FamilyTree' )

        self.ftGraph = FTG.FamilyTreeGraph( self.ftXML )


    # --------------------------------------------------------------------
    #  destroy()
    # --------------------------------------------------------------------

    def destroy(self):

        if ( self.fileOutXML is not None ):

            print 'Writing modified XML to file:', self.fileOutXML
            fout = open( self.fileOutXML, 'wb' )
            fout.write( ET.tostring( self.ftXML ) )
            fout.close()


    # --------------------------------------------------------------------
    # InitialiseMemberParameters
    # --------------------------------------------------------------------

    def InitialiseMemberParameters(self):

        self.idIndividual = None

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        if ( theIndividual is None ):

            theIndividual = self.ftGraph.CreateIndividual()

        self.idIndividual = self.ftGraph.GetIndividualID( theIndividual )
        print self.idIndividual

        self.varSelectedSubject = StringVar()
        self.varSelectedSubject.set( "" )

        self.varSelectedID = StringVar()
        self.varSelectedFamilySpouseID = StringVar()
        self.varSelectedFamilyChildID = StringVar()

        self.varSelectedLastName = StringVar()
        self.varSelectedFirstName = StringVar()

        self.varSelectedSex = StringVar()

        self.varSelectedBirthDay   = StringVar()
        self.varSelectedBirthMonth = StringVar()
        self.varSelectedBirthYear  = StringVar()

        self.varSelectedDeathDay   = StringVar()
        self.varSelectedDeathMonth = StringVar()
        self.varSelectedDeathYear  = StringVar()

        self.varSelectedMarriedDay   = StringVar()
        self.varSelectedMarriedMonth = StringVar()
        self.varSelectedMarriedYear  = StringVar()

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

        fileMenu.add_command( label="Save", underline=0, command=self.SaveTreeXML )
        fileMenu.add_command( label="SaveAs", underline=0, command=self.SaveAsTreeXML )

        fileMenu.add_separator()

        fileMenu.add_command(label="Quit", underline=0, command=self.quit)

        menubar.add_cascade(label="File", underline=0, menu=fileMenu)


       # The Plot Menu

        plotMenu = Menu(menubar)

        plotMenu.add_command( label="Plot Entire Tree",
                              underline=0, command=self.OnPlotEntireTree )

        plotMenu.add_command( label="Plot Subject's Tree",
                              underline=0, command=self.OnPlotSubjectTree )

        plotMenu.add_command( label="Plot Tree of Subject's Ancestors",
                              underline=0, command=self.OnPlotAncestors )

        plotMenu.add_command( label="Plot Tree of Subject's Descendents",
                              underline=0, command=self.OnPlotDescendents )

        menubar.add_cascade(label="Plot", underline=0, menu=plotMenu)


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

        # New subject
        self.buttonNewSubject = Button(self)
        self.buttonNewSubject['text'] = 'New Subject'
        self.buttonNewSubject['command'] = self.OnNewSubject

        self.buttonNewSubject.grid(row=iRow, column=0, columnspan=2, sticky=N+S+E+W)


        iRow = 0
        iCol = 4

        # Subject
        self.labelID = Label(self, text='Subject')
        self.labelID.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S)

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

        self.entrySelectedLastName.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=3,
                                         sticky=N+S+E+W )
        self.varSelectedLastName.trace( "w", self.OnLastNameEdited )

        iRow = iRow + 1

        # First name
        self.labelFirstName = Label(self, text='First Name:', anchor=W, justify=LEFT)
        self.labelFirstName.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.entrySelectedFirstName = \
            Entry(self, textvariable=self.varSelectedFirstName)

        self.entrySelectedFirstName.grid( row=iRow, rowspan=1,
                                          column=iCol+1, columnspan=3, sticky=N+S+E+W )
        self.varSelectedFirstName.trace( "w", self.OnFirstNameEdited )

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
        self.labelBirth = Label(self, text='Birth:', anchor=W, justify=LEFT)
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
                                          column=iCol+3, columnspan=1, sticky=N+S+E+W )
        self.varSelectedBirthYear.trace( "w", self.OnBirthYearEdited )

        iRow = iRow + 1

        # Death Date
        self.labelDeath = Label(self, text='Death:', anchor=W, justify=LEFT)
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
                                          column=iCol+3, columnspan=1, sticky=N+S+E+W )
        self.varSelectedDeathYear.trace( "w", self.OnDeathYearEdited )




        iRow = 22

        # Delete subject
        self.buttonDeleteSubject = Button(self)
        self.buttonDeleteSubject['text'] = 'Delete Subject'
        self.buttonDeleteSubject['command'] = self.OnDeleteSubject

        self.buttonDeleteSubject.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S+E+W)



        iRow = 1
        iCol = iCol + 4

        # Parents
        self.labelID = Label(self, text='Parents')
        self.labelID.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S)

        iRow = iRow + 1

        # Father
        self.labelFather = Label(self, text='Father:', anchor=W, justify=LEFT)
        self.labelFather.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.buttonAddFather = Button(self)
        self.buttonAddFather.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S+E+W)

        self.UpdateFatherButtonAdd()

        iRow = iRow + 1

        # Mother
        self.labelMother = Label(self, text='Mother:', anchor=W, justify=LEFT)
        self.labelMother.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.buttonAddMother = Button(self)
        self.buttonAddMother.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S+E+W)

        self.UpdateMotherButtonAdd()

        iRow = iRow + 1

        # Remove Parents
        self.buttonRemoveParents = Button(self)
        self.buttonRemoveParents['text'] = 'Remove Parents'
        self.buttonRemoveParents['command'] =  self.OnRemoveParents

        self.buttonRemoveParents.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S+E+W)


        iRow = iRow + 2

        # Spouse
        self.labelID = Label(self, text='Spouse')
        self.labelID.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S)

        iRow = iRow + 1

        # Add Spouse
        self.buttonAddSpouse = Button(self)
        self.buttonAddSpouse.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S+E+W)

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
                                          column=iCol+3, columnspan=1, sticky=N+S+E+W )
        self.varSelectedMarriedYear.trace( "w", self.OnMarriedYearEdited )

        iRow = iRow + 1

        # Remove Spouse
        self.buttonRemoveSpouse = Button(self)
        self.buttonRemoveSpouse['text'] = 'Remove Spouse'
        self.buttonRemoveSpouse['command'] =  self.OnRemoveSpouse

        self.buttonRemoveSpouse.grid(row=iRow, column=iCol+1, columnspan=3, sticky=N+S+E+W)

        iRow = iRow + 1



        iRow = 1
        iCol = iCol + 4

        # Children
        self.CreateChildrenListbox( iCol, iRow )

        iRow = 21

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


        for column in range( 30 ):
            self.columnconfigure(column, weight=1)

        for row in range( 30 ):
            self.rowconfigure(row, weight=1)


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
                                    rowspan=nRows,
                                    sticky=N+S)
        self.SubjectScrollbarY.rowconfigure(row+1, weight=1)

        self.SubjectScrollbarX = Scrollbar(self, orient=HORIZONTAL)
        self.SubjectScrollbarX.grid(row=row+nRows+1, column=column,
                                    columnspan=nColumns,
                                    sticky=E+W)

        self.SubjectListbox = \
            Listbox( self, selectmode=SINGLE,
                     xscrollcommand=self.SubjectScrollbarX.set,
                     yscrollcommand=self.SubjectScrollbarY.set,
                     exportselection=0 )

        self.UpdateSubjectListboxItems( False )

        self.SubjectListbox.grid(row=row+1, rowspan=nRows,
                                 column=column, columnspan=nColumns,
                                 sticky=N+S+E+W)
        self.SubjectListbox.columnconfigure(column, weight=1)
        self.SubjectListbox.rowconfigure(row+1, weight=1)

        self.SubjectScrollbarX['command'] = self.SubjectListbox.xview
        self.SubjectScrollbarY['command'] = self.SubjectListbox.yview

        self.SubjectListbox.bind( '<<ListboxSelect>>',
                                 self.OnSubjectListboxSelect )


    # --------------------------------------------------------------------
    # CreateChildrenListbox
    # --------------------------------------------------------------------

    def CreateChildrenListbox(self, column, row):

        nColumns = 2
        nRows = 18

        self.labelChildren = Label(self, text='Children')
        self.labelChildren.grid(row=row, column=column,
                               columnspan=nColumns, sticky=N+S)

        self.ChildrenScrollbarY = Scrollbar(self, orient=VERTICAL)
        self.ChildrenScrollbarY.grid(row=row+1, column=column+nColumns,
                                    rowspan=nRows,
                                    sticky=N+S)
        self.ChildrenScrollbarY.rowconfigure(row+1, weight=1)

        self.ChildrenScrollbarX = Scrollbar(self, orient=HORIZONTAL)
        self.ChildrenScrollbarX.grid(row=row+nRows+1, column=column,
                                    columnspan=nColumns,
                                    sticky=E+W)

        self.ChildrenListbox = \
            Listbox( self, selectmode=SINGLE,
                     xscrollcommand=self.ChildrenScrollbarX.set,
                     yscrollcommand=self.ChildrenScrollbarY.set,
                     exportselection=0 )

        self.UpdateChildrenListboxItems()

        self.ChildrenListbox.grid(row=row+1, rowspan=nRows,
                                 column=column, columnspan=nColumns,
                                 sticky=N+S+E+W)
        self.ChildrenListbox.columnconfigure(column, weight=1)
        self.ChildrenListbox.rowconfigure(row+1, weight=1)

        self.ChildrenScrollbarX['command'] = self.ChildrenListbox.xview
        self.ChildrenScrollbarY['command'] = self.ChildrenListbox.yview

        self.ChildrenListbox.bind( '<<ListboxSelect>>',
                                 self.OnChildrenListboxSelect )


    # --------------------------------------------------------------------
    # OnSubjectListboxSelect
    # --------------------------------------------------------------------

    def OnSubjectListboxSelect(self, val):

        sender = val.widget

        idx = sender.curselection()
        value = sender.get(idx).split( ', ' )

        self.idIndividual = value[2]

        self.UpdateSelectedSubject()


    # --------------------------------------------------------------------
    # OnChildrenListboxSelect
    # --------------------------------------------------------------------

    def OnChildrenListboxSelect(self, val):

        sender = val.widget

        idx = sender.curselection()
        value = sender.get(idx).split( ', ' )

        self.idIndividual = value[2]

        self.UpdateSelectedSubject()


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

            value = self.idSelectedFather.split( ', ' )
            self.idSelectedFather = value[2]

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
            self.idIndividual = self.ftGraph.GetIndividualID( father )
            self.UpdateSelectedSubject()


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

            value = self.idSelectedMother.split( ', ' )
            self.idSelectedMother = value[2]

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
            self.idIndividual = self.ftGraph.GetIndividualID( mother )
            self.UpdateSelectedSubject()


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

            value = self.idSelectedSpouse.split( ', ' )
            self.idSelectedSpouse = value[2]

        # Set the spouse

        if ( sex == 'M' ):
            self.ftGraph.SetSex( self.idSelectedSpouse, 'F' )
        elif ( sex == 'F' ):
            self.ftGraph.SetSex( self.idSelectedSpouse, 'M' )

        self.ftGraph.SetSpouse( self.idIndividual, self.idSelectedSpouse )
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
        spouse, idFamilySpouse, dateMarriage = self.ftGraph.GetSpouse( theIndividual )

        if ( spouse is not None ):
            self.idIndividual = self.ftGraph.GetIndividualID( spouse )
            self.UpdateSelectedSubject()


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

        else:

            value = self.idSelectedChild.split( ', ' )
            self.idSelectedChild = value[2]

        # Set the child

        self.ftGraph.SetChild( self.idIndividual, self.idSelectedChild )
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

        print 'OnSelectedRemoveChild()'

        if ( not val is None ):

            sender = val.widget
            idx = sender.curselection()
            selected = sender.get(idx)
            value = selected.split( ', ' )

            self.idSelectedChild = value[2]

            print self.idSelectedChild

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

        self.varSelectedSex.set( theIndividual.findtext('SEX') or '' )

        self.varSelectedBirthDay.set(   theIndividual.findtext('BIRTH/DATE/day') or '' )
        self.varSelectedBirthMonth.set( theIndividual.findtext('BIRTH/DATE/month') or '' )
        self.varSelectedBirthYear.set(  theIndividual.findtext('BIRTH/DATE/year') or '' )

        self.varSelectedDeathDay.set(   theIndividual.findtext('DEATH/DATE/day') or '' )
        self.varSelectedDeathMonth.set( theIndividual.findtext('DEATH/DATE/month') or '' )
        self.varSelectedDeathYear.set(  theIndividual.findtext('DEATH/DATE/year') or '' )

        marriageDate = self.ftGraph.GetDateMarried( theIndividual )

        if ( ( not marriageDate is None ) and ( len( marriageDate ) > 0 ) ):

            marriageDate = marriageDate.split()

            self.varSelectedMarriedDay.set(   marriageDate[0] )
            self.varSelectedMarriedMonth.set( marriageDate[1] )
            self.varSelectedMarriedYear.set(  marriageDate[2] )

        else:

            self.varSelectedMarriedDay.set( '' )
            self.varSelectedMarriedMonth.set( '' )
            self.varSelectedMarriedYear.set( '' )

        self.varSelectedSpouse.set( theIndividual.findtext( 'FAMILY_SPOUSE' ) )


    # --------------------------------------------------------------------
    # UpdateSelectedSubject
    # --------------------------------------------------------------------

    def UpdateSelectedSubject(self):

        self.InitialiseSelectedSubject()

        self.UpdateFatherButtonAdd()
        self.UpdateMotherButtonAdd()
        self.UpdateSpouseButtonAdd()

        self.UpdateChildrenListboxItems()


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

            self.buttonAddFather['text'] = self.ftGraph.GetName( father )
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

            self.buttonAddMother['text'] = self.ftGraph.GetName( mother )
            self.buttonAddMother['command'] = self.OnGoToMother


    # --------------------------------------------------------------------
    # UpdateSpouseButtonAdd
    # --------------------------------------------------------------------

    def UpdateSpouseButtonAdd(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )
        spouse, idFamilySpouse, dateMarriage = self.ftGraph.GetSpouse( theIndividual )

        if ( spouse is None ):

            self.buttonAddSpouse['text'] = 'Add Spouse'
            self.buttonAddSpouse['command'] = self.OnAddSpouse

        else:

            self.buttonAddSpouse['text'] = self.ftGraph.GetName( spouse )
            self.buttonAddSpouse['command'] = self.OnGoToSpouse


    # --------------------------------------------------------------------
    # UpdateSubjectListboxItems
    # --------------------------------------------------------------------

    def UpdateSubjectListboxItems(self, flgActivateSelectedIndividual):

        self.SubjectListbox.delete( 0, END )

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        labels = []
        theLabel  = None
        for individual in self.ftGraph.GetIndividuals():

            idIndividual = individual.attrib['id']
            forename = individual.findtext('NAME/forename') or ''
            surname  = individual.findtext('NAME/surname') or ''

            label = ', '.join( [ surname, forename, idIndividual,  ] )
            labels.append( label )

            if ( individual == theIndividual ):
                theLabel = label

        labels = sorted( labels )

        index = None
        for label in labels:
            self.SubjectListbox.insert( END, label )

            if ( flgActivateSelectedIndividual and ( label == theLabel ) ):

                self.SubjectListbox.selection_set( END )
                index = self.SubjectListbox.curselection()

        if ( index is not None ):
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

            idChild = child.attrib['id']
            forename = child.findtext('NAME/forename') or ''
            surname  = child.findtext('NAME/surname') or ''

            label = ', '.join( [ surname, forename, idChild,  ] )
            labels.append( label )

        labels = sorted( labels )

        for label in labels:
            self.ChildrenListbox.insert( END, label )


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

        theIndividual = self.ftGraph.CreateIndividual( None, None )

        self.idIndividual = self.ftGraph.GetIndividualID( theIndividual )

        self.UpdateSelectedSubject()
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
            label = label + ' ' + forename

        if ( not surname is None ):
            label = label + ' ' + surname

        if ( tkMessageBox.askyesno( "Delete",
                                    "Delete subject: " + label + "?",
                                    default='yes' ) and
             tkMessageBox.askyesno( "Delete",
                                    "Are you sure you want to delete subject: "  + label + "?",
                                    default='no' ) ):

            self.idIndividual = self.ftGraph.DeleteIndividual( self.idIndividual )

            if ( self.idIndividual is None ):

                theIndividual = self.ftGraph.CreateIndividual()
                self.idIndividual = self.ftGraph.GetIndividualID( theIndividual )

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

            fout = open( self.fileOutXML, 'wb' )
            fout.write( ET.tostring( self.ftXML ) )
            fout.close()

        elif ( self.fileInXML is None ):

            self.SaveAsTreeXML()

        else:

            print 'Saving tree data to filename:', self.fileInXML

            fout = open( self.fileInXML, 'wb' )
            fout.write( ET.tostring( self.ftXML ) )
            fout.close()


    # --------------------------------------------------------------------
    # SaveAsTreeXML
    # --------------------------------------------------------------------

    def SaveAsTreeXML( self ):

        options = {}

        options['defaultextension'] = '.xml'
        options['filetypes'] = [('all files', '.*'), ('image files', '.xml')]
        options['initialfile'] = 'FamilyTree.xml'
        options['parent'] = self
        options['title'] = 'Save Family Tree Data'

        filename = tkFileDialog.asksaveasfilename( **options )

        print 'Saving tree data to filename:', filename

        fout = open( filename, 'wb' )
        fout.write( ET.tostring( self.ftXML ) )
        fout.close()


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
    # OnPlotSubjectTree
    # --------------------------------------------------------------------

    def OnPlotSubjectTree( self ):

        options = {}

        options['defaultextension'] = '.png'
        options['filetypes'] = [('all files', '.*'), ('image files', '.png')]
        options['initialfile'] = 'FamilyTree.png'
        options['parent'] = self
        options['title'] = "Specify Subject's Family Tree Plot File"

        filename = tkFileDialog.asksaveasfilename( **options )

        print "Saving subject's tree plot to filename:", filename

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
    # OnKeypress
    # --------------------------------------------------------------------

    def OnKeypress( self, event ):

        print "OnKeypress(): ", event.keysym






# ========================================================================
# Main()
# ========================================================================


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

