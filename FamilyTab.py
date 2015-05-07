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

from lxml import etree as ET

from Tkinter import *
from ttk import *

# from ImageTk import PhotoImage

import Dialogs
import FamilyTreeGraph as FTG


# ========================================================================
# FamilyTab
# ========================================================================

class FamilyTab:

    def __init__( self, master, parent, ftGraph,
                  idIndividual, idFamily, familyColumn,
                  fnOnSubjectListboxSelect, fnGetNewIndividual,
                  fnUpdateSelectedSubject, fnChangeSubject ):

        
        self.master = master
        self.parent = parent
        self.ftGraph = ftGraph
        self.idIndividual = idIndividual
        self.idFamily = idFamily
        self.familyColumn = familyColumn
        self.OnSubjectListboxSelect = fnOnSubjectListboxSelect
        self.GetNewIndividual = fnGetNewIndividual
        self.UpdateSelectedSubject = fnUpdateSelectedSubject
        self.ChangeSubject = fnChangeSubject

        self.days = [ '' ] + [str(x) for x in range( 1, 31 )]

        self.months = [ '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]

        self.InitialiseMemberParameters()

        self.CreateWidgets()
        
             
    # --------------------------------------------------------------------
    # InitialiseMemberParameters
    # --------------------------------------------------------------------

    def InitialiseMemberParameters(self):

        self.varSelectedMarriedDay   = StringVar()
        self.varSelectedMarriedMonth = StringVar()
        self.varSelectedMarriedYear  = StringVar()
        self.varSelectedMarriedPlace = StringVar()

        self.varSelectedDivorcedDay   = StringVar()
        self.varSelectedDivorcedMonth = StringVar()
        self.varSelectedDivorcedYear  = StringVar()

        self.InitialiseFamily()


    # --------------------------------------------------------------------
    # InitialiseFamily
    # --------------------------------------------------------------------

    def InitialiseFamily( self ):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        marriageDay, marriageMonth, marriageYear = self.ftGraph.GetDateMarried( theIndividual, self.idFamily )

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

        divorceDay, divorceMonth, divorceYear = self.ftGraph.GetDateDivorced( theIndividual, self.idFamily )

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


    # --------------------------------------------------------------------
    # CreateWidgets
    # --------------------------------------------------------------------

    def CreateWidgets(self):

        self.familyFrame = Frame( self.parent, style='My.TFrame' )
        self.familyFrame.grid( row=1, column=1, sticky=N+E+W )

        iRow = 1
        iCol = self.familyColumn

        # Spouse
        self.labelID = Label(self.familyFrame, text='Spouse:', anchor=W, justify=LEFT)
        self.labelID.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        # Add Spouse
        self.buttonAddSpouse = Button(self.familyFrame)
        self.buttonAddSpouse.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)

        #self.UpdateSpouseButtonAdd()

        iRow = iRow + 1
 
        # Remove Spouse
        self.buttonRemoveSpouse = Button(self.familyFrame)
        self.buttonRemoveSpouse['text'] = 'Remove Spouse'
        self.buttonRemoveSpouse['command'] =  self.OnRemoveSpouse

        self.buttonRemoveSpouse.grid(row=iRow, column=iCol+1, columnspan=4, sticky=N+S+E+W)

        iRow = iRow + 1

        # Empty
        self.labelEmpty4 = Label( self.familyFrame )
        self.labelEmpty4.grid( row=iRow, rowspan=1, column=iCol, columnspan=1 )

        iRow = iRow + 1
 
        # Married Date
        self.labelMarried = Label(self.familyFrame, text='Married:', anchor=W, justify=LEFT)
        self.labelMarried.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedMarriedDay = OptionMenu( self.familyFrame, self.varSelectedMarriedDay, *self.days )
        self.optionSelectedMarriedDay.bind( '<<ListboxSelect>>', self.OnMarriedDayOptionSelect )

        self.optionSelectedMarriedDay.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedMarriedDay.trace( "w", self.OnMarriedDayOptionSelect )

        self.optionSelectedMarriedMonth = OptionMenu( self.familyFrame, self.varSelectedMarriedMonth, *self.months )
        self.optionSelectedMarriedMonth.bind( '<<ListboxSelect>>', self.OnMarriedMonthOptionSelect )

        self.optionSelectedMarriedMonth.grid( row=iRow, rowspan=1, column=iCol+2, columnspan=1, sticky=N+S+E+W )
        self.varSelectedMarriedMonth.trace( "w", self.OnMarriedMonthOptionSelect )

        self.entrySelectedMarriedYear = \
            Entry(self.familyFrame, textvariable=self.varSelectedMarriedYear, width=4)

        self.entrySelectedMarriedYear.grid( row=iRow, rowspan=1,
                                                 column=iCol+3, columnspan=2, sticky=N+S+E+W )
        self.varSelectedMarriedYear.trace( "w", self.OnMarriedYearEdited )

        iRow = iRow + 1

        self.labelMarriedPlace = Label(self.familyFrame, text='Location:', anchor=W, justify=RIGHT)
        self.labelMarriedPlace.grid(row=iRow, column=iCol+1, columnspan=1, sticky=W)

        self.entrySelectedMarriedPlace = \
            Entry(self.familyFrame, textvariable=self.varSelectedMarriedPlace)

        self.entrySelectedMarriedPlace.grid( row=iRow, rowspan=1,
                                          column=iCol+2, columnspan=3, sticky=N+S+E+W )
        self.varSelectedMarriedPlace.trace( "w", self.OnMarriedPlaceEdited )

        iRow = iRow + 1

        # Divorced Date
        self.labelDivorced = Label(self.familyFrame, text='Divorced:', anchor=W, justify=LEFT)
        self.labelDivorced.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.optionSelectedDivorcedDay = OptionMenu( self.familyFrame, self.varSelectedDivorcedDay, *self.days )
        self.optionSelectedDivorcedDay.bind( '<<ListboxSelect>>', self.OnDivorcedDayOptionSelect )

        self.optionSelectedDivorcedDay.grid( row=iRow, rowspan=1, column=iCol+1, columnspan=1, sticky=N+S+E+W )
        self.varSelectedDivorcedDay.trace( "w", self.OnDivorcedDayOptionSelect )

        self.optionSelectedDivorcedMonth = OptionMenu( self.familyFrame, self.varSelectedDivorcedMonth, *self.months )
        self.optionSelectedDivorcedMonth.bind( '<<ListboxSelect>>', self.OnDivorcedMonthOptionSelect )

        self.optionSelectedDivorcedMonth.grid( row=iRow, rowspan=1, column=iCol+2, columnspan=1, sticky=N+S+E+W )
        self.varSelectedDivorcedMonth.trace( "w", self.OnDivorcedMonthOptionSelect )

        self.entrySelectedDivorcedYear = \
            Entry(self.familyFrame, textvariable=self.varSelectedDivorcedYear, width=4)

        self.entrySelectedDivorcedYear.grid( row=iRow, rowspan=1,
                                             column=iCol+3, columnspan=2, sticky=N+S+E+W )
        self.varSelectedDivorcedYear.trace( "w", self.OnDivorcedYearEdited )

        iRow = iRow + 1

        # Empty
        self.labelEmpty5 = Label( self.familyFrame )
        self.labelEmpty5.grid( row=iRow, rowspan=1, column=iCol, columnspan=1 )

        iRow = iRow + 1
 
        # Family Note

        nColumns = 4
        nRows = 10

        iCol = self.familyColumn

        self.labelFamilyNote = Label(self.familyFrame, text='Family Notes:', anchor=NW, justify=LEFT)
        self.labelFamilyNote.grid(row=iRow, column=iCol, columnspan=1, sticky=W)

        self.FamilyNoteScrollbarY = Scrollbar(self.familyFrame, orient=VERTICAL)
        self.FamilyNoteScrollbarY.grid( row=iRow, column=iCol+nColumns+1,
                                        padx=2, pady=2,
                                        rowspan=nRows, columnspan=1,
                                        sticky=N+S )
        self.FamilyNoteScrollbarY.rowconfigure(iRow+1, weight=1)

        self.FamilyNoteScrollbarX = Scrollbar(self.familyFrame, orient=HORIZONTAL)
        self.FamilyNoteScrollbarX.grid( row=iRow+nRows, column=iCol+1,
                                        padx=2, pady=2,
                                        rowspan=1, columnspan=nColumns,
                                        sticky=E+W )

        self.textFamilyNote = Text( self.familyFrame, height=nRows, width=nColumns,
                                    xscrollcommand=self.FamilyNoteScrollbarX.set,
                                    yscrollcommand=self.FamilyNoteScrollbarY.set,
                                    wrap=WORD )
        self.textFamilyNote.grid( row=iRow, column=iCol+1,
                                  rowspan=nRows, columnspan=nColumns, sticky=N+S+E+W )

 
        iRow = 0
        iCol = iCol + 6

        # Children
        nColumns = 2
        nRows = 18
        self.CreateChildrenListbox( nColumns, nRows, iCol, iRow )

        iRow = iRow + nRows + 2

        # Add child
        self.buttonAddChild = Button(self.familyFrame)
        self.buttonAddChild['text'] = 'Add Child'
        self.buttonAddChild['command'] = self.OnAddChild

        self.buttonAddChild.grid(row=iRow, column=iCol, columnspan=2, sticky=N+S+E+W)

        iRow = iRow + 1

        # Remove child
        self.buttonRemoveChild = Button(self.familyFrame)
        self.buttonRemoveChild['text'] = 'Remove Child'
        self.buttonRemoveChild['command'] = self.OnRemoveChild

        self.buttonRemoveChild.grid(row=iRow, column=iCol, columnspan=2, sticky=N+S+E+W)


 
        iRow = iRow + 1

        # Empty
        nRows = 12
        self.labelEmpty6 = Label( self.familyFrame )
        self.labelEmpty6.grid( row=iRow, rowspan=nRows, column=iCol, columnspan=1 )


    # --------------------------------------------------------------------
    # CreateChildrenListbox
    # --------------------------------------------------------------------

    def CreateChildrenListbox(self, nColumns, nRows, column, row):

        self.labelChildren = Label(self.familyFrame, text='Children')
        self.labelChildren.grid(row=row, column=column,
                               columnspan=nColumns, sticky=N+S)

        self.ChildrenScrollbarY = Scrollbar(self.familyFrame, orient=VERTICAL)
        self.ChildrenScrollbarY.grid(row=row+1, column=column+nColumns,
                                     padx=2, pady=2, rowspan=nRows,
                                     sticky=N+S)
        self.ChildrenScrollbarY.rowconfigure(row+1, weight=1)

        self.ChildrenScrollbarX = Scrollbar(self.familyFrame, orient=HORIZONTAL)
        self.ChildrenScrollbarX.grid(row=row+nRows+1, column=column,
                                     padx=2, pady=2, columnspan=nColumns,
                                     sticky=E+W)

        self.ChildrenListbox = \
            Listbox( self.familyFrame, selectmode=SINGLE,
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

        #for c in range( column, column + nColumns - 1 ):
        #    self.columnconfigure(c, weight=1)



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

            d = Dialogs.DialogSelectSubject( self.master, self.ftGraph, 'Select a spouse',
                                             self.OnSelectedSpouse, self.OnSelectedSpouseCancel,
                                             [ '***  New Individual ***' ],
                                             'F', idsExcluded )
        elif ( sex == 'F' ):

            d = Dialogs.DialogSelectSubject( self.master, self.ftGraph, 'Select a spouse',
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

        self.ftGraph.SetSpouse( self.idIndividual, self.idSelectedSpouse,  self.idFamily )
        self.ftGraph.SetSpouse( self.idSelectedSpouse, self.idIndividual,  self.idFamily )

        self.UpdateSelectedSubject()



    # --------------------------------------------------------------------
    # OnSelectedSpouse
    # --------------------------------------------------------------------

    def OnSelectedSpouse(self, val):

        # If val is None then this means there were no individuals to
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
        spouse, idFamilySpouse, dateMarriage, dateDivorced = \
                self.ftGraph.GetSpouse( theIndividual, self.idFamily )

        if ( spouse is not None ):
            self.ChangeSubject( self.ftGraph.GetIndividualID( spouse ), self.idFamily )


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

        children = self.ftGraph.GetChildren( theIndividual, self.idFamily )
        idsChildren = []
        for child in children:
            idsChildren.append( child.attrib['id'] )


        self.idSelectedChild = None
        d = Dialogs.DialogSelectSubject( self.master, self.ftGraph, 'Select a child',
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
                spouse, idFamilySpouse, dateMarriage, dateDivorced = \
                        self.ftGraph.GetSpouse( theIndividual, self.idFamily )

                if ( spouse is not None ):
                    surname = spouse.findtext('NAME/surname')
    
        else:

            self.idSelectedChild = re.search( 'I\d\d\d$', self.idSelectedChild ).group( 0 )

        # Set the child

        self.ftGraph.SetChild( self.idIndividual, self.idSelectedChild, self.idFamily )

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
        children = self.ftGraph.GetChildren( theIndividual, self.idFamily )

        d = Dialogs.DialogSelectSubject( self.master, self.ftGraph, 'Select a child to remove',
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
    # UpdateSpouseButtonAdd
    # --------------------------------------------------------------------

    def UpdateSpouseButtonAdd(self):

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        spouse, idFamilySpouse, dateMarriage, dateDivorce = \
                self.ftGraph.GetSpouse( theIndividual, self.idFamily )

        if ( spouse is None ):

            self.buttonAddSpouse['text'] = 'Add Spouse'
            self.buttonAddSpouse['command'] = self.OnAddSpouse

        else:

            self.buttonAddSpouse['text'] = self.ftGraph.GetLabel( spouse )
            self.buttonAddSpouse['command'] = self.OnGoToSpouse

    # --------------------------------------------------------------------
    # UpdateChildrenListboxItems
    # --------------------------------------------------------------------

    def UpdateChildrenListboxItems( self ):

        self.ChildrenListbox.delete( 0, END )

        theIndividual = self.ftGraph.GetIndividual( self.idIndividual )

        labels = []
        theLabel  = None

        children = self.ftGraph.GetChildren( theIndividual, self.idFamily )

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
    # OnMarriedDayOptionSelect
    # --------------------------------------------------------------------

    def OnMarriedDayOptionSelect(self, *args):

        self.ftGraph.SetMarriedDay( self.idIndividual, self.varSelectedMarriedDay.get(), self.idFamily )


    # --------------------------------------------------------------------
    # OnMarriedMonthOptionSelect
    # --------------------------------------------------------------------

    def OnMarriedMonthOptionSelect(self, *args):

        self.ftGraph.SetMarriedMonth( self.idIndividual, self.varSelectedMarriedMonth.get(), self.idFamily )


    # --------------------------------------------------------------------
    # OnMarriedYearEdited
    # --------------------------------------------------------------------

    def OnMarriedYearEdited(self, *args):

        self.ftGraph.SetMarriedYear( self.idIndividual, self.varSelectedMarriedYear.get(), self.idFamily )


    # --------------------------------------------------------------------
    # OnMarriedPlaceEdited
    # --------------------------------------------------------------------

    def OnMarriedPlaceEdited(self, *args):

        self.ftGraph.SetMarriedPlace( self.idIndividual, self.varSelectedMarriedPlace.get(), self.idFamily )


    # --------------------------------------------------------------------
    # OnDivorcedDayOptionSelect
    # --------------------------------------------------------------------

    def OnDivorcedDayOptionSelect(self, *args):

        self.ftGraph.SetDivorcedDay( self.idIndividual, self.varSelectedDivorcedDay.get(), self.idFamily )


    # --------------------------------------------------------------------
    # OnDivorcedMonthOptionSelect
    # --------------------------------------------------------------------

    def OnDivorcedMonthOptionSelect(self, *args):

        self.ftGraph.SetDivorcedMonth( self.idIndividual, self.varSelectedDivorcedMonth.get(), self.idFamily )


    # --------------------------------------------------------------------
    # OnDivorcedYearEdited
    # --------------------------------------------------------------------

    def OnDivorcedYearEdited(self, *args):

        self.ftGraph.SetDivorcedYear( self.idIndividual, self.varSelectedDivorcedYear.get(), self.idFamily )

