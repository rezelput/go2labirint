import pickle
class Agent:
    def __init__(self, location, heading=0, speed=0,
                 angular_vel=0, radius=8.0,
                 range_finder_range=100.0):
        self.heading = heading
        self.speed = speed
        self.angular_vel = angular_vel
        self.radius = radius
        self.range_finder_range = range_finder_range
        self.location = location
        self.range_finder_angels = [-90.0, -45.0, 0.0, 45.0, 90.0, -180.0]
        self.radar_angles = [(315.0, 405.0), (45.0, 135.0),
                             (135.0, 225.0), (225.0, 315.0)]
        self.range_finders = [None] * len(self.range_finder_angles)
        self.radar = [None] * len(self.radar_angles)

        class AgentRecord:
            def __init__(self, generation, agent_id):
                self.generation = generation
                self.agent_id = agent_id
                self.x = -1
                self.y = -1
                self.fitness = -1
                self.hit_exit = False
                self.species_id = -1
                self.species_age = -1

        class AgentRecordStore:
            def __init__(self):
                self.records = []

            def add_record(self, record):
                self.records.append(record)

            def load(self, file):
                with open(file, 'rb') as dump_file:
                    self.records = pickle.load(dump_file)

            def dump(self, file):
                with open(file, 'wb') as dump_file:
                    pickle.dump(self.records, dump_file)