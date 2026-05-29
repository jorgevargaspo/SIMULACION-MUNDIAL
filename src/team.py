import pandas as pd
import numpy as np

class Team:
    """
    Clase que representa una selección nacional de fútbol
    """
    
    def __init__(self, name, ranking, elo_rating, wins, losses, draws, 
                 goals_scored, goals_conceded):
        self.name = name
        self.ranking = ranking
        self.elo_rating = elo_rating
        self.wins = wins
        self.losses = losses
        self.draws = draws
        self.goals_scored = goals_scored
        self.goals_conceded = goals_conceded
        
        # Estadísticas para la simulación
        self.total_matches = wins + losses + draws
        self.attack_strength = None
        self.defense_strength = None
        self.overall_strength = None
        
        # Estadísticas del torneo
        self.group_points = 0
        self.group_goals_for = 0
        self.group_goals_against = 0
        self.group_goal_diff = 0
        self.group_position = 0
        
        self._calculate_strengths()
    
    def _calculate_strengths(self):
        """
        Calcula las fortalezas ofensiva, defensiva y general del equipo
        """
        # Fortaleza ofensiva (goles promedio por partido)
        self.attack_strength = self.goals_scored / self.total_matches if self.total_matches > 0 else 1.0
        
        # Fortaleza defensiva (goles concedidos promedio por partido)
        self.defense_strength = self.goals_conceded / self.total_matches if self.total_matches > 0 else 1.0
        
        # Fortaleza general combinada (ponderada)
        # Se usa el ranking mundial (menor número = mejor equipo)
        ranking_weight = max(0, 1 - (self.ranking - 1) / 100)
        elo_weight = self.elo_rating / 2200
        
        self.overall_strength = (ranking_weight * 0.6 + elo_weight * 0.4)
        
        # Normalizar ataque y defensa basado en la fuerza general
        self.attack_strength *= self.overall_strength
        self.defense_strength *= (1 - self.overall_strength * 0.3)
    
    def reset_tournament_stats(self):
        """
        Reinicia las estadísticas del torneo para una nueva simulación
        """
        self.group_points = 0
        self.group_goals_for = 0
        self.group_goals_against = 0
        self.group_goal_diff = 0
        self.group_position = 0
    
    def __str__(self):
        return f"{self.name} (Ranking: {self.ranking}, Elo: {self.elo_rating})"
    
    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def load_from_csv(cls, filepath):
        """
        Carga los equipos desde un archivo CSV
        """
        df = pd.read_csv(filepath)
        teams = []
        
        for _, row in df.iterrows():
            team = cls(
                name=row['team'],
                ranking=row['ranking'],
                elo_rating=row['elo_rating'],
                wins=row['wins'],
                losses=row['losses'],
                draws=row['draws'],
                goals_scored=row['goals_scored'],
                goals_conceded=row['goals_conceded']
            )
            teams.append(team)
        
        return teams