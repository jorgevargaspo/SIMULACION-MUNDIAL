import numpy as np
from itertools import combinations
from .match_simulator import MatchSimulator

class GroupStage:
    """
    Simula la fase de grupos del mundial
    """
    
    def __init__(self, teams, match_simulator):
        """
        Inicializa la fase de grupos
        
        Args:
            teams: Lista de 48 equipos
            match_simulator: Instancia de MatchSimulator
        """
        self.teams = teams
        self.match_simulator = match_simulator
        self.groups = self._create_groups()
        self.group_results = {}
    
    def _create_groups(self):
        """
        Crea 12 grupos de 4 equipos cada uno basado en el ranking
        """
        # Ordenar equipos por ranking
        sorted_teams = sorted(self.teams, key=lambda t: t.ranking)
        
        num_groups = 12
        teams_per_group = 4
        
        # Asegurar que tenemos suficientes equipos
        total_needed = num_groups * teams_per_group
        
        # Si no hay suficientes equipos, duplicar algunos (solo para simulación)
        if len(sorted_teams) < total_needed:
            # Completar con equipos repetidos (esto no debería pasar con 48 equipos)
            while len(sorted_teams) < total_needed:
                sorted_teams.extend(sorted_teams[:min(10, total_needed - len(sorted_teams))])
        
        # Usar solo los primeros 48 equipos
        sorted_teams = sorted_teams[:total_needed]
        
        groups = []
        
        # Distribución por bombos (como en el mundial real)
        for i in range(num_groups):
            groups.append([])
        
        # Asignar equipos a grupos (sistema de sorteo: 1 por bombo)
        for idx, team in enumerate(sorted_teams):
            group_idx = idx % num_groups
            groups[group_idx].append(team)
        
        # Verificar que cada grupo tenga exactamente 4 equipos
        for i in range(len(groups)):
            while len(groups[i]) < 4:
                # Si falta un equipo, añadir el mejor disponible no asignado
                available = [t for group in groups for t in group]
                all_teams = sorted_teams
                for team in all_teams:
                    if team not in available:
                        groups[i].append(team)
                        break
                else:
                    # Si no hay más, repetir un equipo
                    groups[i].append(sorted_teams[0])
        
        # Asignar nombres de grupos (A-L)
        group_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        groups_with_names = [(group_names[i], groups[i]) for i in range(num_groups)]
        
        return groups_with_names
    
    def simulate_group_matches(self, group_teams):
        """
        Simula todos los partidos de un grupo
        """
        # Reiniciar estadísticas para los equipos del grupo
        for team in group_teams:
            team.reset_tournament_stats()
        
        # Simular todos los partidos (cada equipo juega contra los otros 3)
        for team_a, team_b in combinations(group_teams, 2):
            result = self.match_simulator.get_match_result(team_a, team_b, neutral_ground=True)
            
            # Actualizar estadísticas
            if result['result'] == 'win':
                if result['winner'] == team_a.name:
                    team_a.group_points += 3
                else:
                    team_b.group_points += 3
            elif result['result'] == 'draw':
                team_a.group_points += 1
                team_b.group_points += 1
            
            # Actualizar goles
            team_a.group_goals_for += result['goals_a']
            team_a.group_goals_against += result['goals_b']
            team_b.group_goals_for += result['goals_b']
            team_b.group_goals_against += result['goals_a']
        
        # Calcular diferencia de goles
        for team in group_teams:
            team.group_goal_diff = team.group_goals_for - team.group_goals_against
        
        # Ordenar equipos por puntos, diferencia de goles, goles a favor
        sorted_teams = sorted(group_teams, 
                            key=lambda t: (t.group_points, t.group_goal_diff, 
                                         t.group_goals_for), 
                            reverse=True)
        
        # Asignar posiciones
        for idx, team in enumerate(sorted_teams):
            team.group_position = idx + 1
        
        return sorted_teams
    
    def run_group_stage(self):
        """
        Ejecuta toda la fase de grupos
        
        Returns:
            Lista de equipos clasificados (primeros y segundos de cada grupo)
        """
        qualified_teams = []
        self.group_results = {}
        
        for group_name, group_teams in self.groups:
            if len(group_teams) >= 2:  # Al menos 2 equipos para jugar
                sorted_teams = self.simulate_group_matches(group_teams)
                self.group_results[group_name] = sorted_teams
                
                # Los primeros y segundos de cada grupo clasifican
                qualified_teams.extend(sorted_teams[:2])
        
        return qualified_teams
    
    def get_group_summary(self):
        """
        Genera un resumen de la fase de grupos
        """
        summary = {}
        for group_name, teams in self.group_results.items():
            summary[group_name] = []
            for team in teams:
                summary[group_name].append({
                    'team': team.name,
                    'points': team.group_points,
                    'goals_for': team.group_goals_for,
                    'goals_against': team.group_goals_against,
                    'goal_diff': team.group_goal_diff,
                    'position': team.group_position
                })
        return summary