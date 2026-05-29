import numpy as np
from collections import defaultdict
from .team import Team
from .match_simulator import MatchSimulator
from .group_stage import GroupStage
from .knockout_stage import KnockoutStage

class MonteCarloSimulation:
    """
    Ejecuta simulaciones Monte Carlo del torneo completo
    """
    
    def __init__(self, teams, num_simulations=2000):
        """
        Inicializa la simulación Monte Carlo
        
        Args:
            teams: Lista de equipos participantes
            num_simulations: Número de simulaciones a ejecutar
        """
        self.original_teams = teams
        self.num_simulations = num_simulations
        self.match_simulator = MatchSimulator()
        
        # Almacenar resultados
        self.results = {
            'champion': defaultdict(int),
            'runner_up': defaultdict(int),
            'third_place': defaultdict(int),
            'semifinalists': defaultdict(int),
            'quarterfinalists': defaultdict(int),
            'round_of_16': defaultdict(int),
            'group_stage_exit': defaultdict(int)
        }
    
    def deep_copy_teams(self):
        """
        Crea una copia profunda de los equipos para cada simulación
        """
        copied_teams = []
        for team in self.original_teams:
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
        return copied_teams
    
    def run_single_simulation(self):
        """
        Ejecuta una simulación completa del torneo
        """
        try:
            # Crear copia de equipos para esta simulación
            teams = self.deep_copy_teams()
            
            # Fase de grupos
            group_stage = GroupStage(teams, self.match_simulator)
            qualified_teams = group_stage.run_group_stage()
            
            # Verificar que tenemos suficientes equipos
            if len(qualified_teams) < 24:
                return None
            
            # Fase eliminatoria
            knockout = KnockoutStage(self.match_simulator)
            
            # Ronda de 32 (con 24 equipos de grupos, necesitamos 8 más)
            # Para simplificar, si tenemos 24, hacemos una ronda preliminar con los 16 mejores?
            # En realidad, en el mundial 2026: 24 clasificados + 8 mejores terceros = 32 equipos
            # Por simplicidad en la simulación, tomamos los mejores 32 por ranking si hay más de 32
            # o si hay menos, avanzan directamente a octavos
            
            if len(qualified_teams) >= 32:
                # Ronda de 32 normal
                round_32_winners = knockout.run_round_of_32(qualified_teams)
                next_round = round_32_winners
            else:
                # Si tenemos menos de 32, pasamos directamente a octavos
                next_round = qualified_teams
            
            # Octavos (necesitamos 16 equipos)
            if len(next_round) >= 16:
                round_16_winners = knockout.run_round_of_16(next_round)
            else:
                # Si no hay suficientes, avanzan los que hay
                round_16_winners = next_round
            
            if len(round_16_winners) < 8:
                return None
            
            # Cuartos (necesitamos 8 equipos)
            if len(round_16_winners) >= 8:
                quarter_winners = knockout.run_quarterfinals(round_16_winners)
            else:
                quarter_winners = round_16_winners
            
            if len(quarter_winners) < 4:
                return None
            
            # Semifinales (necesitamos 4 equipos)
            if len(quarter_winners) >= 4:
                semi_winners = knockout.run_semifinals(quarter_winners)
            else:
                semi_winners = quarter_winners
            
            if len(semi_winners) < 2:
                return None
            
            # Final
            finalist_a = semi_winners[0]
            finalist_b = semi_winners[1] if len(semi_winners) > 1 else semi_winners[0]
            
            champion, runner_up, _ = knockout.run_final(finalist_a, finalist_b)
            
            if champion is None:
                return None
            
            # Tercer lugar
            third_place, _ = knockout.run_third_place_match(finalist_a, finalist_b)
            if third_place is None:
                third_place = champion
            
            # Recolectar resultados
            return {
                'champion': champion.name,
                'runner_up': runner_up.name if runner_up else champion.name,
                'third_place': third_place.name,
                'semifinalists': set([t.name for t in semi_winners]),
                'quarterfinalists': set([t.name for t in quarter_winners]),
                'round_of_16': set([t.name for t in round_16_winners]),
                'group_stage_exit': set()
            }
        
        except Exception as e:
            return None
    
    def run_simulations(self):
        """
        Ejecuta todas las simulaciones Monte Carlo
        """
        print(f"Iniciando {self.num_simulations} simulaciones del Mundial FIFA 2026...")
        print("=" * 60)
        
        successful_sims = 0
        
        for sim_num in range(self.num_simulations):
            if (sim_num + 1) % 200 == 0:
                print(f"Progreso: {sim_num + 1}/{self.num_simulations} simulaciones completadas - {successful_sims} exitosas")
            
            result = self.run_single_simulation()
            
            if result is not None:
                successful_sims += 1
                
                # Actualizar resultados
                self.results['champion'][result['champion']] += 1
                self.results['runner_up'][result['runner_up']] += 1
                self.results['third_place'][result['third_place']] += 1
                
                for team in result['semifinalists']:
                    self.results['semifinalists'][team] += 1
                
                for team in result['quarterfinalists']:
                    self.results['quarterfinalists'][team] += 1
                
                for team in result['round_of_16']:
                    self.results['round_of_16'][team] += 1
        
        print(f"\n¡Simulación completada! {successful_sims}/{self.num_simulations} simulaciones exitosas.")
        print("=" * 60)
        
        return self.results
    
    def get_probabilities(self):
        """
        Calcula las probabilidades a partir de los resultados
        """
        total_sims = sum(self.results['champion'].values())
        if total_sims == 0:
            total_sims = 1
        
        probabilities = {}
        
        for stage in self.results:
            probabilities[stage] = {}
            for team, count in self.results[stage].items():
                prob = (count / total_sims) * 100
                probabilities[stage][team] = prob
        
        return probabilities
    
    def get_top_teams(self, stage='champion', n=10):
        """
        Obtiene los n mejores equipos en una etapa específica
        """
        total_sims = sum(self.results['champion'].values())
        if total_sims == 0:
            total_sims = 1
            
        sorted_teams = sorted(self.results[stage].items(), key=lambda x: x[1], reverse=True)
        return [(team, (count / total_sims) * 100) for team, count in sorted_teams[:n]]
    
    def print_summary(self):
        """
        Imprime un resumen de los resultados
        """
        total_sims = sum(self.results['champion'].values())
        if total_sims == 0:
            print("\n⚠️ No se pudieron completar simulaciones exitosas.")
            print("   Verifica los datos de los equipos e intenta nuevamente.")
            return
        
        probabilities = self.get_probabilities()
        
        print("\n" + "=" * 70)
        print("RESULTADOS DE LA SIMULACIÓN MONTE CARLO - MUNDIAL FIFA 2026")
        print(f"Basado en {total_sims} simulaciones exitosas")
        print("=" * 70)
        
        print("\n🏆 PROBABILIDADES DE CAMPEÓN (Top 10):")
        print("-" * 50)
        for i, (team, prob) in enumerate(self.get_top_teams('champion', 10), 1):
            if team:
                bar_length = int(prob / 2)
                bar = "█" * bar_length + "░" * (50 - bar_length)
                print(f"{i:2d}. {team:20s} {bar} {prob:5.2f}%")
        
        print("\n🥈 PROBABILIDADES DE SUBCAMPEÓN (Top 10):")
        print("-" * 50)
        for i, (team, prob) in enumerate(self.get_top_teams('runner_up', 10), 1):
            if team:
                print(f"{i:2d}. {team:20s} {prob:5.2f}%")
        
        print("\n🥉 PROBABILIDADES DE TERCER LUGAR (Top 10):")
        print("-" * 50)
        for i, (team, prob) in enumerate(self.get_top_teams('third_place', 10), 1):
            if team:
                print(f"{i:2d}. {team:20s} {prob:5.2f}%")
        
        print("\n📊 OTRAS ESTADÍSTICAS IMPORTANTES:")
        print("-" * 50)
        
        # Probabilidad de llegar a Semifinales
        print("\n🎯 Probabilidad de llegar a SEMIFINALES (Top 10):")
        for i, (team, prob) in enumerate(self.get_top_teams('semifinalists', 10), 1):
            if team:
                print(f"   {i:2d}. {team:20s} {prob:5.2f}%")
        
        # Probabilidad de llegar a Cuartos
        print("\n🎯 Probabilidad de llegar a CUARTOS DE FINAL (Top 10):")
        for i, (team, prob) in enumerate(self.get_top_teams('quarterfinalists', 10), 1):
            if team:
                print(f"   {i:2d}. {team:20s} {prob:5.2f}%")
        
        print("\n" + "=" * 70)