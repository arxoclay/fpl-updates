from unidecode import unidecode
import unittest

class Event:
    def __init__(self, name, player, quantity):
        self.name = name
        self.player = player
        self.quantity = quantity

    def __str__(self):
        return ', '.join([self.name, unidecode(self.player), str(self.quantity)])

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
    
    @staticmethod
    def GetEventUpdates(oldEvents, newEvents):

        result = []
        newSavesEvents = filter(lambda x: x.name == "Saves", newEvents)
        if len(newSavesEvents) > 0:
            oldSavesEvents = filter(lambda x: x.name == "Saves", oldEvents)
            if len(oldSavesEvents) > 0:
                for newSavesEvent in newSavesEvents:
                    oldSavesEvent = next((x for x in oldSavesEvents if x.player == newSavesEvent.player), None)
                    if not oldSavesEvent or (oldSavesEvent and oldSavesEvent.quantity/3 < newSavesEvent.quantity/3):
                        result.append(newSavesEvent)
            else:
                result.extend(newSavesEvents)
        result.extend(filter(lambda x: x not in oldEvents and x.name != "Saves", newEvents))
        return result

class TestEvent(unittest.TestCase):
    def test_onePlayerNoSavesIncrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 3)
        events = Event.GetEventUpdates([e1], [e2])
        self.assertEqual(len(events), 0)

    def test_onePlayerMinorSavesIncrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 5)
        events = Event.GetEventUpdates([e1], [e2])
        self.assertEqual(len(events), 0)

    def test_onePlayerSavesDecrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 2)
        events = Event.GetEventUpdates([e1], [e2])
        self.assertEqual(len(events), 0)

    def test_onePlayerValidSavesIncrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 6)
        events = Event.GetEventUpdates([e1], [e2])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], e2)

    def test_onePlayerValidSavesIncrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 14)
        events = Event.GetEventUpdates([e1], [e2])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], e2)

    def test_onePlayerNewSaves(self):
        e1 = Event("Foo", u"Cech", 0)
        e2 = Event("Saves", u"Cech", 14)
        events = Event.GetEventUpdates([e1], [e2])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], e2)

    def test_onePlayerOldSaves(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Foo", u"Cech", 14)
        events = Event.GetEventUpdates([e1], [e2])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "Foo")

    def test_twoPlayersNoSavesIncrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 3)
        e3 = Event("Saves", u"Guzan", 5)
        e4 = Event("Saves", u"Guzan", 5)
        events = Event.GetEventUpdates([e1, e3], [e2, e4])
        self.assertEqual(len(events), 0)

    def test_twoPlayersMinorSavesIncrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 5)
        e3 = Event("Saves", u"Guzan", 6)
        e4 = Event("Saves", u"Guzan", 8)
        events = Event.GetEventUpdates([e1, e3], [e2, e4])
        self.assertEqual(len(events), 0)

    def test_twoPlayersValidSavesIncrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 6)
        e3 = Event("Saves", u"Guzan", 7)
        e4 = Event("Saves", u"Guzan", 9)
        events = Event.GetEventUpdates([e1, e3], [e2, e4])
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0], e2)
        self.assertEqual(events[1], e4)

    def test_twoPlayersOnePlayerValidSavesIncrement(self):
        e1 = Event("Saves", u"Cech", 3)
        e2 = Event("Saves", u"Cech", 5)
        e3 = Event("Saves", u"Guzan", 7)
        e4 = Event("Saves", u"Guzan", 9)
        events = Event.GetEventUpdates([e1, e3], [e2, e4])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], e4)

    def test_twoPlayersNewSaves(self):
        e1 = Event("Foo", u"Cech", 0)
        e2 = Event("Saves", u"Cech", 14)
        e3 = Event("Saves", u"Guzan", 7)
        events = Event.GetEventUpdates([e1], [e2, e3])
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0], e2)
        self.assertEqual(events[1], e3)

    def test_twoPlayersOnePlayerNewSaves(self):
        e1 = Event("Saves", u"Cech", 14)
        e2 = Event("Saves", u"Cech", 14)
        e3 = Event("Saves", u"Guzan", 7)
        events = Event.GetEventUpdates([e1], [e2, e3])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], e3)

if __name__ == '__main__':
    unittest.main()
