#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET


# ========================================================================
# Class to access family tree XML
# ========================================================================

class FamilyTreeXML( object ):


    # --------------------------------------------------------------------
    #  __init__
    # --------------------------------------------------------------------

    def __init__( self,
                  xmlFamilyTree ):

        self.ftXML = xmlFamilyTree


    # ----------------------------------------------------------------------
    def GetIndividual( self, idIndi ):

        individuals = self.GetIndividuals()

        if ( individuals is None ):
            return None

        elif ( idIndi is None ):
            return self.ftXML.find( 'INDIVIDUAL' )

        else:
            for individual in individuals:

                if ( individual.attrib['id'] == idIndi ):
                    return individual

        return None


    # ----------------------------------------------------------------------
    def GetIndividualID( self, individual ):

        return individual.attrib['id']


    # ----------------------------------------------------------------------
    def GetIndividuals( self ):
        
        return self.ftXML.findall( 'INDIVIDUAL' )


    # ----------------------------------------------------------------------
    def GetFamilies( self ):
        
        return self.ftXML.findall( 'FAMILY' )


    # ----------------------------------------------------------------------
    def GetForename(  self, individual ):
    
        return individual.findtext('NAME/forename')
    

    # ----------------------------------------------------------------------
    def GetSurname(  self, individual ):
    
        return individual.findtext('NAME/surname')
    

    # ----------------------------------------------------------------------
    def GetName(  self, individual ):
    
        forename = self.GetForename( individual ) or '?'
        surname  = self.GetSurname( individual ) or '?'
    
        return ' '.join( [ forename, surname ] )
    

    # ----------------------------------------------------------------------
    def GetNameAndID(  self, individual ):
    
        idIndi = individual.attrib['id']
        
        name = self.GetName( individual )
    
        return ''.join( [ idIndi + '\n', name ] )
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetFamilyWithID( self, id ):
    
        foundFamilies = []
    
        for family in self.GetFamilies():

            if ( family.attrib['id'] == id ):
                foundFamilies.append( family )
    
        return foundFamilies
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetIndividualWithID( self, id ):
    
        foundIndividuals = []
    
        for individual in self.GetIndividuals():
            if ( individual.attrib['id'] == id ):
                foundIndividuals.append( individual )
    
        if ( len( foundIndividuals ) > 1 ):
            raise Exception( 'ERROR: Found multiple individuals with the same ID: {:s}'.format ( id ) )
    
        elif ( len( foundIndividuals ) == 1 ):
            return foundIndividuals[0]
    
        else:
            return None
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetDate( self, element ):
    
        dateText = None
    
        if ( element is not None ):
            date = element.find( 'DATE' )
        
            if ( date is not None ):
    
                dateList = []
    
                day   = date.findtext('day')
                if ( day ):
                    dateList.append( day )
    
                month = date.findtext('month')
                if ( month ):
                    dateList.append( month )
    
                year  = date.findtext('year')
                if ( year ):
                    dateList.append( year )
    
                dateText = ' '.join( dateList )
    
        return dateText
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetDateMarried( self, individual ):
    
        spouse = None
        dateMarriage = None
    
        idFamilySpouse = individual.findtext('FAMILY_SPOUSE')
        
        if ( idFamilySpouse ):
            for family in self.GetFamilyWithID( idFamilySpouse ):
    
                marriage = family.find('MARRIAGE')
    
                if ( marriage is not None ):
                    return self.GetDate( marriage )
    
        return None
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetWife( self, individual ):
    
        sex = individual.findtext('SEX')
    
        if ( sex == 'F' ):
            return None, None, None
    
        wife, idFamilySpouse, dateMarriage = self.GetSpouse( individual )
    
        return ( wife, idFamilySpouse, dateMarriage )
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetSpouse( self, individual ):
    
        spouse = None
        dateMarriage = None
    
        sex = individual.findtext('SEX')
        idFamilySpouse = individual.findtext('FAMILY_SPOUSE')
        
        if ( idFamilySpouse ):
            for family in self.GetFamilyWithID( idFamilySpouse ):
    
                if ( sex == 'M' ):
                    idSpouse = family.findtext('WIFE')
                else:
                    idSpouse = family.findtext('HUSBAND')
    
                if ( idSpouse is None ):
                    return ( None, idFamilySpouse, dateMarriage )
    
                flgFoundSpouse = False
                for spouse in self.GetIndividuals():
                    if ( spouse.attrib['id'] == idSpouse ):
                        flgFoundSpouse = True
                        break
    
                if ( flgFoundSpouse ):
                    marriage = family.find('MARRIAGE')
    
                    if ( marriage is not None ):
                        dateMarriage = self.GetDate( marriage )
                        break
    
        return ( spouse, idFamilySpouse, dateMarriage )
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetChildren( self, individual ):
    
        children = []
    
        idFamilySpouse = individual.findtext('FAMILY_SPOUSE')
        
        if ( idFamilySpouse ):
    
            for family in self.GetFamilyWithID( idFamilySpouse ):
    
                for child in family.findall( 'CHILD' ):
    
                    individualChild = self.GetIndividualWithID( child.text )
                    
                    if ( individualChild is not None ):
                        children.append( individualChild )
    
        return ( children, idFamilySpouse )
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetParents( self, individual ):
    
        mother = None
        father = None
    
        idFamilyChild  = individual.findtext('FAMILY_CHILD')
        
        if ( idFamilyChild ):
            for family in self.GetFamilyWithID( idFamilyChild ):
    
                idMother = family.findtext('WIFE')
                idFather = family.findtext('HUSBAND')
    
                for parent in self.GetIndividuals():
                    if ( parent.attrib['id'] == idMother ):
                        mother = parent
                    elif ( parent.attrib['id'] == idFather ):
                        father = parent
                        
                    if ( ( mother is not None ) and ( father  is not None ) ):
                        break
    
        return ( mother, father, idFamilyChild )
    
    # ----------------------------------------------------------------------
    
    
    # ----------------------------------------------------------------------
    def GetSiblings( self, individual ):
    
        siblings = []
    
        idFamilyChild  = individual.findtext('FAMILY_CHILD')
        
        if ( idFamilyChild ):
    
            for family in self.GetFamilyWithID( idFamilyChild ):
    
                for sibling in family.findall( 'CHILD' ):
    
                    if ( individual.attrib['id'] != sibling.text ):
    
                        individualSibling = self.GetIndividualWithID( sibling.text )
    
                        if ( individualSibling is not None ):
                            siblings.append( individualSibling )
    
        return ( siblings, idFamilyChild )
    
    # ----------------------------------------------------------------------
    
            
    # ----------------------------------------------------------------------
    def CreateIndividual( self, idFamilyChild=None, idFamilySpouse=None ):

        ids = []
        for individual in self.GetIndividuals():
            ids.append( individual.attrib['id'] )

        i = 1
        idIndi = 'I{:03d}'.format ( i )
        while ( idIndi in ids ):
            i = i + 1
            idIndi = 'I{:03d}'.format ( i )

        return ET.SubElement( self.ftXML, 'INDIVIDUAL', { 'id': idIndi } )
    # ----------------------------------------------------------------------
    
            
    # ----------------------------------------------------------------------
    def DeleteIndividual( self, idIndividual ):

        prevIndividual = None
        theIndividual  = None
        nextIndividual = None

        lastIndividual = None

        print 'DeleteIndividual()', idIndividual

        # Find the individual

        for individual in self.GetIndividuals():

            if ( individual.attrib['id'] == idIndividual ):

                theIndividual = individual
                prevIndividual = lastIndividual

            elif ( not theIndividual is None ):

                nextIndividual = individual
                break                   

            lastIndividual = individual
                
        self.ftXML.remove( theIndividual )

        # Also delete spouse references

        idFamilySpouse = theIndividual.findtext('FAMILY_SPOUSE')

        for family in self.GetFamilyWithID( idFamilySpouse ):

            if ( idIndividual == family.findtext('WIFE') ):

                eWife = family.find('WIFE')
                family.remove( eWife )

            if ( idIndividual == family.findtext('HUSBAND') ):

                eHusband = family.find('HUSBAND')
                family.remove( eHusband )

            # If the family has no spouses or children then delete is

            if ( ( family.findtext('WIFE') is None ) and
                 ( family.findtext('HUSBAND') is None ) and
                 ( family.findtext('CHILD') is None ) ):

                self.ftXML.remove( family )

        # and child references

        idFamilyChild = theIndividual.findtext('FAMILY_CHILD')

        for family in self.GetFamilyWithID( idFamilyChild ):

            if ( idIndividual == family.findtext('CHILD') ):

                eChild = family.find('CHILD')
                family.remove( eChild )

            # If the family has no spouses or children then delete is

            if ( ( family.findtext('WIFE') is None ) and
                 ( family.findtext('HUSBAND') is None ) and
                 ( family.findtext('CHILD') is None ) ):

                self.ftXML.remove( family )


        # Return the id of an adjacent individual

        if ( not prevIndividual is None ):
            return prevIndividual.attrib['id']

        elif ( not nextIndividual is None ):
            return nextIndividual.attrib['id']

        return None
    
            
    # ----------------------------------------------------------------------
    def SetFirstName( self, idIndividual, name ):

        theIndividual = self.GetIndividual( idIndividual )

        if ( not theIndividual is None ):
            
            eName = theIndividual.find('NAME')
        
            if ( eName is None ):
                eName = ET.SubElement( theIndividual, 'NAME' )
            
            eFirstName = eName.find('forename')

            if ( eFirstName is None ):
                eFirstName = ET.SubElement( eName, 'forename' )

            eFirstName.text = name
    
            
    # ----------------------------------------------------------------------
    def SetLastName( self, idIndividual, name ):

        theIndividual = self.GetIndividual( idIndividual )

        if ( not theIndividual is None ):
            
            eName = theIndividual.find('NAME')

            if ( eName is None ):
                eName = ET.SubElement( theIndividual, 'NAME' )
            
            eLastName = eName.find('surname')

            if ( eLastName is None ):
                eLastName = ET.SubElement( eName, 'surname' )

            eLastName.text = name
    
            
    # ----------------------------------------------------------------------
    def SetSex( self, idIndividual, sex ):

        theIndividual = self.GetIndividual( idIndividual )

        if ( not theIndividual is None ):
            
            eSex = theIndividual.find('SEX')

            if ( eSex is None ):
                eSex = ET.SubElement( theIndividual, 'SEX' )

            eSex.text = sex
    
            
    # ----------------------------------------------------------------------
    def SetBirthDay( self, idIndividual, day ):

        theIndividual = self.GetIndividual( idIndividual )

        if ( not theIndividual is None ):
            
            eBirth = theIndividual.find('BIRTH')

            if ( eBirth is None ):
                eBirth = ET.SubElement(theIndividual, 'BIRTH' )

            eBirthDate = eBirth.find('DATE')

            if ( eBirthDate is None ):
                eBirthDate = ET.SubElement(eBirth, 'DATE' )

            eBirthDay  = eBirthDate.find('day')

            if ( eBirthDay is None ):
                eBirthDay = ET.SubElement(eBirthDate, 'day' )

            eBirthDay.text = day
    
            
    # ----------------------------------------------------------------------
    def SetBirthMonth( self, idIndividual, month ):

        theIndividual = self.GetIndividual( idIndividual )

        if ( not theIndividual is None ):
            
            eBirth = theIndividual.find('BIRTH')

            if ( eBirth is None ):
                eBirth = ET.SubElement(theIndividual, 'BIRTH' )

            eBirthDate = eBirth.find('DATE')

            if ( eBirthDate is None ):
                eBirthDate = ET.SubElement(eBirth, 'DATE' )

            eBirthMonth  = eBirthDate.find('month')

            if ( eBirthMonth is None ):
                eBirthMonth = ET.SubElement(eBirthDate, 'month' )

            eBirthMonth.text = month
    
            
    # ----------------------------------------------------------------------
    def SetBirthYear( self, idIndividual, year ):

        theIndividual = self.GetIndividual( self.idIndividual )

        if ( not theIndividual is None ):
            
            eBirth     = theIndividual.find('BIRTH')

            if ( eBirth is None ):
                eBirth = ET.SubElement(theIndividual, 'BIRTH' )

            eBirthDate = eBirth.find('DATE')

            if ( eBirthDate is None ):
                eBirthDate = ET.SubElement(eBirth, 'DATE' )

            eBirthYear  = eBirthDate.find('year')

            if ( eBirthYear is None ):
                eBirthYear = ET.SubElement(eBirthDate, 'year' )

            eBirthYear.text = year
    
            
    # ----------------------------------------------------------------------
    def SetDeathDay( self, idIndividual, day ):

        theIndividual = self.GetIndividual( idIndividual )

        if ( not theIndividual is None ):
            
            eDeath = theIndividual.find('DEATH')
            
            if ( eDeath is None ):
                eDeath = ET.SubElement(theIndividual, 'DEATH' )

            eDeathDate = eDeath.find('DATE')

            if ( eDeathDate is None ):
                eDeathDate = ET.SubElement(eDeath, 'DATE' )

            eDeathDay  = eDeathDate.find('day')

            if ( eDeathDay is None ):
                eDeathDay = ET.SubElement(eDeathDate, 'day' )

            eDeathDay.text = day
    
            
    # ----------------------------------------------------------------------
    def SetDeathMonth( self, idIndividual, month ):

        theIndividual = self.GetIndividual( idIndividual )

        if ( not theIndividual is None ):
            
            eDeath = theIndividual.find('DEATH')

            if ( eDeath is None ):
                eDeath = ET.SubElement(theIndividual, 'DEATH' )

            eDeathDate = eDeath.find('DATE')

            if ( eDeathDate is None ):
                eDeathDate = ET.SubElement(eDeath, 'DATE' )

            eDeathMonth  = eDeathDate.find('month')

            if ( eDeathMonth is None ):
                eDeathMonth = ET.SubElement(eDeathDate, 'month' )

            eDeathMonth.text = month
    
            
    # ----------------------------------------------------------------------
    def SetDeathYear( self, idIndividual, year ):

        theIndividual = self.GetIndividual( self.idIndividual )

        if ( not theIndividual is None ):
            
            eDeath = theIndividual.find('DEATH')

            if ( eDeath is None ):
                eDeath = ET.SubElement(theIndividual, 'DEATH' )

            eDeathDate = eDeath.find('DATE')

            if ( eDeathDate is None ):
                eDeathDate = ET.SubElement(eDeath, 'DATE' )

            eDeathYear  = eDeathDate.find('year')

            if ( eDeathYear is None ):
                eDeathYear = ET.SubElement(eDeathDate, 'year' )

            eDeathYear.text = year


