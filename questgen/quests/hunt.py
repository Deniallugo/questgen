# coding: utf-8
import random

from questgen.quests.base_quest import QuestBetween2, ROLES, RESULTS
from questgen import facts


class Hunt(QuestBetween2):
    TYPE = 'hunt'
    TAGS = ('can_start', )
    HUNT_LOOPS = (2, 4)

    @classmethod
    def get_mob(cls, selector):
        return selector._kb[selector.preferences_mob().mob]

    @classmethod
    def construct_from_place(cls, nesting, selector, start_place):

        mob = cls.get_mob(selector)

        return cls.construct(nesting=nesting,
                             selector=selector,
                             initiator=None,
                             initiator_position=start_place,
                             receiver=None,
                             receiver_position=selector.new_place(terrains=mob.terrains))


    @classmethod
    def construct(cls, nesting, selector, initiator, initiator_position, receiver, receiver_position):

        mob = cls.get_mob(selector)

        hero = selector.heroes()[0]

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start',
                      type=cls.TYPE,
                      nesting=nesting,
                      description=u'Начало: задание на охоту',
                      require=[facts.LocatedIn(object=hero.uid, place=initiator_position.uid)],
                      actions=[facts.Message(type='intro')])

        participants = [facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=ROLES.RECEIVER_POSITION) ]

        start_hunting = facts.State(uid=ns+'start_hunting',
                              description=u'Прибытие в город охоты',
                              require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)])

        hunt_loop = []

        for i in xrange(random.randint(*cls.HUNT_LOOPS)):

            hunt = facts.State(uid=ns+'hunt_%d' % i,
                         description=u'Охота',
                         actions=[facts.MoveNear(object=hero.uid, place=receiver_position.uid, terrains=mob.terrains)])

            fight = facts.State(uid=ns+'fight_%d' % i,
                          description=u'Сражение с жертвой',
                          actions=[facts.Message(type='fight'),
                                   facts.Fight(uid='fight_%d' % i, mob=mob.uid)])

            if hunt_loop:
                hunt_loop.append(facts.Jump(state_from=hunt_loop[-1].uid, state_to=hunt.uid, start_actions=[facts.Message(type='start_track'),]))

            hunt_loop.extend([hunt,
                              facts.Jump(state_from=hunt.uid, state_to=fight.uid),
                              fight])

        sell_prey = facts.Finish(uid=ns+'sell_prey',
                           start=start.uid,
                           results={receiver_position.uid: RESULTS.SUCCESSED},
                           nesting=nesting,
                           description=u'Продать добычу',
                           require=[facts.LocatedIn(object=hero.uid, place=receiver_position.uid)],
                           actions=[facts.GiveReward(object=hero.uid, type='sell_prey'),
                                    facts.GivePower(object=receiver_position.uid, power=1)])

        line = [ start,
                  start_hunting,
                  sell_prey,

                  facts.Jump(state_from=start.uid, state_to=start_hunting.uid, start_actions=[facts.Message(type='move_to_hunt'),]),
                  facts.Jump(state_from=start_hunting.uid, state_to=hunt_loop[0].uid, start_actions=[facts.Message(type='start_track'),]),
                  facts.Jump(state_from=hunt_loop[-1].uid, state_to=sell_prey.uid, start_actions=[facts.Message(type='return_with_prey'),]),
                ]

        line.extend(hunt_loop)
        line.extend(participants)

        return line
