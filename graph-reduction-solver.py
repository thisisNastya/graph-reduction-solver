import sys

def check_for_cycles(num_nodes, edges):
    adj = {i: [] for i in range(1, num_nodes + 1)}
    for u, v, w in edges:
        adj[u].append(v)

    visited = {i: 0 for i in range(1, num_nodes + 1)} 

    def dfs(v):
        visited[v] = 1 
        for u in adj[v]:
            if visited[u] == 1: 
                return True
            if visited[u] == 0:
                if dfs(u):
                    return True
        visited[v] = 2 
        return False

    for i in range(1, num_nodes + 1):
        if visited[i] == 0:
            if dfs(i):
                return True
    return False

def solve_by_substitution(num_nodes, edges, source_node=1):
    print("\n==================================================")
    print("РЕЖИМ 1: Метод прямой подстановки (Топологический расчет)")
    print("==================================================")
    
    in_degree = {i: 0 for i in range(1, num_nodes + 1)}
    adj = {i: [] for i in range(1, num_nodes + 1)}
    for u, v, w in edges:
        adj[u].append((v, w))
        in_degree[v] += 1

    X = {i: 0.0 for i in range(1, num_nodes + 1)}
    X[source_node] = 1.0
    
    # Словарь для хранения истории того, что пришло в каждую вершину
    calc_history = {i: [] for i in range(1, num_nodes + 1)}

    queue = [i for i in range(1, num_nodes + 1) if in_degree[i] == 0]
    
    if source_node not in queue:
        queue.append(source_node)

    print(f"Известно по условию: X{source_node} = 1.0\n")

    while queue:
        u = queue.pop(0)
        
        for v, w in adj[u]:
            added_value = X[u] * w
            X[v] += added_value
            
            # Сохраняем информацию о слагаемом
            calc_history[v].append({
                'node': u,
                'weight': w,
                'u_val': X[u]
            })
            
            in_degree[v] -= 1
            # Когда все входящие стрелки в вершину 'v' обработаны
            if in_degree[v] == 0:
                queue.append(v)
                
                print(f"---> ШАГ: Считаем вершину X{v}")
                formula_parts = []
                subst_parts = []
                
                # Формируем строки для вывода
                for item in calc_history[v]:
                    formula_parts.append(f"{item['weight']:g}*X{item['node']}")
                    
                    # Если значение отрицательное, берем его в скобки для красоты
                    u_val_str = f"({item['u_val']:g})" if item['u_val'] < 0 else f"{item['u_val']:g}"
                    subst_parts.append(f"{item['weight']:g} * {u_val_str}")
                    
                formula_str = " + ".join(formula_parts)
                subst_str = " + ".join(subst_parts)
                
                print(f"Формула:     X{v} = {formula_str}")
                print(f"Подстановка: X{v} = {subst_str} = {X[v]:.4g}\n")

    print("==================================================")
    print("ИТОГОВЫЙ ОТВЕТ (Прямая подстановка):")
    print("==================================================")
    for i in range(1, num_nodes + 1):
        print(f"X{i} = {X[i]:.6g}")

def solve_by_elimination(num_nodes, edges, source_node=1, target_node=2):
    print("\n==================================================")
    print("РЕЖИМ 2: Метод последовательного исключения вершин")
    print("==================================================")

    nodes = set(range(1, num_nodes + 1))
    adj = {}
    for u, v, w in edges:
        if u not in adj: adj[u] = {}
        if v not in adj[u]: adj[u][v] = 0.0
        adj[u][v] += w

    nodes_to_eliminate = [n for n in nodes if n != source_node and n != target_node]
    nodes_to_eliminate.sort(reverse=True)
    equations = {}

    print("--- ЭТАП 1: ПРЯМОЙ ХОД (Исключение вершин) ---")
    for k in nodes_to_eliminate:
        print(f"\n---> ШАГ: Исключаем вершину X{k}")
        
        incoming = {u: adj[u][k] for u in nodes if u in adj and k in adj[u] and u != k}
        outgoing = {v: adj[k][v] for v in nodes if k in adj and v in adj[k] and v != k}
        self_loop = adj.get(k, {}).get(k, 0.0)

        denom = 1.0 - self_loop
        if denom == 0:
            print(f"КРИТИЧЕСКАЯ ОШИБКА: Петля на вершине X{k} равна 1. Деление на ноль!")
            return

        eq_coeffs = {}
        eq_str_parts = []
        for u, w_in in incoming.items():
            coeff = w_in / denom
            eq_coeffs[u] = coeff
            eq_str_parts.append(f"{coeff:.4g}*X{u}")
        
        equations[k] = eq_coeffs
        eq_str = " + ".join(eq_str_parts) if eq_str_parts else "0"
        
        if self_loop != 0:
            print(f"Запоминаем формулу (с учетом петли {self_loop}): X{k} = {eq_str}")
        else:
            print(f"Запоминаем формулу: X{k} = {eq_str}")

        for u, w_in in incoming.items():
            for v, w_out in outgoing.items():
                delta = (w_in * w_out) / denom
                
                if u not in adj: adj[u] = {}
                old_weight = adj[u].get(v, 0.0)
                adj[u][v] = old_weight + delta
                
                print(f"  [+] Обнаружен путь через удаляемую вершину: X{u} -> X{k} -> X{v}")
                if self_loop == 0:
                    print(f"      Расчет новой дуги: {w_in:.4g} (входящая) * {w_out:.4g} (исходящая) = {delta:.4g}")
                else:
                    print(f"      Расчет новой дуги с учетом петли: ({w_in:.4g} * {w_out:.4g}) / (1 - {self_loop:.4g}) = {delta:.4g}")
                
                print(f"      Обновляем прямую дугу X{u} -> X{v}: было {old_weight:.4g}, добавлено {delta:.4g}, стало {adj[u][v]:.4g}")

        if k in adj: del adj[k]
        for u in list(adj.keys()):
            if k in adj[u]: del adj[u][k]
        nodes.remove(k)

        print("\n  Текущие дуги в графе после шага:")
        for u_ in sorted(adj.keys()):
            for v_, w_ in adj[u_].items():
                if w_ != 0:
                    print(f"    X{u_} -> X{v_}  (вес: {w_:.4g})")

    print(f"\n--- РАСЧЕТ ФИНАЛЬНОЙ ВЕРШИНЫ X{target_node} ---")
    X = {source_node: 1.0}
    print(f"Известно по условию: X{source_node} = 1.0")

    incoming_to_target = {u: adj[u][target_node] for u in nodes if u in adj and target_node in adj[u] and u != target_node}
    target_loop = adj.get(target_node, {}).get(target_node, 0.0)
    target_denom = 1.0 - target_loop

    val_target = 0
    for u, w in incoming_to_target.items():
        val_target += (w / target_denom) * X[u]

    X[target_node] = val_target
    print(f"РЕЗУЛЬТАТ: X{target_node} = {X[target_node]:.4g}")

    print("\n--- ЭТАП 2: ОБРАТНЫЙ ХОД (Подстановка) ---")
    for k in reversed(nodes_to_eliminate):
        val = 0
        calc_str_parts = []
        for u, coeff in equations[k].items():
            val += coeff * X[u]
            u_val_str = f"({X[u]:.4g})" if X[u] < 0 else f"{X[u]:.4g}"
            calc_str_parts.append(f"{coeff:.4g} * {u_val_str}")
            
        X[k] = val
        calc_str = " + ".join(calc_str_parts) if calc_str_parts else "0"
        print(f"Считаем X{k}: {calc_str} = {X[k]:.4g}")

    print("\n==================================================")
    print("ИТОГОВЫЙ ОТВЕТ (Исключение вершин):")
    print("==================================================")
    for i in range(1, num_nodes + 1):
        if i in X: print(f"X{i} = {X[i]:.6g}")
        else: print(f"X{i} = 0")


def main():
    print("=== Универсальный Калькулятор Графов ===")
    while True:
        try:
            num_nodes = int(input("Введите количество вершин в графе: "))
            if num_nodes < 2:
                print("Минимум 2 вершины.")
                continue
            break
        except ValueError:
            print("Введите целое число.")

    print("\n--- Ввод связей ---")
    print("Формат: ОТКУДА КУДА ВЕС. Пример: 1 3 -2 (Enter для завершения)")

    edges = []
    while True:
        line = input("Связь: ").strip()
        if not line: break
        parts = line.split()
        if len(parts) != 3:
            print("Нужно 3 числа.")
            continue
        try:
            u, v, w = int(parts[0]), int(parts[1]), float(parts[2])
            if u < 1 or u > num_nodes or v < 1 or v > num_nodes:
                print(f"Вершины должны быть от 1 до {num_nodes}.")
                continue
            edges.append((u, v, w))
        except ValueError:
            print("Ошибка формата.")

    if not edges: return

    print("\n[Анализ графа...]")
    has_cycles = check_for_cycles(num_nodes, edges)
    
    if has_cycles:
        print("ВНИМАНИЕ: В графе обнаружены циклы (обратные связи или петли).")
        print("Метод прямой подстановки НЕ ПРИМЕНИМ.")
    else:
        print("Граф ацикличный (без петель и обратных связей). Доступны все методы.")

    print("\nВЫБЕРИТЕ РЕЖИМ РЕШЕНИЯ:")
    if not has_cycles:
        print("1 - Метод прямой подстановки (идет от входа к выходу)")
    print("2 - Метод последовательного исключения вершин (универсальный)")

    while True:
        choice = input("Ваш выбор: ").strip()
        if choice == '1' and not has_cycles:
            solve_by_substitution(num_nodes, edges)
            break
        elif choice == '2':
            solve_by_elimination(num_nodes, edges)
            break
        elif choice == '1' and has_cycles:
            print("Ошибка: Граф содержит циклы. Выберите режим 2.")
        else:
            print("Неверный выбор. Введите 1 или 2.")

if __name__ == "__main__":
    main()