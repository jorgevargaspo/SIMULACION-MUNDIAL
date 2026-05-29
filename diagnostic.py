# diagnostic.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.team import Team
from src.match_simulator import MatchSimulator
from src.group_stage import GroupStage
from src.knockout_stage import KnockoutStage

def run_detailed_simulation():
    print("=== DIAGNÓSTICO COMPLETO DE SIMULACIÓN ===\n")
    
    # 1. Cargar equipos
    print("1. Cargando equipos...")
    teams = Team.load_from_csv('data/world_cup_teams.csv')
    print(f"   ✓ {len(teams)} equipos cargados\n")
    
    # 2. Crear copia
    print("2. Creando copia de equipos...")
    copied_teams = []
    for team in teams:
        copied_team = Team(
            name=team.name,
            ranking=team.ranking,
            elo_rating=team.elo_rating,
            wins=team.wins,
            losses=team.losses,
            draws=team.draws,
            goals_scored=team.goals_scored,
            goals_conceded=team.goals_conceded
        )
        copied_teams.append(copied_team)
    print(f"   ✓ {len(copied_teams)} equipos copiados\n")
    
    # 3. Fase de grupos
    print("3. Ejecutando fase de grupos...")
    match_sim = MatchSimulator()
    group_stage = GroupStage(copied_teams, match_sim)
    qualified_teams = group_stage.run_group_stage()
    print(f"   ✓ Equipos clasificados: {len(qualified_teams)}")
    
    if len(qualified_teams) == 0:
        print("   ❌ ERROR: No hay equipos clasificados")
        return
    
    # Mostrar algunos clasificados
    print(f"   Ejemplo de clasificados: {[t.name for t in qualified_teams[:5]]}\n")
    
    # 4. Ronda de 32
    print("4. Ejecutando ronda de 32...")
    knockout = KnockoutStage(match_sim)
    
    # Asegurar que tenemos exactamente 32 equipos (tomar los mejores 32 por ranking)
    if len(qualified_teams) > 32:
        qualified_teams = sorted(qualified_teams, key=lambda t: t.ranking)[:32]
        print(f"   ✓ Reducido a 32 equipos: {len(qualified_teams)}")
    
    round_32_winners = knockout.run_round_of_32(qualified_teams)
    print(f"   ✓ Ganadores ronda 32: {len(round_32_winners)}")
    
    if len(round_32_winners) < 16:
        print(f"   ❌ ERROR: Se esperaban 16 ganadores, se obtuvieron {len(round_32_winners)}")
        return
    
    # 5. Octavos
    print("\n5. Ejecutando octavos de final...")
    round_16_winners = knockout.run_round_of_16(round_32_winners)
    print(f"   ✓ Ganadores octavos: {len(round_16_winners)}")
    
    if len(round_16_winners) < 8:
        print(f"   ❌ ERROR: Se esperaban 8 ganadores, se obtuvieron {len(round_16_winners)}")
        return
    
    # 6. Cuartos
    print("\n6. Ejecutando cuartos de final...")
    quarter_winners = knockout.run_quarterfinals(round_16_winners)
    print(f"   ✓ Ganadores cuartos: {len(quarter_winners)}")
    
    if len(quarter_winners) < 4:
        print(f"   ❌ ERROR: Se esperaban 4 ganadores, se obtuvieron {len(quarter_winners)}")
        return
    
    # 7. Semifinales
    print("\n7. Ejecutando semifinales...")
    semi_winners = knockout.run_semifinals(quarter_winners)
    print(f"   ✓ Ganadores semifinales: {len(semi_winners)}")
    
    if len(semi_winners) < 2:
        print(f"   ❌ ERROR: Se esperaban 2 ganadores, se obtuvieron {len(semi_winners)}")
        return
    
    # 8. Final
    print("\n8. Ejecutando final...")
    finalist_a = semi_winners[0]
    finalist_b = semi_winners[1]
    print(f"   Finalistas: {finalist_a.name} vs {finalist_b.name}")
    
    champion, runner_up, _ = knockout.run_final(finalist_a, finalist_b)
    print(f"   ✓ CAMPEÓN: {champion.name}")
    
    # 9. Tercer lugar
    print("\n9. Ejecutando partido por tercer lugar...")
    third_place, _ = knockout.run_third_place_match(finalist_a, finalist_b)
    print(f"   ✓ Tercer lugar: {third_place.name}")
    
    print("\n" + "="*50)
    print("✅ ¡SIMULACIÓN COMPLETA EXITOSA!")
    print("="*50)
    
    return {
        'champion': champion.name,
        'runner_up': runner_up.name,
        'third_place': third_place.name
    }

if __name__ == "__main__":
    result = run_detailed_simulation()
    
    if result:
        print("\nResultados:")
        print(f"  Campeón: {result['champion']}")
        print(f"  Subcampeón: {result['runner_up']}")
        print(f"  3er Lugar: {result['third_place']}")
    else:
        print("\n❌ La simulación falló en algún paso")