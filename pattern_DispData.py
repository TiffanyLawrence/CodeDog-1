#/////////////////  Use this pattern to write dump() or drawData() to display each member of the model for a struct.

import progSpec
import codeDogParser
from progSpec import cdlog, cdErr

import pattern_GenSymbols

thisPatternAlreadyUsedOnce=False

classesToProcess=[]
classesEncoded={}

#---------------------------------------------------------------  TEXT GEN
def displayTextFieldAction(label, fieldName, field, fldCat):
    global classesToProcess
    global classesEncoded
    valStr=''
    if(fldCat=='int' or fldCat=='double'):
        valStr='toString('+fieldName+')'
    elif(fldCat=='string' or fldCat=='char'):
        valStr= "'"+fieldName+"'"
    elif(fldCat=='flag' or fldCat=='bool'):
        valStr='dispBool('+fieldName+')'
    elif(fldCat=='mode'):
        valStr='toString('+fieldName+')'  #fieldName+'Strings['+fieldName+'] '
    elif(fldCat=='struct'):
        valStr=fieldName+'.dump(indent+"|   ")\n'

        structTypeName=field['typeSpec']['fieldType'][0]
        if not(structTypeName in classesEncoded):
            #print "TO ENDODE:", structTypeName
            classesEncoded[structTypeName]=1
            classesToProcess.append(structTypeName)
    if(fldCat=='struct'):
        S="    "+'print(indent, dispFieldAsText("'+label+'", 15), "\\n")\n    '+valStr+'\n    print("\\n")\n'
    else:
        S="    "+'print(indent, dispFieldAsText("'+label+'", 15), '+valStr+', "\\n")\n'
    return S

def encodeFieldText(fieldName, field, fldCat):
    S=""
    if fldCat=='func': return ''
    typeSpec=field['typeSpec']
    if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:
        innerFieldType=typeSpec['fieldType']
        #print "ARRAYSPEC:",innerFieldType, field
        fldCatInner=progSpec.innerTypeCategory(innerFieldType)
        calcdName=fieldName+'["+toString(_item_key)+"]'
        S+="    withEach _item in "+fieldName+":{\n"
        S+="        "+displayTextFieldAction(calcdName, '_item', field, fldCatInner)+"    }\n"
    else: S+=displayTextFieldAction(fieldName, fieldName, field, fldCat)
    if progSpec.typeIsPointer(typeSpec):
        T ="    if("+fieldName+' == NULL){print('+'indent, dispFieldAsText("'+fieldName+'", 15)+"NULL\\n")}\n'
        T+="    else{\n    "+S+"    }\n"
        S=T
    return S

#---------------------------------------------------------------  DRAW GEN
def displayDrawFieldAction(label, fieldName, field, fldCat):
    global classesToProcess
    global classesEncoded
    valStr=''
    if(fldCat=='int' or fldCat=='double'):
        valStr='toString('+fieldName+')'
    elif(fldCat=='string' or fldCat=='char'):
        valStr= "'"+fieldName+"'"
    elif(fldCat=='flag' or fldCat=='bool'):
        valStr='dispBool('+fieldName+')'
    elif(fldCat=='mode'):
        valStr= label+'Strings['+fieldName+'] '
    elif(fldCat=='struct'):
        valStr= fieldName+'.mySymbol()'

        # Add new classname to a list so it can be encoded.
        structTypeName=field['typeSpec']['fieldType'][0]
        if not(structTypeName in classesEncoded):
            classesEncoded[structTypeName]=1
            classesToProcess.append(structTypeName)

    if(fldCat=='struct'):
        S="    "+'DS <- drawField(cr, x,y, "'+label+'", '+valStr+')\n    y <- y + DS.height\n'
        if progSpec.typeIsPointer(field['typeSpec']):
            targetRef = fieldName
        #    S+="    "+targetRef+'.fromList.pushLast(this)\n'
        #    S+="    "+'cousins.pushLast(' + targetRef + ')'
        else:
            S+="    "+'DS <- ' + fieldName+'.drawData(cr, x+20, y)\n    y <- y + DS.height\n'
    else:
        S="    "+'DS <- drawField(cr, x,y, "'+label+'", '+valStr+')\n    y <- y + DS.height\n'
    return S

def encodeFieldDraw(fieldName, field, fldCat):
    S=""
    if fldCat=='func': return ''
    typeSpec=field['typeSpec']
    if 'arraySpec' in typeSpec and typeSpec['arraySpec']!=None:
        innerFieldType=typeSpec['fieldType']
        fldCatInner=progSpec.innerTypeCategory(innerFieldType)
        calcdName=fieldName+'["+toString(_item_key)+"]'
        S+="    withEach _item in "+fieldName+":{\n"
        S+="        "+displayDrawFieldAction(calcdName, '_item', field, fldCatInner)+"    }\n"
    else: S+=displayDrawFieldAction(fieldName, fieldName, field, fldCat)
    if progSpec.typeIsPointer(typeSpec):
        T ="    if("+fieldName+' == NULL){DS <- drawField(cr, '+'x,y, "'+fieldName+'", "NULL")\n    y <- y + DS.height}\n'
        T+="    else{\n    "+S+"    }\n"
        S=T
    return S

#---------------------------------------------------------------  DUMP MAKING CODE

def EncodeDumpFunction(classes, className, dispMode):
    global classesEncoded
    cdlog(2, "ENCODING: "+ className)
    classesEncoded[className]=1
    textFuncBody=''
    drawFuncBody=''
    modelRef = progSpec.findSpecOf(classes[0], className, 'model')
    if modelRef==None:
        cdErr('To write a dump function for class '+className+' a model is needed but is not found.')
    ### Write code for each field
    for field in modelRef['fields']:
        fldCat=progSpec.fieldsTypeCategory(field['typeSpec'])
        fieldName=field['fieldName']

        if(dispMode=='text' or dispMode=='both'):
            textFuncBody+=encodeFieldText(fieldName, field, fldCat)
        if(dispMode=='draw' or dispMode=='both'):
            drawFuncBody+=encodeFieldDraw(fieldName, field, fldCat)

    #### Write code to draw rectangle around the data.
    drawFuncBody+='cr.fillNow()\n'
    drawFuncBody+="cr.rectangle(initialX, initialY, initialX+DS.width, initialY+DS.height)\n"
    drawFuncBody+='cr.strokeNow()\n'

    if(dispMode=='text' or dispMode=='both'):
        Code="me void: dump(me string:indent) <- {\n"+textFuncBody+"    }\n"
        Code=progSpec.wrapFieldListInObjectDef(className, Code)
        codeDogParser.AddToObjectFromText(classes[0], classes[1], Code)

    if(dispMode=='draw' or dispMode=='both'):
        Code='''
    me deltaSize: drawData(me GUI_ctxt: cr, me int:x, me int:y) <- {
        me int: initialX <- x
        me int: initialY <- y
        me deltaSize: DS
    '''+drawFuncBody+'''
        /-DS.width <- maxWidth
        DS.height <- y-initialY
        return(DS)
    }\n'''
        Code=progSpec.wrapFieldListInObjectDef(className, Code)
        codeDogParser.AddToObjectFromText(classes[0], classes[1], Code)

def apply(classes, tags, className, dispMode):
    global classesToProcess
    global thisPatternAlreadyUsedOnce
    if(not thisPatternAlreadyUsedOnce):
        thisPatternAlreadyUsedOnce=True
        CODE="""
struct GLOBAL{
    me string: dispBool(me bool: tf) <- {
        if(tf){return("true")} else {return("false")}
    }
    """
        if(dispMode=='text' or dispMode=='both'):
            CODE+="""
    me string: dispFieldAsText(me string: label, me int:labelLen) <- {
        me string: S <- ""
        me int: labelSize<-label.size()
        withEach count in RANGE(0..labelLen):{
            if (count<labelSize){S <- S+label[count]}
            else if(count==labelSize){ S <- S+":"}
            else {S <- S+" "}
        }
        return(S)
    }
    """
        if(dispMode=='draw' or dispMode=='both'):
            CODE+="""
    const int: fontSize <- 10
    me deltaSize: drawField(me GUI_ctxt: cr, me int:x, me int:y, me string: label, me string: value) <- {
        me deltaSize: DS1
        me deltaSize: DS2
        me deltaSize: DS3
        DS1 <- renderText(cr, label, "Ariel",  fontSize, x, y)
        DS2 <- renderText(cr, value, "Ariel",  fontSize, x+90, y)
        DS3.width <- DS2.width+90
        DS3.height <- DS2.height
        return(DS3)
    }
    """
        CODE+="""
}
    """
        codeDogParser.AddToObjectFromText(classes[0], classes[1], CODE)

    classesToProcess.append(className)
    for classToEncode in classesToProcess:
        pattern_GenSymbols.apply(classes, {}, [classToEncode])      # Invoke the GenSymbols pattern
        EncodeDumpFunction(classes, classToEncode, dispMode)
    return
