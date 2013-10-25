# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen import logic


class CollectDebt(QuestBetween2):
    TYPE = 'collect_debt'
    TAGS = ('can_start', 'has_subquests') # can_continue can not be used, since quest has no FAILED finish

    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                            type=cls.TYPE,
                            nesting=nesting,
                            description=u'Начало: выбить долг',
                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid),
                                     facts.LocatedIn(object=receiver.uid, place=receiver_position.uid)],
                            actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER) ]

        choose_method = facts.Choice(uid=ns+'choose_method',
                                     description=u'Выбрать метод получения долга',
                                     require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                     actions=[facts.Message(type='move_to_receiver')])


        attack = facts.Question(uid=ns+'attack',
                                description=u'сражение с подручными должника',
                                require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                                actions=[facts.Message(type='attack'),
                                         facts.Fight(uid='attack', mercenary=True)],
                                condition=(facts.IsAlive(object=hero.uid),))

        finish_attack_successed = facts.Finish(uid=ns+'finish_attack_successed',
                                               start=start.uid,
                                               results={ initiator.uid: RESULTS.SUCCESSED,
                                                         receiver.uid: RESULTS.FAILED},
                                               nesting=nesting,
                                               description=u'долг выбит',
                                               require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                               actions=[facts.GiveReward(object=hero.uid, type='finish_attack_successed'),
                                                        facts.GivePower(object=initiator.uid, power=1),
                                                        facts.GivePower(object=receiver.uid, power=-1)])

        finish_attack_failed = facts.Finish(uid=ns+'finish_attack_failed',
                                            start=start.uid,
                                            results={ initiator.uid: RESULTS.FAILED,
                                                      receiver.uid: RESULTS.SUCCESSED},
                                            nesting=nesting,
                                            description=u'не удалось выбить долг',
                                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                            actions=[facts.Message(type='finish_attack_failed'),
                                                     facts.GivePower(object=initiator.uid, power=-1),
                                                     facts.GivePower(object=receiver.uid, power=1)])

        help = facts.State(uid=ns+'help',
                           description=u'помочь должнику',
                           require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        finish_help = facts.Finish(uid=ns+'finish_help',
                                   start=start.uid,
                                   results={ initiator.uid: RESULTS.SUCCESSED,
                                             receiver.uid: RESULTS.SUCCESSED},
                                   nesting=nesting,
                                   description=u'помощь оказана',
                                   require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                                   actions=[facts.GiveReward(object=hero.uid, type='finish_help'),
                                            facts.GivePower(object=initiator.uid, power=1),
                                            facts.GivePower(object=receiver.uid, power=1)])

        help_quest = selector.create_quest_from_person(nesting=nesting+1, initiator=receiver, tags=('can_continue',))
        help_extra = []

        for help_fact in logic.filter_subquest(help_quest, nesting):
            if isinstance(help_fact, facts.Start):
                help_extra.append(facts.Jump(state_from=help.uid, state_to=help_fact.uid, start_actions=[facts.Message(type='before_help')]))
            elif isinstance(help_fact, facts.Finish):
                if help_fact.results[receiver.uid] == RESULTS.SUCCESSED:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=finish_help.uid, start_actions=[facts.Message(type='after_successed_help')]))
                else:
                    help_extra.append(facts.Jump(state_from=help_fact.uid, state_to=attack.uid, start_actions=[facts.Message(type='after_failed_help')]))

        subquest = facts.SubQuest(uid=ns+'help_subquest', members=logic.get_subquest_members(help_quest))

        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=choose_method.uid),

                 choose_method,

                 facts.Option(state_from=choose_method.uid, state_to=attack.uid, type='attack'),
                 facts.Option(state_from=choose_method.uid, state_to=help.uid, type='help'),

                 help,
                 attack,

                 facts.Answer(state_from=attack.uid, state_to=finish_attack_successed.uid, condition=True),
                 facts.Answer(state_from=attack.uid, state_to=finish_attack_failed.uid, condition=False),

                 finish_attack_successed,
                 finish_attack_failed,
                 finish_help,

                 subquest
                ]

        line.extend(participants)
        line.extend(help_quest)
        line.extend(help_extra)

        return line
