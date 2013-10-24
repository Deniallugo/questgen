# coding: utf-8
import itertools

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import logic


class InterfereEnemy(QuestBetween2):
    TYPE = 'interfere_enemy'
    TAGS = ('can_start', 'has_subquests')

    @classmethod
    def get_enemy(cls, selector):
        return selector._kb[selector.preferences_enemy().person]

    @classmethod
    def construct_from_place(cls, nesting, selector, start_place):

        enemy = cls.get_enemy(selector)

        return cls.construct(nesting=nesting,
                             selector=selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=selector.new_person(first_initiator=False, candidates=(enemy.uid, )),
                             receiver_position=selector.place_for(objects=(enemy.uid, )))


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        antagonist = selector.new_person(first_initiator=False)
        antagonist_position = selector.place_for(objects=(antagonist.uid,))

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description=u'Начало: навредить противнику',
                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER),
                        facts.QuestParticipant(start=start.uid, participant=antagonist_position.uid, role=ROLES.ANTAGONIST_POSITION) ]

        finish = facts.Finish(uid=ns+'finish',
                              result=RESULTS.SUCCESSED,
                              nesting=nesting,
                              description=u'навредили противнику',
                              actions=[facts.GiveReward(object=hero.uid, type='finish'),
                                       facts.GivePower(object=receiver.uid, power=-1),
                                       facts.GivePower(object=antagonist_position.uid, power=-1)])

        help_quest = selector.create_quest_between_2(nesting=nesting+1, initiator=antagonist, receiver=receiver, tags=('can_continue',))
        help_extra = []

        for help_fact in logic.filter_subquest(help_quest, nesting):
            if isinstance(help_fact, facts.Start):
                help_extra.append(facts.Jump(state_from=start.uid, state_to=help_fact.uid))
            elif isinstance(help_fact, facts.Finish):
                if help_fact.result == RESULTS.FAILED:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=finish.uid, start_actions=[facts.Message(type='after_interfere')]))

        subquest = facts.SubQuest(uid=ns+'interfere_subquest', members=logic.get_subquest_members(itertools.chain(help_quest, help_extra)))

        line = [ start,
                 finish,
                 subquest
                ]

        line.extend(participants)
        line.extend(help_quest)
        line.extend(help_extra)

        return line
