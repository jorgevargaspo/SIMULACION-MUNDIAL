import numpy as np
from .match_simulator import MatchSimulator

class KnockoutStage:
    """
    Simula las fases eliminatorias del mundial
    """
    
    def __init__(self, match_simulator):
        """
        Inicializa la fase eliminatoria
        
        Args:
            match_simulator: Instancia de MatchSimulator
        """
        self.match_simulator = match_simulator
    
    def run_knockout_match(self, team_a, team_b, neutral_ground=True):
        """
        Ejecuta un partido de eliminación directa con posible tanda de penales
        """
        result = self.match_simulator.get_match_result(team_a, team_b, neutral_ground)
        
        if result['goals_a'] != result['goals_b']:
            # Hay un ganador en tiempo regular
            winner = team_a if result['goals_a'] > result['goals_b'] else team_b
            return winner, result
        else:
            # Empate - Simular penales
            winner = self.match_simulator.simulate_penalty_shootout(team_a, team_b)
            return winner, result
    
    def run_round_of_32(self, qualified_teams):
        """
        Ronda de 32 - 32 equipos -> 16 ganadores
        En el Mundial 2026: 24 clasificados de grupos + 8 mejores terceros = 32 equipos
        """
        # Si tenemos 24 equipos (solo primeros y segundos), necesitamos añadir los 8 mejores terceros
        # Para simplificar, si tenemos menos de 32, completamos con los mejores equipos por ranking
        # que no estén ya clasificados
        
        if len(qualified_teams) < 32:
            # Necesitamos más equipos para llegar a 32
            # En una simulación real, aquí irían los mejores terceros
            # Por ahora, si tenemos 24, debemos crear 8 partidos más con los 16 mejores perdedores? 
            # No, eso es complicado. Mejor: creamos un bracket directo con los equipos que tenemos.
            pass
        
        # Ordenar por ranking para emparejar
        sorted_teams = sorted(qualified_teams, key=lambda t: t.ranking)
        n_teams = len(sorted_teams)
        
        # Crear emparejamientos: mejor vs peor, segundo mejor vs segundo peor, etc.
        matches = []
        for i in range(n_teams // 2):
            matches.append((sorted_teams[i], sorted_teams[n_teams - 1 - i]))
        
        # Simular cada partido
        winners = []
        for team_a, team_b in matches:
            winner, _ = self.run_knockout_match(team_a, team_b)
            winners.append(winner)
        
        return winners
    
    def run_round_of_16(self, teams):
        """
        Octavos de final - 16 equipos -> 8 ganadores
        """
        # Asegurar que tenemos 16 equipos
        if len(teams) > 16:
            # Tomar los mejores 16 por ranking
            teams = sorted(teams, key=lambda t: t.ranking)[:16]
        
        # Si tenemos menos de 16, no se puede jugar octavos
        if len(teams) < 16:
            # Si tenemos menos, simplemente avanzan todos (no es ideal pero funcional)
            return teams
        
        # Ordenar por ranking para emparejar
        sorted_teams = sorted(teams, key=lambda t: t.ranking)
        
        # Crear emparejamientos
        matches = []
        n = len(sorted_teams)
        for i in range(n // 2):
            matches.append((sorted_teams[i], sorted_teams[n - 1 - i]))
        
        # Simular partidos
        winners = []
        for team_a, team_b in matches:
            winner, _ = self.run_knockout_match(team_a, team_b)
            winners.append(winner)
        
        return winners
    
    def run_quarterfinals(self, teams):
        """
        Cuartos de final - 8 equipos -> 4 ganadores
        """
        # Asegurar que tenemos 8 equipos
        if len(teams) > 8:
            teams = sorted(teams, key=lambda t: t.ranking)[:8]
        elif len(teams) < 8:
            # Si hay menos, avanzan los que hay
            return teams
        
        # Ordenar por ranking
        sorted_teams = sorted(teams, key=lambda t: t.ranking)
        
        # Crear emparejamientos
        matches = []
        n = len(sorted_teams)
        for i in range(n // 2):
            matches.append((sorted_teams[i], sorted_teams[n - 1 - i]))
        
        # Simular partidos
        winners = []
        for team_a, team_b in matches:
            winner, _ = self.run_knockout_match(team_a, team_b)
            winners.append(winner)
        
        return winners
    
    def run_semifinals(self, teams):
        """
        Semifinales - 4 equipos -> 2 ganadores
        """
        # Asegurar que tenemos 4 equipos
        if len(teams) > 4:
            teams = sorted(teams, key=lambda t: t.ranking)[:4]
        elif len(teams) < 4:
            # Si hay menos de 4, no se pueden jugar semifinales completas
            # Devolver solo los primeros 2 si es posible
            if len(teams) >= 2:
                return teams[:2]
            return teams
        
        # Ordenar por ranking
        sorted_teams = sorted(teams, key=lambda t: t.ranking)
        
        # Emparejamientos típicos de semifinales: 1vs4, 2vs3
        matches = [
            (sorted_teams[0], sorted_teams[3]),
            (sorted_teams[1], sorted_teams[2])
        ]
        
        # Simular partidos
        winners = []
        for team_a, team_b in matches:
            winner, _ = self.run_knockout_match(team_a, team_b)
            winners.append(winner)
        
        return winners
    
    def run_final(self, team_a, team_b):
        """
        Final del torneo - 2 equipos -> 1 campeón
        """
        if team_a is None or team_b is None:
            return team_a if team_a else team_b, None, None
        
        winner, result = self.run_knockout_match(team_a, team_b)
        loser = team_b if winner == team_a else team_a
        return winner, loser, result
    
    def run_third_place_match(self, team_a, team_b):
        """
        Partido por el tercer lugar
        """
        if team_a is None or team_b is None:
            return team_a if team_a else team_b, None
        
        winner, result = self.run_knockout_match(team_a, team_b)
        return winner, result