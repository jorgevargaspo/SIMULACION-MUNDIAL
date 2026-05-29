# debug_simulation.py - Script para depurar la simulación
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.team import Team
from src.match_simulator import MatchSimulator
from src.group_stage import GroupStage
from src.knockout_stage import KnockoutStage

def debug_single_simulation():
    print("=== DEBUG SIMULACIÓN ===")
    
    # Cargar equipos
    teams = Team.load_from_csv('data/world_cup_teams.csv')
    print(f"1. Equipos cargados: {len(teams)}")
    
    # Crear simulador
    match_sim = MatchSimulator()
    print("2. Simulador creado")
    
    # Fase de grupos
    print("3. Iniciando fase de grupos...")
    group_stage = GroupStage(teams, match_sim)
    print(f"   - Grupos creados: {len(group_stage.groups)}")
    
    for name, group in group_stage.groups:
        print(f"   - Grupo {name}: {len(group)} equipos")
        for team in group:
            print(f"     * {team.name}")
    
    qualified_teams = group_stage.run_group_stage()
    print(f"4. Equipos clasificados: {len(qualified_teams)}")
    
    if len(qualified_teams) < 2:
        print("❌ ERROR: No hay suficientes equipos clasificados")
        return
    
    # Fase eliminatoria
    print("5. Iniciando fase eliminatoria...")
    knockout = KnockoutStage(match_sim)
    
    # Ronda de 32
    round_32_winners, _ = knockout.run_round_of_32(qualified_teams)
    print(f"   - Ronda 32: {len(round_32_winners)} ganadores")
    
    if len(round_32_winners) < 2:
        print("❌ ERROR: No hay suficientes ganadores en ronda de 32")
        return
    
    # Octavos
    round_16_winners, _ = knockout.run_round_of_16(round_32_winners)
    print(f"   - Octavos: {len(round_16_winners)} ganadores")
    
    if len(round_16_winners) < 2:
        print("❌ ERROR: No hay suficientes ganadores en octavos")
        return
    
    # Cuartos
    quarter_winners, _ = knockout.run_quarterfinals(round_16_winners)
    print(f"   - Cuartos: {len(quarter_winners)} ganadores")
    
    if len(quarter_winners) < 2:
        print("❌ ERROR: No hay suficientes ganadores en cuartos")
        return
    
    # Semifinales
    semi_winners, _ = knockout.run_semifinals(quarter_winners)
    print(f"   - Semifinales: {len(semi_winners)} ganadores")
    
    if len(semi_winners) < 2:
        print("❌ ERROR: No hay suficientes ganadores en semifinales")
        return
    
    # Final
    finalist_a, finalist_b = semi_winners[0], semi_winners[1]
    print(f"   - Finalistas: {finalist_a.name} vs {finalist_b.name}")
    
    champion, runner_up, _ = knockout.run_final(finalist_a, finalist_b)
    print(f"6. ¡CAMPEÓN: {champion.name}!")
    
    return champion

if __name__ == "__main__":
    debug_single_simulation()