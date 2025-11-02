#!/usr/bin/env python3
import sys
from collections import defaultdict, deque


class GraphHelper:
    @staticmethod
    def get_graph(edges: list[tuple[str, str]]) -> tuple[set[tuple[str, str]], set[str], defaultdict[str, set[str]]]:
        """
        Просто инициализация графа

        Args:
            edges: рёбра

        Returns:
            Доступные шлюзы, все шлюзы, граф
        """

        graph = defaultdict(set)
        gateways = set()
        available_gateways = set()

        for u, v in edges:
            graph[u].add(v)
            graph[v].add(u)

            is_u_gw = u.isupper()
            is_v_gw = v.isupper()

            if is_u_gw:
                gateways.add(u)
            if is_v_gw:
                gateways.add(v)

            if is_u_gw and not is_v_gw:
                available_gateways.add((u, v))
            elif is_v_gw and not is_u_gw:
                available_gateways.add((v, u))

        return available_gateways, gateways, graph

    @staticmethod
    def bfs(start_node: str, graph: dict[str, set[str]]) -> dict[str, int]:
        """Выполняет поиск в ширину, возвращая расстояния от start_node
        Args:
            start_node: начальная точка
            graph: граф сети

        Returns:
            словарь расстояний
        """

        distances = {start_node: 0}
        queue = deque([start_node])

        while queue:
            current = queue.popleft()
            for neighbor in graph[current]:
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    @staticmethod
    def close_edge(available_gateways: set[tuple[str, str]], edge_to_close: tuple[str, str],
                   graph: dict[str, set[str]], result: list[str]) -> None:
        """
        Закрываем ребро

        Args:
            available_gateways: все шлюзы, к которым есть проход
            edge_to_close: ребро, которое закрываем
            graph: граф
            result: результат
        """
        g, n = edge_to_close
        result.append(f"{g}-{n}")
        graph[g].remove(n)
        graph[n].remove(g)
        available_gateways.remove(edge_to_close)


class VirusHelper:
    @staticmethod
    def get_virus_move(start: str, graph: dict[str, set[str]], gateways: set[str]) \
            -> tuple[str | None, str | None, float | int]:
        """
        Считаем следующий шаг вируса: целевой шлюз, следующий узел и расстояние.

        Args:
            start: откуда идём
            graph: граф сети
            gateways: шлюзы

        Returns:
            Следующий по плану щлюз, следующий по плану узел и расстояние до ближайшего шлюза
        """

        distances_from_start = GraphHelper.bfs(start, graph)

        min_dist, target_gateways = VirusHelper.get_virus_nearest_gateway(distances_from_start, gateways)
        if min_dist == float('inf'):
            return None, None, float("inf")

        target_gateway = target_gateways[0]

        return (target_gateway, VirusHelper.get_virus_next_node(gateways, graph, min_dist, start, target_gateway),
                min_dist)

    @staticmethod
    def get_virus_next_node(gateways: set[str], graph: dict[str, set[str]], min_dist: float | int,
                            start: str, target_gateway: str):
        """
        Возвращает следующий узел в проходе вируса

        Args:
            gateways: шлюзы
            graph: граф сети
            min_dist: расстояние до ближайшего шлюза
            start: стартовая точка
            target_gateway: целевой шлюз

        Returns:
            следующий узел
        """

        distances_to_target = GraphHelper.bfs(target_gateway, graph)
        next_node = None

        for neighbor in sorted(list(graph[start])):
            if neighbor in gateways:
                continue

            dist_to_target = distances_to_target.get(neighbor, float('inf'))
            if dist_to_target == min_dist - 1:
                next_node = neighbor
                break
        return next_node

    @staticmethod
    def get_virus_nearest_gateway(distances_from_start: dict[str, int], gateways: set[str]) \
            -> tuple[float | int, list[str]]:
        """
        Возвращает ближайший шлюз от вируса

        Args:
            distances_from_start: расстояние от вируса
            gateways: шлюзы

        Returns:
            минимальное расстояние до шлюза и список шлюзов с таким расстоянием (если что,
            потом выберем лексикографически наименьший)
        """
        min_dist = float('inf')
        target_gateways = []

        for g in sorted(list(gateways)):
            dist = distances_from_start.get(g, float('inf'))
            if dist < min_dist:
                min_dist = dist
                target_gateways = [g]
            elif dist == min_dist:
                target_gateways.append(g)

        return min_dist, target_gateways

    @staticmethod
    def check_virus_one_step_to_win(gateways: set[str], graph: dict[str, set[str]], next_node: str) \
            -> list[tuple[str, str]]:
        """
        Список шлюзов, к которым вирус будет в одном шаге при каком-то раскладе

        Args:
            gateways: шлюзы
            graph: граф
            next_node: следующий узел

        Returns:
            опасные шлюзы
        """

        pre_dangerous_gateways = []
        if next_node:
            for neighbor in graph[next_node]:
                if neighbor in gateways:
                    pre_dangerous_gateways.append((neighbor, next_node))
        return pre_dangerous_gateways

    @staticmethod
    def check_virus_win_now(gateways: set[str], graph: dict[str, set[str]], virus_pos: str) -> list[tuple[str, str]]:
        """
        Проверяем, в какие шлюзы вирус может дойти прямо сейчас

        Args:
            gateways: все шлюзы
            graph: граф
            virus_pos: позиция вируса

        Returns:
            Шлюзы, которые под угрозой, так скажем
        """

        dangerous_gateways = []
        for neighbor in graph[virus_pos]:
            if neighbor in gateways:
                dangerous_gateways.append((neighbor, virus_pos))
        return dangerous_gateways


def solve(edges: list[tuple[str, str]]) -> list[str]:
    """
    Решение задачи об изоляции вируса

    Args:
        edges: список коридоров в формате (узел1, узел2)

    Returns:
        список отключаемых коридоров в формате "Шлюз-узел"
    """

    available_gateways, gateways, graph = GraphHelper.get_graph(edges)

    virus_pos = 'a'
    result = []

    while True:
        danger_gateways = VirusHelper.check_virus_win_now(gateways, graph, virus_pos)

        if danger_gateways:
            edge_to_close = sorted(danger_gateways)[0]
        else:
            target, next_node, min_dist = VirusHelper.get_virus_move(virus_pos, graph, gateways)

            if target is None:
                break

            pre_dangerous_gateways = VirusHelper.check_virus_one_step_to_win(gateways, graph, next_node)

            if pre_dangerous_gateways:
                next_virus_gateway = (target, next_node)

                if next_virus_gateway in pre_dangerous_gateways:
                    edge_to_close = next_virus_gateway
                else:
                    edge_to_close = sorted(pre_dangerous_gateways)[0]
            else:
                if not available_gateways:
                    break

                edge_to_close = sorted(list(available_gateways))[0]

        GraphHelper.close_edge(available_gateways, edge_to_close, graph, result)

        virus_win_now = VirusHelper.check_virus_win_now(gateways, graph, virus_pos)

        if virus_win_now:
            break
        else:
            new_virus_target, new_virus_pos, new_min_dist = VirusHelper.get_virus_move(virus_pos, graph, gateways)

            if new_virus_pos is None:
                break

            virus_pos = new_virus_pos

    return result


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()
