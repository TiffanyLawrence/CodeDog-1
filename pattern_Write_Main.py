#/////////////////////////////////////////////////  R o u t i n e s   t o   G e n e r a t e  " m a i n ( ) "

import progSpec
import codeDogParser

mainFuncCode=r"// No Main given"
def apply(objects, tags, codeToRun):
    # TODO: Make initCode, runCode and deInitCode work better and more automated by patterns.
    initFuncCode=''; initCode=''; runCode=''; deinitCode=''

    if 'initCode'   in tags: initCode  = tags['initCode']
    if 'runCode'    in tags: runCode   = tags['runCode']+';'
    if 'deinitCode' in tags: deinitCode= tags['deinitCode']

    tags['Include'] += ",<signal.h>"

    initFuncCode=r"""
    me void: initialize() <- {
        %s
    }

    me void: deinitialize() <- {
        %s
    }
    """ % (initCode, deinitCode)

    # TODO: Some deInitialize items should automatically run during abort().
    # TODO: Deinitialize items should happen in reverse order.
    mainFuncCode="""
    me int32: main(me int32: argc, me int32: argv ) <- <%{
    signal(SIGSEGV, reportFault);
    std::ios_base::sync_with_stdio(false);
    initialize();
    """ + runCode + """
    deinitialize();
    return 0;
    } %>

"""

    progSpec.addObject(objects[0], objects[1], 'GLOBAL', 'struct', 'SEQ')
    codeDogParser.AddToObjectFromText(objects[0], objects[1], progSpec.wrapFieldListInObjectDef('GLOBAL', initFuncCode + mainFuncCode ))
