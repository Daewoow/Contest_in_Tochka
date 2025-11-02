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
            Доступные шлюзы (кортежи 'Шлюз-узел'), все шлюзы (set), граф
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
        """
        Поиск в ширину
        Args:
            start_node: стартовая точка
            graph: граф
        Returns:
            словарь расстояний
        """

        distances = {start_node: 0}
        queue = deque([start_node])

        while queue:
            current = queue.popleft()
            for neighbor in sorted(list(graph[current])):
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
            available_gateways: доступные шлюзы для вируса
            edge_to_close: ребро для щакрытия
            graph: граф
            result: результат
        """
        g, n = edge_to_close
        result.append(f"{g}-{n}")

        if n in graph[g]:
            graph[g].remove(n)
        if g in graph[n]:
            graph[n].remove(g)

        if edge_to_close in available_gateways:
            available_gateways.remove(edge_to_close)


class VirusHelper:
    @staticmethod
    def get_virus_move(start: str, graph: dict[str, set[str]], gateways: set[str]) \
            -> tuple[str | None, str | None, float | int]:
        """
        Считаем следующий шаг вируса: целевой шлюз, следующий узел и расстояние.

        Args:
            start: стартовая точка
            graph: граф
            gateways: все шлюзы

        Returns:
            целевой шлюз, следующий узел и расстояние
        """

        distances_from_start = GraphHelper.bfs(start, graph)

        min_dist, target_gateways = VirusHelper.get_virus_nearest_gateway(distances_from_start, gateways)
        if min_dist == float('inf'):
            return None, None, float("inf")

        target_gateway = sorted(target_gateways)[0]

        if min_dist == 1:
            return target_gateway, None, min_dist

        return (target_gateway, VirusHelper.get_virus_next_node(gateways, graph, min_dist, start, target_gateway),
                min_dist)

    @staticmethod
    def get_virus_next_node(gateways: set[str], graph: dict[str, set[str]], min_dist: float | int,
                            start: str, target_gateway: str):
        """
        Возвращает следующий узел в проходе вируса

        Args:
            gateways: все шлюзы
            graph: граф
            min_dist: минимальное расстояние до какого-нибудь шлюза
            start: стартовая точка
            target_gateway: целевой шлюз
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
            distances_from_start: словарь расстояний от стартовой точки
            gateways: все шлюзы

        Returns:
            Tuple шлюзов с минимальным расстоянием (если что возьмём минимальный)
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
    def check_virus_win_now(gateways: set[str], graph: dict[str, set[str]], virus_pos: str) -> list[tuple[str, str]]:
        """
        Проверяем, в какие шлюзы вирус может дойти прямо сейчас

        Args:
            gateways: шлюзы
            graph: граф
            virus_pos: позиция вируса

        Returns:
            Список шлюзов, куда может дойти вирус сейчас
        """
        dangerous_gateways = []
        for neighbor in sorted(list(graph[virus_pos])):
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

    while available_gateways:
        danger_gateways = VirusHelper.check_virus_win_now(gateways, graph, virus_pos)

        if danger_gateways:
            edge_to_close = sorted(danger_gateways)[0]
        else:
            if not available_gateways:
                break
            edge_to_close = sorted(list(available_gateways))[0]

        GraphHelper.close_edge(available_gateways, edge_to_close, graph, result)
        next_virus_target, next_virus_node, next_min_dist = VirusHelper.get_virus_move(virus_pos, graph, gateways)

        if next_virus_target is None:
            break

        if next_virus_node is not None:
            virus_pos = next_virus_node

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
