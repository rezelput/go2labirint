import math

import agent_navigation
import geometry

MAX_AGENT_SPEED = 3.0


class MakeLab:
    def __init__(self, agent, walls, exit_point, exit_range=5.0):
        self.walls = walls
        self.exit_point = exit_point
        self.exit_range = exit_range
        self.agent = agent
        self.exit_found = False
        self.initial_distance = self.agent_distance_to_exit()

        self.update_rangefinder_sensors()
        self.update_radars()

    def agent_distance_to_exit(self):
        return self.agent.location.distance(self.exit_point)

    def test_wall_collision(self, loc):
        for w in self.walls:
            if w.distance(loc) < self.agent.radius:
                return True

        return False

    def create_net_inputs(self):
        inputs = []
        for ri in self.agent.range_finders:
            inputs.append(ri)

        for rs in self.agent.radar:
            inputs.append(rs)

        return inputs

    def apply_control_signals(self, control_signals):
        self.agent.angular_vel += (control_signals[0] - 0.5)
        self.agent.speed += (control_signals[1] - 0.5)

        if self.agent.speed > MAX_AGENT_SPEED:
            self.agent.speed = MAX_AGENT_SPEED

        if self.agent.speed < -MAX_AGENT_SPEED:
            self.agent.speed = -MAX_AGENT_SPEED

        if self.agent.angular_vel > MAX_AGENT_SPEED:
            self.agent.angular_vel = MAX_AGENT_SPEED

        if self.agent.angular_vel < -MAX_AGENT_SPEED:
            self.agent.angular_vel = -MAX_AGENT_SPEED

    def update_rangefinder_sensors(self):
        for i, angle in enumerate(self.agent.range_finder_angles):
            rad = geometry.deg_to_rad(angle)
            projection_point = geometry.Point(
                x=self.agent.location.x + math.cos(rad) * self.agent.range_finder_range,
                y=self.agent.location.y + math.sin(rad) * self.agent.range_finder_range
            )
            projection_point.rotate(self.agent.heading, self.agent.location)
            projection_line = geometry.Line(
                a=self.agent.location,
                b=projection_point
            )

            min_range = self.agent.range_finder_range

            for wall in self.walls:
                found, intersection = wall.intersection(projection_line)
                if found:
                    found_range = intersection.distance(self.agent.location)
                    if found_range < min_range:
                        min_range = found_range

            self.agent.range_finders[i] = min_range

    def update_radars(self):
        target = geometry.Point(self.exit_point.x, self.exit_point.y)
        target.rotate(self.agent.heading, self.agent.location)
        target.x -= self.agent.location.x
        target.y -= self.agent.location.y
        angle = target.angle()
        for i, r_angles in enumerate(self.agent.radar_angles):
            self.agent.radar[i] = 0.0

            if (angle >= r_angles[0] and angle < r_angles[1]) or (
                    angle + 360 >= r_angles[0] and angle + 360 < r_angles[1]):
                self.agent.radar[i] = 1.0

    def update(self, control_signals):

        if self.exit_found:
            return True

        self.apply_control_signals(control_signals)

        vx = math.cos(geometry.deg_to_rad(self.agent.heading)) * self.agent.speed
        vy = math.sin(geometry.deg_to_rad(self.agent.heading)) * self.agent.speed

        self.agent.heading += self.agent.angular_vel

        if self.agent.heading > 360:
            self.agent.heading -= 360
        elif self.agent.heading < 0:
            self.agent.heading += 360

        new_loc = geometry.Point(
            x=self.agent.location.x + vx,
            y=self.agent.location.y + vy
        )

        if not self.test_wall_collision(new_loc):
            self.agent.location = new_loc

        self.update_rangefinder_sensors()
        self.update_radars()

        distance = self.agent_distance_to_exit()
        self.exit_found = (distance < self.exit_range)
        return self.exit_found

    def __str__(self):

        str = "MAZE\nAgent at: (%.1f, %.1f)" % (self.agent.location.x, self.agent.location.y)
        str += "\nExit  at: (%.1f, %.1f), exit range: %.1f" % (self.exit_point.x, self.exit_point.y, self.exit_range)
        str += "\nWalls [%d]" % len(self.walls)
        for w in self.walls:
            str += "\n\t%s" % w
        return str


def read_environment(file_path):
    num_lines, index = -1, 0
    walls = []
    maze_agent, maze_exit = None, None
    with open(file_path, 'r') as file:
        for line in file.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            if index == 0:
                num_lines = int(line)
            elif index == 1:
                loc = geometry.read_point(line)
                maze_agent = agent_navigation.Agent(location=loc)
            elif index == 2:
                maze_agent.heading = float(line)
            elif index == 3:
                maze_exit = geometry.read_point(line)
            else:
                wall = geometry.read_line(line)
                walls.append(wall)
            index += 1

    assert len(walls) == num_lines

    print("Maze environment configured successfully from the file: %s" % file_path)
    # create and return the maze environment
    return MakeLab(agent=maze_agent, walls=walls, exit_point=maze_exit)


def maze_simulation_evaluate(env, net, time_steps):
    for i in range(time_steps):
        if maze_simulation_step(env, net):
            print("Maze solved in %d steps" % (i + 1))
            return 1.0
    fitness = env.agent_distance_to_exit()
    fitness = (env.initial_distance - fitness) / env.initial_distance
    if fitness <= 0.01:
        fitness = 0.01

    return fitness


def maze_simulation_step(env, net):
    inputs = env.create_net_inputs()
    output = net.activate(inputs)
    return env.update(output)
