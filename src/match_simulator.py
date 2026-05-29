import numpy as np
from scipy.stats import poisson

class MatchSimulator:
    """
    Simula un partido de fútbol usando distribución de Poisson
    """
    
    def __init__(self, home_advantage=0.15):
        """
        Inicializa el simulador de partidos
        
        Args:
            home_advantage: Ventaja de jugar en casa (factor multiplicador)
        """
        self.home_advantage = home_advantage
    
    def expected_goals(self, team_attack, team_defense, is_home=False):
        """
        Calcula los goles esperados para un equipo
        
        Args:
            team_attack: Fortaleza ofensiva del equipo
            team_defense: Fortaleza defensiva del equipo
            is_home: Si el equipo juega en casa
        
        Returns:
            Goles esperados
        """
        base_goals = team_attack / team_defense
        base_goals = max(0.1, min(3.5, base_goals))
        
        if is_home:
            base_goals *= (1 + self.home_advantage)
        
        return base_goals
    
    def simulate_match(self, team_a, team_b, neutral_ground=True):
        """
        Simula un partido entre dos equipos
        
        Args:
            team_a: Equipo A
            team_b: Equipo B
            neutral_ground: Si es campo neutral o no
        
        Returns:
            Tupla (goles_a, goles_b)
        """
        # Calcular goles esperados
        if neutral_ground:
            expected_a = self.expected_goals(team_a.attack_strength, 
                                             team_b.defense_strength, 
                                             is_home=False)
            expected_b = self.expected_goals(team_b.attack_strength, 
                                             team_a.defense_strength, 
                                             is_home=False)
        else:
            # Con ventaja de local
            expected_a = self.expected_goals(team_a.attack_strength, 
                                             team_b.defense_strength, 
                                             is_home=True)
            expected_b = self.expected_goals(team_b.attack_strength, 
                                             team_a.defense_strength, 
                                             is_home=False)
        
        # Simular goles usando distribución de Poisson
        goals_a = np.random.poisson(expected_a)
        goals_b = np.random.poisson(expected_b)
        
        return goals_a, goals_b
    
    def get_match_result(self, team_a, team_b, neutral_ground=True):
        """
        Simula un partido y devuelve el resultado con información adicional
        
        Returns:
            Diccionario con resultados detallados
        """
        goals_a, goals_b = self.simulate_match(team_a, team_b, neutral_ground)
        
        if goals_a > goals_b:
            winner = team_a
            loser = team_b
            result = 'win'
        elif goals_b > goals_a:
            winner = team_b
            loser = team_a
            result = 'loss'
        else:
            winner = None
            loser = None
            result = 'draw'
        
        return {
            'team_a': team_a.name,
            'team_b': team_b.name,
            'goals_a': goals_a,
            'goals_b': goals_b,
            'result': result,
            'winner': winner.name if winner else None,
            'goals_a_expected': self.expected_goals(team_a.attack_strength, 
                                                    team_b.defense_strength),
            'goals_b_expected': self.expected_goals(team_b.attack_strength, 
                                                    team_a.defense_strength)
        }
    
    def simulate_penalty_shootout(self, team_a, team_b):
        """
        Simula una tanda de penales
        
        Returns:
            Equipo ganador
        """
        # Probabilidad de anotar cada penal (basada en la fuerza del equipo)
        prob_a = 0.65 + (team_a.overall_strength * 0.15)
        prob_b = 0.65 + (team_b.overall_strength * 0.15)
        
        prob_a = min(0.95, max(0.5, prob_a))
        prob_b = min(0.95, max(0.5, prob_b))
        
        # 5 penales por equipo
        score_a = sum([1 for _ in range(5) if np.random.random() < prob_a])
        score_b = sum([1 for _ in range(5) if np.random.random() < prob_b])
        
        # Muerte súbita si es necesario
        round_num = 5
        while score_a == score_b:
            round_num += 1
            score_a += 1 if np.random.random() < prob_a else 0
            score_b += 1 if np.random.random() < prob_b else 0
            
            if round_num > 10:  # Límite de seguridad
                break
        
        return team_a if score_a > score_b else team_b