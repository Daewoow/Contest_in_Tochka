#!/usr/bin/env python3
import sys
import heapq

costs = {
    'A': 1,
    'B': 10,
    'C': 100,
    'D': 1000
}

obj_room = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3
}

rooms_poses = (2, 4, 6, 8)
between_poses = (0, 1, 3, 5, 7, 9, 10)


class Parser:
    @staticmethod
    def parse(lines: list[str]) -> tuple[str, str, int]:
        room_depth = len(lines) - 3
        corridor = lines[1][1:12]

        room_indexes = [3, 5, 7, 9]
        objects_in_rooms = [[] for _ in range(4)]

        for i in range(room_depth):
            line = lines[2 + i]
            for obj in range(4):
                objects_in_rooms[obj].append(line[room_indexes[obj]])

        start_rooms = ""
        for room_list in objects_in_rooms:
            start_rooms += "".join(room_list)

        start_state = corridor + start_rooms

        final_corridor = "." * 11
        final_rooms = ""
        for i in range(4):
            final_type = 'A' if i == 0 else 'B' if i == 1 else 'C' if i == 2 else 'D'
            final_rooms += final_type * room_depth

        final_state = final_corridor + final_rooms
        return start_state, final_state, room_depth

    @staticmethod
    def deserialize(room_depth: int, room_idx: int, state: str):
        room_start_idx = 11 + room_idx * room_depth
        room_str = state[room_start_idx: room_start_idx + room_depth]
        return room_start_idx, room_str


class AStarHelper:
    @staticmethod
    def get_heuristic(state: str, room_depth: int) -> int:
        h = 0
        corridor = state[0:11]

        h += AStarHelper.add_corridor(corridor)

        for room_idx in range(4):
            target_door = rooms_poses[room_idx]
            start, room = Parser.deserialize(room_depth, room_idx, state)

            for depth_idx, obj in enumerate(room):
                if obj == '.':
                    continue

                needed_room_index = obj_room[obj]

                if room_idx == needed_room_index:
                    h += AStarHelper.add_self_room(depth_idx, obj, room_depth, room)
                else:
                    h += AStarHelper.add_foreign_room(needed_room_index, depth_idx, obj, target_door)

        return h

    @staticmethod
    def add_foreign_room(cur_room_index: int, depth_idx: int, obj: str, target_door: int):
        target_room_portal = rooms_poses[cur_room_index]
        cost_to_exit = (depth_idx + 1) * costs[obj]
        cost_hall_move = abs(target_door - target_room_portal) * costs[obj]
        cost_to_enter = 1 * costs[obj]
        return cost_to_exit + cost_hall_move + cost_to_enter

    @staticmethod
    def add_self_room(depth_idx: int, obj: str, room_depth: int, room: str):
        add_h = 0
        only_family = True
        for d in range(depth_idx + 1, room_depth):
            if room[d] != obj:
                only_family = False
                break
        if not only_family:
            cost_to_exit = (depth_idx + 1) * costs[obj]
            cost_to_exit_and_open = (2 + 1) * costs[obj]
            add_h += cost_to_exit + cost_to_exit_and_open
        return add_h

    @staticmethod
    def add_corridor(corridor: str) -> int:
        add_h = 0
        for hall_idx, obj in enumerate(corridor):
            if obj != '.':
                target_room = obj_room[obj]
                target_door = rooms_poses[target_room]
                cost_to_door = abs(hall_idx - target_door) * costs[obj]
                cost_to_enter = 1 * costs[obj]
                add_h += cost_to_door + cost_to_enter
        return add_h


class Solver:
    @staticmethod
    def make_step(state: str, room_depth: int) -> list[tuple[str, int]]:
        moves = []
        corridor = state[0:11]

        Solver.room_to_corridor(corridor, moves, room_depth, state)
        Solver.from_corridor_to_room(corridor, moves, room_depth, state)

        return moves

    @staticmethod
    def from_corridor_to_room(corridor: str, moves: list[tuple[str, int]], room_depth: int, state: str) -> None:
        for corridor_index, obj in enumerate(corridor):
            if obj == '.':
                continue

            target_room_idx = obj_room[obj]
            door = rooms_poses[target_room_idx]
            room_start_idx, target_room = Parser.deserialize(room_depth, target_room_idx, state)

            if not all(a == '.' or a == obj for a in target_room):
                continue

            if corridor_index < door:
                path_indexes = range(corridor_index + 1, door + 1)
            else:
                path_indexes = range(door, corridor_index)

            if not all(corridor[i] == '.' for i in path_indexes):
                continue

            target_depth = -1
            for d in range(room_depth - 1, -1, -1):
                if target_room[d] == '.':
                    target_depth = d
                    break

            if target_depth == -1:
                continue

            move_cost = Solver.make_cost(target_depth, door, corridor_index, obj)

            new_state_list = list(state)
            new_state_list[corridor_index] = '.'
            obj_index_to_room = room_start_idx + target_depth
            new_state_list[obj_index_to_room] = obj
            new_state = "".join(new_state_list)
            moves.append((new_state, move_cost))

    @staticmethod
    def make_cost(dest_depth: int, door: int, coridoor_index: int, obj: str):
        corridor_steps = abs(coridoor_index - door)
        room_steps = dest_depth + 1
        move_cost = (corridor_steps + room_steps) * costs[obj]
        return move_cost

    @staticmethod
    def room_to_corridor(corridor: str, moves: list, room_depth: int, state: str) -> None:
        for room_idx in range(4):
            target_type = 'A' if room_idx == 0 else 'B' if room_idx == 1 else 'C' if room_idx == 2 else 'D'
            room_start_idx, room_str = Parser.deserialize(room_depth, room_idx, state)

            if all(a == '.' or a == target_type for a in room_str):
                continue

            for depth_idx, cur_obj in enumerate(room_str):
                if cur_obj != '.':
                    steps_to_exit = depth_idx + 1
                    door = rooms_poses[room_idx]

                    for stop_pos in between_poses:
                        if stop_pos < door:
                            path_indexes = range(stop_pos, door)
                        else:
                            path_indexes = range(door + 1, stop_pos + 1)

                        if all(corridor[i] == '.' for i in path_indexes):
                            move_cost = (steps_to_exit + abs(stop_pos - door)) * costs[cur_obj]
                            new_state_list = list(state)
                            new_state_list[stop_pos] = cur_obj
                            char_index_in_room = room_start_idx + depth_idx
                            new_state_list[char_index_in_room] = '.'
                            new_state_str = "".join(new_state_list)
                            moves.append((new_state_str, move_cost))

                    break


def solve(lines: list[str]) -> int:
    start_state, target_state, room_depth = Parser.parse(lines)
    start_h = AStarHelper.get_heuristic(start_state, room_depth)
    queue = [(start_h, 0, start_state)]

    min_costs = {start_state: 0}

    while queue:
        f, g, current_state = heapq.heappop(queue)

        if current_state == target_state:
            return g

        if g > min_costs.get(current_state, float('inf')):
            continue

        for new_state, move_cost in Solver.make_step(current_state, room_depth):
            new_g_cost = g + move_cost
            if new_g_cost < min_costs.get(new_state, float('inf')):
                min_costs[new_state] = new_g_cost
                new_h_cost = AStarHelper.get_heuristic(new_state, room_depth)
                new_f_cost = new_g_cost + new_h_cost
                heapq.heappush(queue, (new_f_cost, new_g_cost, new_state))


def main():
    lines = []
    for line in sys.stdin:
        cleaned_line = line.rstrip('\n')
        if cleaned_line:
            lines.append(cleaned_line)

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()
