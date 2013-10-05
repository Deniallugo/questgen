# coding: utf-8


class QuestgenError(Exception):
    MSG = None

    def __init__(self, **kwargs):
        super(QuestgenError, self).__init__(self.MSG % kwargs)

####################################################################
# knowledge base
####################################################################p

class KnowledgeBaseError(QuestgenError): pass

class DuplicatedFactError(KnowledgeBaseError):
    MSG = u'can not add fact %(fact)r to knowlege base - it already in base'

class WrongFactTypeError(KnowledgeBaseError):
    MSG = u'can not add fact %(fact)r to knowlege base - wrong type'

class NoFactError(KnowledgeBaseError):
    MSG = u'%(fact)s not in knowledge base'

####################################################################
# facts
####################################################################
class FactsError(QuestgenError): pass

class WrongChangeAttributeError(KnowledgeBaseError):
    MSG = u'can not change fact %(fact)r - unknown attribute "%(attribute)s"'

class RequiredAttributeError(KnowledgeBaseError):
    MSG = u'can not create fact %(fact)r - attribute "%(attribute)s" not specified'

class WrongAttributeError(KnowledgeBaseError):
    MSG = u'can not create fact %(fact)r - wrong attribute "%(attribute)s"'

# class OptionUIDWithoutChoicePart(FactsError):
#     MSG = u'Option uid "%(option)r" MUST starts with parent choice uid followed by dot'

class UIDDidNotSetupped(FactsError):
    MSG = u'uid for "%(fact)r did not setupped'

####################################################################
# machine
####################################################################
class MachineError(QuestgenError): pass

class NoJumpsAvailableError(MachineError):
    MSG = u'no jumps available for state %(state)r'

class NoJumpsFromLastStateError(MachineError):
    MSG = u'no jumps available for last state %(state)r'

class MoreThenOneJumpsAvailableError(MachineError):
    MSG = u'more then oneo jumps available for state %(state)r'


####################################################################
# transformators
####################################################################
class TransformatorsError(QuestgenError): pass

class NoEventMembersError(TransformatorsError):
    MSG = u'no tagged event members for event "%(event)r"'

class OptionWithTwoLinksError(TransformatorsError):
    MSG = u'option "%(option)r" has more then one link'

class LinkedOptionWithProcessedChoiceError(TransformatorsError):
    MSG = u'choice of option "%(option)r" has already had default option. Probably you have mess with linked options'


####################################################################
# quests
####################################################################

class QuestsBaseError(QuestgenError): pass

class DuplicatedQuestError(QuestsBaseError):
    MSG = u'can not add quest %(quest)r to quests base - it already in base'

class WrongQuestTypeError(QuestsBaseError):
    MSG = u'can not add quest %(quest)r to quests base - wrong type'


####################################################################
# roll back errors
####################################################################

class RollBackError(QuestgenError):
    MSG = u'something is wrong (%(message)), do rollback'

class NoQuestChoicesRollBackError(RollBackError):
    MSG = u'no quests choices for next quest'


####################################################################
# selectoes
####################################################################

class SelectorsBaseError(RollBackError): pass

class NoFactSelectedError(SelectorsBaseError):
    MSG = u'can not found fact with method "%(method)s" and arguments: %(arguments)s'
