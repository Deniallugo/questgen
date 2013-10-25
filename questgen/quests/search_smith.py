# coding: utf-8

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts
from questgen.relations import PROFESSION
from questgen import logic


class SearchSmith(QuestBetween2):
    TYPE = 'search_smith'
    TAGS = ('can_start', 'has_subquests')

    @classmethod
    def construct_from_place(cls, nesting, selector, start_place):

        receiver = selector.new_person(first_initiator=False, professions=(PROFESSION.BLACKSMITH,))
        receiver_position = selector.place_for(objects=(receiver.uid,))

        return cls.construct(nesting=nesting,
                             selector=selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=receiver,
                             receiver_position=receiver_position)


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        hero = selector.heroes()[0]

        upgrade_equipment_cost = selector.upgrade_equipment_cost().money

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start_search_smith',
                            type=cls.TYPE,
                            nesting=nesting,
                            description=u'Начало: посещение кузнеца',
                            require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                            actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER) ]

        arriving = facts.Question(uid=ns+'arriving',
                                  description=u'Прибытие в город',
                                  condition=(facts.HasMoney(object=hero.uid, money=upgrade_equipment_cost),),
                                  require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        upgrade_for_money = facts.State(uid=ns+'upgrade_for_money',
                                        description=u'Обновление экипировки за деньги',
                                        actions=[facts.UpgradeEquipment(cost=upgrade_equipment_cost)],
                                        require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        upgrade_for_quest = facts.State(uid=ns+'upgrade_for_quest',
                                        description=u'Обновление экипировки за задание',
                                        actions=[facts.UpgradeEquipment(cost=None)],
                                        require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        finish_successed = facts.Finish(uid=ns+'finish_successed',
                                        start=start.uid,
                                        results={ receiver.uid: RESULTS.SUCCESSED},
                                        nesting=nesting,
                                        description=u'завершить задание',
                                        actions=[facts.GivePower(object=receiver.uid, power=1)])

        finish_quest_failed = facts.Finish(uid=ns+'finish_quest_failed',
                                           start=start.uid,
                                           results={ receiver.uid: RESULTS.NEUTRAL},
                                           nesting=nesting,
                                           description=u'завершить задание')


        help_quest = selector.create_quest_from_person(nesting=nesting+1, initiator=receiver, tags=('can_continue',))
        help_extra = []

        for help_fact in logic.filter_subquest(help_quest, nesting):
            if isinstance(help_fact, facts.Start):
                help_extra.append(facts.Answer(state_from=arriving.uid,
                                               state_to=help_fact.uid,
                                               condition=False,
                                               start_actions=[facts.Message(type='start_quest')]))
            elif isinstance(help_fact, facts.Finish):
                if help_fact.results[receiver.uid] == RESULTS.SUCCESSED:
                    help_extra.append(facts.Jump(state_from=help_fact.uid,
                                                 state_to=upgrade_for_quest.uid,
                                                 start_actions=[facts.Message(type='quest_successed')]))
                else:
                    help_extra.append(facts.Jump(state_from=help_fact.uid,
                                                 state_to=finish_quest_failed.uid,
                                                 start_actions=[facts.Message(type='quest_failed')]))

        subquest = facts.SubQuest(uid=ns+'help_subquest', members=logic.get_subquest_members(help_quest))


        line = [ start,

                 facts.Jump(state_from=start.uid, state_to=arriving.uid),

                 arriving,

                 facts.Answer(state_from=arriving.uid, state_to=upgrade_for_money.uid, condition=True),

                 upgrade_for_money,
                 upgrade_for_quest,

                 facts.Jump(state_from=upgrade_for_money.uid, state_to=finish_successed.uid),
                 facts.Jump(state_from=upgrade_for_quest.uid, state_to=finish_successed.uid),

                 finish_successed,
                 finish_quest_failed,

                 subquest
               ]

        line.extend(participants)
        line.extend(help_quest)
        line.extend(help_extra)

        return line
